"""connectors/confluence_client.py 单元测试。"""
from __future__ import annotations

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from config import ConfluenceConfig
from connectors.confluence_client import ChromeCdpSession, ConfluenceClient


@pytest.fixture
def config() -> ConfluenceConfig:
    return ConfluenceConfig(
        base_url="https://confluence.test.com",
        context_path="/confluence",
        username="user",
        api_token="token",
        auth_method="basic",
    )


@pytest.fixture
def bearer_config() -> ConfluenceConfig:
    return ConfluenceConfig(
        base_url="https://confluence.test.com",
        context_path="/confluence",
        api_token="my-pat-token",
        auth_method="bearer",
    )


@pytest.fixture
def client(config: ConfluenceConfig) -> ConfluenceClient:
    return ConfluenceClient(config)


# ── URL Parsing Tests ──


class TestParsePageUrl:
    """URL 解析是静态方法，不需要 HTTP。"""

    def test_spaces_pages_format(self) -> None:
        url = "https://inside-docupedia.bosch.com/confluence/spaces/CARSFW/pages/5446571801/Newcomer+s+Handbook"
        result = ConfluenceClient.parse_page_url(url)
        assert result["space_key"] == "CARSFW"
        assert result["page_id"] == "5446571801"

    def test_spaces_pages_format_no_title(self) -> None:
        url = "https://host.com/confluence/spaces/ABC/pages/12345"
        result = ConfluenceClient.parse_page_url(url)
        assert result["space_key"] == "ABC"
        assert result["page_id"] == "12345"

    def test_viewpage_format(self) -> None:
        url = "https://host.com/confluence/pages/viewpage.action?pageId=67890"
        result = ConfluenceClient.parse_page_url(url)
        assert result["page_id"] == "67890"

    def test_display_format(self) -> None:
        url = "https://host.com/confluence/display/MYSPACE/Page+Title"
        result = ConfluenceClient.parse_page_url(url)
        assert result["space_key"] == "MYSPACE"
        assert result["page_id"] == ""

    def test_invalid_url(self) -> None:
        result = ConfluenceClient.parse_page_url("https://example.com/random")
        assert result["page_id"] == ""
        assert result["space_key"] == ""

    def test_url_with_encoded_chars(self) -> None:
        url = "https://host.com/confluence/spaces/TEAM%20A/pages/111/My%20Page"
        result = ConfluenceClient.parse_page_url(url)
        assert result["space_key"] == "TEAM A"
        assert result["page_id"] == "111"


# ── Client Construction ──


class TestClientConstruction:
    def test_basic_auth_client(self, config: ConfluenceConfig) -> None:
        client = ConfluenceClient(config)
        assert client._client is not None
        assert client._download_client is not None

    def test_bearer_auth_client(self, bearer_config: ConfluenceConfig) -> None:
        client = ConfluenceClient(bearer_config)
        assert "Authorization" in client._client.headers
        assert client._client.headers["Authorization"] == "Bearer my-pat-token"


# ── API Methods (mocked) ──


class TestGetPage:
    @pytest.mark.asyncio
    async def test_get_page_success(self, client: ConfluenceClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "123",
            "title": "Test Page",
            "body": {"storage": {"value": "<p>content</p>"}},
            "version": {"number": 1},
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            client._client, "get", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await client.get_page("123")
            assert result["title"] == "Test Page"
            assert result["body"]["storage"]["value"] == "<p>content</p>"

    @pytest.mark.asyncio
    async def test_get_page_custom_expand(self, client: ConfluenceClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "456", "title": "Custom"}
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            client._client, "get", new_callable=AsyncMock, return_value=mock_response
        ) as mock_get:
            await client.get_page("456", expand="body.storage")
            mock_get.assert_called_once_with(
                "/content/456", params={"expand": "body.storage"}
            )


class TestGetAllChildPages:
    @pytest.mark.asyncio
    async def test_single_page(self, client: ConfluenceClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [{"id": "1"}, {"id": "2"}],
            "size": 2,
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            client._client, "get", new_callable=AsyncMock, return_value=mock_response
        ):
            children = await client.get_all_child_pages("root")
            assert len(children) == 2

    @pytest.mark.asyncio
    async def test_pagination(self, client: ConfluenceClient) -> None:
        """验证分页循环直到 size < limit。"""
        page1_resp = MagicMock()
        page1_resp.json.return_value = {
            "results": [{"id": str(i)} for i in range(100)],
            "size": 100,
        }
        page1_resp.raise_for_status = MagicMock()

        page2_resp = MagicMock()
        page2_resp.json.return_value = {
            "results": [{"id": str(i)} for i in range(100, 120)],
            "size": 20,
        }
        page2_resp.raise_for_status = MagicMock()

        with patch.object(
            client._client,
            "get",
            new_callable=AsyncMock,
            side_effect=[page1_resp, page2_resp],
        ):
            children = await client.get_all_child_pages("root")
            assert len(children) == 120

    @pytest.mark.asyncio
    async def test_empty_children(self, client: ConfluenceClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [], "size": 0}
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            client._client, "get", new_callable=AsyncMock, return_value=mock_response
        ):
            children = await client.get_all_child_pages("leaf")
            assert children == []


