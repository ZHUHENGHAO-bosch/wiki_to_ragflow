"""
write_report.py — Node 6: 格式化报告 + 写回 Bug 管理系统

输入 State 字段: 所有字段
输出 State 字段: analysis_duration
依赖: BugTrackerClient, AppConfig, ReportFormatter

支持 Jira 和 RTC 双系统写回。
"""
from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from config import AppConfig
from connectors.bug_tracker import BugTrackerClient
from connectors.report_formatter import ReportFormatter
from connectors.teams_client import TeamsClient
from state import AnalysisState

logger = logging.getLogger(__name__)


def create_write_report_node(
    tracker: BugTrackerClient,
    config: AppConfig,
    formatter: ReportFormatter,
    teams_client: TeamsClient | None = None,
):

    async def write_report(state: AnalysisState) -> dict[str, Any]:
        start = time.monotonic()
        bug_key = state["bug_key"]
        logger.info(f"[Node 6] 写报告: {bug_key} (source={tracker.source_type})")

        # 确定最终状态
        status = _determine_status(state)

        # 格式化报告
        comment = formatter.format_report(state, status)

        # 写回 Bug 管理系统
        try:
            await tracker.add_comment(bug_key, comment)
            logger.info(f"[Node 6] 已写入评论到 {bug_key}")
        except Exception as e:
            logger.error(f"[Node 6] 写入评论失败: {e}")

        # 添加 label / tag
        try:
            await tracker.update_labels(
                bug_key, add_labels=[config.writer.analyzed_label]
            )
        except Exception as e:
            logger.warning(f"[Node 6] 更新 label 失败: {e}")

        # 自动创建关联 Bug (如果配置开启)
        if config.writer.auto_create_related_bugs:
            await _create_related_bugs(tracker, config, state)

        # 发送通知 (通用 Webhook)
        if config.writer.notify_webhook:
            _send_notification(state, config.writer.notify_webhook, status)

        # 发送 Teams 通知
        if teams_client and config.teams.notify_on_analysis_complete:
            try:
                await teams_client.send_analysis_result(state)
            except Exception as e:
                logger.warning(f"[Node 6] Teams 通知发送失败: {e}")

        elapsed = time.monotonic() - start
        total_duration = state.get("analysis_duration", 0.0) + elapsed

        return {
            "analysis_duration": total_duration,
            "status": status,
        }

    return write_report


def _determine_status(state: AnalysisState) -> str:
    """根据分析结果确定最终状态。"""
    if state.get("status") == "failed":
        return "failed"
    if state.get("root_cause") is None:
        return "partial"
    if state.get("errors"):
        return "partial"
    return "success"


async def _create_related_bugs(
    tracker: BugTrackerClient, config: AppConfig, state: AnalysisState
) -> None:
    """为高风险影响项创建关联 Bug。"""
    impact = state.get("impact")
    if not impact:
        return

    bug_key = state["bug_key"]
    bug_info = state.get("bug_info")

    # 确定 project key（多 Jira / 多 RTC 时取首个作为默认）
    if tracker.source_type == "jira":
        jira_cfg = config.get_jira_config()
        project_key = jira_cfg.project_key if jira_cfg else ""
        if not project_key and bug_info:
            project_key = bug_key.split("-")[0]
        issue_type = jira_cfg.bug_issue_type if jira_cfg else "Bug"
    else:
        rtc_cfg = config.get_rtc_config()
        project_key = rtc_cfg.project_area_name if rtc_cfg else ""
        issue_type = rtc_cfg.bug_work_item_type if rtc_cfg else "defect"

    for item in impact.affected_items:
        if item.risk_level != "high":
            continue
        if item.note == "未追溯，需人工确认":
            continue

        try:
            summary = (
                f"[影响扩散] {item.module_name} 可能受 {bug_key} 影响"
            )
            description = (
                f"由 Bug Analysis Agent 自动创建。\n\n"
                f"源 Bug: {bug_key}\n"
                f"受影响模块: {item.module_name}\n"
                f"受影响文件: {item.file_path}\n"
                f"关联测试: {', '.join(item.related_test_cases)}"
            )
            new_key = await tracker.create_issue(
                project_key=project_key,
                issue_type=issue_type,
                summary=summary,
                description=description,
            )
            await tracker.create_link(
                "relates to", inward_key=bug_key, outward_key=new_key
            )
            logger.info(f"[Node 6] 创建关联 Bug: {new_key}")
        except Exception as e:
            logger.warning(f"[Node 6] 创建关联 Bug 失败: {e}")


def _send_notification(
    state: AnalysisState, webhook_url: str, status: str
) -> None:
    """POST 到 webhook URL 发送通知。"""
    root_cause = state.get("root_cause")
    payload = {
        "bug_key": state["bug_key"],
        "status": status,
        "root_cause_level": root_cause.level.value if root_cause else None,
        "root_cause_summary": root_cause.summary if root_cause else None,
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(webhook_url, json=payload)
            resp.raise_for_status()
            logger.info(f"[Node 6] 通知发送成功: {webhook_url}")
    except Exception as e:
        logger.warning(f"[Node 6] 通知发送失败: {e}")
