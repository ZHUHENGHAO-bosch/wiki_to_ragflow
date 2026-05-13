"""
search_testcase.py — Node 1b: Bug 无关联 Test Case 时的降级搜索

触发条件: state["test_cases"] 为空
输入 State 字段: bug_info.components, bug_info.summary
输出 State 字段: test_cases, errors (追加)
依赖: BugTrackerClient (JiraClient 或 RtcClient)
"""
from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

from config import JiraConfig, RtcConfig
from connectors.bug_tracker import BugTrackerClient
from nodes.read_testcase import _read_single_tc
from state import AnalysisState

logger = logging.getLogger(__name__)


def create_search_testcase_node(
    tracker: BugTrackerClient, config: JiraConfig | RtcConfig
):

    async def search_testcase(state: AnalysisState) -> dict[str, Any]:
        bug_info = state.get("bug_info")
        if not bug_info:
            return {
                "test_cases": [],
                "errors": state.get("errors", []) + ["降级搜索: bug_info 为空"],
            }

        logger.info("[Node 1b] 降级搜索 Test Case")

        # 构建搜索关键词
        keywords = _extract_keywords(bug_info.summary, bug_info.components)

        if isinstance(config, JiraConfig):
            # Jira: 构造 JQL
            jql_parts: list[str] = [
                f'issuetype = "{config.test_case_issue_type}"'
            ]

            if bug_info.components:
                comp_str = ", ".join(f'"{c}"' for c in bug_info.components)
                jql_parts.append(f"component in ({comp_str})")

            if keywords:
                kw_query = " OR ".join(f'summary ~ "{kw}"' for kw in keywords[:5])
                jql_parts.append(f"({kw_query})")

            if len(jql_parts) > 1:
                query = f"{jql_parts[0]} AND ({' OR '.join(jql_parts[1:])})"
            else:
                query = jql_parts[0]
        else:
            # RTC: 使用 Saved Query ID 或内联查询
            if isinstance(config, RtcConfig) and config.saved_query_id:
                query = config.saved_query_id
            else:
                # 内联查询: 简单关键词组合
                kw_part = " OR ".join(keywords[:5]) if keywords else ""
                query = kw_part or "type=defect"

        logger.debug(f"[Node 1b] Query: {query}")

        try:
            issues = await tracker.search_issues(query, max_results=5)
        except Exception as e:
            logger.error(f"[Node 1b] 搜索失败: {e}")
            return {
                "test_cases": [],
                "errors": state.get("errors", [])
                + [f"降级搜索 Test Case 失败: {e}"],
            }

        if not issues:
            logger.info("[Node 1b] 未搜索到 Test Case")
            return {
                "test_cases": [],
                "errors": state.get("errors", []) + ["未找到关联 Test Case"],
            }

        # 读取详情
        keys = [issue["key"] for issue in issues]
        tasks = [_read_single_tc(tracker, config, key) for key in keys]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        test_cases = [r for r in results if r and not isinstance(r, Exception)]

        msg = f"通过关键词搜索找到 {len(test_cases)} 个 Test Case"
        logger.info(f"[Node 1b] {msg}")

        return {
            "test_cases": test_cases,
            "errors": state.get("errors", []) + [msg],
        }

    return search_testcase


def _extract_keywords(summary: str, components: list[str]) -> list[str]:
    """从 summary 中提取有意义的关键词。"""
    stop_words = {
        "the", "is", "at", "which", "on", "a", "an", "and", "or", "not",
        "bug", "error", "issue", "fail", "failed", "failure", "problem",
    }

    words = re.findall(r"[a-zA-Z_]\w{2,}", summary)
    keywords = [w for w in words if w.lower() not in stop_words]

    # 加入 components
    keywords.extend(components)

    # 去重保序
    seen: set[str] = set()
    result: list[str] = []
    for kw in keywords:
        if kw.lower() not in seen:
            seen.add(kw.lower())
            result.append(kw)

    return result
