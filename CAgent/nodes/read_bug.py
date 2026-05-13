"""
read_bug.py — Node 0: 从 Bug 管理系统读取 Bug 信息

输入 State 字段: bug_key
输出 State 字段: bug_info, bug_source
依赖: BugTrackerClient (JiraClient 或 RtcClient)
"""
from __future__ import annotations

import logging
from typing import Any

from config import JiraConfig, RtcConfig
from connectors.bug_tracker import BugTrackerClient
from models import AttachmentInfo, BugInfo
from state import AnalysisState

logger = logging.getLogger(__name__)


def create_read_bug_node(
    tracker: BugTrackerClient, config: JiraConfig | RtcConfig
):
    """
    工厂函数，返回绑定了 tracker 的 Node 函数。

    LangGraph Node 必须是 (state) -> dict 签名，
    所以用闭包捕获外部依赖。
    """

    async def read_bug(state: AnalysisState) -> dict[str, Any]:
        bug_key = state["bug_key"]
        logger.info(f"[Node 0] 读取 Bug: {bug_key} (source={tracker.source_type})")

        try:
            issue = await tracker.get_issue(bug_key)
            fields = issue.get("fields", {})

            # 获取关联的 Test Case
            link_type = (
                config.test_case_link_type
                if isinstance(config, JiraConfig)
                else "children"
            )
            links = await tracker.get_issue_links(bug_key, link_type)
            linked_tc_keys = [link["key"] for link in links]

            # 提取 components
            components = [
                c.get("name", "") if isinstance(c, dict) else str(c)
                for c in fields.get("components", [])
            ]

            # 提取 reporter
            reporter_obj = fields.get("reporter") or {}
            if isinstance(reporter_obj, dict):
                reporter = reporter_obj.get("displayName", reporter_obj.get("name", ""))
            else:
                reporter = str(reporter_obj)

            # 获取附件列表 (仅元数据，不下载)
            attachment_list: list[AttachmentInfo] = []
            try:
                raw_attachments = await tracker.get_attachments(bug_key)
                attachment_list = [
                    AttachmentInfo(
                        name=att.get("name", ""),
                        url=att.get("url", ""),
                        attachment_id=att.get("attachment_id", ""),
                    )
                    for att in raw_attachments
                ]
            except Exception as e:
                logger.warning(
                    f"[Node 0] 获取 Bug {bug_key} 附件列表失败: {e}"
                )

            bug_info = BugInfo(
                key=bug_key,
                summary=fields.get("summary", ""),
                description=fields.get("description", "") or "",
                priority=_extract_priority(fields),
                components=components,
                environment=fields.get("environment", "") or "",
                labels=fields.get("labels", []),
                created=fields.get("created", ""),
                reporter=reporter,
                linked_test_case_keys=linked_tc_keys,
                attachments=attachment_list,
                raw_fields=fields,
            )

            logger.info(
                f"[Node 0] Bug {bug_key}: "
                f"关联 {len(linked_tc_keys)} 个 Test Case, "
                f"{len(attachment_list)} 个附件"
            )
            return {"bug_info": bug_info, "bug_source": tracker.source_type}

        except Exception as e:
            logger.error(f"[Node 0] 读取 Bug {bug_key} 失败: {e}")
            return {
                "bug_info": None,
                "bug_source": tracker.source_type,
                "errors": state.get("errors", []) + [f"读取 Bug 失败: {e}"],
                "status": "failed",
            }

    return read_bug


def _extract_priority(fields: dict[str, Any]) -> str:
    """从 fields 提取 priority name。"""
    priority = fields.get("priority")
    if isinstance(priority, dict):
        return priority.get("name", "")
    return str(priority) if priority else ""
