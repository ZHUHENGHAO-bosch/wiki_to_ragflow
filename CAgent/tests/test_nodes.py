"""nodes 单元测试 — 使用 mock 避免真实 API 调用。"""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from config import JiraConfig
from models import (
    BugInfo,
    CodeInfo,
    CodeSnippet,
    GitCommit,
    RequirementInfo,
    RootCauseLevel,
    TestCaseInfo,
    TestStep,
)
from nodes.read_bug import create_read_bug_node
from nodes.read_testcase import (
    _parse_test_steps,
    _extract_req_id_from_url,
    create_read_testcase_node,
)
from nodes.search_testcase import _extract_keywords
from nodes.read_code import _extract_snippets, _infer_language
from nodes.analyze_root_cause import _parse_response, _build_prompt, LEVEL_MAP
from nodes.analyze_impact import (
    _extract_function_name,
    _module_matches_file,
    _extract_module_from_path,
    _assess_risk,
)
from nodes.write_report import _determine_status
from connectors.report_formatter import JiraWikiFormatter


# ── read_bug tests ──


class TestReadBug:
    @pytest.mark.asyncio
    async def test_success(self):
        jira = AsyncMock()
        jira.get_issue.return_value = {
            "fields": {
                "summary": "crash on cold start",
                "description": "ECU crashes",
                "priority": {"name": "Critical"},
                "components": [{"name": "ModuleA"}],
                "environment": "ECU v2",
                "labels": ["regression"],
                "created": "2025-01-01",
                "reporter": {"displayName": "张三"},
            }
        }
        jira.get_issue_links.return_value = [
            {"key": "TC-1", "type": "is tested by", "direction": "outward"}
        ]
        jira.get_attachments.return_value = []

        config = JiraConfig(base_url="https://j.com")
        node = create_read_bug_node(jira, config)
        result = await node({"bug_key": "PRJ-1", "errors": []})

        assert result["bug_info"] is not None
        assert result["bug_info"].key == "PRJ-1"
        assert result["bug_info"].summary == "crash on cold start"
        assert result["bug_info"].linked_test_case_keys == ["TC-1"]

    @pytest.mark.asyncio
    async def test_success_with_attachments(self):
        """测试 read_bug 在分析流程中获取附件元数据。"""
        jira = AsyncMock()
        jira.get_issue.return_value = {
            "fields": {
                "summary": "crash on cold start",
                "description": "ECU crashes",
                "priority": {"name": "Critical"},
                "components": [],
                "environment": "",
                "labels": [],
                "created": "2025-01-01",
                "reporter": {"displayName": "张三"},
            }
        }
        jira.get_issue_links.return_value = []
        jira.get_attachments.return_value = [
            {"name": "report.xlsx", "url": "https://rtc/att/1", "attachment_id": "1001"},
            {"name": "log.txt", "url": "https://rtc/att/2", "attachment_id": "1002"},
        ]

        config = JiraConfig(base_url="https://j.com")
        node = create_read_bug_node(jira, config)
        result = await node({"bug_key": "PRJ-1", "errors": []})

        assert result["bug_info"] is not None
        assert len(result["bug_info"].attachments) == 2
        assert result["bug_info"].attachments[0].name == "report.xlsx"
        assert result["bug_info"].attachments[0].attachment_id == "1001"
        assert result["bug_info"].attachments[1].name == "log.txt"

    @pytest.mark.asyncio
    async def test_success_no_attachments(self):
        """测试 get_attachments 返回空列表时 attachments 为空。"""
        jira = AsyncMock()
        jira.get_issue.return_value = {
            "fields": {
                "summary": "minor issue",
                "description": "",
                "priority": {"name": "Low"},
                "components": [],
                "environment": "",
                "labels": [],
                "created": "2025-01-01",
                "reporter": {},
            }
        }
        jira.get_issue_links.return_value = []
        jira.get_attachments.return_value = []

        config = JiraConfig(base_url="https://j.com")
        node = create_read_bug_node(jira, config)
        result = await node({"bug_key": "PRJ-2", "errors": []})

        assert result["bug_info"] is not None
        assert result["bug_info"].attachments == []

    @pytest.mark.asyncio
    async def test_attachment_fetch_failure_non_blocking(self):
        """测试 get_attachments 失败不阻塞整个分析流程。"""
        jira = AsyncMock()
        jira.get_issue.return_value = {
            "fields": {
                "summary": "some bug",
                "description": "",
                "priority": {"name": "Medium"},
                "components": [],
                "environment": "",
                "labels": [],
                "created": "2025-01-01",
                "reporter": {},
            }
        }
        jira.get_issue_links.return_value = []
        jira.get_attachments.side_effect = Exception("connection timeout")

        config = JiraConfig(base_url="https://j.com")
        node = create_read_bug_node(jira, config)
        result = await node({"bug_key": "PRJ-3", "errors": []})

        # 分析流程应正常完成，只是 attachments 为空
        assert result["bug_info"] is not None
        assert result["bug_info"].attachments == []
        assert result["bug_info"].summary == "some bug"

    @pytest.mark.asyncio
    async def test_failure(self):
        jira = AsyncMock()
        jira.get_issue.side_effect = Exception("connection refused")

        config = JiraConfig(base_url="https://j.com")
        node = create_read_bug_node(jira, config)
        result = await node({"bug_key": "PRJ-1", "errors": []})

        assert result["bug_info"] is None
        assert len(result["errors"]) > 0


