"""
connectors/ragflow_client.py -- RAGFlow 知识库异步客户端

使用 ragflow-sdk（同步库）通过 run_in_executor 包装为 async 接口。
支持 dataset 查找/创建、文件上传、解析触发。
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from config import RAGFlowConfig

logger = logging.getLogger(__name__)


class RAGFlowClient:
    """RAGFlow 知识库异步客户端（包装 ragflow-sdk）。"""

    def __init__(self, config: RAGFlowConfig) -> None:
        self._config = config
        self._rag: Any = None  # ragflow_sdk.RAGFlow instance
        self._dataset: Any = None  # ragflow_sdk DataSet instance

    @staticmethod
    def _ensure_no_proxy(base_url: str) -> None:
        """将 RAGFlow 主机加入 NO_PROXY，防止内网请求走代理。"""
        host = urlparse(base_url).hostname
        if not host:
            return
        for var in ("no_proxy", "NO_PROXY"):
            current = os.environ.get(var, "")
            if host not in current:
                os.environ[var] = f"{host},{current}" if current else host
                logger.debug(f"{var} 已追加 {host}")

    async def init(self, dataset_name: str | None = None) -> None:
        """初始化 SDK 连接 + 查找/创建 dataset。

        Args:
            dataset_name: 覆盖 config 中的 dataset_name（None 则使用默认值）。

        必须在使用 upload/parse 之前调用。
        """
        self._ensure_no_proxy(self._config.base_url)
        loop = asyncio.get_event_loop()

        def _create_rag() -> Any:
            from ragflow_sdk import RAGFlow
            return RAGFlow(
                api_key=self._config.api_key,
                base_url=self._config.base_url,
            )

        self._rag = await loop.run_in_executor(None, _create_rag)
        logger.info(f"RAGFlow SDK 连接: {self._config.base_url}")

        resolved_name = dataset_name or self._config.dataset_name
        self._dataset = await self._resolve_dataset(resolved_name)
        logger.info(f"RAGFlow dataset: {self._dataset.name} (id={self._dataset.id})")

    async def _resolve_dataset(self, name: str) -> Any:
        """按名字查找 dataset，不存在则创建。"""
        loop = asyncio.get_event_loop()

        def _find_or_create() -> Any:
            try:
                datasets = self._rag.list_datasets(name=name)
                if datasets:
                    return datasets[0]
            except Exception as e:
                # RAGFlow SDK 对不存在的 dataset 可能抛权限异常，降级为创建
                logger.debug(f"list_datasets(name={name!r}) 失败: {e}，尝试创建...")
            logger.info(f"RAGFlow dataset '{name}' 不存在，创建中...")
            return self._rag.create_dataset(name=name)

        return await loop.run_in_executor(None, _find_or_create)

    async def upload_documents(
        self, file_paths: list[Path],
    ) -> list[str]:
        """上传文件到 dataset，返回上传成功的 doc_id 列表。

        跳过不存在的文件，空列表直接返回。
        """
        if not file_paths:
            return []

        # 读取文件 bytes（仅包含存在的文件）
        docs_to_upload: list[dict[str, Any]] = []
        for fp in file_paths:
            p = Path(fp)
            if not p.exists():
                logger.warning(f"文件不存在，跳过: {p}")
                continue
            docs_to_upload.append({
                "display_name": p.name,
                "blob": p.read_bytes(),
            })

        if not docs_to_upload:
            logger.warning("没有有效文件可上传")
            return []

        loop = asyncio.get_event_loop()

        def _upload() -> list[Any]:
            return self._dataset.upload_documents(docs_to_upload)

        uploaded = await loop.run_in_executor(None, _upload)
        doc_ids = [doc.id for doc in uploaded]
        logger.info(
            f"RAGFlow 上传完成: {len(doc_ids)} 个文件 "
            f"({', '.join(d['display_name'] for d in docs_to_upload)})"
        )
        return doc_ids

    async def parse_documents(self, doc_ids: list[str]) -> int:
        """触发指定文档的异步解析。返回提交解析的文档数。"""
        if not doc_ids:
            return 0

        loop = asyncio.get_event_loop()

        def _parse() -> None:
            self._dataset.async_parse_documents(doc_ids)

        await loop.run_in_executor(None, _parse)
        logger.info(f"RAGFlow 解析已触发: {len(doc_ids)} 个文档")
        return len(doc_ids)

    async def upload_and_parse(
        self, file_paths: list[Path],
    ) -> dict[str, Any]:
        """组合方法：上传文件 + 触发解析。

        Returns:
            {"uploaded": list[str], "parse_count": int}
        """
        doc_ids = await self.upload_documents(file_paths)

        parse_count = 0
        if doc_ids and self._config.parse_after_upload:
            parse_count = await self.parse_documents(doc_ids)

        return {
            "uploaded": doc_ids,
            "parse_count": parse_count,
        }

    async def list_documents(
        self, doc_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """查询文档状态。

        Args:
            doc_ids: 要查询的文档 ID 列表。None 则返回 dataset 中所有文档。

        Returns:
            文档信息 dict 列表，包含 id, name, run, progress, progress_msg,
            chunk_count, token_count。
        """
        loop = asyncio.get_event_loop()

        def _list() -> list[Any]:
            if doc_ids:
                results = []
                for doc_id in doc_ids:
                    docs = self._dataset.list_documents(id=doc_id)
                    results.extend(docs)
                return results
            return self._dataset.list_documents()

        raw_docs = await loop.run_in_executor(None, _list)
        return [
            {
                "id": doc.id,
                "name": getattr(doc, "name", ""),
                "run": getattr(doc, "run", "UNSTART"),
                "progress": getattr(doc, "progress", 0.0),
                "progress_msg": getattr(doc, "progress_msg", ""),
                "chunk_count": getattr(doc, "chunk_count", 0),
                "token_count": getattr(doc, "token_count", 0),
            }
            for doc in raw_docs
        ]

    async def wait_for_parsing(
        self,
        doc_ids: list[str],
        timeout: float | None = None,
        poll_interval: float | None = None,
        on_progress: Callable[[list[dict[str, Any]]], None] | None = None,
    ) -> dict[str, Any]:
        """轮询等待文档解析完成。

        Args:
            doc_ids: 要等待的文档 ID 列表。
            timeout: 最大等待秒数（None 则使用 config.parse_timeout）。
            poll_interval: 轮询间隔秒数（None 则使用 config.parse_poll_interval）。
            on_progress: 每轮轮询回调，接收当前文档状态列表。

        Returns:
            {
                "completed": [...],    # run == DONE 的文档
                "failed": [...],       # run == FAIL 的文档
                "timed_out": [...],    # 超时仍未完成的文档
                "total_chunks": int,
                "total_tokens": int,
                "elapsed_seconds": float,
            }
        """
        if timeout is None:
            timeout = self._config.parse_timeout
        if poll_interval is None:
            poll_interval = self._config.parse_poll_interval

        terminal_states = {"DONE", "FAIL", "CANCEL"}
        start = time.monotonic()

        while True:
            docs = await self.list_documents(doc_ids)
            if on_progress:
                on_progress(docs)

            # 检查是否所有文档都到达终态
            all_terminal = all(
                doc["run"] in terminal_states for doc in docs
            )
            if all_terminal:
                break

            elapsed = time.monotonic() - start
            if elapsed >= timeout:
                break

            await asyncio.sleep(poll_interval)

        elapsed = time.monotonic() - start

        completed = [d for d in docs if d["run"] == "DONE"]
        failed = [d for d in docs if d["run"] in ("FAIL", "CANCEL")]
        timed_out = [d for d in docs if d["run"] not in terminal_states]

        return {
            "completed": completed,
            "failed": failed,
            "timed_out": timed_out,
            "total_chunks": sum(d["chunk_count"] for d in completed),
            "total_tokens": sum(d["token_count"] for d in completed),
            "elapsed_seconds": elapsed,
        }

    # ─── 数据集管理 (不依赖 init 调用，可独立使用) ─────────────────────

    async def connect(self) -> None:
        """仅建立 RAGFlow SDK 连接，不绑定 dataset。

        用于 list/delete 这类不需要预先选定 dataset 的运维操作。
        """
        if self._rag is not None:
            return
        self._ensure_no_proxy(self._config.base_url)
        loop = asyncio.get_event_loop()

        def _create_rag() -> Any:
            from ragflow_sdk import RAGFlow
            return RAGFlow(
                api_key=self._config.api_key,
                base_url=self._config.base_url,
            )

        self._rag = await loop.run_in_executor(None, _create_rag)
        logger.info(f"RAGFlow SDK 连接: {self._config.base_url}")

    async def list_all_datasets(
        self, page_size: int = 100,
    ) -> list[dict[str, Any]]:
        """分页列出当前 API key 可见的所有 dataset。

        Returns:
            [{id, name, document_count, chunk_count, embedding_model,
              chunk_method, permission}]
        """
        await self.connect()
        loop = asyncio.get_event_loop()

        def _list_page(page: int) -> list[Any]:
            return self._rag.list_datasets(page=page, page_size=page_size)

        all_ds: list[Any] = []
        page = 1
        while True:
            batch = await loop.run_in_executor(None, _list_page, page)
            if not batch:
                break
            all_ds.extend(batch)
            if len(batch) < page_size:
                break
            page += 1

        return [
            {
                "id": ds.id,
                "name": getattr(ds, "name", ""),
                "document_count": getattr(ds, "document_count", 0),
                "chunk_count": getattr(ds, "chunk_count", 0),
                "embedding_model": getattr(ds, "embedding_model", ""),
                "chunk_method": getattr(ds, "chunk_method", ""),
                "permission": getattr(ds, "permission", ""),
            }
            for ds in all_ds
        ]

    async def delete_dataset(
        self, name_or_id: str, by_id: bool = False,
    ) -> dict[str, Any]:
        """按名称或 id 删除一个 dataset。

        绕过 ragflow-sdk 0.25.4 的 `delete_datasets()` bug —— 该版本会
        发送 `delete_all` 字段，而 RAGFlow 服务端用 strict schema 拒绝
        该额外字段。这里直接走原始 DELETE /api/v1/datasets 接口。

        Args:
            name_or_id: dataset 名称（默认）或 id。
            by_id: True 表示传入的是 dataset id，跳过名字解析。

        Returns:
            {"id": str, "name": str, "deleted": bool}

        Raises:
            ValueError: 名称未匹配到任何 dataset，或匹配到多个。
            RuntimeError: 服务端返回非 0 错误码。
        """
        await self.connect()
        loop = asyncio.get_event_loop()

        if by_id:
            target_id = name_or_id
            target_name = name_or_id
        else:
            datasets = await self.list_all_datasets()
            matched = [d for d in datasets if d["name"] == name_or_id]
            if not matched:
                raise ValueError(
                    f"dataset 名称 '{name_or_id}' 未找到。可用: "
                    f"{[d['name'] for d in datasets]}"
                )
            if len(matched) > 1:
                raise ValueError(
                    f"dataset 名称 '{name_or_id}' 匹配到多个: "
                    f"{[d['id'] for d in matched]}，请改用 by_id=True"
                )
            target_id = matched[0]["id"]
            target_name = matched[0]["name"]

        def _delete() -> dict[str, Any]:
            # 注意：故意不传 delete_all 字段——这是 SDK 0.25.4 的 bug 触发点。
            res = self._rag.delete("/datasets", {"ids": [target_id]})
            return res.json()

        body = await loop.run_in_executor(None, _delete)
        code = body.get("code")
        if code != 0:
            raise RuntimeError(
                f"删除 dataset '{target_name}' (id={target_id}) 失败: "
                f"code={code} message={body.get('message')}"
            )

        logger.info(f"已删除 dataset '{target_name}' (id={target_id})")
        return {"id": target_id, "name": target_name, "deleted": True}

    async def close(self) -> None:
        """清理引用。"""
        self._rag = None
        self._dataset = None
        logger.debug("RAGFlow 客户端已关闭")
