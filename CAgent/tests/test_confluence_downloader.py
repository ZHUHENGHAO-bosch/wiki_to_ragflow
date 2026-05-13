"""services/confluence_downloader.py 单元测试。"""
from __future__ import annotations

import asyncio
import io
import json
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from config import ConfluenceConfig
from connectors.confluence_client import ConfluenceClient
from services.confluence_downloader import ConfluenceDownloader, DownloadProgress


@pytest.fixture
def config() -> ConfluenceConfig:
    return ConfluenceConfig(
        base_url="https://confluence.test.com",
        context_path="/confluence",
        username="user",
        api_token="token",
        max_depth=2,
        max_concurrent_requests=3,
        download_attachments=True,
        default_output_dir="./test_downloads",
    )


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock(spec=ConfluenceClient)
    client.get_page = AsyncMock()
    client.get_all_child_pages = AsyncMock(return_value=[])
    client.get_all_attachments = AsyncMock(return_value=[])
    client.download_attachment = AsyncMock(return_value=b"data")
    client.close = AsyncMock()
    return client


# ── DownloadProgress Tests ──


class TestDownloadProgress:
    def test_to_dict(self) -> None:
        p = DownloadProgress(task_id="t1", root_page_id="123")
        d = p.to_dict()
        assert d["task_id"] == "t1"
        assert d["root_page_id"] == "123"
        assert d["status"] == "running"

    def test_elapsed_seconds_running(self) -> None:
        p = DownloadProgress(
            task_id="t1", root_page_id="123", started_at=time.time() - 10
        )
        assert p.elapsed_seconds >= 9.0

    def test_elapsed_seconds_finished(self) -> None:
        now = time.time()
        p = DownloadProgress(
            task_id="t1",
            root_page_id="123",
            started_at=now - 5,
            finished_at=now,
        )
        assert abs(p.elapsed_seconds - 5.0) < 0.1

    def test_elapsed_seconds_not_started(self) -> None:
        p = DownloadProgress(task_id="t1", root_page_id="123")
        assert p.elapsed_seconds == 0.0

    def test_errors_capped_in_dict(self) -> None:
        p = DownloadProgress(
            task_id="t1",
            root_page_id="123",
            errors=[f"error-{i}" for i in range(20)],
        )
        d = p.to_dict()
        assert len(d["errors"]) == 10
        assert d["errors"][0] == "error-10"  # last 10


# ── Sanitize Filename Tests ──


class TestSanitizeFilename:
    def test_normal_name(self) -> None:
        assert ConfluenceDownloader._sanitize_filename("Normal Title") == "Normal Title"

    def test_special_chars(self) -> None:
        assert ConfluenceDownloader._sanitize_filename('a/b:c*d?"e<f>g|h') == "a_b_c_d__e_f_g_h"

    def test_empty_string(self) -> None:
        assert ConfluenceDownloader._sanitize_filename("") == "unnamed"

    def test_dots_only(self) -> None:
        assert ConfluenceDownloader._sanitize_filename("...") == "unnamed"

    def test_long_name(self) -> None:
        long_name = "x" * 300
        result = ConfluenceDownloader._sanitize_filename(long_name)
        assert len(result) <= 200

    def test_backslash(self) -> None:
        assert ConfluenceDownloader._sanitize_filename("path\\name") == "path_name"


# ── Start Download Tests ──