# ── read_testcase helper tests ──


class TestParseTestSteps:
    def test_json_list(self):
        raw = [
            {"step": "Turn on", "expected": "LED green", "actual": "LED red"},
            {"step": "Wait"},
        ]
        steps = _parse_test_steps(raw)
        assert len(steps) == 2
        assert steps[0].actual == "LED red"

    def test_json_string(self):
        raw = json.dumps([{"step": "Step 1", "expectedResult": "OK"}])
        steps = _parse_test_steps(raw)
        assert len(steps) == 1
        assert steps[0].expected == "OK"

    def test_plain_text(self):
        raw = "Step 1: do something\nStep 2: check result"
        steps = _parse_test_steps(raw)
        assert len(steps) == 2

    def test_none(self):
        assert _parse_test_steps(None) == []

    def test_empty_string(self):
        assert _parse_test_steps("") == []


class TestExtractReqIdFromUrl:
    def test_dng_url(self):
        url = "https://dng.example.com/rm/resources/REQ-042"
        assert _extract_req_id_from_url(url) == "REQ-042"

    def test_with_query(self):
        url = "https://dng.example.com/rm/resources/REQ-042?revision=3"
        assert _extract_req_id_from_url(url) == "REQ-042"

    def test_empty(self):
        assert _extract_req_id_from_url("") is None

    def test_generic_url(self):
        url = "https://example.com/items/12345"
        assert _extract_req_id_from_url(url) == "12345"


# ── search_testcase tests ──


class TestExtractKeywords:
    def test_filters_stop_words(self):
        keywords = _extract_keywords("Bug in the cold start module", ["ModuleA"])
        assert "the" not in [k.lower() for k in keywords]
        assert "cold" in [k.lower() for k in keywords]
        assert "modulea" in [k.lower() for k in keywords]

    def test_dedup(self):
        keywords = _extract_keywords("ModuleA ModuleA test", ["ModuleA"])
        lower = [k.lower() for k in keywords]
        assert lower.count("modulea") == 1


# ── read_code helper tests ──


class TestExtractSnippets:
    def test_finds_keyword(self):
        content = "int main() {\n  cold_filter();\n  return 0;\n}"
        snippets = _extract_snippets(content, ["cold_filter"], "test.c")
        assert len(snippets) >= 1
        assert "cold_filter" in snippets[0].content

    def test_no_match(self):
        content = "int main() { return 0; }"
        snippets = _extract_snippets(content, ["nonexistent"], "test.c")
        assert snippets == []


class TestInferLanguage:
    def test_c_file(self):
        assert _infer_language("src/main.c") == "c"

    def test_header(self):
        assert _infer_language("include/types.h") == "c"

    def test_python(self):
        assert _infer_language("script.py") == "python"

    def test_unknown(self):
        assert _infer_language("Makefile") == ""


# ── analyze_root_cause helper tests ──


