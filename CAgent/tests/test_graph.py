"""graph.py 条件路由单元测试。"""
from __future__ import annotations

from unittest.mock import MagicMock

from graph import (
    _route_after_read_bug,
    _route_after_read_testcase,
    _route_after_read_requirement,
)


class TestRouteAfterReadBug:
    def test_success(self):
        state = {"bug_info": MagicMock()}
        assert _route_after_read_bug(state) == "read_testcase"

    def test_failure(self):
        state = {"bug_info": None}
        assert _route_after_read_bug(state) == "write_report"


class TestRouteAfterReadTestcase:
    def test_has_test_cases(self):
        state = {"test_cases": [MagicMock()]}
        assert _route_after_read_testcase(state) == "read_requirement"

    def test_empty(self):
        state = {"test_cases": []}
        assert _route_after_read_testcase(state) == "search_testcase"

    def test_none(self):
        state = {}
        assert _route_after_read_testcase(state) == "search_testcase"


class TestRouteAfterReadRequirement:
    def test_has_requirements(self):
        state = {"requirements": [MagicMock()]}
        assert _route_after_read_requirement(state) == "read_code"

    def test_empty(self):
        state = {"requirements": []}
        assert _route_after_read_requirement(state) == "search_requirement"
