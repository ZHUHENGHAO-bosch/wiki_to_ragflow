"""BugTrackerClient Protocol 合规测试。

验证 JiraClient 和 RtcClient 均满足 BugTrackerClient Protocol。
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from config import JiraConfig, RtcConfig
from connectors.bug_tracker import BugTrackerClient
from connectors.jira_client import JiraClient
from connectors.rtc_client import RtcClient
from connectors.report_formatter import (
    ReportFormatter,
    JiraWikiFormatter,
    RtcHtmlFormatter,
)


# ── BugTrackerClient Protocol 合规 ──


class TestJiraClientProtocol:
    def test_jira_is_bug_tracker_client(self):
        """JiraClient 实例应满足 BugTrackerClient Protocol (结构子类型)。"""
        # Python 3.12+ 不支持对含非方法成员的 Protocol 使用 issubclass，
        # 使用 isinstance 实例检查代替
        jira = JiraClient(JiraConfig(base_url="https://j.com"))
        assert isinstance(jira, BugTrackerClient)

    def test_jira_instance_check(self):
        """JiraClient 实例应通过 isinstance 检查。"""
        jira = JiraClient(JiraConfig(base_url="https://j.com"))
        assert isinstance(jira, BugTrackerClient)

    def test_jira_source_type(self):
        jira = JiraClient(JiraConfig(base_url="https://j.com"))
        assert jira.source_type == "jira"

    def test_jira_has_all_protocol_methods(self):
        """验证 JiraClient 实现了 Protocol 要求的所有方法。"""
        required_methods = [
            "get_issue",
            "get_issue_links",
            "get_remote_links",
            "search_issues",
            "add_comment",
            "update_labels",
            "create_issue",
            "create_link",
            "close",
        ]
        for method in required_methods:
            assert hasattr(JiraClient, method), f"JiraClient 缺少方法: {method}"


class TestRtcClientProtocol:
    def test_rtc_is_bug_tracker_client(self):
        """RtcClient 实例应满足 BugTrackerClient Protocol (结构子类型)。"""
        rtc = RtcClient(RtcConfig(ccm_url="https://rtc.com/ccm"))
        assert isinstance(rtc, BugTrackerClient)

    def test_rtc_instance_check(self):
        """RtcClient 实例应通过 isinstance 检查。"""
        rtc = RtcClient(RtcConfig(ccm_url="https://rtc.com/ccm"))
        assert isinstance(rtc, BugTrackerClient)

    def test_rtc_source_type(self):
        rtc = RtcClient(RtcConfig(ccm_url="https://rtc.com/ccm"))
        assert rtc.source_type == "rtc"

    def test_rtc_has_all_protocol_methods(self):
        """验证 RtcClient 实现了 Protocol 要求的所有方法。"""
        required_methods = [
            "get_issue",
            "get_issue_links",
            "get_remote_links",
            "search_issues",
            "add_comment",
            "update_labels",
            "create_issue",
            "create_link",
            "close",
        ]
        for method in required_methods:
            assert hasattr(RtcClient, method), f"RtcClient 缺少方法: {method}"


# ── ReportFormatter Protocol 合规 ──


class TestReportFormatterProtocol:
    def test_jira_formatter_is_report_formatter(self):
        formatter = JiraWikiFormatter()
        assert isinstance(formatter, ReportFormatter)

    def test_rtc_formatter_is_report_formatter(self):
        formatter = RtcHtmlFormatter()
        assert isinstance(formatter, ReportFormatter)


# ── Mock 的 BugTrackerClient 可互换使用 ──


class TestMockTrackerInterchangeability:
    def test_mock_as_jira(self):
        """AsyncMock 模拟 Jira tracker。"""
        tracker = AsyncMock()
        tracker.source_type = "jira"

        assert tracker.source_type == "jira"

    def test_mock_as_rtc(self):
        """AsyncMock 模拟 RTC tracker。"""
        tracker = AsyncMock()
        tracker.source_type = "rtc"

        assert tracker.source_type == "rtc"

    @pytest.mark.asyncio
    async def test_mock_tracker_methods(self):
        """验证 mock tracker 方法签名可正常调用。"""
        tracker = AsyncMock()
        tracker.source_type = "jira"

        # 所有 Protocol 方法应该可调用
        await tracker.get_issue("KEY-1")
        await tracker.get_issue_links("KEY-1", "is tested by")
        await tracker.get_remote_links("KEY-1")
        await tracker.search_issues("query", fields="summary", max_results=10)
        await tracker.add_comment("KEY-1", "comment")
        await tracker.update_labels("KEY-1", add_labels=["label"])
        await tracker.create_issue("PRJ", "Bug", "title")
        await tracker.create_link("relates to", "KEY-1", "KEY-2")
        await tracker.close()

        assert tracker.get_issue.call_count == 1
        assert tracker.close.call_count == 1


# ── Formatter 输出格式 ──


class TestFormatterOutput:
    def _make_state(self) -> dict:
        return {
            "bug_key": "PRJ-1",
            "bug_info": None,
            "test_cases": [],
            "requirements": [],
            "code_info": None,
            "root_cause": None,
            "impact": None,
            "errors": [],
            "analysis_duration": 2.5,
        }

    def test_jira_formatter_contains_wiki_markup(self):
        state = self._make_state()
        report = JiraWikiFormatter().format_report(state, "partial")
        assert "{panel" in report
        assert "h4." in report

    def test_rtc_formatter_contains_html(self):
        state = self._make_state()
        report = RtcHtmlFormatter().format_report(state, "partial")
        assert "<div" in report
        assert "<h4>" in report
        assert "<h3>" in report

    def test_both_formatters_include_status(self):
        state = self._make_state()
        jira_report = JiraWikiFormatter().format_report(state, "success")
        rtc_report = RtcHtmlFormatter().format_report(state, "success")
        assert "完成" in jira_report
        assert "完成" in rtc_report

    def test_both_formatters_include_duration(self):
        state = self._make_state()
        jira_report = JiraWikiFormatter().format_report(state, "success")
        rtc_report = RtcHtmlFormatter().format_report(state, "success")
        assert "2.5s" in jira_report
        assert "2.5s" in rtc_report
