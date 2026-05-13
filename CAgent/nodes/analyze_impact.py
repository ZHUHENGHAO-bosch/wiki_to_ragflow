"""
analyze_impact.py — Node 5: 影响扩散分析

输入 State 字段: root_cause, code_info, requirements
输出 State 字段: impact
依赖: GitClient, DngClient
"""
from __future__ import annotations

import logging
import re
from typing import Any

from connectors.dng_client import DngClient
from connectors.git_client import GitClient
from models import ImpactItem, ImpactResult
from state import AnalysisState

logger = logging.getLogger(__name__)


def create_analyze_impact_node(git: GitClient, dng: DngClient):

    async def analyze_impact(state: AnalysisState) -> dict[str, Any]:
        root_cause = state.get("root_cause")
        code_info = state.get("code_info")

        if not root_cause or not code_info:
            logger.info("[Node 5] root_cause 或 code_info 为空，跳过影响分析")
            return {"impact": None}

        logger.info("[Node 5] 开始影响扩散分析")

        # 1. 从 problem_location 提取函数名
        function_name = _extract_function_name(
            root_cause.problem_location, code_info
        )

        if not function_name:
            logger.info("[Node 5] 未能提取函数名，跳过调用方搜索")
            return {
                "impact": ImpactResult(
                    affected_items=[],
                    regression_test_list=_collect_direct_tests(state),
                    total_affected_modules=0,
                ),
            }

        logger.info(f"[Node 5] 问题函数: {function_name}")

        # 2. 搜索所有调用方
        affected_items: list[ImpactItem] = []
        all_callers: list[dict[str, Any]] = []

        for file_info in code_info.files:
            parts = file_info.split("/", 1)
            if len(parts) != 2:
                continue
            repo_name = parts[0]
            callers = git.search_callers(repo_name, function_name)
            all_callers.extend(callers)

        logger.info(f"[Node 5] 找到 {len(all_callers)} 个调用文件")

        # 3. 对每个调用文件匹配需求和测试
        requirements = state.get("requirements", [])
        for caller in all_callers:
            file_path = caller["file_path"]
            repo_name = caller["repo_name"]

            # 匹配模块名
            related_reqs: list[str] = []
            related_tcs: list[str] = []
            matched = False

            for req in requirements:
                for module in req.linked_module_names:
                    if _module_matches_file(module, file_path):
                        related_reqs.append(req.req_id)
                        related_tcs.extend(req.linked_test_case_ids)
                        matched = True

            risk = _assess_risk(caller, matched)

            affected_items.append(
                ImpactItem(
                    module_name=_extract_module_from_path(file_path),
                    file_path=f"{repo_name}/{file_path}",
                    related_test_cases=list(set(related_tcs)),
                    related_requirements=list(set(related_reqs)),
                    risk_level=risk,
                    note="" if matched else "未追溯，需人工确认",
                )
            )

        # 4. 汇总回归测试清单
        regression_tests = _build_regression_test_list(state, affected_items)

        impact = ImpactResult(
            affected_items=affected_items,
            regression_test_list=regression_tests,
            total_affected_modules=len(affected_items),
        )

        logger.info(
            f"[Node 5] 影响模块: {impact.total_affected_modules}, "
            f"回归测试: {len(impact.regression_test_list)}"
        )
        return {"impact": impact}

    return analyze_impact


def _extract_function_name(
    problem_location: str, code_info: Any
) -> str | None:
    """
    从 problem_location 提取函数名。

    格式: "file.c:142-155" → 读该行范围提取函数名
    或: "apply_cold_filter" → 直接使用
    """
    if not problem_location:
        return None

    # 格式: file:line-line
    match = re.match(r"(.+):(\d+)-(\d+)", problem_location)
    if match:
        file_path = match.group(1)
        start_line = int(match.group(2))
        # 在代码片段中查找该行范围内的函数名
        if code_info and code_info.snippets:
            for snippet in code_info.snippets:
                if file_path in snippet.file_path:
                    func = _find_function_in_snippet(
                        snippet.content, start_line, snippet.start_line
                    )
                    if func:
                        return func
        return None

    # 格式: file:line
    match = re.match(r"(.+):(\d+)", problem_location)
    if match:
        return None

    # 直接是函数名
    if re.match(r"^[a-zA-Z_]\w*$", problem_location):
        return problem_location

    # 尝试从字符串中提取函数名
    func_match = re.search(r"([a-zA-Z_]\w+)\s*\(", problem_location)
    if func_match:
        return func_match.group(1)

    return None


def _find_function_in_snippet(
    content: str, target_line: int, snippet_start: int
) -> str | None:
    """在代码片段中查找指定行附近的函数定义。"""
    lines = content.split("\n")
    offset = target_line - snippet_start

    # 从目标行向上搜索函数定义
    func_pattern = re.compile(r"([a-zA-Z_]\w+)\s*\(")
    for i in range(min(offset, len(lines) - 1), max(offset - 30, -1), -1):
        if i < 0:
            break
        match = func_pattern.search(lines[i])
        if match:
            return match.group(1)
    return None


def _module_matches_file(module_name: str, file_path: str) -> bool:
    """检查模块名是否匹配文件路径。"""
    module_lower = module_name.lower()
    file_lower = file_path.lower()

    # 直接包含
    if module_lower in file_lower:
        return True

    # 去除扩展名比较
    file_stem = file_path.rsplit(".", 1)[0].rsplit("/", 1)[-1].lower()
    if module_lower == file_stem:
        return True

    return False


def _extract_module_from_path(file_path: str) -> str:
    """从文件路径提取模块名。"""
    name = file_path.rsplit("/", 1)[-1]
    return name.rsplit(".", 1)[0] if "." in name else name


def _assess_risk(caller: dict[str, Any], has_traceability: bool) -> str:
    """评估风险等级。"""
    call_count = caller.get("call_count", 0)
    if not has_traceability:
        return "high"
    if call_count > 3:
        return "high"
    if call_count > 1:
        return "medium"
    return "low"


def _collect_direct_tests(state: AnalysisState) -> list[str]:
    """收集直接关联的 Test Case。"""
    test_cases = state.get("test_cases", [])
    return [tc.key for tc in test_cases]


def _build_regression_test_list(
    state: AnalysisState, affected_items: list[ImpactItem]
) -> list[str]:
    """汇总去重的回归测试列表。"""
    tests: list[str] = []
    seen: set[str] = set()

    # 直接关联
    for tc in state.get("test_cases", []):
        if tc.key not in seen:
            seen.add(tc.key)
            tests.append(tc.key)

    # 扩散发现
    for item in affected_items:
        for tc_id in item.related_test_cases:
            if tc_id not in seen:
                seen.add(tc_id)
                tests.append(tc_id)

    return tests