class TestParseResponse:
    def test_valid_json(self):
        resp = json.dumps({
            "level": "实现偏离",
            "summary": "代码未按需求实现",
            "detail": "filter 函数缺少检查",
            "problem_location": "filter.c:42",
            "introducer": "张三",
            "introducing_commit": "abc1234",
            "fix_suggestions": [
                {"label": "A", "description": "fix it", "effort": "small"}
            ],
        })
        result = _parse_response(resp)
        assert result.level == RootCauseLevel.IMPLEMENTATION_DEVIATION
        assert result.summary == "代码未按需求实现"
        assert len(result.fix_suggestions) == 1

    def test_json_in_markdown(self):
        resp = '```json\n{"level": "需求遗漏", "summary": "缺少场景"}\n```'
        result = _parse_response(resp)
        assert result.level == RootCauseLevel.REQUIREMENT_MISSING

    def test_fallback(self):
        resp = "这是一个实现偏离的问题，无法解析为 JSON"
        result = _parse_response(resp)
        assert result.level == RootCauseLevel.IMPLEMENTATION_DEVIATION

    def test_all_levels_mapped(self):
        assert len(LEVEL_MAP) == 6
        for key, val in LEVEL_MAP.items():
            assert isinstance(val, RootCauseLevel)


# ── analyze_impact helper tests ──


class TestExtractFunctionName:
    def test_file_line_range(self):
        code_info = CodeInfo(
            files=[],
            snippets=[
                CodeSnippet(
                    file_path="filter.c",
                    start_line=40,
                    end_line=60,
                    content="void apply_cold_filter(int x) {\n  // ...\n}",
                    language="c",
                )
            ],
        )
        result = _extract_function_name("filter.c:42-55", code_info)
        assert result == "apply_cold_filter"

    def test_plain_function_name(self):
        result = _extract_function_name("apply_cold_filter", None)
        assert result == "apply_cold_filter"

    def test_function_call_format(self):
        result = _extract_function_name("调用 apply_cold_filter() 出错", None)
        assert result == "apply_cold_filter"

    def test_empty(self):
        result = _extract_function_name("", None)
        assert result is None


class TestModuleMatchesFile:
    def test_exact(self):
        assert _module_matches_file("cold_filter", "src/cold_filter.c")

    def test_case_insensitive(self):
        assert _module_matches_file("ColdFilter", "src/coldfilter.c")

    def test_no_match(self):
        assert not _module_matches_file("scheduler", "src/cold_filter.c")


class TestExtractModuleFromPath:
    def test_simple(self):
        assert _extract_module_from_path("src/main.c") == "main"

    def test_nested(self):
        assert _extract_module_from_path("a/b/c/driver.cpp") == "driver"

    def test_no_ext(self):
        assert _extract_module_from_path("Makefile") == "Makefile"


class TestAssessRisk:
    def test_no_traceability(self):
        assert _assess_risk({"call_count": 1}, False) == "high"

    def test_high_calls(self):
        assert _assess_risk({"call_count": 5}, True) == "high"

    def test_medium_calls(self):
        assert _assess_risk({"call_count": 2}, True) == "medium"

    def test_low_calls(self):
        assert _assess_risk({"call_count": 1}, True) == "low"


# ── write_report helper tests ──


class TestDetermineStatus:
    def test_success(self):
        state = {
            "status": "success",
            "root_cause": MagicMock(),
            "errors": [],
        }
        assert _determine_status(state) == "success"

    def test_failed(self):
        state = {"status": "failed", "root_cause": None, "errors": []}
        assert _determine_status(state) == "failed"

    def test_partial_no_root_cause(self):
        state = {"status": "success", "root_cause": None, "errors": []}
        assert _determine_status(state) == "partial"

    def test_partial_with_errors(self):
        state = {
            "status": "success",
            "root_cause": MagicMock(),
            "errors": ["warning"],
        }
        assert _determine_status(state) == "partial"


class TestFormatReport:
    def test_basic_format(self):
        state = {
            "bug_key": "PRJ-1",
            "bug_info": None,
            "test_cases": [],
            "requirements": [],
            "code_info": None,
            "root_cause": None,
            "impact": None,
            "errors": [],
            "analysis_duration": 1.5,
        }
        formatter = JiraWikiFormatter()
        report = formatter.format_report(state, "partial")
        assert "PRJ-1" not in report or "Bug Analysis" in report
        assert "分析状态" in report
        assert "{panel" in report