class TestExtractChildrenFromPage:
    """extract_children_from_page 静态方法测试。"""

    def test_children_present(self) -> None:
        page_data = {
            "children": {"page": {
                "results": [{"id": "a"}, {"id": "b"}],
                "size": 2, "limit": 25,
            }},
        }
        children, needs_more = ConfluenceClient.extract_children_from_page(page_data)
        assert len(children) == 2
        assert children[0]["id"] == "a"
        assert needs_more is False

    def test_needs_pagination(self) -> None:
        page_data = {
            "children": {"page": {
                "results": [{"id": str(i)} for i in range(25)],
                "size": 25, "limit": 25,
            }},
        }
        children, needs_more = ConfluenceClient.extract_children_from_page(page_data)
        assert len(children) == 25
        assert needs_more is True

    def test_no_children_key(self) -> None:
        page_data = {"id": "123", "title": "Leaf"}
        children, needs_more = ConfluenceClient.extract_children_from_page(page_data)
        assert children == []
        assert needs_more is False

    def test_empty_children(self) -> None:
        page_data = {
            "children": {"page": {"results": [], "size": 0, "limit": 25}},
        }
        children, needs_more = ConfluenceClient.extract_children_from_page(page_data)
        assert children == []
        assert needs_more is False


class TestGetAllAttachments:
    @pytest.mark.asyncio
    async def test_attachments(self, client: ConfluenceClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {"title": "file.pdf", "_links": {"download": "/download/att/1/file.pdf"}},
            ],
            "size": 1,
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            client._client, "get", new_callable=AsyncMock, return_value=mock_response
        ):
            attachments = await client.get_all_attachments("123")
            assert len(attachments) == 1
            assert attachments[0]["title"] == "file.pdf"


class TestDownloadAttachment:
    @pytest.mark.asyncio
    async def test_download(self, client: ConfluenceClient) -> None:
        mock_response = MagicMock()
        mock_response.content = b"PDF_CONTENT"
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            client._download_client, "get", new_callable=AsyncMock, return_value=mock_response
        ):
            data = await client.download_attachment("/download/att/1/file.pdf")
            assert data == b"PDF_CONTENT"


class TestSearchPages:
    @pytest.mark.asyncio
    async def test_search(self, client: ConfluenceClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [{"id": "100", "title": "Found"}],
            "size": 1,
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            client._client, "get", new_callable=AsyncMock, return_value=mock_response
        ) as mock_get:
            result = await client.search_pages('space = "TEST"')
            assert result["results"][0]["title"] == "Found"
            mock_get.assert_called_once()


class TestClose:
    @pytest.mark.asyncio
    async def test_close_both_clients(self, client: ConfluenceClient) -> None:
        with patch.object(
            client._client, "aclose", new_callable=AsyncMock
        ) as mock1, patch.object(
            client._download_client, "aclose", new_callable=AsyncMock
        ) as mock2:
            await client.close()
            mock1.assert_called_once()
            mock2.assert_called_once()


# ── _find_chrome Tests ──


class TestFindChrome:
    def test_env_var_chrome_path(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: os.PathLike
    ) -> None:
        """CHROME_PATH 环境变量优先。"""
        fake_chrome = tmp_path / "chrome.exe"
        fake_chrome.write_text("fake")
        monkeypatch.setenv("CHROME_PATH", str(fake_chrome))

        result = ConfluenceClient._find_chrome()
        assert result == str(fake_chrome)

    def test_env_var_nonexistent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """CHROME_PATH 指向不存在的路径时继续搜索候选列表。"""
        monkeypatch.setenv("CHROME_PATH", "/nonexistent/chrome")

        with patch(
            "connectors.confluence_client._CHROME_CANDIDATES", []
        ):
            result = ConfluenceClient._find_chrome()
            assert result is None

    def test_candidate_found(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: os.PathLike
    ) -> None:
        """候选路径中找到 Chrome。"""
        monkeypatch.delenv("CHROME_PATH", raising=False)
        fake_chrome = tmp_path / "chrome.exe"
        fake_chrome.write_text("fake")

        with patch(
            "connectors.confluence_client._CHROME_CANDIDATES",
            [str(fake_chrome)],
        ):
            result = ConfluenceClient._find_chrome()
            assert result == str(fake_chrome)

    def test_no_chrome_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """所有候选路径都不存在时返回 None。"""
        monkeypatch.delenv("CHROME_PATH", raising=False)

        with patch(
            "connectors.confluence_client._CHROME_CANDIDATES",
            ["/no/chrome/here", "/also/no/chrome"],
        ):
            result = ConfluenceClient._find_chrome()
            assert result is None


