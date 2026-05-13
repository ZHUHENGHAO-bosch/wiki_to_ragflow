"""
read_testcase.py — Node 1: 读取关联的 Test Case

输入 State 字段: bug_info.linked_test_case_keys
输出 State 字段: test_cases
依赖: BugTrackerClient (JiraClient 或 RtcClient)
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any

from config import JiraConfig, RtcConfig
from connectors.bug_tracker import BugTrackerClient
from models import TestCaseInfo, TestStep
from state import AnalysisState

logger = logging.getLogger(__name__)


def create_read_testcase_node(
    tracker: BugTrackerClient, config: JiraConfig | RtcConfig
):

    async def read_testcase(state: AnalysisState) -> dict[str, Any]:
        bug_info = state.get("bug_info")
        if not bug_info:
            logger.warning("[Node 1] bug_info 为空，跳过")
            return {"test_cases": []}

        tc_keys = bug_info.linked_test_case_keys
        if not tc_keys:
            logger.info("[Node 1] 无关联 Test Case")
            return {"test_cases": []}

        logger.info(f"[Node 1] 读取 {len(tc_keys)} 个 Test Case")

        tasks = [_read_single_tc(tracker, config, key) for key in tc_keys]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        test_cases: list[TestCaseInfo] = []
        errors: list[str] = []
        for key, result in zip(tc_keys, results):
            if isinstance(result, Exception):
                errors.append(f"读取 Test Case {key} 失败: {result}")
                logger.warning(f"[Node 1] 读取 {key} 失败: {result}")
            elif result:
                test_cases.append(result)

        logger.info(f"[Node 1] 成功读取 {len(test_cases)} 个 Test Case")

        update: dict[str, Any] = {"test_cases": test_cases}
        if errors:
            update["errors"] = state.get("errors", []) + errors
        return update

    return read_testcase


async def _read_single_tc(
    tracker: BugTrackerClient, config: JiraConfig | RtcConfig, key: str
) -> TestCaseInfo | None:
    """读取并解析单个 Test Case。"""
    issue = await tracker.get_issue(key)
    fields = issue.get("fields", {})

    # 解析测试步骤
    test_steps_field = (
        config.test_steps_field if isinstance(config, JiraConfig) else ""
    )
    steps = _parse_test_steps(fields.get(test_steps_field) if test_steps_field else None)

    # 获取关联需求 ID
    req_ids = await _extract_requirement_ids(tracker, config, key, fields)

    # 提取 status
    status_obj = fields.get("status") or {}
    status = status_obj.get("name", "") if isinstance(status_obj, dict) else ""

    return TestCaseInfo(
        key=key,
        summary=fields.get("summary", ""),
        description=fields.get("description", "") or "",
        steps=steps,
        linked_requirement_ids=req_ids,
        status=status,
        priority=_extract_priority(fields),
    )


def _parse_test_steps(raw: Any) -> list[TestStep]:
    """
    解析测试步骤字段。

    支持格式:
    - JSON 数组: [{"step": "...", "expected": "...", "actual": "..."}]
    - 纯文本: 按行拆分
    - None: 返回空列表
    """
    if raw is None:
        return []

    if isinstance(raw, list):
        return [
            TestStep(
                step=item.get("step", ""),
                expected=item.get("expected", item.get("expectedResult", "")),
                actual=item.get("actual", item.get("actualResult", "")),
            )
            for item in raw
            if isinstance(item, dict)
        ]

    if isinstance(raw, str):
        raw = raw.strip()
        if not raw:
            return []

        # 尝试 JSON 解析
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return _parse_test_steps(parsed)
        except json.JSONDecodeError:
            pass

        # 按行拆分为步骤
        lines = [line.strip() for line in raw.split("\n") if line.strip()]
        return [TestStep(step=line) for line in lines]

    return []


async def _extract_requirement_ids(
    tracker: BugTrackerClient,
    config: JiraConfig | RtcConfig,
    key: str,
    fields: dict[str, Any],
) -> list[str]:
    """
    从 Test Case 中提取关联的需求 ID。

    两种来源:
    1. Remote Links 中的 DNG 链接
    2. 自定义字段直接存储需求 ID
    """
    req_ids: list[str] = []

    # 方式 1: Remote Links
    try:
        remote_links = await tracker.get_remote_links(key)
        for rl in remote_links:
            url = (rl.get("object") or {}).get("url", "")
            extracted = _extract_req_id_from_url(url)
            if extracted:
                req_ids.append(extracted)
    except Exception as e:
        logger.debug(f"获取 {key} Remote Links 失败: {e}")

    # 方式 2: 自定义字段 (仅 Jira)
    if isinstance(config, JiraConfig):
        req_field_value = fields.get(config.requirement_field)
        if req_field_value:
            if isinstance(req_field_value, str):
                for part in req_field_value.split(","):
                    part = part.strip()
                    if part:
                        req_ids.append(part)
            elif isinstance(req_field_value, list):
                req_ids.extend(str(v) for v in req_field_value if v)

    return list(dict.fromkeys(req_ids))  # 去重保序


def _extract_req_id_from_url(url: str) -> str | None:
    """从 DNG Remote Link URL 中正则提取需求 ID。"""
    if not url:
        return None
    # 常见格式: .../rm/resources/REQ-042 或 .../rm/resources/_abc123
    match = re.search(r"/rm/resources/([^/?#]+)", url)
    if match:
        return match.group(1)
    # 退 fallback: URL 最后一段
    parts = url.rstrip("/").split("/")
    if parts:
        return parts[-1]
    return None


def _extract_priority(fields: dict[str, Any]) -> str:
    priority = fields.get("priority")
    if isinstance(priority, dict):
        return priority.get("name", "")
    return str(priority) if priority else ""
