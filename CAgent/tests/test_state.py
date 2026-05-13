"""state.py 单元测试。"""
from __future__ import annotations

from state import AnalysisState


class TestAnalysisState:
    def test_is_typed_dict(self):
        """AnalysisState 应该是 TypedDict。"""
        hints = AnalysisState.__annotations__
        assert "bug_key" in hints
        assert "bug_info" in hints
        assert "test_cases" in hints
        assert "requirements" in hints
        assert "code_info" in hints
        assert "root_cause" in hints
        assert "impact" in hints
        assert "status" in hints
        assert "errors" in hints
        assert "analysis_duration" in hints

    def test_can_create_instance(self):
        """可以像 dict 一样创建。"""
        state: AnalysisState = {
            "bug_key": "PRJ-1",
            "bug_info": None,
            "test_cases": [],
            "requirements": [],
            "code_info": None,
            "root_cause": None,
            "impact": None,
            "status": "success",
            "errors": [],
            "analysis_duration": 0.0,
        }
        assert state["bug_key"] == "PRJ-1"
        assert state["test_cases"] == []