# ── export_page_pdf Tests ──


class TestExportPagePdf:
    @pytest.mark.asyncio
    async def test_chrome_not_found_raises(self, client: ConfluenceClient) -> None:
        """Chrome 未找到时抛出 RuntimeError。"""
        with patch.object(
            ConfluenceClient, "_find_chrome", return_value=None
        ):
            with pytest.raises(RuntimeError, match="Chrome not found"):
                await client.export_page_pdf("123")

    @pytest.mark.asyncio
    async def test_chrome_nonzero_exit(self, client: ConfluenceClient) -> None:
        """Chrome 返回非零退出码时抛出 RuntimeError。"""
        mock_proc = MagicMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b"Error: crash"))
        mock_proc.returncode = 1

        with patch.object(
            ConfluenceClient, "_find_chrome", return_value="/usr/bin/chrome"
        ), patch(
            "asyncio.create_subprocess_exec",
            new_callable=AsyncMock,
            return_value=mock_proc,
        ):
            with pytest.raises(RuntimeError, match="Chrome PDF export failed"):
                await client.export_page_pdf("123")


# ── export_pages_pdf_parallel Tests ──


class TestExportPagesPdfParallel:
    @pytest.mark.asyncio
    async def test_chrome_not_found_raises(self, client: ConfluenceClient) -> None:
        """Chrome 未找到时抛出 RuntimeError。"""
        with patch.object(
            ConfluenceClient, "_find_chrome", return_value=None
        ):
            with pytest.raises(RuntimeError, match="Chrome not found"):
                await client.export_pages_pdf_parallel(["p1", "p2"])


# ── export_pages_pdf_stream Tests ──


class TestExportPagesPdfStream:
    @pytest.mark.asyncio
    async def test_chrome_not_found_raises(self, client: ConfluenceClient) -> None:
        """Chrome 未找到时抛出 RuntimeError。"""
        queue: asyncio.Queue[str | None] = asyncio.Queue()
        queue.put_nowait(None)

        with patch.object(
            ConfluenceClient, "_find_chrome", return_value=None
        ):
            with pytest.raises(RuntimeError, match="Chrome not found"):
                await client.export_pages_pdf_stream(queue)


# ── ChromeCdpSession Tests ──


class TestChromeCdpSession:
    def test_init(self) -> None:
        """基本初始化。"""
        session = ChromeCdpSession("/usr/bin/chrome", concurrency=4)
        assert session._chrome == "/usr/bin/chrome"
        assert session._concurrency == 4

    def test_default_concurrency(self) -> None:
        """默认并发数为 4。"""
        session = ChromeCdpSession("/usr/bin/chrome")
        assert session._concurrency == 4


# ── Native PDF Export Tests (export_view + WeasyPrint) ──


class TestGetExportViewHtml:
    """_get_export_view_html 测试。"""

    @pytest.mark.asyncio
    async def test_get_export_view(self, client: ConfluenceClient) -> None:
        """成功获取 export_view HTML。"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "123",
            "title": "Test Page",
            "body": {"export_view": {"value": "<p>rendered content</p>"}},
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            client._client, "get", new_callable=AsyncMock, return_value=mock_response
        ) as mock_get:
            title, body = await client._get_export_view_html("123")

        assert title == "Test Page"
        assert body == "<p>rendered content</p>"
        mock_get.assert_called_once_with(
            "/content/123",
            params={"expand": "body.export_view"},
        )

    @pytest.mark.asyncio
    async def test_get_export_view_empty_body(self, client: ConfluenceClient) -> None:
        """export_view 为空时返回空字符串。"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "456",
            "title": "Empty",
            "body": {"export_view": {"value": ""}},
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            client._client, "get", new_callable=AsyncMock, return_value=mock_response
        ):
            title, body = await client._get_export_view_html("456")

        assert title == "Empty"
        assert body == ""


