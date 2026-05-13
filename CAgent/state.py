"""
state.py — LangGraph State 定义

所有 Node 共享这个 State。每个 Node 只更新自己负责的字段。
使用 TypedDict 定义，LangGraph 要求。
"""
from __future__ import annotations

from typing import TypedDict

from models import (
    AnalysisStatus,
    BugInfo,
    CodeInfo,
    ImpactResult,
    RequirementInfo,
    RootCauseResult,
    TestCaseInfo,
)


class AnalysisState(TypedDict):
    """LangGraph 状态，贯穿整个分析流程。"""

    # ── 输入 ──
    bug_key: str

    # ── Step 0: read_bug 填充 ──
    bug_info: BugInfo | None

    # ── Step 1: read_testcase / search_testcase 填充 ──
    test_cases: list[TestCaseInfo]

    # ── Step 2: read_requirement / search_requirement 填充 ──
    requirements: list[RequirementInfo]

    # ── Step 3: read_code 填充 ──
    code_info: CodeInfo | None

    # ── Step 4: analyze_root_cause 填充 ──
    root_cause: RootCauseResult | None

    # ── Step 5: analyze_impact 填充 ──
    impact: ImpactResult | None

    # ── 流程控制 ──
    bug_source: str  # "jira" | "rtc"
    status: AnalysisStatus
    errors: list[str]
    analysis_duration: float
