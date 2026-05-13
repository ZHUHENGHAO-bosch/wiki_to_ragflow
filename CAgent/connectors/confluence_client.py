"""
connectors/confluence_client.py -- Confluence Server/Data Center REST API v1

Pure API wrapper. Uses httpx.AsyncClient with BasicAuth or Bearer Token (PAT).
Supports page content retrieval, child page traversal, attachment download.
PDF export supports two methods:
  - Chrome headless (CDP) — uses Windows SPNEGO for Kerberos environments
  - Native — REST API body.export_view + WeasyPrint (no Chrome needed)
"""
from __future__ import annotations

import asyncio
import base64
import json as _json
import logging
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, unquote, urlparse

import httpx
import websockets
from weasyprint import HTML as WeasyHTML

from config import ConfluenceConfig

logger = logging.getLogger(__name__)

# Chrome executable auto-detection paths (Windows)
_CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
]


class ChromeCdpSession:
    """Chrome DevTools Protocol session — one browser, multiple parallel tabs.

    Usage::

        async with ChromeCdpSession(chrome_path, concurrency=4) as session:
            pdf_bytes = await session.print_page_pdf(url)
    """

    def __init__(self, chrome_path: str, concurrency: int = 4) -> None:
        self._chrome = chrome_path
        self._concurrency = concurrency
        self._proc: asyncio.subprocess.Process | None = None
        self._debug_port: int = 0
        self._semaphore = asyncio.Semaphore(concurrency)
        self._http = httpx.AsyncClient(timeout=10.0)

    # ── Lifecycle ──

    async def __aenter__(self) -> ChromeCdpSession:
        self._proc = await asyncio.create_subprocess_exec(
            self._chrome,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-extensions",
            "--disable-software-rasterizer",
            "--remote-debugging-port=0",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        self._debug_port = await self._parse_debug_port()
        logger.info(f"Chrome CDP started on port {self._debug_port}")
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._http.aclose()
        if self._proc:
            self._proc.terminate()
            try:
                await asyncio.wait_for(self._proc.wait(), timeout=5)
            except asyncio.TimeoutError:
                self._proc.kill()

    async def _parse_debug_port(self) -> int:
        """Read Chrome stderr to find the DevTools debugging port."""
        assert self._proc and self._proc.stderr
        while True:
            line = await asyncio.wait_for(
                self._proc.stderr.readline(), timeout=30
            )
            if not line:
                raise RuntimeError("Chrome exited before reporting debug port")
            text = line.decode(errors="replace")
            if "DevTools listening on" in text:
                m = re.search(r":(\d+)/", text)
                if m:
                    return int(m.group(1))
                raise RuntimeError(f"Cannot parse port from: {text}")

    # ── Tab management ──

    async def _create_tab(self, url: str = "") -> dict[str, Any]:
        """Create a new browser tab via CDP HTTP API."""
        endpoint = f"http://127.0.0.1:{self._debug_port}/json/new"
        if url:
            endpoint += f"?{url}"
        resp = await self._http.put(endpoint)
        resp.raise_for_status()
        return resp.json()

    async def _close_tab(self, tab_id: str) -> None:
        """Close a browser tab via CDP HTTP API."""
        try:
            resp = await self._http.get(
                f"http://127.0.0.1:{self._debug_port}/json/close/{tab_id}"
            )
            resp.raise_for_status()
        except Exception:
            pass  # best-effort cleanup

    # ── CDP WebSocket helpers ──

    @staticmethod
    async def _cdp_send(
        ws: Any,
        method: str,
        params: dict[str, Any] | None = None,
        msg_id: int = 1,
    ) -> dict[str, Any]:
        """Send a CDP command and wait for matching response."""
        payload = {"id": msg_id, "method": method}
        if params:
            payload["params"] = params
        await ws.send(_json.dumps(payload))

        # Read messages until we get the response with matching id
        while True:
            raw = await ws.recv()
            data = _json.loads(raw)
            if data.get("id") == msg_id:
                if "error" in data:
                    raise RuntimeError(
                        f"CDP {method} error: {data['error']}"
                    )
                return data.get("result", {})
            # else: event message, ignore

    @staticmethod
    async def _wait_for_event(
        ws: Any,
        event_name: str,
        timeout: float = 60,
    ) -> dict[str, Any]:
        """Wait for a specific CDP event."""
        deadline = asyncio.get_event_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_event_loop().time()
            if remaining <= 0:
                raise asyncio.TimeoutError(
                    f"Timeout waiting for {event_name}"
                )
            raw = await asyncio.wait_for(ws.recv(), timeout=remaining)
            data = _json.loads(raw)
            if data.get("method") == event_name:
                return data.get("params", {})

    # ── CDP event helpers ──

    @staticmethod
    async def _wait_for_network_idle(
        ws: Any,
        timeout: float = 30,
        idle_time: float = 0.5,
    ) -> None:
        """Wait until no network activity for *idle_time* seconds.

        Listens to Page.lifecycleEvent for 'networkIdle'.  Falls back to
        a short fixed wait if the event never fires (e.g. very simple pages).
        """
        try:
            deadline = asyncio.get_event_loop().time() + timeout
            while True:
                remaining = deadline - asyncio.get_event_loop().time()
                if remaining <= 0:
                    break
                raw = await asyncio.wait_for(ws.recv(), timeout=remaining)
                data = _json.loads(raw)
                if (
                    data.get("method") == "Page.lifecycleEvent"
                    and data.get("params", {}).get("name") == "networkIdle"
                ):
                    # Give a tiny extra breath for late JS rendering
                    await asyncio.sleep(idle_time)
                    return
        except asyncio.TimeoutError:
            pass
        # Fallback: short fixed wait
        await asyncio.sleep(idle_time)

    # ── PDF export ──

    # JS 注入：消除 Confluence 溢出样式，强制表格适应 A4 页宽，
    # 单元格内容自动换行向垂直方向扩展。
    _FIX_OVERFLOW_JS = """(() => {
        // 1. 去掉 table-wrap 容器的 overflow（消除水平滚动条）
        document.querySelectorAll('.table-wrap').forEach(el => {
            el.style.overflow = 'visible';
            el.style.overflowX = 'visible';
        });
        // 2. 表格强制适应页宽，去掉 fixed-width 类，列宽由内容自动分配
        document.querySelectorAll('table').forEach(t => {
            t.style.width = '100%';
            t.classList.remove('fixed-width');
        });
        // 3. 去掉 <col> 上的百分比宽度，让列宽由内容自动决定
        document.querySelectorAll('col[style*="width"]').forEach(c => {
            c.style.removeProperty('width');
        });
        // 4. 单元格自动换行 + 行不跨页
        document.querySelectorAll('td, th').forEach(c => {
            c.style.wordBreak = 'break-all';
            c.style.wordWrap = 'break-word';
            c.style.overflowWrap = 'break-word';
            c.style.verticalAlign = 'top';
        });
        document.querySelectorAll('tr').forEach(r => {
            r.style.breakInside = 'avoid';
            r.style.pageBreakInside = 'avoid';
        });
        // 5. 将 tbody 内只含 th 的首行移入 thead，使表头每页重复
        document.querySelectorAll('table').forEach(table => {
            if (table.querySelector('thead')) return;
            const tbody = table.querySelector('tbody');
            if (!tbody) return;
            const headerRows = [];
            for (const row of [...tbody.rows]) {
                const ths = row.querySelectorAll('th');
                const tds = row.querySelectorAll('td');
                if (ths.length > 0 && tds.length === 0) {
                    headerRows.push(row);
                } else {
                    break;
                }
            }
            if (headerRows.length === 0) return;
            const thead = document.createElement('thead');
            headerRows.forEach(r => thead.appendChild(r));
            table.insertBefore(thead, tbody);
            thead.style.display = 'table-header-group';
        });
        // 6. 去掉 Confluence 内容区的 max-width 限制
        const main = document.getElementById('main-content')
                  || document.getElementById('content')
                  || document.querySelector('.wiki-content');
        if (main) main.style.maxWidth = 'none';
    })()"""

    async def print_page_pdf(self, page_url: str) -> bytes:
        """Navigate to URL in a new tab and export as PDF via CDP.

        A4 横向 + JS 注入强制表格自动换行，内容向垂直方向扩展。
        """
        async with self._semaphore:
            tab_info = await self._create_tab()
            tab_id = tab_info["id"]
            ws_url = tab_info["webSocketDebuggerUrl"]

            try:
                async with websockets.connect(
                    ws_url,
                    max_size=50 * 1024 * 1024,  # 50MB for large PDFs
                    proxy=None,  # bypass system proxy for localhost CDP
                ) as ws:
                    # Enable Page + Lifecycle events
                    await self._cdp_send(ws, "Page.enable", msg_id=1)
                    await self._cdp_send(
                        ws, "Page.setLifecycleEventsEnabled",
                        {"enabled": True},
                        msg_id=2,
                    )

                    # Navigate
                    await self._cdp_send(
                        ws, "Page.navigate",
                        {"url": page_url},
                        msg_id=3,
                    )

                    # Wait for page load
                    await self._wait_for_event(
                        ws, "Page.loadEventFired", timeout=60
                    )

                    # Wait for network idle
                    await self._wait_for_network_idle(ws, timeout=10)

                    # 注入 JS：消除溢出，强制表格适应页宽
                    await self._cdp_send(
                        ws, "Runtime.evaluate",
                        {"expression": self._FIX_OVERFLOW_JS},
                        msg_id=10,
                    )

                    # A4 横向，小页边距
                    MARGIN_INCH = 0.31  # ~8mm
                    result = await self._cdp_send(
                        ws, "Page.printToPDF",
                        {
                            "printBackground": True,
                            "preferCSSPageSize": False,
                            "landscape": True,
                            "paperWidth": 11.69,   # A4 (297mm)
                            "paperHeight": 8.27,   # A4 (210mm)
                            "marginTop": MARGIN_INCH,
                            "marginBottom": MARGIN_INCH,
                            "marginLeft": MARGIN_INCH,
                            "marginRight": MARGIN_INCH,
                        },
                        msg_id=4,
                    )

                    return base64.b64decode(result["data"])
            finally:
                await self._close_tab(tab_id)


class ConfluenceClient:
    """Confluence Server/Data Center REST API v1 client."""

    def __init__(self, config: ConfluenceConfig) -> None:
        self._config = config
        self._base = config.base_url.rstrip("/")
        ctx = config.context_path.rstrip("/")

        # Auth setup -- Basic Auth or Bearer Token (PAT)
        auth = None
        headers: dict[str, str] = {}
        if config.auth_method == "bearer":
            headers["Authorization"] = f"Bearer {config.api_token}"
        elif config.username and config.api_token:
            auth = (config.username, config.api_token)

        self._client = httpx.AsyncClient(
            base_url=f"{self._base}{ctx}/rest/api",
            auth=auth,
            headers=headers,
            verify=config.verify_ssl,
            timeout=config.timeout,
        )

        # Separate client for binary downloads (longer timeout)
        self._download_client = httpx.AsyncClient(
            base_url=f"{self._base}{ctx}",
            auth=auth,
            headers=headers,
            verify=config.verify_ssl,
            timeout=120.0,
        )

        # Global rate limiter: serializes timing of HTTP requests across
        # all concurrent workers to prevent server overload.
        self._rate_lock = asyncio.Lock()
        self._last_request_time: float = 0.0


    # ── Global rate limiter ──

    async def _throttle(self) -> None:
        """Enforce minimum delay between consecutive API requests.

        Serializes the timing across ALL concurrent workers so the server
        never receives requests faster than ``config.request_delay``.
        """
        delay = self._config.request_delay
        if delay <= 0:
            return
        async with self._rate_lock:
            loop = asyncio.get_event_loop()
            elapsed = loop.time() - self._last_request_time
            wait = delay - elapsed
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_request_time = loop.time()

    # ── Page operations ──

    async def get_page(
        self,
        page_id: str,
        expand: str = "body.storage,version,ancestors,children.page",
    ) -> dict[str, Any]:
        """
        Get a single page by ID with body content in storage format.

        Returns page JSON including title, body.storage.value, version, etc.
        """
        await self._throttle()
        resp = await self._client.get(
            f"/content/{page_id}",
            params={"expand": expand},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_child_pages(
        self,
        page_id: str,
        start: int = 0,
        limit: int = 100,
    ) -> dict[str, Any]:
        """
        Get child pages (paginated).

        Confluence Server uses start/limit offset pagination.
        """
        await self._throttle()
        resp = await self._client.get(
            f"/content/{page_id}/child/page",
            params={"start": start, "limit": limit, "expand": "version"},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_all_child_pages(self, page_id: str) -> list[dict[str, Any]]:
        """Get ALL child pages, auto-handling pagination."""
        all_children: list[dict[str, Any]] = []
        start = 0
        limit = 100
        while True:
            data = await self.get_child_pages(page_id, start=start, limit=limit)
            results = data.get("results", [])
            all_children.extend(results)
            if data.get("size", 0) < limit:
                break
            start += limit
        return all_children

    @staticmethod
    def extract_children_from_page(
        page_data: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], bool]:
        """Extract child pages embedded in a get_page() response.

        Returns (children_list, needs_pagination).
        ``needs_pagination`` is True when the embedded result set is full,
        meaning additional pages may exist beyond the first batch.
        """
        children_obj = page_data.get("children", {}).get("page", {})
        results = children_obj.get("results", [])
        size = children_obj.get("size", 0)
        limit = children_obj.get("limit", 25)
        return results, size >= limit

    async def get_attachments(
        self,
        page_id: str,
        start: int = 0,
        limit: int = 25,
    ) -> dict[str, Any]:
        """Get attachments of a page (paginated)."""
        await self._throttle()
        resp = await self._client.get(
            f"/content/{page_id}/child/attachment",
            params={"start": start, "limit": limit},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_all_attachments(self, page_id: str) -> list[dict[str, Any]]:
        """Get ALL attachments, auto-handling pagination."""
        all_attachments: list[dict[str, Any]] = []
        start = 0
        limit = 25
        while True:
            data = await self.get_attachments(page_id, start=start, limit=limit)
            results = data.get("results", [])
            all_attachments.extend(results)
            if data.get("size", 0) < limit:
                break
            start += limit
        return all_attachments

    async def download_attachment(self, download_path: str) -> bytes:
        """
        Download attachment binary.

        download_path: relative path from _links.download
        (e.g. /download/attachments/12345/file.pdf)
        """
        await self._throttle()
        resp = await self._download_client.get(download_path)
        resp.raise_for_status()
        return resp.content

    async def export_page_pdf(self, page_id: str) -> bytes:
        """
        Export a single page as PDF using Chrome headless.

        Confluence's flyingpdf endpoint requires Kerberos (Negotiate) auth
        which PAT tokens cannot satisfy. Chrome headless authenticates via
        the Windows domain session automatically (SPNEGO).

        Returns the PDF binary content.
        """
        chrome = self._find_chrome()
        if not chrome:
            raise RuntimeError(
                "Chrome not found. Install Chrome or set CHROME_PATH env var."
            )

        page_url = (
            f"{self._base}{self._config.context_path.rstrip('/')}"
            f"/pages/viewpage.action?pageId={page_id}"
        )

        # Use a temp file for PDF output
        with tempfile.NamedTemporaryFile(
            suffix=".pdf", delete=False
        ) as tmp:
            tmp_path = tmp.name

        try:
            proc = await asyncio.create_subprocess_exec(
                chrome,
                "--headless",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-extensions",
                "--disable-software-rasterizer",
                f"--print-to-pdf={tmp_path}",
                page_url,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)

            if proc.returncode != 0:
                err_msg = stderr.decode(errors="replace").strip()
                raise RuntimeError(
                    f"Chrome PDF export failed (rc={proc.returncode}): {err_msg}"
                )

            pdf_path = Path(tmp_path)
            if not pdf_path.exists() or pdf_path.stat().st_size == 0:
                raise RuntimeError("Chrome produced empty PDF output")

            pdf_bytes = pdf_path.read_bytes()
            logger.info(
                f"PDF exported via Chrome: page {page_id}, "
                f"{len(pdf_bytes)} bytes"
            )
            return pdf_bytes

        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    async def export_pages_pdf_parallel(
        self,
        page_ids: list[str],
        concurrency: int = 4,
        on_page_done: Callable[[str, int], None] | None = None,
    ) -> dict[str, bytes]:
        """Export multiple pages as PDF in parallel via CDP.

        Args:
            page_ids: List of Confluence page IDs to export.
            concurrency: Max concurrent Chrome tabs.
            on_page_done: Optional callback(page_id, pdf_size) after each page.

        Returns:
            Dict mapping page_id to PDF bytes. Missing keys = failed pages.
        """
        chrome = self._find_chrome()
        if not chrome:
            raise RuntimeError(
                "Chrome not found. Install Chrome or set CHROME_PATH env var."
            )

        results: dict[str, bytes] = {}

        async with ChromeCdpSession(chrome, concurrency) as session:
            async def _export_one(pid: str) -> None:
                url = (
                    f"{self._base}{self._config.context_path.rstrip('/')}"
                    f"/pages/viewpage.action?pageId={pid}"
                )
                try:
                    pdf_bytes = await session.print_page_pdf(url)
                    results[pid] = pdf_bytes
                    logger.info(
                        f"PDF exported via CDP: page {pid}, "
                        f"{len(pdf_bytes)} bytes"
                    )
                    if on_page_done:
                        on_page_done(pid, len(pdf_bytes))
                except Exception as e:
                    logger.error(f"CDP PDF export failed for page {pid}: {e}")

            await asyncio.gather(
                *[_export_one(pid) for pid in page_ids],
                return_exceptions=True,
            )

        return results

    async def export_pages_pdf_stream(
        self,
        page_queue: asyncio.Queue[str | None],
        concurrency: int = 6,
        on_page_done: Callable[[str, int], None] | None = None,
    ) -> dict[str, bytes]:
        """Export pages as PDF, consuming page IDs from an async queue.

        The producer feeds page IDs into *page_queue* as they are discovered.
        A sentinel ``None`` signals that no more pages will be added.
        Up to *concurrency* pages are downloaded simultaneously.

        Returns:
            Dict mapping page_id to PDF bytes. Missing keys = failed pages.
        """
        chrome = self._find_chrome()
        if not chrome:
            raise RuntimeError(
                "Chrome not found. Install Chrome or set CHROME_PATH env var."
            )

        results: dict[str, bytes] = {}
        tasks: list[asyncio.Task[None]] = []

        async with ChromeCdpSession(chrome, concurrency) as session:

            async def _export_one(pid: str) -> None:
                url = (
                    f"{self._base}{self._config.context_path.rstrip('/')}"
                    f"/pages/viewpage.action?pageId={pid}"
                )
                try:
                    pdf_bytes = await session.print_page_pdf(url)
                    results[pid] = pdf_bytes
                    logger.info(
                        f"PDF exported via CDP: page {pid}, "
                        f"{len(pdf_bytes)} bytes"
                    )
                    if on_page_done:
                        on_page_done(pid, len(pdf_bytes))
                except Exception as e:
                    logger.error(f"CDP PDF export failed for page {pid}: {e}")

            # Consume queue until sentinel None
            while True:
                pid = await page_queue.get()
                if pid is None:
                    break
                task = asyncio.create_task(_export_one(pid))
                tasks.append(task)

            # Wait for all in-flight downloads to finish
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

        return results

    @staticmethod
    def _find_chrome() -> str | None:
        """Auto-detect Chrome executable path."""
        # Check env var first
        env_path = os.environ.get("CHROME_PATH")
        if env_path and os.path.isfile(env_path):
            return env_path

        for candidate in _CHROME_CANDIDATES:
            if os.path.isfile(candidate):
                return candidate

        return None

    # ── Native PDF export (REST API export_view + WeasyPrint) ──

    async def _get_export_view_html(self, page_id: str) -> tuple[str, str]:
        """Fetch page content in export_view format (fully rendered HTML).

        Returns (title, html_body).
        """
        await self._throttle()
        resp = await self._client.get(
            f"/content/{page_id}",
            params={"expand": "body.export_view"},
        )
        resp.raise_for_status()
        data = resp.json()
        title = data.get("title", f"page_{page_id}")
        body = data.get("body", {}).get("export_view", {}).get("value", "")
        return title, body

    @staticmethod
    def _estimate_max_columns(html_body: str) -> int:
        """统计 HTML 中所有表格的最大列数（含 colspan）。"""
        max_cols = 0
        for table in re.finditer(
            r"<table[^>]*>(.*?)</table>", html_body, re.DOTALL
        ):
            for row in re.finditer(
                r"<tr[^>]*>(.*?)</tr>", table.group(1), re.DOTALL
            ):
                cols = 0
                for cell in re.finditer(r"<(td|th)[^>]*>", row.group(1)):
                    cm = re.search(
                        r'colspan\s*=\s*["\']?(\d+)', cell.group(0)
                    )
                    cols += int(cm.group(1)) if cm else 1
                max_cols = max(max_cols, cols)
        return max_cols

    @staticmethod
    def _sanitize_html_for_pdf(body: str) -> str:
        """预处理 HTML，消除导致 PDF 截断的溢出样式。

        Confluence 宽表格的两种溢出模式：
        A) 百分比溢出: width: 165% + <col> 百分比宽度 → 浏览器水平滚动
        B) 像素溢出:   width: 3096px + <col> 像素宽度 + fixed-width 类
        PDF 无法滚动，必须消除这些溢出源。
        """
        # 1. 去掉 <table> 上溢出的 width 内联样式（百分比 >100% 或像素值）
        def _fix_table_width(m: re.Match) -> str:
            tag = m.group(0)
            # 百分比 >100%
            w_pct = re.search(r'width\s*:\s*([\d.]+)%', tag)
            if w_pct and float(w_pct.group(1)) > 100:
                tag = re.sub(r'width\s*:\s*[\d.]+%\s*;?\s*', '', tag)
            # 像素宽度（任何固定像素都删除，由 CSS width:100% 接管）
            w_px = re.search(r'width\s*:\s*[\d.]+px', tag)
            if w_px:
                tag = re.sub(r'width\s*:\s*[\d.]+px\s*;?\s*', '', tag)
            # 去掉 fixed-width 类（Confluence 用它启用 table-layout:fixed）
            tag = re.sub(r'\bfixed-width\b\s*', '', tag)
            return tag

        body = re.sub(r'<table[^>]*>', _fix_table_width, body)

        # 2. 去掉 <col> 上的 width（百分比或像素），让列宽由内容自动决定
        body = re.sub(
            r'(<col\b[^/]*?)style="[^"]*width\s*:\s*[\d.]+[^"]*"',
            r'\1',
            body,
        )

        # 3. 去掉 table-wrap 容器上的 overflow 样式
        body = re.sub(
            r'(<div[^>]*class="[^"]*table-wrap[^"]*"[^>]*?)style="[^"]*"',
            r'\1',
            body,
        )

        # 4. 将 <tbody> 内只含 <th> 的首行移入 <thead>，使表头每页重复
        #    Confluence 不生成 <thead>，表头行（全是 <th>）直接放在 <tbody> 内
        def _inject_thead(m: re.Match) -> str:
            tbody_content = m.group(1)
            # 找到连续的只含 <th> 的行（可能有多行表头）
            header_rows: list[str] = []
            remaining = tbody_content
            while True:
                row_m = re.match(
                    r'(\s*<tr[^>]*>.*?</tr>)(.*)',
                    remaining,
                    re.DOTALL,
                )
                if not row_m:
                    break
                row_html = row_m.group(1)
                has_th = bool(re.search(r'<th[\s>]', row_html))
                has_td = bool(re.search(r'<td[\s>]', row_html))
                if has_th and not has_td:
                    header_rows.append(row_html)
                    remaining = row_m.group(2)
                else:
                    break
            if not header_rows:
                return m.group(0)
            thead = "<thead>" + "".join(header_rows) + "</thead>\n"
            return thead + "<tbody>" + remaining

        body = re.sub(
            r'<tbody[^>]*>(.*?)</tbody>',
            _inject_thead,
            body,
            flags=re.DOTALL,
        )
        return body

    def _wrap_export_html(self, title: str, body: str) -> str:
        """Wrap export_view body in a full HTML document with print styles.

        A4 横向 + 小页边距 + table-layout:fixed 强制表格适应页宽，
        单元格内容自动换行向垂直方向扩展，不截断任何数据。
        """
        ctx = self._config.context_path.rstrip("/")
        body = self._sanitize_html_for_pdf(body)
        max_cols = self._estimate_max_columns(body)
        # 列数多时缩小字体以提高信息密度
        font_size = "9px" if max_cols > 12 else "10px" if max_cols > 7 else "12px"
        return (
            "<!DOCTYPE html>\n"
            '<html>\n<head>\n<meta charset="UTF-8">\n'
            f"<title>{title}</title>\n"
            f'<base href="{self._base}{ctx}/">\n'
            "<style>\n"
            "  @page { size: A4 landscape; margin: 8mm; }\n"
            "  body { font-family: -apple-system, BlinkMacSystemFont, "
            "'Segoe UI', Roboto, sans-serif; "
            f"margin: 0; padding: 5px; font-size: {font_size}; }}\n"
            "  img { max-width: 100%; height: auto; }\n"
            "  table { border-collapse: collapse; width: 100%; }\n"
            "  thead { display: table-header-group; }\n"
            "  tr { break-inside: avoid; page-break-inside: avoid; }\n"
            "  td, th { border: 1px solid #ddd; padding: 3px 4px;\n"
            "    word-break: break-all; word-wrap: break-word;\n"
            "    overflow-wrap: break-word; vertical-align: top; }\n"
            "  pre, code { background: #f4f4f4; padding: 2px 4px; "
            f"font-size: {font_size}; white-space: pre-wrap;\n"
            "    word-wrap: break-word; }\n"
            "  pre { padding: 6px; }\n"
            "</style>\n"
            "</head>\n<body>\n"
            f"<h1>{title}</h1>\n{body}\n"
            "</body>\n</html>"
        )

    async def export_page_pdf_native(self, page_id: str) -> bytes:
        """Export a single page as PDF via REST API + WeasyPrint.

        Fetches body.export_view (fully rendered HTML with macros expanded),
        then converts to PDF using WeasyPrint. Reuses the existing REST API
        auth (Basic / Bearer), so no Chrome or Kerberos is needed.

        Returns the PDF binary content.
        """
        title, body = await self._get_export_view_html(page_id)
        if not body:
            logger.warning(
                f"export_view returned empty body for page {page_id}, "
                f"generating title-only placeholder PDF"
            )
            body = "<p><em>（此页面没有正文内容）</em></p>"

        html_doc = self._wrap_export_html(title, body)

        # WeasyPrint: convert HTML string to PDF bytes
        # base_url lets it resolve relative image/CSS URLs
        ctx = self._config.context_path.rstrip("/")
        pdf_bytes = WeasyHTML(
            string=html_doc,
            base_url=f"{self._base}{ctx}/",
        ).write_pdf()

        logger.info(
            f"PDF exported via native: page {page_id}, {len(pdf_bytes)} bytes"
        )
        return pdf_bytes

    async def export_pages_pdf_native_stream(
        self,
        page_queue: asyncio.Queue[str | None],
        concurrency: int = 6,
        on_page_done: Callable[[str, int], None] | None = None,
    ) -> dict[str, bytes]:
        """Export pages as PDF via REST API + WeasyPrint, consuming from queue.

        Same interface as export_pages_pdf_stream (CDP version) — drop-in
        replacement that does not require Chrome.

        HTTP requests are globally rate-limited by ``_throttle()`` in the
        client, so no per-worker delay is needed.  Retry with exponential
        backoff handles transient server errors.

        The producer feeds page IDs into *page_queue* as they are discovered.
        A sentinel ``None`` signals that no more pages will be added.
        Up to *concurrency* pages are converted simultaneously.

        Returns:
            Dict mapping page_id to PDF bytes. Missing keys = failed pages.
        """
        results: dict[str, bytes] = {}
        semaphore = asyncio.Semaphore(concurrency)
        tasks: list[asyncio.Task[None]] = []

        max_retries = getattr(self._config, "max_retries", 2)
        base_delay = max(self._config.request_delay, 1.0)

        async def _export_one(pid: str) -> None:
            async with semaphore:
                last_err: Exception | None = None
                for attempt in range(1 + max_retries):
                    try:
                        if attempt > 0:
                            wait = base_delay * (2 ** attempt)
                            logger.info(
                                f"Retry {attempt}/{max_retries} for page "
                                f"{pid} after {wait:.1f}s"
                            )
                            await asyncio.sleep(wait)
                        pdf_bytes = await self.export_page_pdf_native(pid)
                        results[pid] = pdf_bytes
                        if on_page_done:
                            on_page_done(pid, len(pdf_bytes))
                        return
                    except Exception as e:
                        last_err = e
                # All retries exhausted
                logger.error(
                    f"Native PDF export failed for page {pid} "
                    f"after {1 + max_retries} attempts: {last_err}"
                )

        # Consume queue until sentinel None
        while True:
            pid = await page_queue.get()
            if pid is None:
                break
            task = asyncio.create_task(_export_one(pid))
            tasks.append(task)

        # Wait for all in-flight downloads to finish
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        return results

    async def search_pages(
        self,
        cql: str,
        start: int = 0,
        limit: int = 25,
    ) -> dict[str, Any]:
        """
        Search pages using CQL (Confluence Query Language).

        Example CQL: 'space = "CARSFW" AND type = page'
        """
        await self._throttle()
        resp = await self._client.get(
            "/content/search",
            params={"cql": cql, "start": start, "limit": limit},
        )
        resp.raise_for_status()
        return resp.json()

    # ── URL parsing ──

    @staticmethod
    def parse_page_url(url: str) -> dict[str, str]:
        """
        Parse a Confluence page URL to extract space_key and page_id.

        Supported formats:
        - /confluence/spaces/CARSFW/pages/5446571801/Title
        - /confluence/pages/viewpage.action?pageId=5446571801
        - /confluence/display/CARSFW/Page+Title
        """
        parsed = urlparse(url)
        path = unquote(parsed.path)

        # Format 1: /spaces/{SPACE}/pages/{ID}/...
        m = re.search(r"/spaces/([^/]+)/pages/(\d+)", path)
        if m:
            return {"space_key": m.group(1), "page_id": m.group(2)}

        # Format 2: ?pageId=...
        if parsed.query and "pageId" in parsed.query:
            params = parse_qs(parsed.query)
            page_id = params.get("pageId", [""])[0]
            return {"space_key": "", "page_id": page_id}

        # Format 3: /display/{SPACE}/...
        m = re.search(r"/display/([^/]+)", path)
        if m:
            return {"space_key": m.group(1), "page_id": ""}

        return {"space_key": "", "page_id": ""}

    # ── Lifecycle ──

    async def close(self) -> None:
        """Close HTTP clients."""
        await self._client.aclose()
        await self._download_client.aclose()