class TestStartDownload:
    @pytest.mark.asyncio
    async def test_from_url(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        downloader = ConfluenceDownloader(mock_client, config)
        mock_client.get_page.return_value = {
            "id": "123",
            "title": "Root",
            "body": {"storage": {"value": "<p>hello</p>"}},
            "version": {"number": 1, "when": "", "by": {}},
            "_links": {"webui": "/pages/123"},
        }

        task_id = await downloader.start_download(
            page_url="https://host.com/confluence/spaces/SP/pages/123/Root",
            output_dir=str(tmp_path),
        )
        assert task_id.startswith("conf-123-")

        # Wait for background task to finish
        await asyncio.sleep(0.5)

        progress = downloader.get_progress(task_id)
        assert progress is not None
        assert progress["status"] in ("completed", "running")

    @pytest.mark.asyncio
    async def test_from_page_id(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        downloader = ConfluenceDownloader(mock_client, config)
        mock_client.get_page.return_value = {
            "id": "456",
            "title": "Direct",
            "body": {"storage": {"value": ""}},
            "version": {"number": 1, "when": "", "by": {}},
            "_links": {},
        }

        task_id = await downloader.start_download(
            page_id="456",
            output_dir=str(tmp_path),
        )
        assert task_id.startswith("conf-456-")

    @pytest.mark.asyncio
    async def test_missing_url_and_id(
        self, mock_client: MagicMock, config: ConfluenceConfig
    ) -> None:
        downloader = ConfluenceDownloader(mock_client, config)
        with pytest.raises(ValueError, match="Either page_url or page_id"):
            await downloader.start_download()

    @pytest.mark.asyncio
    async def test_invalid_url(
        self, mock_client: MagicMock, config: ConfluenceConfig
    ) -> None:
        downloader = ConfluenceDownloader(mock_client, config)
        with pytest.raises(ValueError, match="Cannot extract page_id"):
            await downloader.start_download(page_url="https://example.com/random")


# ── Cancel Download Tests ──


class TestCancelDownload:
    def test_cancel_existing(
        self, mock_client: MagicMock, config: ConfluenceConfig
    ) -> None:
        downloader = ConfluenceDownloader(mock_client, config)
        downloader._cancel_flags["t1"] = False
        assert downloader.cancel_download("t1") is True
        assert downloader._cancel_flags["t1"] is True

    def test_cancel_nonexistent(
        self, mock_client: MagicMock, config: ConfluenceConfig
    ) -> None:
        downloader = ConfluenceDownloader(mock_client, config)
        assert downloader.cancel_download("no-such") is False


# ── List Tasks Tests ──


class TestListTasks:
    def test_empty_list(
        self, mock_client: MagicMock, config: ConfluenceConfig
    ) -> None:
        downloader = ConfluenceDownloader(mock_client, config)
        assert downloader.list_tasks() == []

    def test_with_tasks(
        self, mock_client: MagicMock, config: ConfluenceConfig
    ) -> None:
        downloader = ConfluenceDownloader(mock_client, config)
        downloader._active_tasks["t1"] = DownloadProgress(
            task_id="t1", root_page_id="123"
        )
        tasks = downloader.list_tasks()
        assert len(tasks) == 1
        assert tasks[0]["task_id"] == "t1"


# ── Download Tree (integration-style, mocked HTTP) ──


class TestDownloadTree:
    @pytest.mark.asyncio
    async def test_download_single_page(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """下载单个页面，验证文件输出。"""
        mock_client.get_page.return_value = {
            "id": "100",
            "title": "Test Page",
            "body": {"storage": {"value": "<p>Hello World</p>"}},
            "version": {"number": 3, "when": "2025-01-01", "by": {"displayName": "Alice"}},
            "_links": {"webui": "/spaces/SP/pages/100"},
        }

        downloader = ConfluenceDownloader(mock_client, config)
        task_id = await downloader.start_download(
            page_id="100",
            output_dir=str(tmp_path),
            max_depth=0,  # no children
        )

        # Wait for task completion
        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress is not None
        assert progress["status"] == "completed"
        assert progress["pages_downloaded"] == 1

        # Verify files
        page_dir = tmp_path / "Test Page"
        assert (page_dir / "content.html").exists()
        assert (page_dir / "_metadata.json").exists()

        metadata = json.loads((page_dir / "_metadata.json").read_text(encoding="utf-8"))
        assert metadata["page_id"] == "100"
        assert metadata["title"] == "Test Page"
        assert metadata["version"] == 3

    @pytest.mark.asyncio
    async def test_download_with_children(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """下载页面树（1 级子页面）。"""

        def mock_get_page(page_id, **kwargs):
            pages = {
                "root": {
                    "id": "root",
                    "title": "Root",
                    "body": {"storage": {"value": "<p>root</p>"}},
                    "version": {"number": 1, "when": "", "by": {}},
                    "_links": {},
                },
                "child1": {
                    "id": "child1",
                    "title": "Child One",
                    "body": {"storage": {"value": "<p>child1</p>"}},
                    "version": {"number": 1, "when": "", "by": {}},
                    "_links": {},
                },
            }
            return pages.get(page_id, pages["root"])

        mock_client.get_page = AsyncMock(side_effect=mock_get_page)
        mock_client.get_all_child_pages = AsyncMock(
            side_effect=lambda pid: [{"id": "child1"}] if pid == "root" else []
        )

        downloader = ConfluenceDownloader(mock_client, config)
        task_id = await downloader.start_download(
            page_id="root",
            output_dir=str(tmp_path),
            max_depth=1,
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "completed"
        assert progress["pages_downloaded"] == 2

    @pytest.mark.asyncio
    async def test_resume_skips_existing(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """断点续传：跳过已下载且版本相同的页面。"""
        # Pre-create metadata file
        page_dir = tmp_path / "Existing Page"
        page_dir.mkdir()
        (page_dir / "_metadata.json").write_text(
            json.dumps({"page_id": "200", "version": 5}), encoding="utf-8"
        )
        (page_dir / "content.html").write_text("<html>old</html>", encoding="utf-8")

        mock_client.get_page.return_value = {
            "id": "200",
            "title": "Existing Page",
            "body": {"storage": {"value": "<p>same</p>"}},
            "version": {"number": 5, "when": "", "by": {}},
            "_links": {},
        }

        downloader = ConfluenceDownloader(mock_client, config)
        task_id = await downloader.start_download(
            page_id="200",
            output_dir=str(tmp_path),
            max_depth=0,
            resume=True,
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["pages_skipped"] == 1
        assert progress["pages_downloaded"] == 0

        # Content should NOT be overwritten
        content = (page_dir / "content.html").read_text(encoding="utf-8")
        assert content == "<html>old</html>"

    @pytest.mark.asyncio
    async def test_page_fetch_failure(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """页面获取失败时记录错误并继续。"""
        mock_client.get_page = AsyncMock(side_effect=Exception("Connection refused"))

        downloader = ConfluenceDownloader(mock_client, config)
        task_id = await downloader.start_download(
            page_id="999",
            output_dir=str(tmp_path),
            max_depth=0,
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["pages_failed"] == 1
        assert len(progress["errors"]) > 0

    @pytest.mark.asyncio
    async def test_output_filename_html_mode(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """output_filename 参数控制 HTML 模式根目录名。"""
        mock_client.get_page.return_value = {
            "id": "300",
            "title": "Original Title",
            "body": {"storage": {"value": "<p>content</p>"}},
            "version": {"number": 1, "when": "", "by": {}},
            "_links": {},
        }

        downloader = ConfluenceDownloader(mock_client, config)
        task_id = await downloader.start_download(
            page_id="300",
            output_dir=str(tmp_path),
            max_depth=0,
            save_format="html",
            output_filename="自定义名称",
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "completed"

        # 根目录应使用 output_filename 而非页面标题
        custom_dir = tmp_path / "自定义名称"
        assert custom_dir.exists(), f"Expected dir '自定义名称', got: {list(tmp_path.iterdir())}"
        assert (custom_dir / "content.html").exists()
        assert not (tmp_path / "Original Title").exists()

    @pytest.mark.asyncio
    async def test_output_filename_pdf_mode(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """output_filename 参数控制 PDF 合并文件名（使用流水线 CDP 下载）。"""
        mock_client.get_page.return_value = {
            "id": "400",
            "title": "PDF Page Title",
            "body": {"storage": {"value": ""}},
            "version": {"number": 1, "when": "", "by": {}},
            "_links": {},
        }
        # 返回一个极简的合法 PDF
        minimal_pdf = (
            b"%PDF-1.0\n1 0 obj<</Pages 2 0 R/Type/Catalog>>endobj\n"
            b"2 0 obj<</Kids[3 0 R]/Count 1/Type/Pages>>endobj\n"
            b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n"
            b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n"
            b"0000000058 00000 n \n0000000115 00000 n \n"
            b"trailer<</Root 1 0 R/Size 4>>\nstartxref\n190\n%%EOF"
        )

        # Mock stream-based PDF export: consume queue then return results
        async def _mock_stream(page_queue, concurrency=6, on_page_done=None):
            results = {}
            while True:
                pid = await page_queue.get()
                if pid is None:
                    break
                results[pid] = minimal_pdf
                if on_page_done:
                    on_page_done(pid, len(minimal_pdf))
            return results

        mock_client.export_pages_pdf_stream = AsyncMock(side_effect=_mock_stream)

        downloader = ConfluenceDownloader(mock_client, config)
        task_id = await downloader.start_download(
            page_id="400",
            output_dir=str(tmp_path),
            max_depth=0,
            save_format="pdf",
            output_filename="我的文档",
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "completed"

        # PDF 文件应使用 output_filename + 日期后缀
        date_suffix = datetime.now().strftime("%Y%m%d")
        expected_pdf = tmp_path / f"我的文档_{date_suffix}.pdf"
        assert expected_pdf.exists(), f"Expected '我的文档_{date_suffix}.pdf', got: {list(tmp_path.iterdir())}"
        # 不应存在以页面标题命名的 PDF
        assert not (tmp_path / "PDF Page Title.pdf").exists()

    @pytest.mark.asyncio
    async def test_output_filename_none_uses_title(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """output_filename 为 None 时使用页面标题（回退行为不变）。"""
        mock_client.get_page.return_value = {
            "id": "500",
            "title": "Fallback Title",
            "body": {"storage": {"value": "<p>data</p>"}},
            "version": {"number": 1, "when": "", "by": {}},
            "_links": {},
        }

        downloader = ConfluenceDownloader(mock_client, config)
        task_id = await downloader.start_download(
            page_id="500",
            output_dir=str(tmp_path),
            max_depth=0,
            save_format="html",
            output_filename=None,  # 不指定
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "completed"
        assert (tmp_path / "Fallback Title").exists()


# ── RAGFlow Auto-Upload Hook Tests ──


class TestRAGFlowHook:
    """PDF 模式下 RAGFlow 自动上传钩子测试。"""

    @staticmethod
    def _minimal_pdf() -> bytes:
        return (
            b"%PDF-1.0\n1 0 obj<</Pages 2 0 R/Type/Catalog>>endobj\n"
            b"2 0 obj<</Kids[3 0 R]/Count 1/Type/Pages>>endobj\n"
            b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n"
            b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n"
            b"0000000058 00000 n \n0000000115 00000 n \n"
            b"trailer<</Root 1 0 R/Size 4>>\nstartxref\n190\n%%EOF"
        )

    @staticmethod
    async def _mock_pdf_stream(page_queue, concurrency=6, on_page_done=None):
        """模拟 export_pages_pdf_stream：消费队列并返回 PDF bytes。"""
        minimal_pdf = TestRAGFlowHook._minimal_pdf()
        results = {}
        while True:
            pid = await page_queue.get()
            if pid is None:
                break
            results[pid] = minimal_pdf
            if on_page_done:
                on_page_done(pid, len(minimal_pdf))
        return results

    @pytest.mark.asyncio
    async def test_ragflow_hook_called_on_pdf_success(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """PDF 合并后自动调用 RAGFlow upload_and_parse。"""
        mock_client.get_page.return_value = {
            "id": "600",
            "title": "Hook Test",
            "body": {"storage": {"value": ""}},
            "version": {"number": 1, "when": "", "by": {}},
            "_links": {},
        }
        mock_client.export_pages_pdf_stream = AsyncMock(
            side_effect=self._mock_pdf_stream
        )

        mock_ragflow = AsyncMock()
        mock_ragflow.upload_and_parse = AsyncMock(
            return_value={"uploaded": ["doc-1"], "parse_count": 1}
        )

        downloader = ConfluenceDownloader(
            mock_client, config, ragflow_client=mock_ragflow
        )
        task_id = await downloader.start_download(
            page_id="600",
            output_dir=str(tmp_path),
            max_depth=0,
            save_format="pdf",
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "completed"
        mock_ragflow.upload_and_parse.assert_called_once()
        # 验证传入的是 Path 列表
        call_args = mock_ragflow.upload_and_parse.call_args[0][0]
        assert len(call_args) == 1
        assert str(call_args[0]).endswith(".pdf")

    @pytest.mark.asyncio
    async def test_ragflow_hook_failure_does_not_affect_status(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """RAGFlow 上传失败不影响下载状态（仍为 completed）。"""
        mock_client.get_page.return_value = {
            "id": "601",
            "title": "Hook Fail Test",
            "body": {"storage": {"value": ""}},
            "version": {"number": 1, "when": "", "by": {}},
            "_links": {},
        }
        mock_client.export_pages_pdf_stream = AsyncMock(
            side_effect=self._mock_pdf_stream
        )

        mock_ragflow = AsyncMock()
        mock_ragflow.upload_and_parse = AsyncMock(
            side_effect=Exception("RAGFlow connection timeout")
        )

        downloader = ConfluenceDownloader(
            mock_client, config, ragflow_client=mock_ragflow
        )
        task_id = await downloader.start_download(
            page_id="601",
            output_dir=str(tmp_path),
            max_depth=0,
            save_format="pdf",
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "completed"  # 不受 RAGFlow 失败影响
        assert any("RAGFlow" in e for e in progress["errors"])

    @pytest.mark.asyncio
    async def test_no_ragflow_hook_when_none(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """ragflow_client=None 时不触发上传。"""
        mock_client.get_page.return_value = {
            "id": "602",
            "title": "No Hook",
            "body": {"storage": {"value": ""}},
            "version": {"number": 1, "when": "", "by": {}},
            "_links": {},
        }
        mock_client.export_pages_pdf_stream = AsyncMock(
            side_effect=self._mock_pdf_stream
        )

        downloader = ConfluenceDownloader(
            mock_client, config, ragflow_client=None
        )
        task_id = await downloader.start_download(
            page_id="602",
            output_dir=str(tmp_path),
            max_depth=0,
            save_format="pdf",
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "completed"
        assert not any("RAGFlow" in e for e in progress["errors"])


# ── Attachment Download Tests ──


class TestAttachmentDownload:
    @pytest.mark.asyncio
    async def test_download_attachments_success(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """附件成功下载。"""
        mock_client.get_page.return_value = {
            "id": "700",
            "title": "Attach Page",
            "body": {"storage": {"value": "<p>content</p>"}},
            "version": {"number": 1, "when": "", "by": {}},
            "_links": {},
        }
        mock_client.get_all_attachments = AsyncMock(
            return_value=[
                {
                    "title": "diagram.png",
                    "_links": {"download": "/download/att/700/diagram.png"},
                },
                {
                    "title": "spec.pdf",
                    "_links": {"download": "/download/att/700/spec.pdf"},
                },
            ]
        )
        mock_client.download_attachment = AsyncMock(return_value=b"binary-data")

        downloader = ConfluenceDownloader(mock_client, config)
        task_id = await downloader.start_download(
            page_id="700",
            output_dir=str(tmp_path),
            max_depth=0,
            download_attachments=True,
            save_format="html",
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "completed"
        assert progress["attachments_downloaded"] == 2

        att_dir = tmp_path / "Attach Page" / "_attachments"
        assert (att_dir / "diagram.png").exists()
        assert (att_dir / "spec.pdf").exists()

    @pytest.mark.asyncio
    async def test_attachment_download_failure(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """附件下载失败时记录错误但继续。"""
        mock_client.get_page.return_value = {
            "id": "701",
            "title": "Fail Attach",
            "body": {"storage": {"value": ""}},
            "version": {"number": 1, "when": "", "by": {}},
            "_links": {},
        }
        mock_client.get_all_attachments = AsyncMock(
            return_value=[
                {
                    "title": "broken.pdf",
                    "_links": {"download": "/download/att/701/broken.pdf"},
                },
            ]
        )
        mock_client.download_attachment = AsyncMock(
            side_effect=Exception("Download timeout")
        )

        downloader = ConfluenceDownloader(mock_client, config)
        task_id = await downloader.start_download(
            page_id="701",
            output_dir=str(tmp_path),
            max_depth=0,
            download_attachments=True,
            save_format="html",
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "completed"
        assert progress["attachments_failed"] == 1
        assert progress["pages_downloaded"] == 1

    @pytest.mark.asyncio
    async def test_no_attachments_when_disabled(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """download_attachments=False 时跳过附件。"""
        mock_client.get_page.return_value = {
            "id": "702",
            "title": "No Attach",
            "body": {"storage": {"value": ""}},
            "version": {"number": 1, "when": "", "by": {}},
            "_links": {},
        }
        mock_client.get_all_attachments = AsyncMock(
            return_value=[
                {"title": "file.pdf", "_links": {"download": "/dl/file.pdf"}},
            ]
        )

        downloader = ConfluenceDownloader(mock_client, config)
        task_id = await downloader.start_download(
            page_id="702",
            output_dir=str(tmp_path),
            max_depth=0,
            download_attachments=False,
            save_format="html",
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["attachments_downloaded"] == 0
        # get_all_attachments 不应被调用
        mock_client.get_all_attachments.assert_not_called()


# ── Cancel During Download Tests ──


class TestCancelDuringDownload:
    @pytest.mark.asyncio
    async def test_cancel_html_mode(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """HTML 模式下取消下载。"""
        call_count = 0

        async def slow_get_page(page_id, **kwargs):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.3)
            return {
                "id": page_id,
                "title": f"Page {page_id}",
                "body": {"storage": {"value": ""}},
                "version": {"number": 1, "when": "", "by": {}},
                "_links": {},
            }

        mock_client.get_page = AsyncMock(side_effect=slow_get_page)
        mock_client.get_all_child_pages = AsyncMock(
            side_effect=lambda pid: [{"id": f"child-{i}"} for i in range(5)]
            if pid == "root"
            else []
        )

        downloader = ConfluenceDownloader(mock_client, config)
        task_id = await downloader.start_download(
            page_id="root",
            output_dir=str(tmp_path),
            max_depth=1,
            save_format="html",
        )

        # 等一小段后触发取消
        await asyncio.sleep(0.5)
        assert downloader.cancel_download(task_id) is True

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "cancelled"
        # 应该没有下载完所有 6 个页面
        assert progress["pages_downloaded"] < 6


# ── PDF Mode Multi-Page Tests ──


class TestPdfModeMultiPage:
    @staticmethod
    def _minimal_pdf() -> bytes:
        return (
            b"%PDF-1.0\n1 0 obj<</Pages 2 0 R/Type/Catalog>>endobj\n"
            b"2 0 obj<</Kids[3 0 R]/Count 1/Type/Pages>>endobj\n"
            b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n"
            b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n"
            b"0000000058 00000 n \n0000000115 00000 n \n"
            b"trailer<</Root 1 0 R/Size 4>>\nstartxref\n190\n%%EOF"
        )

    @pytest.mark.asyncio
    async def test_pdf_mode_merges_children(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """PDF 模式：多页面合并为一个 PDF。"""
        minimal_pdf = self._minimal_pdf()

        def mock_get_page(page_id, **kwargs):
            pages = {
                "root": {
                    "id": "root", "title": "Root Doc",
                    "body": {"storage": {"value": ""}},
                    "version": {"number": 1, "when": "", "by": {}},
                    "children": {"page": {
                        "results": [{"id": "c1"}, {"id": "c2"}],
                        "size": 2, "limit": 100,
                    }},
                    "_links": {},
                },
                "c1": {
                    "id": "c1", "title": "Chapter 1",
                    "body": {"storage": {"value": ""}},
                    "version": {"number": 1, "when": "", "by": {}},
                    "children": {"page": {"results": [], "size": 0, "limit": 100}},
                    "_links": {},
                },
                "c2": {
                    "id": "c2", "title": "Chapter 2",
                    "body": {"storage": {"value": ""}},
                    "version": {"number": 1, "when": "", "by": {}},
                    "children": {"page": {"results": [], "size": 0, "limit": 100}},
                    "_links": {},
                },
            }
            return pages.get(page_id, pages["root"])

        mock_client.get_page = AsyncMock(side_effect=mock_get_page)

        async def _mock_stream(page_queue, concurrency=6, on_page_done=None):
            results = {}
            while True:
                pid = await page_queue.get()
                if pid is None:
                    break
                results[pid] = minimal_pdf
                if on_page_done:
                    on_page_done(pid, len(minimal_pdf))
            return results

        mock_client.export_pages_pdf_stream = AsyncMock(side_effect=_mock_stream)

        downloader = ConfluenceDownloader(mock_client, config)
        task_id = await downloader.start_download(
            page_id="root",
            output_dir=str(tmp_path),
            max_depth=1,
            save_format="pdf",
            download_attachments=False,
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "completed"
        assert progress["pages_downloaded"] == 3

        # 验证合并 PDF 文件存在
        date_suffix = datetime.now().strftime("%Y%m%d")
        merged = tmp_path / f"Root Doc_{date_suffix}.pdf"
        assert merged.exists()
        assert merged.stat().st_size > 0

    @pytest.mark.asyncio
    async def test_pdf_mode_partial_failure(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """PDF 模式：部分页面导出失败，其余正常合并。"""
        minimal_pdf = self._minimal_pdf()

        def mock_get_page(page_id, **kwargs):
            children_results = (
                [{"id": "ok"}, {"id": "fail"}] if page_id == "root" else []
            )
            return {
                "id": page_id,
                "title": f"Page {page_id}",
                "body": {"storage": {"value": ""}},
                "version": {"number": 1, "when": "", "by": {}},
                "children": {"page": {
                    "results": children_results,
                    "size": len(children_results), "limit": 100,
                }},
                "_links": {},
            }

        mock_client.get_page = AsyncMock(side_effect=mock_get_page)

        async def _mock_stream_partial(page_queue, concurrency=6, on_page_done=None):
            results = {}
            while True:
                pid = await page_queue.get()
                if pid is None:
                    break
                if pid != "fail":
                    results[pid] = minimal_pdf
                    if on_page_done:
                        on_page_done(pid, len(minimal_pdf))
                # 'fail' 页面不返回，模拟 CDP 失败
            return results

        mock_client.export_pages_pdf_stream = AsyncMock(
            side_effect=_mock_stream_partial
        )

        downloader = ConfluenceDownloader(mock_client, config)
        task_id = await downloader.start_download(
            page_id="root",
            output_dir=str(tmp_path),
            max_depth=1,
            save_format="pdf",
            download_attachments=False,
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "completed"
        assert progress["pages_downloaded"] == 2  # root + ok
        assert progress["pages_failed"] == 1  # fail


# ── Native PDF Export Mode Tests ──


class TestNativePdfMode:
    """pdf_export_method="native" 时使用 flyingpdf 而非 Chrome CDP。"""

    @staticmethod
    def _minimal_pdf() -> bytes:
        return (
            b"%PDF-1.0\n1 0 obj<</Pages 2 0 R/Type/Catalog>>endobj\n"
            b"2 0 obj<</Kids[3 0 R]/Count 1/Type/Pages>>endobj\n"
            b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n"
            b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n"
            b"0000000058 00000 n \n0000000115 00000 n \n"
            b"trailer<</Root 1 0 R/Size 4>>\nstartxref\n190\n%%EOF"
        )

    @pytest.fixture
    def native_config(self) -> ConfluenceConfig:
        """Config with pdf_export_method='native'。"""
        return ConfluenceConfig(
            base_url="https://confluence.test.com",
            context_path="/confluence",
            username="user",
            api_token="token",
            max_depth=2,
            max_concurrent_requests=3,
            download_attachments=False,
            default_output_dir="./test_downloads",
            pdf_export_method="native",
        )

    @pytest.mark.asyncio
    async def test_native_pdf_single_page(
        self, mock_client: MagicMock, native_config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """native 模式：单页面导出。"""
        minimal_pdf = self._minimal_pdf()
        mock_client.get_page.return_value = {
            "id": "800",
            "title": "Native Single",
            "body": {"storage": {"value": ""}},
            "version": {"number": 1, "when": "", "by": {}},
            "_links": {},
        }

        async def _mock_native_stream(page_queue, concurrency=6, on_page_done=None):
            results = {}
            while True:
                pid = await page_queue.get()
                if pid is None:
                    break
                results[pid] = minimal_pdf
                if on_page_done:
                    on_page_done(pid, len(minimal_pdf))
            return results

        mock_client.export_pages_pdf_native_stream = AsyncMock(
            side_effect=_mock_native_stream
        )
        # Chrome stream should NOT be called
        mock_client.export_pages_pdf_stream = AsyncMock(
            side_effect=AssertionError("Chrome CDP should not be used in native mode")
        )

        downloader = ConfluenceDownloader(mock_client, native_config)
        task_id = await downloader.start_download(
            page_id="800",
            output_dir=str(tmp_path),
            max_depth=0,
            save_format="pdf",
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "completed"
        assert progress["pages_downloaded"] == 1

        # 验证 PDF 文件存在
        date_suffix = datetime.now().strftime("%Y%m%d")
        pdf_file = tmp_path / f"Native Single_{date_suffix}.pdf"
        assert pdf_file.exists()
        assert pdf_file.stat().st_size > 0

        # 验证 Chrome 方法未被调用
        mock_client.export_pages_pdf_stream.assert_not_called()

    @pytest.mark.asyncio
    async def test_native_pdf_multi_page(
        self, mock_client: MagicMock, native_config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """native 模式：多页面合并。"""
        minimal_pdf = self._minimal_pdf()

        def mock_get_page(page_id, **kwargs):
            pages = {
                "root": {
                    "id": "root", "title": "Native Root",
                    "body": {"storage": {"value": ""}},
                    "version": {"number": 1, "when": "", "by": {}},
                    "children": {"page": {
                        "results": [{"id": "child1"}],
                        "size": 1, "limit": 100,
                    }},
                    "_links": {},
                },
                "child1": {
                    "id": "child1", "title": "Native Child 1",
                    "body": {"storage": {"value": ""}},
                    "version": {"number": 1, "when": "", "by": {}},
                    "children": {"page": {"results": [], "size": 0, "limit": 100}},
                    "_links": {},
                },
            }
            return pages.get(page_id, pages["root"])

        mock_client.get_page = AsyncMock(side_effect=mock_get_page)

        async def _mock_native_stream(page_queue, concurrency=6, on_page_done=None):
            results = {}
            while True:
                pid = await page_queue.get()
                if pid is None:
                    break
                results[pid] = minimal_pdf
                if on_page_done:
                    on_page_done(pid, len(minimal_pdf))
            return results

        mock_client.export_pages_pdf_native_stream = AsyncMock(
            side_effect=_mock_native_stream
        )

        downloader = ConfluenceDownloader(mock_client, native_config)
        task_id = await downloader.start_download(
            page_id="root",
            output_dir=str(tmp_path),
            max_depth=1,
            save_format="pdf",
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "completed"
        assert progress["pages_downloaded"] == 2

    @pytest.mark.asyncio
    async def test_chrome_mode_uses_cdp_stream(
        self, mock_client: MagicMock, config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """chrome 模式（默认）使用 export_pages_pdf_stream 而非 native。"""
        minimal_pdf = self._minimal_pdf()
        mock_client.get_page.return_value = {
            "id": "900",
            "title": "Chrome Mode",
            "body": {"storage": {"value": ""}},
            "version": {"number": 1, "when": "", "by": {}},
            "_links": {},
        }

        async def _mock_cdp_stream(page_queue, concurrency=6, on_page_done=None):
            results = {}
            while True:
                pid = await page_queue.get()
                if pid is None:
                    break
                results[pid] = minimal_pdf
                if on_page_done:
                    on_page_done(pid, len(minimal_pdf))
            return results

        mock_client.export_pages_pdf_stream = AsyncMock(side_effect=_mock_cdp_stream)
        mock_client.export_pages_pdf_native_stream = AsyncMock(
            side_effect=AssertionError("Native should not be used in chrome mode")
        )

        downloader = ConfluenceDownloader(mock_client, config)
        task_id = await downloader.start_download(
            page_id="900",
            output_dir=str(tmp_path),
            max_depth=0,
            save_format="pdf",
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "completed"
        mock_client.export_pages_pdf_stream.assert_called_once()
        mock_client.export_pages_pdf_native_stream.assert_not_called()

    @pytest.mark.asyncio
    async def test_native_pdf_with_output_filename(
        self, mock_client: MagicMock, native_config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """native 模式 + output_filename 自定义文件名。"""
        minimal_pdf = self._minimal_pdf()
        mock_client.get_page.return_value = {
            "id": "810",
            "title": "Original Name",
            "body": {"storage": {"value": ""}},
            "version": {"number": 1, "when": "", "by": {}},
            "_links": {},
        }

        async def _mock_native_stream(page_queue, concurrency=6, on_page_done=None):
            results = {}
            while True:
                pid = await page_queue.get()
                if pid is None:
                    break
                results[pid] = minimal_pdf
                if on_page_done:
                    on_page_done(pid, len(minimal_pdf))
            return results

        mock_client.export_pages_pdf_native_stream = AsyncMock(
            side_effect=_mock_native_stream
        )

        downloader = ConfluenceDownloader(mock_client, native_config)
        task_id = await downloader.start_download(
            page_id="810",
            output_dir=str(tmp_path),
            max_depth=0,
            save_format="pdf",
            output_filename="自定义导出",
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "completed"

        date_suffix = datetime.now().strftime("%Y%m%d")
        expected_pdf = tmp_path / f"自定义导出_{date_suffix}.pdf"
        assert expected_pdf.exists()
        assert not (tmp_path / f"Original Name_{date_suffix}.pdf").exists()


# ── PDF Incremental Download (Cache) Tests ──


class TestPdfIncrementalDownload:
    """PDF 模式增量下载：基于 _pdf_cache 的版本检测。"""

    @staticmethod
    def _minimal_pdf() -> bytes:
        return (
            b"%PDF-1.0\n1 0 obj<</Pages 2 0 R/Type/Catalog>>endobj\n"
            b"2 0 obj<</Kids[3 0 R]/Count 1/Type/Pages>>endobj\n"
            b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n"
            b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n"
            b"0000000058 00000 n \n0000000115 00000 n \n"
            b"trailer<</Root 1 0 R/Size 4>>\nstartxref\n190\n%%EOF"
        )

    @pytest.fixture
    def native_config(self) -> ConfluenceConfig:
        return ConfluenceConfig(
            base_url="https://confluence.test.com",
            context_path="/confluence",
            username="user",
            api_token="token",
            max_depth=1,
            max_concurrent_requests=3,
            download_attachments=False,
            default_output_dir="./test_downloads",
            pdf_export_method="native",
            request_delay=0,  # no delay in tests
            max_retries=0,
        )

    @pytest.mark.asyncio
    async def test_second_run_uses_cache(
        self, mock_client: MagicMock, native_config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """第二次运行时使用缓存，跳过未变更的页面。"""
        minimal_pdf = self._minimal_pdf()

        mock_client.get_page.return_value = {
            "id": "100",
            "title": "Cached Page",
            "body": {"storage": {"value": ""}},
            "version": {"number": 3, "when": "", "by": {}},
            "_links": {},
        }

        async def _mock_native_stream(page_queue, concurrency=6, on_page_done=None):
            results = {}
            while True:
                pid = await page_queue.get()
                if pid is None:
                    break
                results[pid] = minimal_pdf
                if on_page_done:
                    on_page_done(pid, len(minimal_pdf))
            return results

        mock_client.export_pages_pdf_native_stream = AsyncMock(
            side_effect=_mock_native_stream
        )

        # ── First run: should export ──
        downloader = ConfluenceDownloader(mock_client, native_config)
        task_id = await downloader.start_download(
            page_id="100",
            output_dir=str(tmp_path),
            max_depth=0,
            save_format="pdf",
        )
        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "completed"
        assert progress["pages_downloaded"] == 1
        assert progress["pages_skipped"] == 0

        # Verify cache was written (filename: {page_id}_{safe_title})
        cache_dir = tmp_path / "_pdf_cache"
        assert (cache_dir / "100_Cached Page.pdf").exists()
        assert (cache_dir / "100_Cached Page.json").exists()

        # ── Second run: same version → should use cache ──
        mock_client.export_pages_pdf_native_stream = AsyncMock(
            side_effect=_mock_native_stream
        )
        downloader2 = ConfluenceDownloader(mock_client, native_config)
        task_id2 = await downloader2.start_download(
            page_id="100",
            output_dir=str(tmp_path),
            max_depth=0,
            save_format="pdf",
        )
        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader2.get_progress(task_id2)
            if p and p["status"] != "running":
                break

        progress2 = downloader2.get_progress(task_id2)
        assert progress2["status"] == "completed"
        assert progress2["pages_skipped"] == 1
        assert progress2["pages_downloaded"] == 0

    @pytest.mark.asyncio
    async def test_cache_invalidated_on_version_change(
        self, mock_client: MagicMock, native_config: ConfluenceConfig, tmp_path: Path
    ) -> None:
        """页面版本更新后缓存失效，重新导出。"""
        minimal_pdf = self._minimal_pdf()

        # Pre-populate cache with version 2 (filename: {page_id}_{safe_title})
        cache_dir = tmp_path / "_pdf_cache"
        cache_dir.mkdir(parents=True)
        (cache_dir / "200_Updated Page.pdf").write_bytes(minimal_pdf)
        (cache_dir / "200_Updated Page.json").write_text(
            json.dumps({"page_id": "200", "version": 2}), encoding="utf-8"
        )

        # Server returns version 5 (newer)
        mock_client.get_page.return_value = {
            "id": "200",
            "title": "Updated Page",
            "body": {"storage": {"value": ""}},
            "version": {"number": 5, "when": "", "by": {}},
            "_links": {},
        }

        async def _mock_native_stream(page_queue, concurrency=6, on_page_done=None):
            results = {}
            while True:
                pid = await page_queue.get()
                if pid is None:
                    break
                results[pid] = minimal_pdf
                if on_page_done:
                    on_page_done(pid, len(minimal_pdf))
            return results

        mock_client.export_pages_pdf_native_stream = AsyncMock(
            side_effect=_mock_native_stream
        )

        downloader = ConfluenceDownloader(mock_client, native_config)
        task_id = await downloader.start_download(
            page_id="200",
            output_dir=str(tmp_path),
            max_depth=0,
            save_format="pdf",
        )
        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "completed"
        assert progress["pages_downloaded"] == 1  # re-exported
        assert progress["pages_skipped"] == 0

        # Cache should be updated with new version
        meta = json.loads(
            (cache_dir / "200_Updated Page.json").read_text(encoding="utf-8")
        )
        assert meta["version"] == 5


# ── DFS Tree Ordering Tests ──


class TestDfsOrder:
    """_dfs_order 静态方法：验证 DFS 前序遍历层级顺序。"""

    def test_simple_tree(self) -> None:
        """
        root
        ├── ch1
        │   ├── s1.1
        │   └── s1.2
        └── ch2
            └── s2.1
        """
        children_map = {
            "root": ["ch1", "ch2"],
            "ch1": ["s1.1", "s1.2"],
            "ch2": ["s2.1"],
        }
        valid = {"root", "ch1", "ch2", "s1.1", "s1.2", "s2.1"}
        result = ConfluenceDownloader._dfs_order("root", children_map, valid)
        assert result == ["root", "ch1", "s1.1", "s1.2", "ch2", "s2.1"]

    def test_single_page(self) -> None:
        result = ConfluenceDownloader._dfs_order("only", {}, {"only"})
        assert result == ["only"]

    def test_skips_invalid(self) -> None:
        """未成功下载的页面不在 valid_ids 中，应跳过。"""
        children_map = {"root": ["ok", "fail"]}
        valid = {"root", "ok"}  # 'fail' 不在 valid_ids
        result = ConfluenceDownloader._dfs_order("root", children_map, valid)
        assert result == ["root", "ok"]

    def test_deep_tree(self) -> None:
        """深度嵌套：root → a → b → c。"""
        children_map = {"root": ["a"], "a": ["b"], "b": ["c"]}
        valid = {"root", "a", "b", "c"}
        result = ConfluenceDownloader._dfs_order("root", children_map, valid)
        assert result == ["root", "a", "b", "c"]

    def test_wide_tree(self) -> None:
        """宽树：root 下 10 个子页面，无孙页面。"""
        ids = [f"p{i}" for i in range(10)]
        children_map = {"root": ids}
        valid = {"root"} | set(ids)
        result = ConfluenceDownloader._dfs_order("root", children_map, valid)
        assert result == ["root"] + ids


class TestDfsMergeIntegration:
    """验证 PDF 模式下多层页面树按 DFS 层级顺序合并。"""

    @staticmethod
    def _minimal_pdf() -> bytes:
        buf = io.BytesIO()
        buf.write(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n")
        buf.write(b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n")
        buf.write(b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n")
        buf.write(b"xref\n0 4\n")
        buf.write(b"0000000000 65535 f \n")
        buf.write(b"0000000009 00000 n \n")
        buf.write(b"0000000058 00000 n \n")
        buf.write(b"0000000115 00000 n \n")
        buf.write(b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF")
        return buf.getvalue()

    @pytest.mark.asyncio
    async def test_dfs_order_in_merged_pdf(
        self, mock_client: MagicMock, tmp_path: Path,
    ) -> None:
        """3 层树 root→[ch1, ch2], ch1→[s1] 应按 root,ch1,s1,ch2 合并。"""
        minimal_pdf = self._minimal_pdf()
        config = ConfluenceConfig(
            base_url="https://confluence.test.com",
            context_path="/confluence",
            username="user",
            api_token="token",
            max_depth=3,
            pdf_export_method="native",
        )

        def mock_get_page(page_id, **kwargs):
            tree = {
                "root": {
                    "id": "root", "title": "Root",
                    "version": {"number": 1, "when": "", "by": {}},
                    "children": {"page": {
                        "results": [{"id": "ch1"}, {"id": "ch2"}],
                        "size": 2, "limit": 100,
                    }},
                },
                "ch1": {
                    "id": "ch1", "title": "Chapter 1",
                    "version": {"number": 1, "when": "", "by": {}},
                    "children": {"page": {
                        "results": [{"id": "s1"}],
                        "size": 1, "limit": 100,
                    }},
                },
                "ch2": {
                    "id": "ch2", "title": "Chapter 2",
                    "version": {"number": 1, "when": "", "by": {}},
                    "children": {"page": {"results": [], "size": 0, "limit": 100}},
                },
                "s1": {
                    "id": "s1", "title": "Section 1.1",
                    "version": {"number": 1, "when": "", "by": {}},
                    "children": {"page": {"results": [], "size": 0, "limit": 100}},
                },
            }
            return tree.get(page_id, tree["root"])

        mock_client.get_page = AsyncMock(side_effect=mock_get_page)

        page_order: list[str] = []

        async def _mock_native_stream(page_queue, concurrency=6, on_page_done=None):
            results = {}
            while True:
                pid = await page_queue.get()
                if pid is None:
                    break
                page_order.append(pid)
                results[pid] = minimal_pdf
                if on_page_done:
                    on_page_done(pid, len(minimal_pdf))
            return results

        mock_client.export_pages_pdf_native_stream = AsyncMock(
            side_effect=_mock_native_stream
        )

        downloader = ConfluenceDownloader(mock_client, config)
        task_id = await downloader.start_download(
            page_id="root",
            output_dir=str(tmp_path),
            max_depth=3,
            save_format="pdf",
        )

        for _ in range(20):
            await asyncio.sleep(0.2)
            p = downloader.get_progress(task_id)
            if p and p["status"] != "running":
                break

        progress = downloader.get_progress(task_id)
        assert progress["status"] == "completed"
        assert progress["pages_downloaded"] == 4

        # 验证输出 PDF 存在
        pdf_files = list(tmp_path.glob("*.pdf"))
        assert len(pdf_files) == 1

        # 验证合并后 PDF 有 4 页（每个子页面 1 页）
        from pypdf import PdfReader
        reader = PdfReader(pdf_files[0])
        assert len(reader.pages) == 4
