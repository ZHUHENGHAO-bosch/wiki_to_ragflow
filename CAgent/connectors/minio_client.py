"""
connectors/minio_client.py — MinIO 上传客户端

将 bug 下载产物上传到 MinIO 对象存储，按 input/result 分目录组织。

MinIO 目录结构:
    agent (bucket)
    └── tagent/
        └── <bug_id>/
            ├── input/
            │   ├── description.json
            │   └── attachments/
            │       ├── file1.jpg
            │       └── file2.rar
            └── result/
                └── summary.json
"""
from __future__ import annotations

import logging
from pathlib import Path

from minio import Minio
from minio.error import S3Error

logger = logging.getLogger("minio_client")

# 本地文件 → MinIO 子目录映射
_FILE_MAPPING: dict[str, str] = {
    "description.json": "input/description.json",
    "summary.json": "result/summary.json",
}


class MinioUploader:
    """轻量 MinIO 上传客户端。"""

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str = "agent",
        prefix: str = "tagent",
        secure: bool = False,
    ) -> None:
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self.bucket = bucket
        self.prefix = prefix
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        """确保 bucket 存在，不存在则创建。"""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info("已创建 bucket: %s", self.bucket)
        except S3Error as e:
            logger.error("检查/创建 bucket 失败: %s", e)
            raise

    def upload_file(self, local_path: str | Path, object_name: str) -> bool:
        """上传单个文件到 MinIO。

        Args:
            local_path: 本地文件路径
            object_name: MinIO 对象名（不含 bucket）

        Returns:
            上传是否成功
        """
        local_path = Path(local_path)
        if not local_path.is_file():
            logger.warning("文件不存在，跳过: %s", local_path)
            return False

        try:
            self.client.fput_object(self.bucket, object_name, str(local_path))
            logger.debug("已上传: %s → %s/%s", local_path.name, self.bucket, object_name)
            return True
        except S3Error as e:
            logger.error("上传失败 %s: %s", object_name, e)
            return False

    def upload_bug(self, bug_dir: str | Path, bug_id: str) -> dict:
        """上传一个 bug 的完整产物到 MinIO。

        本地目录结构:
            <bug_dir>/
            ├── description.json  → input/description.json
            ├── summary.json      → result/summary.json
            └── attachments/      → input/attachments/

        Args:
            bug_dir: bug 输出目录（如 output/12345）
            bug_id: bug ID

        Returns:
            {"total": N, "success": N, "failed": N, "files": [...]}
        """
        bug_dir = Path(bug_dir)
        base_prefix = f"{self.prefix}/{bug_id}"

        uploaded: list[str] = []
        failed: list[str] = []

        # 1. 上传映射文件 (description.json → input/, summary.json → result/)
        for local_name, remote_path in _FILE_MAPPING.items():
            local_file = bug_dir / local_name
            object_name = f"{base_prefix}/{remote_path}"
            if self.upload_file(local_file, object_name):
                uploaded.append(object_name)
            elif local_file.exists():
                failed.append(object_name)

        # 2. 上传附件目录 → input/attachments/
        att_dir = bug_dir / "attachments"
        if att_dir.is_dir():
            for att_file in att_dir.iterdir():
                if att_file.is_file():
                    object_name = f"{base_prefix}/input/attachments/{att_file.name}"
                    if self.upload_file(att_file, object_name):
                        uploaded.append(object_name)
                    else:
                        failed.append(object_name)

        total = len(uploaded) + len(failed)
        logger.info(
            "[%s] MinIO 上传完成: %d/%d 成功 → %s/%s/",
            bug_id, len(uploaded), total, self.bucket, base_prefix,
        )

        return {
            "total": total,
            "success": len(uploaded),
            "failed": len(failed),
            "files": uploaded,
        }
