"""watcher 单元测试。"""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from watcher.webhook_handler import router, set_trigger_fn


@pytest.fixture
def app():
    """创建带 webhook router 的 FastAPI app。"""
    _app = FastAPI()
    _app.include_router(router)
    return _app


@pytest.fixture
def client(app):
    return TestClient(app)


class TestWebhookHealth:
    def test_health(self, client):
        resp = client.get("/webhook/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestWebhookJira:
    def test_ignore_non_bug(self, client):
        trigger = AsyncMock()
        set_trigger_fn(trigger, "")

        resp = client.post(
            "/webhook/jira",
            json={
                "webhookEvent": "jira:issue_created",
                "issue": {
                    "key": "PRJ-1",
                    "fields": {
                        "issuetype": {"name": "Story"},
                        "labels": [],
                    },
                },
            },
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "ignored"
        trigger.assert_not_called()

    def test_ignore_already_analyzed(self, client):
        trigger = AsyncMock()
        set_trigger_fn(trigger, "")

        resp = client.post(
            "/webhook/jira",
            json={
                "webhookEvent": "jira:issue_created",
                "issue": {
                    "key": "PRJ-2",
                    "fields": {
                        "issuetype": {"name": "Bug"},
                        "labels": ["analyzed"],
                    },
                },
            },
        )
        assert resp.status_code == 200
        assert resp.json()["reason"] == "already analyzed"

    def test_trigger_analysis(self, client):
        trigger = AsyncMock()
        set_trigger_fn(trigger, "")

        resp = client.post(
            "/webhook/jira",
            json={
                "webhookEvent": "jira:issue_created",
                "issue": {
                    "key": "PRJ-3",
                    "fields": {
                        "issuetype": {"name": "Bug"},
                        "labels": [],
                    },
                },
            },
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "triggered"
        assert resp.json()["bug_key"] == "PRJ-3"
        trigger.assert_called_once_with("PRJ-3")

    def test_ignore_unsupported_event(self, client):
        trigger = AsyncMock()
        set_trigger_fn(trigger, "")

        resp = client.post(
            "/webhook/jira",
            json={
                "webhookEvent": "jira:issue_deleted",
                "issue": {
                    "key": "PRJ-4",
                    "fields": {
                        "issuetype": {"name": "Bug"},
                        "labels": [],
                    },
                },
            },
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "ignored"


class TestPollerUnit:
    @pytest.mark.asyncio
    async def test_poll_triggers(self):
        from watcher.poller import JqlPoller
        from config import WatcherConfig

        jira = AsyncMock()
        jira.search_issues.return_value = [
            {"key": "PRJ-10", "fields": {"summary": "test", "labels": []}},
        ]

        trigger = AsyncMock()
        config = WatcherConfig(polling_interval_seconds=1)
        poller = JqlPoller(jira, config, trigger)

        # 直接调用内部方法测试
        await poller._poll(config.jql_filter)

        trigger.assert_called_once_with("PRJ-10")

    @pytest.mark.asyncio
    async def test_poll_dedup(self):
        from watcher.poller import JqlPoller
        from config import WatcherConfig

        jira = AsyncMock()
        jira.search_issues.return_value = [
            {"key": "PRJ-10", "fields": {"summary": "test", "labels": []}},
        ]

        trigger = AsyncMock()
        config = WatcherConfig(polling_interval_seconds=1)
        poller = JqlPoller(jira, config, trigger)

        await poller._poll(config.jql_filter)
        await poller._poll(config.jql_filter)  # 第二次不应触发

        trigger.assert_called_once_with("PRJ-10")
