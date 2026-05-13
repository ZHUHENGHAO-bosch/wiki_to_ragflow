"""
services/confluence_downloader.py -- Confluence page tree download orchestration

BFS traversal of child pages, saves content as HTML + metadata JSON,
optionally downloads attachments. Supports resume and cancellation.

PDF mode supports two export methods:
  - "chrome": exports via Chrome headless CDP (Kerberos/SPNEGO)
  - "native": exports via Confluence flyingpdf endpoint (form login, no Chrome)
Both methods merge pages into a single PDF file using pypdf.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

from pypdf import PdfWriter

from connectors.confluence_client import ConfluenceClient
from config import ConfluenceConfig

logger = logging.getLogger(__name__)


@dataclass
class DownloadProgress:
    """Download progress tracker for a single task."""

    task_id: str
    root_page_id: str
    root_page_title: str = ""
    status: str = "running"  # running | completed | failed | cancelled
    total_pages_discovered: int = 0
    pages_downloaded: int = 0
    pages_skipped: int = 0  # already existed (resume)
    pages_failed: int = 0
    attachments_downloaded: int = 0
    attachments_failed: int = 0
    started_at: float = 0.0
    finished_at: float = 0.0
    current_page: str = ""
    errors: list[str] = field(default_factory=list)
    output_dir: str = ""

    @property
    def elapsed_seconds(self) -> float:
        end = self.finished_at or time.time()
        return end - self.started_at if self.started_at else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "root_page_id": self.root_page_id,
            "root_page_title": self.root_page_title,
            "status": self.status,
            "total_pages_discovered": self.total_pages_discovered,
            "pages_downloaded": self.pages_downloaded,
            "pages_skipped": self.pages_skipped,
            "pages_failed": self.pages_failed,
            "attachments_downloaded": self.attachments_downloaded,
            "attachments_failed": self.attachments_failed,
            "elapsed_seconds": round(self.elapsed_seconds, 1),
            "current_page": self.current_page,
            "errors": self.errors[-10:],  # last 10 errors
            "output_dir": self.output_dir,
        }


class ConfluenceDownloader:
    """Orchestrates BFS traversal and download of Confluence page trees."""

    def __init__(
        self,
        client: ConfluenceClient,
        config: ConfluenceConfig,
        ragflow_client: Any | None = None,
    ) -> None:
        self._client = client
        self._config = config
        self._ragflow = ragflow_client
        self._active_tasks: dict[str, DownloadProgress] = {}
        self._semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        self._cancel_flags: dict[str, bool] = {}

    async def start_download(
        self,
        page_url: str | None = None,
        page_id: str | None = None,
        output_dir: str | None = None,
        max_depth: int | None = None,
        download_attachments: bool | None = None,
        save_format: str | None = None,
        resume: bool = True,
        output_filename: str | None = None,
    ) -> str:
        """
        Start a download task. Returns task_id.

        Provide either page_url (parsed to extract page_id) or page_id directly.
        save_format: "html" or "pdf" (default from config).
        """
        # Resolve page_id from URL if needed
        if page_url and not page_id:
            parsed = ConfluenceClient.parse_page_url(page_url)
            page_id = parsed.get("page_id", "")
            if not page_id:
                raise ValueError(f"Cannot extract page_id from URL: {page_url}")

        if not page_id:
            raise ValueError("Either page_url or page_id must be provided")

        # Task parameters
        task_id = f"conf-{page_id}-{int(time.time())}"
        out_dir = output_dir or self._config.default_output_dir
        depth = max_depth if max_depth is not None else self._config.max_depth
        dl_attach = (
            download_attachments
            if download_attachments is not None
            else self._config.download_attachments
        )
        fmt = save_format or self._config.save_format

        progress = DownloadProgress(
            task_id=task_id,
            root_page_id=page_id,
            started_at=time.time(),
            output_dir=out_dir,
        )
        self._active_tasks[task_id] = progress
        self._cancel_flags[task_id] = False

        # Fire and forget -- runs in background
        asyncio.create_task(
            self._download_tree(
                task_id=task_id,
                page_id=page_id,
                output_dir=Path(out_dir),
                max_depth=depth,
                download_attachments=dl_attach,
                save_format=fmt,
                resume=resume,
                progress=progress,
                output_filename=output_filename,
            )
        )

        return task_id

    def cancel_download(self, task_id: str) -> bool:
        """Request cancellation of a running download. Returns True if found."""
        if task_id in self._cancel_flags:
            self._cancel_flags[task_id] = True
            return True
        return False

    def get_progress(self, task_id: str) -> dict[str, Any] | None:
        """Get progress for a specific task."""
        progress = self._active_tasks.get(task_id)
        return progress.to_dict() if progress else None

    def list_tasks(self) -> list[dict[str, Any]]:
        """List all active/recent tasks."""
        return [p.to_dict() for p in self._active_tasks.values()]

    # ── Internal BFS traversal ──

    async def _download_tree(
        self,
        task_id: str,
        page_id: str,
        output_dir: Path,
        max_depth: int,
        download_attachments: bool,
        save_format: str,
        resume: bool,
        progress: DownloadProgress,
        output_filename: str | None = None,
    ) -> None:
        """
        BFS traversal of page tree.

        HTML mode: creates per-page directory tree with content.html + metadata.
        PDF mode: two-phase approach — BFS discovery then parallel CDP download.
        """
        if save_format == "pdf":
            await self._download_tree_pdf(
                task_id, page_id, output_dir, max_depth,
                download_attachments, progress, output_filename,
            )
        elif save_format == "json":
            await self._download_tree_json(
                task_id, page_id, output_dir, max_depth,
                download_attachments, resume, progress,
            )
        else:
            await self._download_tree_html(
                task_id, page_id, output_dir, max_depth,
                download_attachments, resume, progress, output_filename,
            )

    # ── JSON mode: BFS traversal → structured content ──

    async def _download_tree_json(
        self,
        task_id: str,
        page_id: str,
        output_dir: Path,
        max_depth: int,
        download_attachments: bool,
        resume: bool,
        progress: DownloadProgress,
    ) -> None:
        """JSON mode: BFS traversal, parse export_view HTML to structured JSON.

        Incremental: caches per-page JSON in ``_json_cache/`` with version
        metadata.  On re-run, pages whose version hasn't changed are loaded
        from cache instead of re-fetched.  Output files are always
        (re)generated from cache, so deleting output files doesn't trigger
        re-download.
        """
        from services.confluence_html_parser import parse_confluence_html

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            cache_dir = output_dir / "_json_cache"
            cache_dir.mkdir(exist_ok=True)

            queue: list[tuple[str, int]] = [(page_id, 0)]
            visited: set[str] = set()
            children_order: dict[str, list[str]] = {}
            # page_id → {"title": ..., "file": ...}
            tree_pages: dict[str, dict[str, Any]] = {}
            max_retries = getattr(self._config, "max_retries", 2)
            base_delay = max(getattr(self._config, "request_delay", 0.5), 1.0)

            while queue:
                if self._cancel_flags.get(task_id, False):
                    progress.status = "cancelled"
                    progress.finished_at = time.time()
                    return

                current_id, depth = queue.pop(0)
                if current_id in visited:
                    continue
                visited.add(current_id)

                progress.current_page = current_id

                # ── Phase 1: BFS discovery (only need version + children) ──
                _bfs_expand = "version,children.page"
                page_data = None
                for attempt in range(1 + max_retries):
                    try:
                        if attempt > 0:
                            wait = base_delay * (2 ** attempt)
                            logger.info(
                                f"Retry get_page {current_id}: "
                                f"{attempt}/{max_retries}, wait {wait:.1f}s"
                            )
                            await asyncio.sleep(wait)
                        async with self._semaphore:
                            page_data = await self._client.get_page(
                                current_id, expand=_bfs_expand,
                            )
                        break
                    except Exception as e:
                        if attempt == max_retries:
                            progress.pages_failed += 1
                            progress.errors.append(f"Page {current_id}: {e}")
                            logger.warning(
                                f"Failed to fetch page {current_id} "
                                f"after {1 + max_retries} attempts: {e}"
                            )

                if page_data is None:
                    continue

                title = page_data.get("title", f"page_{current_id}")
                safe_title = self._sanitize_filename(title)
                version = page_data.get("version", {}).get("number", 0)

                if not progress.root_page_title:
                    progress.root_page_title = title

                progress.total_pages_discovered += 1

                # Enqueue children early (before cache check)
                if depth < max_depth:
                    await self._extract_children_to_queue(
                        page_data, current_id, depth,
                        visited, queue, progress,
                        children_order,
                    )

                # ── Cache check: version match → skip API re-fetch ──
                cache_prefix = f"{current_id}_"
                cache_json = cache_dir / f"{cache_prefix}{safe_title}.json"
                # 兼容旧命名或标题变更：按前缀查找
                if not cache_json.exists():
                    for f in cache_dir.glob(f"{cache_prefix}*.json"):
                        cache_json = f
                        break

                cached_page_json: dict[str, Any] | None = None
                if cache_json.exists():
                    try:
                        cached = json.loads(
                            cache_json.read_text(encoding="utf-8")
                        )
                        if cached.get("version", 0) >= version:
                            cached_page_json = cached
                            progress.pages_skipped += 1
                            logger.info(
                                f"Cache hit: {title} (v{version})"
                            )
                    except Exception:
                        pass  # corrupt cache → re-fetch

                if cached_page_json is None:
                    # ── Cache miss: fetch full content ──
                    _full_expand = "body.export_view,version,ancestors"
                    full_data = None
                    for attempt in range(1 + max_retries):
                        try:
                            if attempt > 0:
                                wait = base_delay * (2 ** attempt)
                                await asyncio.sleep(wait)
                            async with self._semaphore:
                                full_data = await self._client.get_page(
                                    current_id, expand=_full_expand,
                                )
                            break
                        except Exception as e:
                            if attempt == max_retries:
                                progress.pages_failed += 1
                                progress.errors.append(
                                    f"Page content {current_id}: {e}"
                                )
                                logger.warning(
                                    f"Failed to fetch content {current_id}: {e}"
                                )

                    if full_data is None:
                        continue

                    # Parse export_view HTML → structured content
                    body_html = (
                        full_data.get("body", {})
                        .get("export_view", {})
                        .get("value", "")
                    )
                    content_blocks = parse_confluence_html(body_html)

                    # Fetch attachments metadata
                    attachments_meta: list[dict[str, Any]] = []
                    try:
                        async with self._semaphore:
                            raw_attachments = (
                                await self._client.get_all_attachments(
                                    current_id
                                )
                            )
                        for att in raw_attachments:
                            att_title = att.get("title", "")
                            dl_link = (
                                att.get("_links", {}).get("download", "")
                            )
                            local_path = ""
                            if download_attachments and att_title:
                                local_path = (
                                    f"_attachments/{safe_title}/"
                                    f"{self._sanitize_filename(att_title)}"
                                )
                            attachments_meta.append({
                                "title": att_title,
                                "download_link": dl_link,
                                "local_path": local_path,
                            })
                    except Exception as e:
                        progress.errors.append(
                            f"Attachments metadata {current_id}: {e}"
                        )

                    # Build parent_id
                    ancestors = full_data.get("ancestors", [])
                    parent_id = ancestors[-1]["id"] if ancestors else ""

                    # Download images referenced in content blocks
                    img_dir = output_dir / "_images" / safe_title
                    await self._download_content_images(
                        content_blocks, img_dir, progress,
                    )

                    child_ids = children_order.get(current_id, [])

                    # Build page JSON
                    cached_page_json = {
                        "page_id": current_id,
                        "title": title,
                        "version": version,
                        "url": full_data.get("_links", {}).get("webui", ""),
                        "last_modified": (
                            full_data.get("version", {}).get("when", "")
                        ),
                        "last_modified_by": (
                            full_data.get("version", {})
                            .get("by", {})
                            .get("displayName", "")
                        ),
                        "parent_id": parent_id,
                        "children": child_ids,
                        "content": content_blocks,
                        "attachments": attachments_meta,
                    }

                    # ── Write cache (即时写入，防止中断丢失) ──
                    actual_cache = (
                        cache_dir / f"{current_id}_{safe_title}.json"
                    )
                    # 清理旧命名缓存
                    for old in cache_dir.glob(f"{current_id}_*"):
                        if old != actual_cache:
                            old.unlink(missing_ok=True)
                    actual_cache.write_text(
                        json.dumps(
                            cached_page_json, indent=2, ensure_ascii=False,
                        ),
                        encoding="utf-8",
                    )

                    progress.pages_downloaded += 1
                    logger.info(
                        f"Downloaded (json): {title} "
                        f"({progress.pages_downloaded}/"
                        f"{progress.total_pages_discovered})"
                    )

                    # Download attachments binary (if enabled)
                    if download_attachments:
                        att_dir = output_dir / "_attachments" / safe_title
                        await self._download_attachments(
                            current_id, att_dir, progress,
                        )

                # ── Always write output file (from cache or fresh) ──
                # Update children (may have been discovered after cache write)
                child_ids = children_order.get(current_id, [])
                cached_page_json["children"] = child_ids

                actual_file = output_dir / f"{current_id}_{safe_title}.json"
                # 清理旧命名输出文件
                for old in output_dir.glob(f"{current_id}_*.json"):
                    if old != actual_file and old.name != "_tree.json":
                        old.unlink(missing_ok=True)
                actual_file.write_text(
                    json.dumps(
                        cached_page_json, indent=2, ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )

                tree_pages[current_id] = {
                    "title": title,
                    "children": child_ids,
                    "file": actual_file.name,
                }

            # Write _tree.json
            tree_index = {
                "root_page_id": page_id,
                "root_page_title": progress.root_page_title,
                "total_pages": len(tree_pages),
                "exported_at": datetime.now().isoformat(),
                "pages": tree_pages,
            }
            (output_dir / "_tree.json").write_text(
                json.dumps(tree_index, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            progress.status = "completed"

        except Exception as e:
            progress.status = "failed"
            progress.errors.append(f"Fatal: {e}")
            logger.error(f"Download {task_id} failed: {e}")

        finally:
            progress.finished_at = time.time()
            progress.current_page = ""
            logger.info(
                f"Download {task_id} {progress.status}: "
                f"{progress.pages_downloaded} downloaded, "
                f"{progress.pages_skipped} skipped, "
                f"{progress.pages_failed} failed, "
                f"{progress.attachments_downloaded} attachments"
            )

    # ── PDF mode: two-phase (discover → parallel download → merge) ──

    async def _download_tree_pdf(
        self,
        task_id: str,
        page_id: str,
        output_dir: Path,
        max_depth: int,
        download_attachments: bool,
        progress: DownloadProgress,
        output_filename: str | None = None,
    ) -> None:
        """PDF mode: pipeline — BFS discovery feeds export in parallel.

        Incremental: caches per-page PDFs in ``_pdf_cache/`` with version
        metadata.  On re-run, pages whose version hasn't changed are loaded
        from cache instead of re-exported.
        """
        pdf_writer: PdfWriter | None = None

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            cache_dir = output_dir / "_pdf_cache"
            cache_dir.mkdir(exist_ok=True)
            pdf_writer = PdfWriter()

            # Shared state between producer (BFS) and consumer
            discovered: list[tuple[str, str, str]] = []  # (pid, title, safe)
            page_queue: asyncio.Queue[str | None] = asyncio.Queue()
            titles: dict[str, str] = {}       # pid → title
            versions: dict[str, int] = {}     # pid → version number
            cached_pdf: dict[str, bytes] = {}  # pid → pdf bytes (from cache)
            children_order: dict[str, list[str]] = {}  # 记录树结构
            max_retries = getattr(self._config, "max_retries", 2)
            base_delay = max(getattr(self._config, "request_delay", 0.5), 1.0)

            # ── Producer: BFS discovery (with cache check) ──
            async def _bfs_discover() -> None:
                queue: list[tuple[str, int]] = [(page_id, 0)]
                visited: set[str] = set()

                logger.info("Pipeline: BFS discovery started...")

                while queue:
                    if self._cancel_flags.get(task_id, False):
                        break

                    current_id, depth = queue.pop(0)
                    if current_id in visited:
                        continue
                    visited.add(current_id)

                    progress.current_page = current_id
                    # BFS 只需 title/version/children，不需要 body
                    _bfs_expand = "version,children.page"
                    for attempt in range(1 + max_retries):
                        try:
                            if attempt > 0:
                                wait = base_delay * (2 ** attempt)
                                logger.info(
                                    f"Retry get_page {current_id}: "
                                    f"{attempt}/{max_retries}, wait {wait:.1f}s"
                                )
                                await asyncio.sleep(wait)
                            page_data = await self._client.get_page(
                                current_id, expand=_bfs_expand,
                            )
                            break  # success
                        except Exception as e:
                            if attempt == max_retries:
                                progress.pages_failed += 1
                                progress.errors.append(
                                    f"Page {current_id}: {e}"
                                )
                                logger.warning(
                                    f"Failed to fetch page {current_id} "
                                    f"after {1 + max_retries} attempts: {e}"
                                )
                                page_data = None
                    if page_data is None:
                        continue

                    title = page_data.get("title", f"page_{current_id}")
                    safe_title = self._sanitize_filename(title)
                    version = page_data.get("version", {}).get("number", 0)

                    if not progress.root_page_title:
                        progress.root_page_title = title

                    progress.total_pages_discovered += 1
                    discovered.append((current_id, title, safe_title))
                    titles[current_id] = title
                    versions[current_id] = version

                    # ── Incremental check: use cache if version matches ──
                    cache_prefix = f"{current_id}_"
                    cache_pdf = cache_dir / f"{cache_prefix}{safe_title}.pdf"
                    cache_meta = cache_dir / f"{cache_prefix}{safe_title}.json"
                    # 兼容旧命名或标题变更：按前缀查找
                    if not cache_meta.exists():
                        for f in cache_dir.glob(f"{cache_prefix}*.json"):
                            cache_meta = f
                            cache_pdf = f.with_suffix(".pdf")
                            break
                    if cache_pdf.exists() and cache_meta.exists():
                        try:
                            meta = json.loads(
                                cache_meta.read_text(encoding="utf-8")
                            )
                            if meta.get("version", 0) >= version:
                                cached_pdf[current_id] = cache_pdf.read_bytes()
                                progress.pages_skipped += 1
                                logger.info(
                                    f"Cache hit: {title} (v{version})"
                                )
                                # Don't feed to export queue
                                if depth < max_depth:
                                    await self._extract_children_to_queue(
                                        page_data, current_id, depth,
                                        visited, queue, progress,
                                        children_order,
                                    )
                                continue
                        except Exception:
                            pass  # corrupt cache → re-export

                    # Feed page to export consumer
                    await page_queue.put(current_id)

                    if depth < max_depth:
                        await self._extract_children_to_queue(
                            page_data, current_id, depth,
                            visited, queue, progress,
                            children_order,
                        )

                # Signal consumer: no more pages
                await page_queue.put(None)
                logger.info(
                    f"Pipeline: BFS done, {len(discovered)} pages discovered, "
                    f"{len(cached_pdf)} from cache"
                )

            # ── Consumer callback ──
            def _on_page_done(pid: str, size: int) -> None:
                progress.pages_downloaded += 1
                t = titles.get(pid, pid)
                logger.info(
                    f"Downloaded (pdf): {t} "
                    f"({progress.pages_downloaded}/"
                    f"{progress.total_pages_discovered})"
                )
                # 即时写入缓存，防止中断丢失
                try:
                    safe = self._sanitize_filename(
                        titles.get(pid, f"page_{pid}")
                    )
                    cp = cache_dir / f"{pid}_{safe}.pdf"
                    cm = cache_dir / f"{pid}_{safe}.json"
                    for old in cache_dir.glob(f"{pid}_*"):
                        if old != cp and old != cm:
                            old.unlink(missing_ok=True)
                    # pdf_map 尚未填充，从 stream 的 results 中获取
                    # 此处 size > 0 表示导出成功，pdf bytes 会在
                    # consumer_task 返回后可用；先写 meta 标记版本
                    cm.write_text(
                        json.dumps(
                            {"page_id": pid,
                             "version": versions.get(pid, 0)},
                            ensure_ascii=False,
                        ),
                        encoding="utf-8",
                    )
                except Exception:
                    pass  # best-effort

            if self._cancel_flags.get(task_id, False):
                progress.status = "cancelled"
                progress.finished_at = time.time()
                return

            logger.info(
                f"Pipeline: starting (concurrency="
                f"{self._config.pdf_concurrency})..."
            )

            # Choose export method: native or chrome (CDP)
            export_method = getattr(
                self._config, "pdf_export_method", "chrome"
            )
            if export_method == "native":
                stream_fn = self._client.export_pages_pdf_native_stream
            else:
                stream_fn = self._client.export_pages_pdf_stream

            # Run BFS producer and export consumer concurrently
            consumer_task = asyncio.create_task(
                stream_fn(
                    page_queue=page_queue,
                    concurrency=self._config.pdf_concurrency,
                    on_page_done=_on_page_done,
                )
            )
            await _bfs_discover()
            pdf_map = await consumer_task

            # Write PDF bytes to cache (meta already written in callback)
            for pid in pdf_map:
                safe = self._sanitize_filename(titles.get(pid, f"page_{pid}"))
                cache_pdf = cache_dir / f"{pid}_{safe}.pdf"
                try:
                    cache_pdf.write_bytes(pdf_map[pid])
                except Exception:
                    pass  # best-effort cache write

            # Merge cached + newly exported pages
            all_pdf: dict[str, bytes] = {**cached_pdf, **pdf_map}

            # Record failures
            for pid, title, _ in discovered:
                if pid not in all_pdf:
                    progress.pages_failed += 1
                    progress.errors.append(f"PDF export failed: {title}")

            # ── 按 Confluence 层级 DFS 前序遍历合并 PDF ──
            # 每卷不超过 MAX_PDF_PAGES 页，超出自动分卷
            MAX_PDF_PAGES = 200
            discovered_map = {
                pid: (title, safe) for pid, title, safe in discovered
            }
            dfs_ordered = self._dfs_order(
                page_id, children_order, set(discovered_map.keys()),
            )
            logger.info(
                f"Merging PDFs in DFS tree order "
                f"({len(dfs_ordered)} pages)..."
            )
            for pid in dfs_ordered:
                title, safe_title = discovered_map[pid]
                if pid in all_pdf:
                    pdf_writer.append(BytesIO(all_pdf[pid]))

                if download_attachments:
                    att_dir = output_dir / "_attachments" / safe_title
                    await self._download_attachments(pid, att_dir, progress)

            # Write merged PDF (auto-split volumes if > MAX_PDF_PAGES)
            if len(pdf_writer.pages) > 0:
                name = (
                    output_filename
                    or progress.root_page_title
                    or "confluence_export"
                )
                safe_root = self._sanitize_filename(name)
                date_suffix = datetime.now().strftime("%Y%m%d")
                total_pages = len(pdf_writer.pages)
                merged_paths: list[Path] = []

                if total_pages <= MAX_PDF_PAGES:
                    # 单文件输出
                    merged_path = output_dir / f"{safe_root}_{date_suffix}.pdf"
                    with open(merged_path, "wb") as f:
                        pdf_writer.write(f)
                    merged_paths.append(merged_path)
                else:
                    # 分卷输出
                    vol = 1
                    for start in range(0, total_pages, MAX_PDF_PAGES):
                        end = min(start + MAX_PDF_PAGES, total_pages)
                        vol_writer = PdfWriter()
                        for i in range(start, end):
                            vol_writer.add_page(pdf_writer.pages[i])
                        vol_path = output_dir / (
                            f"{safe_root}_{date_suffix}"
                            f"_vol{vol}.pdf"
                        )
                        with open(vol_path, "wb") as f:
                            vol_writer.write(f)
                        vol_writer.close()
                        merged_paths.append(vol_path)
                        logger.info(
                            f"Volume {vol}: {vol_path.name} "
                            f"({end - start} pages)"
                        )
                        vol += 1

                total_size = sum(p.stat().st_size for p in merged_paths)
                logger.info(
                    f"Merged PDF saved: {len(merged_paths)} file(s), "
                    f"{total_pages} PDF pages, "
                    f"{total_size / 1024:.0f} KB"
                )
                progress.output_dir = str(
                    merged_paths[0] if len(merged_paths) == 1
                    else output_dir
                )

                # RAGFlow auto-upload hook
                if self._ragflow is not None:
                    try:
                        result = await self._ragflow.upload_and_parse(
                            merged_paths
                        )
                        logger.info(
                            f"RAGFlow: {len(result['uploaded'])} uploaded, "
                            f"{result['parse_count']} parsing"
                        )
                    except Exception as e:
                        logger.error(f"RAGFlow auto-upload failed: {e}")
                        progress.errors.append(f"RAGFlow upload: {e}")

            progress.status = "completed"

        except Exception as e:
            progress.status = "failed"
            progress.errors.append(f"Fatal: {e}")
            logger.error(f"Download {task_id} failed: {e}")

        finally:
            if pdf_writer is not None:
                pdf_writer.close()
            progress.finished_at = time.time()
            progress.current_page = ""
            logger.info(
                f"Download {task_id} {progress.status}: "
                f"{progress.pages_downloaded} downloaded, "
                f"{progress.pages_skipped} skipped, "
                f"{progress.pages_failed} failed, "
                f"{progress.attachments_downloaded} attachments"
            )

    async def _extract_children_to_queue(
        self,
        page_data: dict[str, Any],
        page_id: str,
        depth: int,
        visited: set[str],
        queue: list[tuple[str, int]],
        progress: DownloadProgress,
        children_order: dict[str, list[str]] | None = None,
    ) -> None:
        """Extract children from get_page response and enqueue for BFS.

        Uses children already embedded in the page response (no extra API call).
        Only fetches remaining pages via API when pagination is needed (rare).
        Records parent→children mapping in *children_order* for DFS merge.
        """
        children, needs_more = ConfluenceClient.extract_children_from_page(
            page_data
        )
        child_ids = [child["id"] for child in children]
        for cid in child_ids:
            if cid not in visited:
                queue.append((cid, depth + 1))
        if needs_more:
            # 子页面超过嵌入限制，追加获取剩余页面
            start = len(children)
            try:
                while True:
                    data = await self._client.get_child_pages(
                        page_id, start=start,
                    )
                    results = data.get("results", [])
                    for child in results:
                        cid = child["id"]
                        child_ids.append(cid)
                        if cid not in visited:
                            queue.append((cid, depth + 1))
                    if data.get("size", 0) < data.get("limit", 100):
                        break
                    start += len(results)
            except Exception as e:
                progress.errors.append(f"Children of {page_id}: {e}")
                logger.warning(f"Pagination fetch failed for {page_id}: {e}")
        if children_order is not None:
            children_order[page_id] = child_ids

    @staticmethod
    def _dfs_order(
        root_id: str,
        children_map: dict[str, list[str]],
        valid_ids: set[str],
    ) -> list[str]:
        """DFS 前序遍历页面树，返回按层级展开的页面 ID 列表。"""
        result: list[str] = []
        stack = [root_id]
        while stack:
            pid = stack.pop()
            if pid in valid_ids:
                result.append(pid)
            # 逆序入栈，保证第一个子页面最先出栈
            for cid in reversed(children_map.get(pid, [])):
                stack.append(cid)
        return result

    async def _enqueue_children_pdf(
        self,
        page_id: str,
        depth: int,
        visited: set[str],
        queue: list[tuple[str, int]],
        progress: DownloadProgress,
        max_retries: int,
        base_delay: float = 1.0,
    ) -> None:
        """Fetch and enqueue child pages for PDF mode (with retry).

        HTTP rate limiting is handled globally by the client's ``_throttle()``.
        """
        for attempt in range(1 + max_retries):
            try:
                if attempt > 0:
                    wait = base_delay * (2 ** attempt)
                    await asyncio.sleep(wait)
                children = await self._client.get_all_child_pages(page_id)
                for child in children:
                    cid = child["id"]
                    if cid not in visited:
                        queue.append((cid, depth + 1))
                return
            except Exception as e:
                if attempt == max_retries:
                    progress.errors.append(f"Children of {page_id}: {e}")
                    logger.warning(
                        f"Failed to get children of {page_id}: {e}"
                    )

    # ── HTML mode: original BFS traversal ──

    async def _download_tree_html(
        self,
        task_id: str,
        page_id: str,
        output_dir: Path,
        max_depth: int,
        download_attachments: bool,
        resume: bool,
        progress: DownloadProgress,
        output_filename: str | None = None,
    ) -> None:
        """HTML mode: BFS traversal with per-page directory tree."""
        try:
            output_dir.mkdir(parents=True, exist_ok=True)

            queue: list[tuple[str, int, Path]] = [(page_id, 0, output_dir)]
            visited: set[str] = set()

            while queue:
                if self._cancel_flags.get(task_id, False):
                    progress.status = "cancelled"
                    progress.finished_at = time.time()
                    logger.info(f"Download {task_id} cancelled")
                    return

                current_id, depth, parent_path = queue.pop(0)

                if current_id in visited:
                    continue
                visited.add(current_id)

                progress.current_page = current_id
                try:
                    async with self._semaphore:
                        page_data = await self._client.get_page(current_id)
                except Exception as e:
                    progress.pages_failed += 1
                    progress.errors.append(f"Page {current_id}: {e}")
                    logger.warning(f"Failed to fetch page {current_id}: {e}")
                    continue

                title = page_data.get("title", f"page_{current_id}")
                safe_title = self._sanitize_filename(title)

                if not progress.root_page_title:
                    progress.root_page_title = title

                progress.total_pages_discovered += 1

                # Use output_filename for root page directory if provided
                if output_filename and current_id == page_id:
                    page_dir = parent_path / self._sanitize_filename(
                        output_filename
                    )
                else:
                    page_dir = parent_path / safe_title

                # Resume check
                metadata_file = page_dir / "_metadata.json"
                if resume and metadata_file.exists():
                    try:
                        existing = json.loads(
                            metadata_file.read_text(encoding="utf-8")
                        )
                        existing_ver = existing.get("version", 0)
                        current_ver = (
                            page_data.get("version", {}).get("number", 0)
                        )
                        if existing_ver >= current_ver:
                            progress.pages_skipped += 1
                            logger.debug(
                                f"Skipping {title} "
                                f"(v{existing_ver} >= v{current_ver})"
                            )
                            if depth < max_depth:
                                await self._enqueue_children(
                                    current_id, depth, page_dir,
                                    visited, queue, progress,
                                )
                            continue
                    except Exception:
                        pass  # re-download if metadata corrupt

                page_dir.mkdir(parents=True, exist_ok=True)
                await self._save_page(page_data, page_dir)
                progress.pages_downloaded += 1
                logger.info(
                    f"Downloaded (html): {title} "
                    f"({progress.pages_downloaded}/"
                    f"{progress.total_pages_discovered})"
                )

                if download_attachments:
                    await self._download_attachments(
                        current_id, page_dir / "_attachments", progress
                    )

                if depth < max_depth:
                    await self._enqueue_children(
                        current_id, depth, page_dir,
                        visited, queue, progress,
                    )

            progress.status = "completed"

        except Exception as e:
            progress.status = "failed"
            progress.errors.append(f"Fatal: {e}")
            logger.error(f"Download {task_id} failed: {e}")

        finally:
            progress.finished_at = time.time()
            progress.current_page = ""
            logger.info(
                f"Download {task_id} {progress.status}: "
                f"{progress.pages_downloaded} downloaded, "
                f"{progress.pages_skipped} skipped, "
                f"{progress.pages_failed} failed, "
                f"{progress.attachments_downloaded} attachments"
            )

    async def _enqueue_children(
        self,
        page_id: str,
        depth: int,
        page_dir: Path,
        visited: set[str],
        queue: list[tuple[str, int, Path]],
        progress: DownloadProgress,
    ) -> None:
        """Fetch and enqueue child pages."""
        try:
            children = await self._client.get_all_child_pages(page_id)
            for child in children:
                child_id = child["id"]
                if child_id not in visited:
                    queue.append((child_id, depth + 1, page_dir))
        except Exception as e:
            progress.errors.append(f"Children of {page_id}: {e}")
            logger.warning(f"Failed to get children of {page_id}: {e}")

    async def _save_page(
        self,
        page_data: dict[str, Any],
        page_dir: Path,
    ) -> None:
        """Save page content as HTML + metadata JSON (HTML mode only)."""
        title = page_data.get("title", "Untitled")
        version = page_data.get("version", {}).get("number", 0)
        page_id = page_data.get("id", "")

        self._save_page_html(page_data, page_dir)

        # Save metadata
        metadata = {
            "page_id": page_id,
            "title": title,
            "version": version,
            "format": "html",
            "url": page_data.get("_links", {}).get("webui", ""),
            "last_modified": page_data.get("version", {}).get("when", ""),
            "last_modified_by": (
                page_data.get("version", {}).get("by", {}).get("displayName", "")
            ),
        }
        (page_dir / "_metadata.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _save_page_html(
        self, page_data: dict[str, Any], page_dir: Path
    ) -> None:
        """Save page content as HTML file."""
        title = page_data.get("title", "Untitled")
        body_html = (
            page_data.get("body", {}).get("storage", {}).get("value", "")
        )
        html_content = (
            "<!DOCTYPE html>\n"
            '<html>\n<head><meta charset="UTF-8">'
            f"<title>{title}</title></head>\n<body>\n"
            f"<h1>{title}</h1>\n{body_html}\n"
            "</body>\n</html>"
        )
        (page_dir / "content.html").write_text(html_content, encoding="utf-8")

    async def _download_attachments(
        self,
        page_id: str,
        attach_dir: Path,
        progress: DownloadProgress,
    ) -> None:
        """
        Download all attachments for a page into attach_dir.

        The caller is responsible for computing the target directory:
        - HTML mode: page_dir / "_attachments"
        - PDF mode:  output_dir / "_attachments" / safe_page_title
        """
        try:
            attachments = await self._client.get_all_attachments(page_id)
        except Exception as e:
            progress.errors.append(f"Attachments of {page_id}: {e}")
            return

        if not attachments:
            return

        attach_dir.mkdir(parents=True, exist_ok=True)

        for att in attachments:
            filename = att.get("title", "unknown")
            download_link = att.get("_links", {}).get("download", "")
            if not download_link:
                continue

            target = attach_dir / self._sanitize_filename(filename)
            if target.exists():
                continue  # skip already downloaded

            try:
                async with self._semaphore:
                    data = await self._client.download_attachment(download_link)
                target.write_bytes(data)
                progress.attachments_downloaded += 1
            except Exception as e:
                progress.attachments_failed += 1
                progress.errors.append(f"Attachment {filename}: {e}")

    async def _download_content_images(
        self,
        content_blocks: list[dict[str, Any]],
        img_dir: Path,
        progress: DownloadProgress,
    ) -> None:
        """Download images referenced in content blocks and update src to local path.

        Modifies content_blocks in-place: replaces ``src`` with relative local path.
        Only downloads images whose ``src`` is a relative Confluence path
        (e.g. ``/download/attachments/...`` or ``/confluence/download/...``).
        """
        image_blocks = [b for b in content_blocks if b.get("type") == "image" and b.get("src")]
        if not image_blocks:
            return

        img_dir.mkdir(parents=True, exist_ok=True)

        for block in image_blocks:
            src: str = block["src"]

            # 提取下载路径：支持绝对 URL（同域）和相对路径
            download_path = src
            if src.startswith("http"):
                # 从完整 URL 中提取路径部分，去掉 context_path 前缀
                from urllib.parse import urlparse
                parsed = urlparse(src)
                download_path = parsed.path
                ctx = getattr(self._config, "context_path", "")
                if ctx and download_path.startswith(ctx):
                    download_path = download_path[len(ctx):]
                if parsed.query:
                    download_path += "?" + parsed.query

            # 只下载 Confluence 附件/缩略图路径
            if "/download/" not in download_path and "/thumbnails/" not in download_path:
                continue

            # 从 URL 中提取文件名
            # e.g. /download/attachments/123/image.png?version=1 → image.png
            path_part = download_path.split("?")[0]
            filename = path_part.rsplit("/", 1)[-1] if "/" in path_part else "image.png"
            safe_filename = self._sanitize_filename(filename)
            target = img_dir / safe_filename

            if target.exists():
                # 已下载，只更新路径
                block["local_path"] = str(target.relative_to(img_dir.parent.parent))
                continue

            try:
                async with self._semaphore:
                    data = await self._client.download_attachment(download_path)
                target.write_bytes(data)
                block["local_path"] = str(target.relative_to(img_dir.parent.parent))
                progress.attachments_downloaded += 1
                logger.debug(f"Downloaded image: {filename}")
            except Exception as e:
                progress.attachments_failed += 1
                progress.errors.append(f"Image {filename}: {e}")
                logger.warning(f"Failed to download image {filename}: {e}")

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Convert page title to safe directory/file name."""
        safe = re.sub(r'[<>:"/\\|?*]', "_", name)
        safe = safe.strip(". ")
        return safe[:200] if safe else "unnamed"
