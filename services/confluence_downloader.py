"""
services/confluence_downloader.py -- Confluence page tree download orchestration

BFS traversal of child pages, saves content as structured JSON or rendered
Markdown. Supports resume / incremental sync via per-page version cache.

Output modes:
  - "json": flat ``<page_id>_<title>.json`` files plus ``_tree.json``
  - "md":   hierarchical tree of ``.md`` / ``_index.md`` files plus
            ``_images/`` and ``_tree.json``
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote

from connectors.confluence_client import ConfluenceClient
from config import ConfluenceConfig

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Tree-layout helpers (Markdown 模式专用)
#
# 设计目标：按 Confluence 的父子关系生成磁盘目录树，"分类页"只生成文件夹，
# "内容页"生成 .md 文件；既有内容又有子页面的页面，文件夹里再放一份 _index.md。
# ─────────────────────────────────────────────────────────────────────────────


# 渲染后判断内容空不空的字符阈值。考虑到 blocks_to_markdown 会自动加上
# H1/Source/Last modified/---/空行等元信息，单纯的"空白页面"渲染出来约 ~80
# 字节左右。这里给到 16 字节做正文阈值（去掉元信息后）。
_EMPTY_BODY_THRESHOLD = 16


def _is_meaningful_content(blocks: list[dict[str, Any]]) -> bool:
    """判断一组内容块渲染出来是否含有"实质性正文"。

    Confluence 里大量"目录页/分类页"导出的 export_view HTML 只有一行空
    paragraph 或一个 TOC 占位，这种页面应当视为"空"，从而仅生成文件夹。
    """
    if not blocks:
        return False
    for block in blocks:
        btype = block.get("type", "")
        if btype == "heading":
            if (block.get("text") or "").strip():
                return True
        elif btype == "paragraph":
            text = (block.get("text") or "").strip()
            # Confluence 偶尔会塞 \xa0 / zero-width 空格，统一过滤
            cleaned = text.replace("\u00a0", "").replace("\u200b", "").strip()
            if len(cleaned) >= _EMPTY_BODY_THRESHOLD:
                return True
            # 短文本但里头嵌了图片/链接也算有内容
            if cleaned and ("![" in text or "](" in text):
                return True
        elif btype in ("image", "table", "code", "list"):
            return True
        elif btype == "macro":
            # toc / children 这类导航宏不算正文
            name = (block.get("name") or "").lower()
            if name not in ("toc", "children", "pagetree"):
                return True
    return False


def _sanitize_folder_name(name: str) -> str:
    """文件夹名清理：去掉 Windows 非法字符并截断长度。

    与 :meth:`ConfluenceDownloader._sanitize_filename` 保持一致的字符集，
    但保留对结尾点/空格的剥离（Windows 不允许目录名以这两者结尾）。
    """
    if not name:
        return "untitled"
    # 与 _sanitize_filename 同集合
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip()
    cleaned = cleaned.rstrip(". ")
    if not cleaned:
        return "untitled"
    # Windows 路径段上限 255，留余量给后续 _images/_index.md
    return cleaned[:120]


def _build_tree_layout(
    root_id: str,
    pages_info: dict[str, dict[str, Any]],
    children_order: dict[str, list[str]],
    output_root: Path,
) -> dict[str, Path | None]:
    """根据父子关系和"是否有正文"规划每个页面的落盘路径。

    Parameters
    ----------
    root_id : str
        BFS 起点页面 id。
    pages_info : dict
        ``page_id`` → ``{"title": str, "safe": str, "has_content": bool}``。
    children_order : dict
        ``page_id`` → 子页面 id 列表（保持 BFS 发现顺序）。
    output_root : Path
        用户传入的 ``--confluence-output`` 目录。

    Returns
    -------
    dict[str, Path | None]
        ``page_id`` → ``Path``（要写的 .md 文件路径）或 ``None``（仅文件夹）。

    布局规则：
    - 有子页面 + 有正文 → 文件夹 ``<safe>/`` + 内部 ``_index.md``
    - 有子页面 + 无正文 → 仅 ``<safe>/`` 文件夹
    - 无子页面 + 有正文 → 父目录下的 ``<safe>.md``
    - 无子页面 + 无正文 → 仍生成 ``<safe>.md``（占位，避免信息丢失）
    """
    result: dict[str, Path | None] = {}

    def visit(pid: str, parent_dir: Path) -> None:
        if pid not in pages_info:
            return
        info = pages_info[pid]
        safe = info["safe"]
        has_content = info.get("has_content", False)
        children = [c for c in children_order.get(pid, []) if c in pages_info]
        has_children = bool(children)

        if has_children:
            page_dir = parent_dir / safe
            result[pid] = (page_dir / "_index.md") if has_content else None
            for cid in children:
                visit(cid, page_dir)
        else:
            result[pid] = parent_dir / f"{safe}.md"

    visit(root_id, output_root)
    return result


_MD_IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def _retarget_image_refs(
    md_text: str,
    md_parent_dir: Path,
    output_root: Path,
) -> str:
    """把渲染后 MD 里所有指向 ``_images/...`` 的图片引用改写成相对 MD 的路径。

    例：MD 位于 ``out/A/B/page.md``，原引用 ``_images/Foo/x.png``（相对
    ``output_root``）→ 改写为 ``../../_images/Foo/x.png``。

    保留外部 URL（``http://...``）和绝对路径不动。
    """
    output_root_abs = output_root.resolve()
    md_parent_abs = md_parent_dir.resolve()

    def _rewrite(match: re.Match[str]) -> str:
        alt, path = match.group(1), match.group(2)
        decoded = unquote(path)
        # 跳过外部 URL / 协议链接
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", decoded):
            return match.group(0)
        # 只处理我们自己写到 _images/ 的本地引用
        if not decoded.startswith("_images/"):
            return match.group(0)
        abs_target = (output_root_abs / decoded).resolve()
        try:
            new_rel = Path(
                os.path.relpath(abs_target, md_parent_abs)
            ).as_posix()
        except ValueError:
            # 跨盘符等极端情况，保持原样
            return match.group(0)
        encoded = quote(new_rel, safe="/:?&=#%~+")
        return f"![{alt}]({encoded})"

    return _MD_IMG_RE.sub(_rewrite, md_text)


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
        discover_only: bool = False,
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
                discover_only=discover_only,
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
        discover_only: bool = False,
    ) -> None:
        """
        BFS traversal of page tree.

        当前仅支持 ``save_format in ("json", "md")``；旧版的 HTML/PDF 直出
        模式已下线，所有路径统一走 ``_download_tree_json``。

        discover_only: 仅做 BFS 发现，不抓正文/图片/写文件。完成后只产出
        ``_tree.json``，用于估算页数和深度。
        """
        if save_format not in ("json", "md"):
            logger.warning(
                f"save_format={save_format!r} 已不再支持，回退为 md。"
            )
            save_format = "md"
        await self._download_tree_json(
            task_id, page_id, output_dir, max_depth,
            download_attachments, resume, progress,
            output_format=save_format,
            discover_only=discover_only,
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
        output_format: str = "json",
        discover_only: bool = False,
    ) -> None:
        """JSON / Markdown mode: BFS traversal, parse export_view HTML to
        structured content blocks.

        Incremental: caches per-page JSON in ``_json_cache/`` with version
        metadata.  On re-run, pages whose version hasn't changed are loaded
        from cache instead of re-fetched.  Output files are always
        (re)generated from cache, so deleting output files doesn't trigger
        re-download.

        ``output_format``:
          - ``"json"``: 输出 ``{page_id}_{title}.json`` (默认)
          - ``"md"``:   输出 ``{page_id}_{title}.md``，由解析后的内容块
                        通过 :func:`blocks_to_markdown` 渲染
        """
        from services.confluence_html_parser import (
            blocks_to_markdown,
            parse_confluence_html,
        )

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

                # ── Discover-only 短路：跳过正文/图片/文件写入 ──
                # 只走 BFS 发现树结构，记录到 tree_pages 后直接进下一轮。
                # _tree.json 仍会在循环结束后写出，方便用户预览整棵树。
                if discover_only:
                    child_ids = children_order.get(current_id, [])
                    tree_pages[current_id] = {
                        "title": title,
                        "safe": safe_title,
                        "depth": depth,
                        # discover-only 不抓正文，无法判定有无内容；
                        # 用是否有子页面近似：有子页面 → 假设是"目录页"，
                        # 没子页面 → 假设是"内容页"。仅用于 _tree.json 提示。
                        "has_content": not bool(child_ids),
                        "children": child_ids,
                        "cached": None,
                        "path": None,
                    }
                    continue

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

                # ── 收集页面信息（暂不落盘 MD/JSON），循环结束后按树状统一写 ──
                # Update children (may have been discovered after cache write)
                child_ids = children_order.get(current_id, [])
                cached_page_json["children"] = child_ids

                content_blocks = cached_page_json.get("content", []) or []
                has_content = _is_meaningful_content(content_blocks)
                tree_pages[current_id] = {
                    "title": title,
                    "safe": safe_title,
                    "depth": depth,
                    "has_content": has_content,
                    "children": child_ids,
                    "cached": cached_page_json,
                    # path 将在 Phase 2 计算后回填，便于 _tree.json 引用
                    "path": None,
                }

            # ─────────────────────────────────────────────────────────────
            # Phase 2: 按发现到的父子关系落盘文件
            # ─────────────────────────────────────────────────────────────
            if not discover_only and output_format == "md":
                # 清理旧的"扁平命名"产物：<page_id>_<title>.md / .json
                # 这些是树状结构改造前的输出，留着会污染。
                # 不动 _tree.json / _json_cache/ / _images/ / _attachments/。
                _flat_re = re.compile(r"^\d+_.*\.(md|json)$")
                for old in output_dir.iterdir():
                    if old.is_file() and _flat_re.match(old.name) \
                            and old.name != "_tree.json":
                        old.unlink(missing_ok=True)

                pages_info = {
                    pid: {
                        "title": info["title"],
                        "safe": info["safe"],
                        "has_content": info["has_content"],
                    }
                    for pid, info in tree_pages.items()
                }
                layout = _build_tree_layout(
                    page_id, pages_info, children_order, output_dir,
                )

                for pid, info in tree_pages.items():
                    md_path = layout.get(pid)
                    info["path"] = (
                        md_path.relative_to(output_dir).as_posix()
                        if md_path else None
                    )
                    if md_path is None:
                        # 纯目录节点（无正文 + 有子页），只建文件夹
                        # 让子节点写入时自然创建即可
                        continue

                    # 单页写入失败（路径过长、非法字符等）只记错，不让整棵树
                    # 一起崩——否则下游 ``_tree.json`` 永远写不出来。
                    try:
                        cached = info["cached"]
                        md_text = blocks_to_markdown(
                            cached.get("content", []),
                            page_title=cached.get("title", ""),
                            page_url=cached.get("url", ""),
                            last_modified=cached.get("last_modified", ""),
                        )
                        md_text = _retarget_image_refs(
                            md_text, md_path.parent, output_dir,
                        )
                        md_path.parent.mkdir(parents=True, exist_ok=True)
                        md_path.write_text(md_text, encoding="utf-8")
                    except Exception as e:
                        progress.pages_failed += 1
                        progress.errors.append(
                            f"Write MD {info['title']!r} → {md_path}: {e}"
                        )
                        logger.warning(
                            f"Skip page {pid} ({info['title']!r}) "
                            f"due to write failure: {e}"
                        )
                        info["path"] = None  # _tree.json 里标记为未落盘

            elif not discover_only and output_format == "json":
                # JSON 模式保持扁平输出（便于机器消费）
                for pid, info in tree_pages.items():
                    cached = info["cached"]
                    safe = info["safe"]
                    actual_file = output_dir / f"{pid}_{safe}.json"
                    for old in output_dir.glob(f"{pid}_*.json"):
                        if old != actual_file and old.name != "_tree.json":
                            old.unlink(missing_ok=True)
                    actual_file.write_text(
                        json.dumps(cached, indent=2, ensure_ascii=False),
                        encoding="utf-8",
                    )
                    info["path"] = actual_file.name

            # Write _tree.json（暴露最终路径，且不携带 cached 内容以免巨大）
            tree_index = {
                "root_page_id": page_id,
                "root_page_title": progress.root_page_title,
                "total_pages": len(tree_pages),
                "exported_at": datetime.now().isoformat(),
                "pages": {
                    pid: {
                        "title": info["title"],
                        "depth": info.get("depth", 0),
                        "has_content": info.get("has_content", False),
                        "children": info.get("children", []),
                        "path": info.get("path"),
                    }
                    for pid, info in tree_pages.items()
                },
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

    async def _download_attachments(
        self,
        page_id: str,
        attach_dir: Path,
        progress: DownloadProgress,
    ) -> None:
        """
        Download all attachments for a page into attach_dir.

        The caller is responsible for computing the target directory,
        e.g. ``output_dir / "_attachments" / safe_page_title``.
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

        Modifies content_blocks in-place:
          - Top-level image blocks: sets ``block["local_path"]``.
          - Table cells: replaces raw ``![alt](src)`` markdown with the local path.

        Only downloads images whose ``src`` is a relative Confluence path
        (e.g. ``/download/attachments/...`` or ``/confluence/download/...``).
        Images referenced inside table cells via inline ``![alt](src)`` are
        also discovered and downloaded.
        """
        # ── 收集所有图片 src（顶层 image block + 表格单元格里的 inline 图片）──
        inline_img_re = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
        all_srcs: list[str] = []
        seen_srcs: set[str] = set()

        for block in content_blocks:
            btype = block.get("type")
            if btype == "image":
                s = block.get("src", "")
                if s and s not in seen_srcs:
                    seen_srcs.add(s)
                    all_srcs.append(s)
            elif btype == "table":
                for row_list in (
                    [block.get("headers", [])] + list(block.get("rows", []) or [])
                ):
                    for cell in row_list:
                        if not isinstance(cell, str):
                            continue
                        for m in inline_img_re.finditer(cell):
                            s = m.group(1)
                            if s and s not in seen_srcs:
                                seen_srcs.add(s)
                                all_srcs.append(s)

        if not all_srcs:
            return

        img_dir.mkdir(parents=True, exist_ok=True)

        # src → local_path（POSIX 风格，跨平台 Markdown 兼容）
        src_to_local: dict[str, str] = {}

        from urllib.parse import urlparse

        base = self._config.base_url.rstrip("/")
        ctx = getattr(self._config, "context_path", "").rstrip("/")

        for src in all_srcs:

            # ── 统一构造绝对 URL ──
            # 让所有下载走 https://... 的完整 URL，httpx 检测到 absolute 就
            # 直接发，不会再和 base_url 做 urljoin 拼接（那是历次错砍/重复
            # 拼接的根源，比如 /confluence/confluence/ 或 /2/download/）。
            if src.startswith("http"):
                abs_url = src
            elif src.startswith("/"):
                abs_url = base + src
            else:
                abs_url = f"{base}{ctx}/{src.lstrip('/')}"

            path_only = urlparse(abs_url).path

            # ── 非附件路径（emoji、特殊 servlet 等）──
            # 既然下载不了，就把它转成"绝对 URL"写进 MD，至少联网时能渲染，
            # 而不是留 "/confluence/..." 那种会被 MD 视为本机根目录的相对引用。
            if "/download/" not in path_only and "/thumbnails/" not in path_only:
                src_to_local[src] = abs_url
                continue

            # ── thumbnail → attachments（thumbnail 在 Bosch 上常 401） ──
            if "/download/thumbnails/" in abs_url:
                abs_url = abs_url.replace(
                    "/download/thumbnails/", "/download/attachments/"
                )
                path_only = urlparse(abs_url).path

            # ── 从 URL 路径里抠文件名，并 URL-decode ──
            filename = path_only.rsplit("/", 1)[-1] if "/" in path_only else "image.png"
            # 不解码会导致磁盘上是字面 "%E5%9B%BE%E5%83%8F.png"，MD 渲染器
            # 又会自动 decode 引用 → 路径对不上 → 显示"图片缺失"。
            decoded = unquote(filename)
            if decoded:
                filename = decoded
            safe_filename = self._sanitize_filename(filename)
            target = img_dir / safe_filename

            # 后续 download_attachment 用 abs_url 调用，httpx 看到 absolute 就直发
            download_path = abs_url

            if target.exists():
                # 已下载，只记录路径映射
                rel = target.relative_to(img_dir.parent.parent)
                src_to_local[src] = rel.as_posix()
                continue

            # 预登记预期的本地路径：即便下载失败，MD 也引用统一的本地占位路径，
            # 而不是保留原始含 query string 的 Confluence URL。这样：
            #   1) MD 渲染时路径规范，不会出现 `image.png?api=v2` 之类的奇怪引用；
            #   2) 用户重跑时下载补齐，那张图自然就能预览出来。
            rel_path = target.relative_to(img_dir.parent.parent).as_posix()
            src_to_local[src] = rel_path

            try:
                async with self._semaphore:
                    data = await self._client.download_attachment(download_path)
                target.write_bytes(data)
                progress.attachments_downloaded += 1
                logger.debug(f"Downloaded image: {filename}")
            except Exception as e:
                progress.attachments_failed += 1
                progress.errors.append(f"Image {filename}: {e}")
                logger.warning(
                    f"Failed to download image {filename}: {e}. "
                    f"MD 仍引用预期路径 {rel_path}（下次重跑可补齐）。"
                )

        if not src_to_local:
            return

        # ── 应用 src → local_path 映射到所有 block ──
        for block in content_blocks:
            btype = block.get("type")
            if btype == "image":
                s = block.get("src", "")
                if s in src_to_local:
                    block["local_path"] = src_to_local[s]
            elif btype == "table":
                headers = block.get("headers", [])
                for i, cell in enumerate(headers):
                    if isinstance(cell, str):
                        new_cell = cell
                        for s, local in src_to_local.items():
                            new_cell = new_cell.replace(s, local)
                        headers[i] = new_cell
                for row in block.get("rows", []) or []:
                    for i, cell in enumerate(row):
                        if isinstance(cell, str):
                            new_cell = cell
                            for s, local in src_to_local.items():
                                new_cell = new_cell.replace(s, local)
                            row[i] = new_cell

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Convert page title to safe directory/file name.

        与模块级 :func:`_sanitize_folder_name` 字符集一致——除 Windows 保留
        字符外，还过滤所有控制字符 ``\\x00-\\x1f``（含 ``\\n`` ``\\r`` ``\\t``）。
        否则一个标题里夹个换行就会让 ``mkdir`` / ``write_text`` 抛 ENOENT。
        """
        safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
        safe = safe.strip(". ")
        return safe[:200] if safe else "unnamed"
