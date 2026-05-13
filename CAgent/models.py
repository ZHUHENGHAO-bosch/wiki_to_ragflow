"""
models.py — Pydantic 数据模型

所有 Node 共享的数据结构定义。不含 LangGraph State（见 state.py）。
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ── Jira 数据 ──


class AttachmentInfo(BaseModel):
    """Bug 附件元数据 (不含文件内容)。"""

    name: str
    url: str = ""
    attachment_id: str = ""
    downloaded_path: str = ""  # 下载后的本地路径 (为空表示未下载)


class BugInfo(BaseModel):
    """从 Jira/RTC 读取的 Bug 信息。"""

    key: str
    summary: str
    description: str = ""
    priority: str = ""
    components: list[str] = Field(default_factory=list)
    environment: str = ""
    labels: list[str] = Field(default_factory=list)
    created: str = ""
    reporter: str = ""
    linked_test_case_keys: list[str] = Field(default_factory=list)
    attachments: list[AttachmentInfo] = Field(default_factory=list)
    raw_fields: dict[str, Any] = Field(default_factory=dict)


class TestStep(BaseModel):
    """测试用例中的单个步骤。"""

    step: str = ""
    expected: str = ""
    actual: str = ""


class TestCaseInfo(BaseModel):
    """从 Jira 读取的 Test Case 信息。"""

    key: str
    summary: str
    description: str = ""
    steps: list[TestStep] = Field(default_factory=list)
    linked_requirement_ids: list[str] = Field(default_factory=list)
    status: str = ""
    priority: str = ""


# ── DNG 数据 ──


class RequirementInfo(BaseModel):
    """从 DNG 读取的需求信息。"""

    req_id: str
    title: str
    description: str = ""
    req_type: str = ""
    asil_level: str = ""
    linked_module_names: list[str] = Field(default_factory=list)
    linked_test_case_ids: list[str] = Field(default_factory=list)
    url: str = ""


# ── Git 数据 ──


class GitCommit(BaseModel):
    """Git commit 信息。"""

    hash: str
    author: str
    date: str
    message: str


class CodeSnippet(BaseModel):
    """代码片段，包含上下文。"""

    file_path: str
    start_line: int
    end_line: int
    content: str
    language: str = ""


class CodeInfo(BaseModel):
    """从 Git 读取的代码相关信息。"""

    files: list[str] = Field(default_factory=list)
    snippets: list[CodeSnippet] = Field(default_factory=list)
    recent_commits: list[GitCommit] = Field(default_factory=list)


# ── 根因分析结果 ──


class RootCauseLevel(str, Enum):
    """根因层级枚举。"""

    IMPLEMENTATION_DEVIATION = "实现偏离"
    IMPLEMENTATION_MISSING = "实现遗漏"
    REQUIREMENT_MISSING = "需求遗漏"
    REQUIREMENT_AMBIGUITY = "需求歧义"
    TEST_DEFECT = "测试缺陷"
    REGRESSION = "回归引入"


class FixSuggestion(BaseModel):
    """修复建议。"""

    label: str
    description: str
    effort: str = ""


class RootCauseResult(BaseModel):
    """根因分析结果。"""

    level: RootCauseLevel
    summary: str
    detail: str = ""
    problem_location: str = ""
    introducer: str | None = None
    introducing_commit: str | None = None
    fix_suggestions: list[FixSuggestion] = Field(default_factory=list)


# ── 影响扩散结果 ──


class ImpactItem(BaseModel):
    """单个受影响项。"""

    module_name: str
    file_path: str = ""
    related_test_cases: list[str] = Field(default_factory=list)
    related_requirements: list[str] = Field(default_factory=list)
    risk_level: str = "medium"
    note: str = ""


class ImpactResult(BaseModel):
    """影响扩散分析结果。"""

    affected_items: list[ImpactItem] = Field(default_factory=list)
    regression_test_list: list[str] = Field(default_factory=list)
    total_affected_modules: int = 0


# ── 流程状态 ──


class AnalysisStatus(str, Enum):
    """分析状态枚举。"""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


# ── 最终报告 ──


class AnalysisReport(BaseModel):
    """最终分析报告，在 write_report Node 中组装。"""

    bug_key: str
    bug_info: BugInfo | None = None
    test_cases: list[TestCaseInfo] = Field(default_factory=list)
    requirements: list[RequirementInfo] = Field(default_factory=list)
    code_info: CodeInfo | None = None
    root_cause: RootCauseResult | None = None
    impact: ImpactResult | None = None
    status: AnalysisStatus = AnalysisStatus.SUCCESS
    errors: list[str] = Field(default_factory=list)
    analysis_duration: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)
