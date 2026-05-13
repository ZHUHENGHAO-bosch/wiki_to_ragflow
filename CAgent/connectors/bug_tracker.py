"""
connectors/bug_tracker.py — Bug 管理系统统一接口

定义 BugTrackerClient Protocol，JiraClient 和 RtcClient 均需满足。
使用 Python 结构化子类型 (duck typing)，无需显式继承。
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class BugTrackerClient(Protocol):
    """Bug 管理系统统一接口。"""

    @property
    def source_type(self) -> str:
        """返回 "jira" 或 "rtc"。"""
        ...

    async def get_issue(self, key: str, fields: str = "*all") -> dict[str, Any]:
        ...

    async def get_issue_links(
        self, key: str, link_type: str | None = None
    ) -> list[dict[str, Any]]:
        ...

    async def get_remote_links(self, key: str) -> list[dict[str, Any]]:
        ...

    async def search_issues(
        self,
        query: str,
        fields: str = "summary,status,priority",
        max_results: int = 50,
    ) -> list[dict[str, Any]]:
        ...

    async def add_comment(self, key: str, body: str) -> dict[str, Any]:
        ...

    async def update_labels(
        self,
        key: str,
        add_labels: list[str],
        remove_labels: list[str] | None = None,
    ) -> None:
        ...

    async def create_issue(
        self,
        project_key: str,
        issue_type: str,
        summary: str,
        description: str = "",
        **extra_fields: Any,
    ) -> str:
        ...

    async def create_link(
        self, link_type: str, inward_key: str, outward_key: str
    ) -> None:
        ...

    async def get_attachments(self, key: str) -> list[dict[str, Any]]:
        """获取 issue 的附件列表。

        返回: [{name, url, attachment_id}, ...]
        """
        ...

    async def download_attachment(self, url: str, save_path: str) -> str:
        """下载单个附件到指定路径，返回保存的文件路径。"""
        ...

    async def download_all_attachments(
        self, key: str, output_dir: str | None = None,
    ) -> list[dict[str, Any]]:
        """下载 issue 的所有附件。

        返回: [{name, path, success, error?}, ...]
        """
        ...

    async def close(self) -> None:
        ...
