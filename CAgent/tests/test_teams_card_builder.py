"""connectors/teams_card_builder.py 单元测试。"""
from __future__ import annotations

from unittest.mock import MagicMock

from connectors.teams_card_builder import (
    build_analysis_result_card,
    build_approval_card,
    build_error_card,
    build_help_card,
    build_history_card,
    build_progress_card,
    build_status_card,
    wrap_for_graph_api,
    wrap_for_workflow_webhook,
)


class TestBuildAnalysisResultCard:
    def test_success_card(self) -> None:
        """成功状态卡片包含正确颜色和字段。"""
        state = {
            "bug_key": "BUG-123",
            "status": "success",
            "root_cause": None,
            "analysis_duration": 5.2,
            "errors": [],
        }
        card = build_analysis_result_card(state)

        assert card["type"] == "AdaptiveCard"
        assert card["version"] == "1.4"
        assert len(card["body"]) >= 2

        # 标题包含 bug key 和状态
        header = card["body"][0]
        assert "BUG-123" in header["text"]
        assert "分析完成" in header["text"]
        assert header["color"] == "good"

    def test_failed_card(self) -> None:
        """失败状态使用 attention 颜色。"""
        state = {
            "bug_key": "BUG-456",
            "status": "failed",
            "root_cause": None,
            "analysis_duration": 1.0,
            "errors": ["读取失败"],
        }
        card = build_analysis_result_card(state)

        header = card["body"][0]
        assert header["color"] == "attention"
        # 应有错误信息块
        texts = [b.get("text", "") for b in card["body"]]
        assert any("读取失败" in t for t in texts)

    def test_partial_card(self) -> None:
        """部分完成使用 warning 颜色。"""
        state = {
            "bug_key": "BUG-789",
            "status": "partial",
            "root_cause": None,
            "analysis_duration": 3.0,
            "errors": [],
        }
        card = build_analysis_result_card(state)
        header = card["body"][0]
        assert header["color"] == "warning"

    def test_with_root_cause(self) -> None:
        """包含 root_cause 时显示根因层级和摘要。"""
        root_cause = MagicMock()
        root_cause.level.value = "实现偏离"
        root_cause.summary = "空指针解引用"
        root_cause.fix_suggestions = []
        root_cause.detail = "详细根因描述"

        state = {
            "bug_key": "BUG-100",
            "status": "success",
            "root_cause": root_cause,
            "analysis_duration": 10.5,
            "errors": [],
        }
        card = build_analysis_result_card(state)

        # 查找 FactSet
        fact_set = None
        for item in card["body"]:
            if item.get("type") == "FactSet":
                fact_set = item
                break
        assert fact_set is not None

        fact_titles = [f["title"] for f in fact_set["facts"]]
        assert "根因层级" in fact_titles
        assert "根因摘要" in fact_titles

    def test_with_fix_suggestions(self) -> None:
        """包含修复建议。"""
        fix = MagicMock()
        fix.label = "修复方案"
        fix.description = "添加空指针检查"

        root_cause = MagicMock()
        root_cause.level.value = "实现偏离"
        root_cause.summary = "空指针"
        root_cause.fix_suggestions = [fix]
        root_cause.detail = ""

        state = {
            "bug_key": "BUG-200",
            "status": "success",
            "root_cause": root_cause,
            "analysis_duration": 2.0,
            "errors": [],
        }
        card = build_analysis_result_card(state)

        fact_set = next(
            b for b in card["body"] if b.get("type") == "FactSet"
        )
        fact_titles = [f["title"] for f in fact_set["facts"]]
        assert "修复建议" in fact_titles


class TestBuildProgressCard:
    def test_progress_card(self) -> None:
        """进度卡片包含步骤信息。"""
        card = build_progress_card(
            "BUG-123", step=3, total_steps=6,
            step_name="定位代码",
            completed_steps=["读取 Bug 信息", "获取测试用例"],
        )
        assert card["type"] == "AdaptiveCard"
        header = card["body"][0]
        assert "BUG-123" in header["text"]
        assert "3/6" in header["text"]

    def test_progress_card_minimal(self) -> None:
        """最小进度卡片。"""
        card = build_progress_card("BUG-1", step=1, total_steps=5)
        assert card["type"] == "AdaptiveCard"


