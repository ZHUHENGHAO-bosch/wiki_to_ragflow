"""connectors/ragflow_client.py 单元测试。"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from config import RAGFlowConfig
from connectors.ragflow_client import RAGFlowClient


@pytest.fixture
def ragflow_config() -> RAGFlowConfig:
    return RAGFlowConfig(
        base_url="http://ragflow.test:9380",
        api_key="test-api-key",
        dataset_name="test_dataset",
        auto_upload_after_confluence=False,
        parse_after_upload=True,
    )


@pytest.fixture
def mock_dataset() -> MagicMock:
    ds = MagicMock()
    ds.name = "test_dataset"
    ds.id = "ds-001"
    ds.upload_documents = MagicMock(return_value=[])
    ds.async_parse_documents = MagicMock()
    ds.list_documents = MagicMock(return_value=[])
    return ds


@pytest.fixture
def mock_rag(mock_dataset: MagicMock) -> MagicMock:
    rag = MagicMock()
    rag.list_datasets = MagicMock(return_value=[mock_dataset])
    rag.create_dataset = MagicMock(return_value=mock_dataset)
    return rag


# ── Init Tests ──


class TestRAGFlowClientInit:
    @pytest.mark.asyncio
    async def test_init_finds_existing_dataset(
        self, ragflow_config: RAGFlowConfig, mock_rag: MagicMock, mock_dataset: MagicMock
    ) -> None:
        """已有 dataset 时直接复用。"""
        client = RAGFlowClient(ragflow_config)

        with patch("ragflow_sdk.RAGFlow", return_value=mock_rag):
            await client.init()

        assert client._dataset is mock_dataset
        mock_rag.list_datasets.assert_called_once_with(name="test_dataset")
        mock_rag.create_dataset.assert_not_called()

    @pytest.mark.asyncio
    async def test_init_creates_new_dataset(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock
    ) -> None:
        """dataset 不存在时自动创建。"""
        mock_rag = MagicMock()
        mock_rag.list_datasets = MagicMock(return_value=[])  # 空列表
        mock_rag.create_dataset = MagicMock(return_value=mock_dataset)

        client = RAGFlowClient(ragflow_config)

        with patch("ragflow_sdk.RAGFlow", return_value=mock_rag):
            await client.init()

        assert client._dataset is mock_dataset
        mock_rag.create_dataset.assert_called_once_with(name="test_dataset")


# ── Upload Tests ──


class TestUploadDocuments:
    @pytest.mark.asyncio
    async def test_upload_single_file(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock, tmp_path: Path
    ) -> None:
        """单文件上传。"""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.0 test content")

        mock_doc = MagicMock()
        mock_doc.id = "doc-001"
        mock_dataset.upload_documents = MagicMock(return_value=[mock_doc])

        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        doc_ids = await client.upload_documents([test_file])

        assert doc_ids == ["doc-001"]
        mock_dataset.upload_documents.assert_called_once()
        call_args = mock_dataset.upload_documents.call_args[0][0]
        assert len(call_args) == 1
        assert call_args[0]["display_name"] == "test.pdf"
        assert call_args[0]["blob"] == b"%PDF-1.0 test content"

    @pytest.mark.asyncio
    async def test_upload_multiple_files(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock, tmp_path: Path
    ) -> None:
        """多文件上传。"""
        f1 = tmp_path / "a.pdf"
        f2 = tmp_path / "b.pdf"
        f1.write_bytes(b"content-a")
        f2.write_bytes(b"content-b")

        doc1 = MagicMock()
        doc1.id = "doc-a"
        doc2 = MagicMock()
        doc2.id = "doc-b"
        mock_dataset.upload_documents = MagicMock(return_value=[doc1, doc2])

        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        doc_ids = await client.upload_documents([f1, f2])

        assert doc_ids == ["doc-a", "doc-b"]
        call_args = mock_dataset.upload_documents.call_args[0][0]
        assert len(call_args) == 2

    @pytest.mark.asyncio
    async def test_upload_skips_nonexistent_files(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock, tmp_path: Path
    ) -> None:
        """不存在的文件被跳过。"""
        existing = tmp_path / "exists.pdf"
        existing.write_bytes(b"data")
        missing = tmp_path / "nope.pdf"

        mock_doc = MagicMock()
        mock_doc.id = "doc-e"
        mock_dataset.upload_documents = MagicMock(return_value=[mock_doc])

        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        doc_ids = await client.upload_documents([existing, missing])

        assert doc_ids == ["doc-e"]
        call_args = mock_dataset.upload_documents.call_args[0][0]
        assert len(call_args) == 1
        assert call_args[0]["display_name"] == "exists.pdf"

    @pytest.mark.asyncio
    async def test_upload_empty_list(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock
    ) -> None:
        """空列表直接返回空。"""
        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        doc_ids = await client.upload_documents([])
        assert doc_ids == []
        mock_dataset.upload_documents.assert_not_called()

    @pytest.mark.asyncio
    async def test_upload_all_nonexistent(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock, tmp_path: Path
    ) -> None:
        """所有文件都不存在时返回空。"""
        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        doc_ids = await client.upload_documents([
            tmp_path / "a.pdf", tmp_path / "b.pdf",
        ])
        assert doc_ids == []
        mock_dataset.upload_documents.assert_not_called()

    @pytest.mark.asyncio
    async def test_upload_sdk_error(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock, tmp_path: Path
    ) -> None:
        """SDK 上传异常向上传播。"""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"data")
        mock_dataset.upload_documents = MagicMock(
            side_effect=Exception("SDK upload error")
        )

        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        with pytest.raises(Exception, match="SDK upload error"):
            await client.upload_documents([test_file])


# ── Parse Tests ──


class TestParseDocuments:
    @pytest.mark.asyncio
    async def test_parse_documents(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock
    ) -> None:
        """正常触发解析。"""
        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        count = await client.parse_documents(["doc-1", "doc-2"])

        assert count == 2
        mock_dataset.async_parse_documents.assert_called_once_with(
            ["doc-1", "doc-2"]
        )

    @pytest.mark.asyncio
    async def test_parse_empty_ids(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock
    ) -> None:
        """空 ID 列表直接返回 0。"""
        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        count = await client.parse_documents([])
        assert count == 0
        mock_dataset.async_parse_documents.assert_not_called()


# ── Upload and Parse Tests ──


class TestUploadAndParse:
    @pytest.mark.asyncio
    async def test_upload_and_parse(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock, tmp_path: Path
    ) -> None:
        """组合调用：上传 + 解析。"""
        test_file = tmp_path / "doc.pdf"
        test_file.write_bytes(b"pdf-data")

        mock_doc = MagicMock()
        mock_doc.id = "doc-x"
        mock_dataset.upload_documents = MagicMock(return_value=[mock_doc])

        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        result = await client.upload_and_parse([test_file])

        assert result["uploaded"] == ["doc-x"]
        assert result["parse_count"] == 1
        mock_dataset.async_parse_documents.assert_called_once_with(["doc-x"])

    @pytest.mark.asyncio
    async def test_upload_and_parse_skip_parse(
        self, mock_dataset: MagicMock, tmp_path: Path
    ) -> None:
        """parse_after_upload=False 时跳过解析。"""
        config = RAGFlowConfig(
            base_url="http://ragflow.test:9380",
            api_key="key",
            dataset_name="ds",
            parse_after_upload=False,
        )

        test_file = tmp_path / "doc.pdf"
        test_file.write_bytes(b"pdf-data")

        mock_doc = MagicMock()
        mock_doc.id = "doc-y"
        mock_dataset.upload_documents = MagicMock(return_value=[mock_doc])

        client = RAGFlowClient(config)
        client._dataset = mock_dataset

        result = await client.upload_and_parse([test_file])

        assert result["uploaded"] == ["doc-y"]
        assert result["parse_count"] == 0
        mock_dataset.async_parse_documents.assert_not_called()

    @pytest.mark.asyncio
    async def test_upload_and_parse_empty_files(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock
    ) -> None:
        """空文件列表：不上传不解析。"""
        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        result = await client.upload_and_parse([])
        assert result["uploaded"] == []
        assert result["parse_count"] == 0


# ── Close Tests ──


class TestClose:
    @pytest.mark.asyncio
    async def test_close_clears_refs(
        self, ragflow_config: RAGFlowConfig
    ) -> None:
        """close() 清除内部引用。"""
        client = RAGFlowClient(ragflow_config)
        client._rag = MagicMock()
        client._dataset = MagicMock()

        await client.close()
        assert client._rag is None
        assert client._dataset is None


# ── _ensure_no_proxy Tests ──


class TestEnsureNoProxy:
    def test_adds_host_to_no_proxy(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """将 RAGFlow 主机追加到 no_proxy。"""
        monkeypatch.setenv("no_proxy", "localhost")
        monkeypatch.setenv("NO_PROXY", "localhost")

        RAGFlowClient._ensure_no_proxy("http://10.161.151.72:8880")

        assert "10.161.151.72" in os.environ["no_proxy"]
        assert "10.161.151.72" in os.environ["NO_PROXY"]
        # 原值保留
        assert "localhost" in os.environ["no_proxy"]

    def test_idempotent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """重复调用不会重复追加。"""
        monkeypatch.setenv("no_proxy", "10.161.151.72,localhost")
        monkeypatch.setenv("NO_PROXY", "10.161.151.72,localhost")

        RAGFlowClient._ensure_no_proxy("http://10.161.151.72:8880")

        # 应只出现一次
        assert os.environ["no_proxy"].count("10.161.151.72") == 1

    def test_empty_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """环境变量为空时正常设置。"""
        monkeypatch.delenv("no_proxy", raising=False)
        monkeypatch.delenv("NO_PROXY", raising=False)

        RAGFlowClient._ensure_no_proxy("http://192.168.1.100:9380")

        assert os.environ.get("no_proxy") == "192.168.1.100"
        assert os.environ.get("NO_PROXY") == "192.168.1.100"

    def test_invalid_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """无效 URL 不会崩溃。"""
        monkeypatch.setenv("no_proxy", "localhost")
        RAGFlowClient._ensure_no_proxy("")
        RAGFlowClient._ensure_no_proxy("not-a-url")
        # 不应崩溃，no_proxy 保持不变
        assert os.environ["no_proxy"] == "localhost"


# ── Init Error Tests ──


class TestInitErrors:
    @pytest.mark.asyncio
    async def test_init_sdk_connection_error(
        self, ragflow_config: RAGFlowConfig
    ) -> None:
        """SDK 连接失败时 init() 抛出异常。"""
        with patch(
            "ragflow_sdk.RAGFlow",
            side_effect=Exception("Connection refused"),
        ):
            client = RAGFlowClient(ragflow_config)
            with pytest.raises(Exception, match="Connection refused"):
                await client.init()

    @pytest.mark.asyncio
    async def test_init_list_datasets_error(
        self, ragflow_config: RAGFlowConfig
    ) -> None:
        """list_datasets 和 create_dataset 均失败时 init() 抛出异常。"""
        mock_rag = MagicMock()
        mock_rag.list_datasets = MagicMock(
            side_effect=Exception("API 403 Forbidden")
        )
        mock_rag.create_dataset = MagicMock(
            side_effect=Exception("API 403 Forbidden")
        )

        with patch("ragflow_sdk.RAGFlow", return_value=mock_rag):
            client = RAGFlowClient(ragflow_config)
            with pytest.raises(Exception, match="API 403 Forbidden"):
                await client.init()


# ── Parse Error Tests ──


class TestParseErrors:
    @pytest.mark.asyncio
    async def test_parse_sdk_error(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock
    ) -> None:
        """SDK 解析异常向上传播。"""
        mock_dataset.async_parse_documents = MagicMock(
            side_effect=Exception("Parse service unavailable")
        )

        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        with pytest.raises(Exception, match="Parse service unavailable"):
            await client.parse_documents(["doc-1"])


# ── Init Dataset Override Tests ──


class TestInitDatasetOverride:
    @pytest.mark.asyncio
    async def test_init_with_custom_dataset_name(
        self, ragflow_config: RAGFlowConfig, mock_rag: MagicMock, mock_dataset: MagicMock
    ) -> None:
        """init(dataset_name=...) 使用自定义名称。"""
        client = RAGFlowClient(ragflow_config)

        mock_module = MagicMock()
        mock_module.RAGFlow = MagicMock(return_value=mock_rag)
        with patch.dict(sys.modules, {"ragflow_sdk": mock_module}):
            await client.init(dataset_name="custom_ds")

        mock_rag.list_datasets.assert_called_once_with(name="custom_ds")

    @pytest.mark.asyncio
    async def test_init_default_dataset_name(
        self, ragflow_config: RAGFlowConfig, mock_rag: MagicMock, mock_dataset: MagicMock
    ) -> None:
        """init() 不指定 dataset_name 时使用 config 默认值。"""
        client = RAGFlowClient(ragflow_config)

        mock_module = MagicMock()
        mock_module.RAGFlow = MagicMock(return_value=mock_rag)
        with patch.dict(sys.modules, {"ragflow_sdk": mock_module}):
            await client.init()

        mock_rag.list_datasets.assert_called_once_with(name="test_dataset")

    @pytest.mark.asyncio
    async def test_init_none_dataset_name_uses_default(
        self, ragflow_config: RAGFlowConfig, mock_rag: MagicMock, mock_dataset: MagicMock
    ) -> None:
        """init(dataset_name=None) 使用 config 默认值。"""
        client = RAGFlowClient(ragflow_config)

        mock_module = MagicMock()
        mock_module.RAGFlow = MagicMock(return_value=mock_rag)
        with patch.dict(sys.modules, {"ragflow_sdk": mock_module}):
            await client.init(dataset_name=None)

        mock_rag.list_datasets.assert_called_once_with(name="test_dataset")


# ── List Documents Tests ──


def _make_mock_doc(
    doc_id: str, name: str = "", run: str = "UNSTART",
    progress: float = 0.0, progress_msg: str = "",
    chunk_count: int = 0, token_count: int = 0,
) -> MagicMock:
    """创建模拟 SDK Document 对象。"""
    doc = MagicMock()
    doc.id = doc_id
    doc.name = name
    doc.run = run
    doc.progress = progress
    doc.progress_msg = progress_msg
    doc.chunk_count = chunk_count
    doc.token_count = token_count
    return doc


class TestListDocuments:
    @pytest.mark.asyncio
    async def test_list_by_ids(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock
    ) -> None:
        """按 ID 查询文档状态。"""
        doc1 = _make_mock_doc("d1", name="a.pdf", run="DONE", chunk_count=10, token_count=500)
        doc2 = _make_mock_doc("d2", name="b.pdf", run="RUNNING", progress=0.5)
        mock_dataset.list_documents = MagicMock(side_effect=[[doc1], [doc2]])

        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        result = await client.list_documents(["d1", "d2"])

        assert len(result) == 2
        assert result[0]["id"] == "d1"
        assert result[0]["run"] == "DONE"
        assert result[0]["chunk_count"] == 10
        assert result[1]["id"] == "d2"
        assert result[1]["run"] == "RUNNING"

    @pytest.mark.asyncio
    async def test_list_all_documents(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock
    ) -> None:
        """不指定 ID 时返回所有文档。"""
        doc1 = _make_mock_doc("d1", name="a.pdf")
        doc2 = _make_mock_doc("d2", name="b.pdf")
        mock_dataset.list_documents = MagicMock(return_value=[doc1, doc2])

        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        result = await client.list_documents()

        assert len(result) == 2
        mock_dataset.list_documents.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_list_empty_result(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock
    ) -> None:
        """空结果。"""
        mock_dataset.list_documents = MagicMock(return_value=[])

        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        result = await client.list_documents()

        assert result == []


# ── Wait For Parsing Tests ──


class TestWaitForParsing:
    @pytest.mark.asyncio
    async def test_all_done(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock
    ) -> None:
        """所有文档解析成功。"""
        doc1 = _make_mock_doc("d1", name="a.pdf", run="DONE", chunk_count=10, token_count=500)
        doc2 = _make_mock_doc("d2", name="b.pdf", run="DONE", chunk_count=20, token_count=1000)
        mock_dataset.list_documents = MagicMock(side_effect=[[doc1], [doc2]])

        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        result = await client.wait_for_parsing(["d1", "d2"], timeout=10, poll_interval=0.01)

        assert len(result["completed"]) == 2
        assert result["failed"] == []
        assert result["timed_out"] == []
        assert result["total_chunks"] == 30
        assert result["total_tokens"] == 1500
        assert result["elapsed_seconds"] >= 0

    @pytest.mark.asyncio
    async def test_partial_failure(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock
    ) -> None:
        """部分失败。"""
        doc1 = _make_mock_doc("d1", name="a.pdf", run="DONE", chunk_count=5, token_count=200)
        doc2 = _make_mock_doc("d2", name="b.pdf", run="FAIL", progress_msg="Parse error")
        mock_dataset.list_documents = MagicMock(side_effect=[[doc1], [doc2]])

        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        result = await client.wait_for_parsing(["d1", "d2"], timeout=10, poll_interval=0.01)

        assert len(result["completed"]) == 1
        assert len(result["failed"]) == 1
        assert result["failed"][0]["name"] == "b.pdf"
        assert result["timed_out"] == []

    @pytest.mark.asyncio
    async def test_timeout(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock
    ) -> None:
        """超时仍有文档在运行。"""
        running_doc = _make_mock_doc("d1", name="a.pdf", run="RUNNING")
        # list_documents 始终返回 RUNNING 状态
        mock_dataset.list_documents = MagicMock(return_value=[running_doc])

        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        result = await client.wait_for_parsing(
            ["d1"], timeout=0.05, poll_interval=0.01,
        )

        assert result["completed"] == []
        assert result["failed"] == []
        assert len(result["timed_out"]) == 1
        assert result["timed_out"][0]["name"] == "a.pdf"

    @pytest.mark.asyncio
    async def test_on_progress_callback(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock
    ) -> None:
        """on_progress 回调被调用。"""
        doc = _make_mock_doc("d1", name="a.pdf", run="DONE", chunk_count=5, token_count=100)
        mock_dataset.list_documents = MagicMock(return_value=[doc])

        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        progress_calls: list = []
        result = await client.wait_for_parsing(
            ["d1"], timeout=10, poll_interval=0.01,
            on_progress=lambda docs: progress_calls.append(docs),
        )

        assert len(progress_calls) >= 1
        assert progress_calls[0][0]["id"] == "d1"

    @pytest.mark.asyncio
    async def test_transition_running_to_done(
        self, ragflow_config: RAGFlowConfig, mock_dataset: MagicMock
    ) -> None:
        """从 RUNNING 状态过渡到 DONE。"""
        running = _make_mock_doc("d1", name="a.pdf", run="RUNNING")
        done = _make_mock_doc("d1", name="a.pdf", run="DONE", chunk_count=10, token_count=300)

        # 第一轮返回 RUNNING，第二轮返回 DONE
        mock_dataset.list_documents = MagicMock(
            side_effect=[[running], [done]]
        )

        client = RAGFlowClient(ragflow_config)
        client._dataset = mock_dataset

        result = await client.wait_for_parsing(
            ["d1"], timeout=10, poll_interval=0.01,
        )

        assert len(result["completed"]) == 1
        assert result["timed_out"] == []
        assert result["total_chunks"] == 10