class TestWrapExportHtml:
    """_wrap_export_html 测试。"""

    def test_wrap_produces_valid_html(self, client: ConfluenceClient) -> None:
        result = client._wrap_export_html("My Title", "<p>content</p>")
        assert "<!DOCTYPE html>" in result
        assert "<title>My Title</title>" in result
        assert "<h1>My Title</h1>" in result
        assert "<p>content</p>" in result
        assert "base href=" in result

    def test_wrap_includes_print_styles(self, client: ConfluenceClient) -> None:
        result = client._wrap_export_html("Title", "<p>body</p>")
        assert "@page" in result
        assert "A4 landscape" in result

    def test_wrap_wide_table_auto_layout(self, client: ConfluenceClient) -> None:
        """宽表格用 A4 横向 + auto layout，列宽按内容自动分配。"""
        cols = "<th>c</th>" * 17
        body = f"<table><tr>{cols}</tr></table>"
        result = client._wrap_export_html("Wide", body)
        assert "A4 landscape" in result
        assert "table-layout" not in result  # auto layout（默认值）
        assert "word-wrap: break-word" in result
        assert "font-size: 9px" in result

    def test_sanitize_strips_overflow_width(self) -> None:
        """_sanitize_html_for_pdf 去掉 >100% 的表格宽度和列宽。"""
        body = (
            '<div class="table-wrap" style="overflow: auto;">'
            '<table class="confluenceTable" style="width: 126.88%;">'
            '<colgroup><col style="width: 50%;"/>'
            '<col style="width: 50%;"/></colgroup>'
            '<tr><td>a</td><td>b</td></tr></table></div>'
        )
        result = ConfluenceClient._sanitize_html_for_pdf(body)
        # 表格 width 126.88% 应被移除
        assert "126.88%" not in result
        # col 上的 width 百分比应被移除
        assert 'width: 50%' not in result
        # table-wrap 的 overflow 应被移除
        assert 'overflow: auto' not in result
        # 内容不丢失
        assert "<td>a</td>" in result
        assert "<td>b</td>" in result

    def test_sanitize_strips_pixel_width(self) -> None:
        """_sanitize_html_for_pdf 去掉像素宽度和 fixed-width 类。"""
        body = (
            '<div class="table-wrap">'
            '<table class="wrapped fixed-width confluenceTable" '
            'style="width: 3096.0px;">'
            '<colgroup><col style="width: 56.0px;"/>'
            '<col style="width: 591.0px;"/></colgroup>'
            '<tr><td>x</td><td>y</td></tr></table></div>'
        )
        result = ConfluenceClient._sanitize_html_for_pdf(body)
        # 像素宽度应被移除
        assert "3096.0px" not in result
        assert "56.0px" not in result
        assert "591.0px" not in result
        # fixed-width 类应被移除
        assert "fixed-width" not in result
        # 其他类保留
        assert "wrapped" in result
        assert "confluenceTable" in result
        # 内容不丢失
        assert "<td>x</td>" in result
        assert "<td>y</td>" in result

    def test_sanitize_injects_thead(self) -> None:
        """_sanitize_html_for_pdf 将 tbody 内 th-only 首行移入 thead。"""
        body = (
            '<table><tbody>'
            '<tr><th>A</th><th>B</th></tr>'
            '<tr><td>1</td><td>2</td></tr>'
            '</tbody></table>'
        )
        result = ConfluenceClient._sanitize_html_for_pdf(body)
        assert "<thead>" in result
        assert "</thead>" in result
        # 表头行在 thead 内
        assert "<thead><tr><th>A</th><th>B</th></tr></thead>" in result
        # 数据行仍在 tbody 内
        assert "<td>1</td>" in result
        assert "<td>2</td>" in result

    def test_sanitize_preserves_existing_thead(self) -> None:
        """已有 thead 的表格不应被修改。"""
        body = (
            '<table><thead><tr><th>X</th></tr></thead>'
            '<tbody><tr><td>1</td></tr></tbody></table>'
        )
        result = ConfluenceClient._sanitize_html_for_pdf(body)
        # thead 保持原样
        assert result.count("<thead>") == 1


