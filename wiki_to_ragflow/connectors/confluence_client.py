"""
connectors/confluence_client.py -- Confluence Server/Data Center REST API v1

Pure API wrapper. Uses httpx.AsyncClient with BasicAuth or Bearer Token (PAT).
Supports page content retrieval, child page traversal, attachment download.
"""
from __future__ import annotations

import asyncio
import logging
import re
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

import httpx

from config import ConfluenceConfig

logger = logging.getLogger(__name__)


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
