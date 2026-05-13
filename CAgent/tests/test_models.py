"""models.py 单元测试。"""
from __future__ import annotations

from models import (
    AnalysisReport,
    AnalysisStatus,
    BugInfo,
    CodeInfo,
    CodeSnippet,
    FixSuggestion,
    GitCommit,
    ImpactItem,
    ImpactResult,
    RequirementInfo,
    RootCauseLevel,
    RootCauseResult,
    TestCaseInfo,
    TestStep,
)


class TestBugInfo:
    def test_minimal(self):
        bug = BugInfo(key="PRJ-1", summary="crash on startup")
        assert bug.key == "PRJ-1"
        assert bug.summary == "crash on startup"
        assert bug.description == ""
        assert bug.components == []
        assert bug.linked_test_case_keys == []

    def test_full(self):
        bug = BugInfo(
            key="PRJ-2",
            summary="null pointer",
            description="Segfault at line 42",
            priority="Critical",
            components=["ModuleA", "ModuleB"],
            environment="ECU v2.0",
            labels=["regression"],
            reporter="张三",
            linked_test_case_keys=["TC-1", "TC-2"],
        )
        assert len(bug.components) == 2
        assert bug.reporter == "张三"
        assert len(bug.linked_test_case_keys) == 2


class TestTestCaseInfo:
    def test_with_steps(self):
        tc = TestCaseInfo(
            key="TC-1",
            summary="Test cold start",
            steps=[
                TestStep(step="Turn on", expected="LED green", actual="LED red"),
                TestStep(step="Wait 5s", expected="Ready"),
            ],
            linked_requirement_ids=["REQ-001"],
        )
        assert len(tc.steps) == 2
        assert tc.steps[0].actual == "LED red"
        assert tc.linked_requirement_ids == ["REQ-001"]

    def test_empty_steps(self):
        tc = TestCaseInfo(key="TC-2", summary="basic")
        assert tc.steps == []


class TestRequirementInfo:
    def test_basic(self):
        req = RequirementInfo(
            req_id="REQ-001",
            title="Cold Start",
            asil_level="ASIL-B",
            linked_module_names=["cold_filter"],
        )
        assert req.asil_level == "ASIL-B"
        assert req.linked_module_names == ["cold_filter"]


class TestCodeInfo:
    def test_with_snippets(self):
        snippet = CodeSnippet(
            file_path="src/main.c",
            start_line=10,
            end_line=20,
            content="int main() { return 0; }",
            language="c",
        )
        commit = GitCommit(
            hash="abc1234", author="dev", date="2025-01-01", message="init"
        )
        code = CodeInfo(
            files=["repo/src/main.c"],
            snippets=[snippet],
            recent_commits=[commit],
        )
        assert len(code.snippets) == 1
        assert code.snippets[0].language == "c"
        assert code.recent_commits[0].hash == "abc1234"


class TestRootCauseResult:
    def test_enum_values(self):
        assert RootCauseLevel.IMPLEMENTATION_DEVIATION.value == "实现偏离"
        assert RootCauseLevel.REGRESSION.value == "回归引入"

    def test_full_result(self):
        result = RootCauseResult(
            level=RootCauseLevel.IMPLEMENTATION_DEVIATION,
            summary="代码未按需求实现",
            detail="apply_cold_filter 函数缺少边界检查",
            problem_location="filter.c:42-50",
            introducer="李四",
            introducing_commit="def5678",
            fix_suggestions=[
                FixSuggestion(
                    label="方案A", description="添加边界检查", effort="small"
                )
            ],
        )
        assert result.level == RootCauseLevel.IMPLEMENTATION_DEVIATION
        assert len(result.fix_suggestions) == 1


class TestImpactResult:
    def test_impact(self):
        item = ImpactItem(
            module_name="scheduler",
            file_path="repo/src/scheduler.c",
            related_test_cases=["TC-5"],
            risk_level="high",
        )
        impact = ImpactResult(
            affected_items=[item],
            regression_test_list=["TC-1", "TC-5"],
            total_affected_modules=1,
        )
        assert impact.total_affected_modules == 1
        assert len(impact.regression_test_list) == 2


class TestAnalysisReport:
    def test_defaults(self):
        report = AnalysisReport(bug_key="PRJ-1")
        assert report.status == AnalysisStatus.SUCCESS
        assert report.errors == []

    def test_status_enum(self):
        assert AnalysisStatus.PARTIAL.value == "partial"
        assert AnalysisStatus.FAILED.value == "failed"