class TestExportPagePdfNative:
    """export_page_pdf_native 测试 (export_view + WeasyPrint)。"""

    @pytest.mark.asyncio
    async def test_export_success(self, config: ConfluenceConfig) -> None:
        """成功导出 PDF（mock WeasyPrint）。"""
        client = ConfluenceClient(config)
        fake_pdf = b"%PDF-1.4 fake pdf"

        # Mock _get_export_view_html
        with patch.object(
            client, "_get_export_view_html",
            new_callable=AsyncMock,
            return_value=("Test Page", "<p>content</p>"),
        ), patch(
            "connectors.confluence_client.WeasyHTML"
        ) as MockWeasyHTML:
            mock_instance = MagicMock()
            mock_instance.write_pdf.return_value = fake_pdf
            MockWeasyHTML.return_value = mock_instance

            result = await client.export_page_pdf_native("12345")

        assert result == fake_pdf
        MockWeasyHTML.assert_called_once()

        await client.close()

    @pytest.mark.asyncio
    async def test_export_empty_body_generates_placeholder(
        self, config: ConfluenceConfig
    ) -> None:
        """export_view body 为空时生成仅含标题的占位 PDF。"""
        client = ConfluenceClient(config)

        mock_pdf = b"%PDF-placeholder"
        with patch.object(
            client, "_get_export_view_html",
            new_callable=AsyncMock,
            return_value=("Empty Page", ""),
        ), patch(
            "connectors.confluence_client.WeasyHTML"
        ) as mock_weasy:
            mock_weasy.return_value.write_pdf.return_value = mock_pdf
            result = await client.export_page_pdf_native("888")

        assert result == mock_pdf
        # 验证生成的 HTML 包含占位提示
        call_kwargs = mock_weasy.call_args
        html_string = call_kwargs.kwargs.get("string") or call_kwargs[1].get("string")
        assert "Empty Page" in html_string
        assert "此页面没有正文内容" in html_string

        await client.close()

    @pytest.mark.asyncio
    async def test_export_api_error_propagates(
        self, config: ConfluenceConfig
    ) -> None:
        """REST API 错误时异常正常传播。"""
        client = ConfluenceClient(config)

        with patch.object(
            client, "_get_export_view_html",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "Not Found", request=MagicMock(), response=MagicMock()
            ),
        ):
            with pytest.raises(httpx.HTTPStatusError):
                await client.export_page_pdf_native("999")

        await client.close()


# ── Native PDF Stream Export Tests ──


class TestExportPagesPdfNativeStream:
    """export_pages_pdf_native_stream 测试。"""

    @pytest.mark.asyncio
    async def test_stream_export_success(
        self, config: ConfluenceConfig
    ) -> None:
        """队列消费：多个页面全部成功。"""
        client = ConfluenceClient(config)
        fake_pdf = b"%PDF-1.4 page content"

        with patch.object(
            client, "export_page_pdf_native",
            new_callable=AsyncMock,
            return_value=fake_pdf,
        ):
            queue: asyncio.Queue[str | None] = asyncio.Queue()
            queue.put_nowait("p1")
            queue.put_nowait("p2")
            queue.put_nowait("p3")
            queue.put_nowait(None)

            done_pages: list[str] = []

            def on_done(pid: str, size: int) -> None:
                done_pages.append(pid)

            results = await client.export_pages_pdf_native_stream(
                queue, concurrency=2, on_page_done=on_done
            )

        assert set(results.keys()) == {"p1", "p2", "p3"}
        assert all(v == fake_pdf for v in results.values())
        assert set(done_pages) == {"p1", "p2", "p3"}

        await client.close()

    @pytest.mark.asyncio
    async def test_stream_export_partial_failure(
        self, config: ConfluenceConfig
    ) -> None:
        """部分页面导出失败，其余正常。"""
        client = ConfluenceClient(config)
        fake_pdf = b"%PDF-1.4 good"

        async def _mock_export(pid: str) -> bytes:
            if pid == "fail":
                raise RuntimeError("export failed")
            return fake_pdf

        with patch.object(
            client, "export_page_pdf_native",
            new_callable=AsyncMock,
            side_effect=_mock_export,
        ):
            queue: asyncio.Queue[str | None] = asyncio.Queue()
            queue.put_nowait("ok1")
            queue.put_nowait("fail")
            queue.put_nowait("ok2")
            queue.put_nowait(None)

            results = await client.export_pages_pdf_native_stream(
                queue, concurrency=3
            )

        assert "ok1" in results
        assert "ok2" in results
        assert "fail" not in results

        await client.close()

    @pytest.mark.asyncio
    async def test_stream_export_empty_queue(
        self, config: ConfluenceConfig
    ) -> None:
        """空队列（只有 sentinel）不应出错。"""
        client = ConfluenceClient(config)

        queue: asyncio.Queue[str | None] = asyncio.Queue()
        queue.put_nowait(None)

        results = await client.export_pages_pdf_native_stream(queue)
        assert results == {}

        await client.close()