class TestBuildApprovalCard:
    def test_approval_card(self) -> None:
        """审批卡片包含命令提示。"""
        card = build_approval_card(
            "BUG-123", summary="空指针解引用",
            root_cause_level="实现偏离",
        )
        assert card["type"] == "AdaptiveCard"

        texts = [b.get("text", "") for b in card["body"]]
        assert any("approve BUG-123" in t for t in texts)
        assert any("reject BUG-123" in t for t in texts)


class TestBuildErrorCard:
    def test_error_card(self) -> None:
        """错误卡片显示错误列表。"""
        card = build_error_card(
            "BUG-123",
            errors=["连接超时", "认证失败"],
            context="分析过程中发生错误",
        )
        assert card["type"] == "AdaptiveCard"
        header = card["body"][0]
        assert header["color"] == "attention"

    def test_error_card_no_context(self) -> None:
        """无上下文的错误卡片。"""
        card = build_error_card("BUG-1", errors=["error"])
        assert len(card["body"]) >= 2


class TestBuildHelpCard:
    def test_help_card(self) -> None:
        """帮助卡片包含命令列表。"""
        card = build_help_card()
        assert card["type"] == "AdaptiveCard"
        fact_set = next(
            b for b in card["body"] if b.get("type") == "FactSet"
        )
        assert len(fact_set["facts"]) > 0


class TestBuildStatusCard:
    def test_status_card(self) -> None:
        """状态卡片包含运行信息。"""
        card = build_status_card(
            mode="polling",
            is_running=True,
            total_analyzed=42,
            total_success=38,
            total_failed=4,
            uptime="2h 30m",
        )
        assert card["type"] == "AdaptiveCard"

        fact_set = next(
            b for b in card["body"] if b.get("type") == "FactSet"
        )
        fact_map = {f["title"]: f["value"] for f in fact_set["facts"]}
        assert fact_map["已分析"] == "42"
        assert fact_map["成功"] == "38"

    def test_status_card_with_active(self) -> None:
        """状态卡片显示正在分析的 Bug。"""
        card = build_status_card(
            mode="webhook",
            is_running=True,
            total_analyzed=5,
            total_success=5,
            total_failed=0,
            active_analyses=["BUG-1", "BUG-2"],
        )
        texts = [b.get("text", "") for b in card["body"]]
        assert any("BUG-1" in t for t in texts)


class TestBuildHistoryCard:
    def test_history_card(self) -> None:
        """历史记录卡片。"""
        records = [
            {"bug_key": "BUG-1", "status": "success", "root_cause_level": "实现偏离", "duration_seconds": 5.0},
            {"bug_key": "BUG-2", "status": "failed", "duration_seconds": 2.0},
        ]
        card = build_history_card(records)
        assert card["type"] == "AdaptiveCard"
        # 至少有标题 + 2 条记录
        assert len(card["body"]) >= 3

    def test_history_card_empty(self) -> None:
        """空历史记录。"""
        card = build_history_card([])
        texts = [b.get("text", "") for b in card["body"]]
        assert any("暂无" in t for t in texts)


class TestWrappers:
    def test_wrap_for_workflow_webhook(self) -> None:
        """Workflow Webhook payload 格式正确。"""
        card = {"type": "AdaptiveCard", "body": [], "version": "1.4"}
        payload = wrap_for_workflow_webhook(card)
        assert payload["type"] == "message"
        assert len(payload["attachments"]) == 1
        assert payload["attachments"][0]["contentType"] == "application/vnd.microsoft.card.adaptive"
        assert payload["attachments"][0]["content"] is card

    def test_wrap_for_graph_api(self) -> None:
        """Graph API payload 格式正确。"""
        card = {"type": "AdaptiveCard", "body": [], "version": "1.4"}
        payload = wrap_for_graph_api(card, text="test")
        assert payload["body"]["contentType"] == "html"
        assert payload["body"]["content"] == "test"
        assert payload["attachments"][0]["id"] == "card"
        assert payload["attachments"][0]["content"] is card

    def test_wrap_for_graph_api_default_text(self) -> None:
        """Graph API 默认文本包含 attachment 引用。"""
        card = {"type": "AdaptiveCard", "body": [], "version": "1.4"}
        payload = wrap_for_graph_api(card)
        assert "attachment" in payload["body"]["content"]
