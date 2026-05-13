"""
connectors/jira_client.py — Jira REST API 封装

纯 API 封装，不感知 LangGraph。

认证方式（与 tools/jira_download.py 保持一致）：
- auth_method="bearer" → Bearer token（Jira Server/Data Center PAT）
- auth_method="basic"  → Basic Auth（Jira Cloud / 用户名+密码）
- auth_method=""       → 自动检测（token 长度 >30 且全为 base64 字符则用 Bearer）
"""
from __future__ import annotations

import logging
import string
from typing import Any

import httpx

from config import JiraConfig

logger = logging.getLogger(__name__)

_BASE64_CHARS = set(string.ascii_letters + string.digits + "+/=")


def _is_likely_pat(token: str, auth_method: str) -> bool:
    """判定是否应走 Bearer token 路径（PAT）。"""
    if auth_method == "bearer":
        return True
    if auth_method == "basic":
        return False
    return bool(token) and len(token) > 30 and all(c in _BASE64_CHARS for c in token)


class JiraClient:
    """Jira REST API v2 客户端。"""

    def __init__(self, config: JiraConfig) -> None:
        self._config = config
        self._base = config.base_url.rstrip("/")

        token = config.api_token or ""
        auth_method = getattr(config, "auth_method", "") or ""
        headers: dict[str, str] = {}
        auth: tuple[str, str] | None = None

        if _is_likely_pat(token, auth_method):
            headers["Authorization"] = f"Bearer {token}"
        else:
            auth = (config.username, token)

        self._client = httpx.AsyncClient(
            base_url=f"{self._base}/rest/api/2",
            auth=auth,
            headers=headers,
            verify=config.verify_ssl,
            timeout=30.0,
        )

    @property
    def source_type(self) -> str:
        return "jira"

    # ── Issue 操作 ──

    async def get_issue(self, key: str, fields: str = "*all") -> dict[str, Any]:
        """获取单个 Issue 的全部字段。"""
        resp = await self._client.get(
            f"/issue/{key}",
            params={"fields": fields},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_issue_links(
        self, key: str, link_type: str | None = None
    ) -> list[dict[str, Any]]:
        """
        获取 Issue 的关联链接。

        如果指定 link_type，只返回该类型的链接。
        返回列表中每项包含: type, inward/outward issue key。
        """
        issue = await self.get_issue(key, fields="issuelinks")
        links = issue.get("fields", {}).get("issuelinks", [])
        results: list[dict[str, Any]] = []
        for link in links:
            lt = link.get("type", {}).get("name", "")
            if link_type and lt != link_type:
                continue
            target: dict[str, Any] | None = link.get(
                "outwardIssue"
            ) or link.get("inwardIssue")
            if target:
                results.append(
                    {
                        "type": lt,
                        "direction": (
                            "outward" if "outwardIssue" in link else "inward"
                        ),
                        "key": target["key"],
                        "summary": target.get("fields", {}).get("summary", ""),
                    }
                )
        return results

    async def get_remote_links(self, key: str) -> list[dict[str, Any]]:
        """获取 Issue 的 Remote Links (常用于关联外部系统如 DNG)。"""
        resp = await self._client.get(f"/issue/{key}/remotelink")
        resp.raise_for_status()
        return resp.json()

    async def search_issues(
        self,
        jql: str,
        fields: str = "summary,status,priority",
        max_results: int = 50,
    ) -> list[dict[str, Any]]:
        """JQL 搜索，返回 issue 列表。"""
        resp = await self._client.post(
            "/search",
            json={
                "jql": jql,
                "fields": [f.strip() for f in fields.split(",")],
                "maxResults": max_results,
            },
        )
        resp.raise_for_status()
        return resp.json().get("issues", [])

    # ── 写操作 ──

    async def add_comment(self, key: str, body: str) -> dict[str, Any]:
        """在 Issue 上添加评论。"""
        resp = await self._client.post(
            f"/issue/{key}/comment",
            json={"body": body},
        )
        resp.raise_for_status()
        return resp.json()

    async def update_labels(
        self, key: str, add_labels: list[str], remove_labels: list[str] | None = None
    ) -> None:
        """更新 Issue 的 labels。"""
        update: dict[str, list[dict[str, str]]] = {
            "add": [{"add": label} for label in add_labels],
        }
        if remove_labels:
            update["remove"] = [{"remove": label} for label in remove_labels]

        resp = await self._client.put(
            f"/issue/{key}",
            json={"update": {"labels": update["add"] + update.get("remove", [])}},
        )
        resp.raise_for_status()

    async def create_issue(
        self,
        project_key: str,
        issue_type: str,
        summary: str,
        description: str = "",
        **extra_fields: Any,
    ) -> str:
        """创建新 Issue，返回 key。"""
        fields: dict[str, Any] = {
            "project": {"key": project_key},
            "issuetype": {"name": issue_type},
            "summary": summary,
        }
        if description:
            fields["description"] = description
        fields.update(extra_fields)

        resp = await self._client.post("/issue", json={"fields": fields})
        resp.raise_for_status()
        return resp.json()["key"]

    async def create_link(
        self, link_type: str, inward_key: str, outward_key: str
    ) -> None:
        """创建两个 Issue 之间的链接。"""
        resp = await self._client.post(
            "/issueLink",
            json={
                "type": {"name": link_type},
                "inwardIssue": {"key": inward_key},
                "outwardIssue": {"key": outward_key},
            },
        )
        resp.raise_for_status()

    # ── 附件操作 ──

    async def get_attachments(self, key: str) -> list[dict[str, Any]]:
        """获取 Issue 的附件列表 (Jira 侧暂未实现)。"""
        return []

    async def download_attachment(self, url: str, save_path: str) -> str:
        """下载附件 (Jira 侧暂未实现)。"""
        raise NotImplementedError("Jira attachment download not implemented")

    async def download_all_attachments(
        self, key: str, output_dir: str | None = None,
    ) -> list[dict[str, Any]]:
        """下载所有附件 (Jira 侧暂未实现)。"""
        return []

    # ── 生命周期 ──

    async def close(self) -> None:
        """关闭 HTTP 客户端。"""
        await self._client.aclose()
