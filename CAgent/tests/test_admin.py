"""admin 单元测试 — RuntimeState + Admin API 端点。"""
from __future__ import annotations

import time
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from admin.admin_router import router, init_admin_router, MUTABLE_FIELDS
from admin.runtime_state import (
    AnalysisRecord,
    DaemonMode,
    DaemonStatus,
    ErrorRecord,
    RuntimeState,
)
from config import AppConfig, DngConfig, JiraConfig


# ── Fixtures ──


@pytest.fixture(autouse=True)
def reset_state():
    """每个测试前重置单例。"""
    RuntimeState.reset()
    yield
    RuntimeState.reset()


@pytest.fixture
def config():
    """最小化配置。"""
    return AppConfig(
        jira=JiraConfig(base_url="https://jira.test", api_token="secret-token"),
        dng=DngConfig(base_url="https://dng.test", password="secret-pass"),
    )


@pytest.fixture
def app(config):
    _app = FastAPI()
    init_admin_router(config)
    _app.include_router(router)
    return _app


@pytest.fixture
def client(app):
    return TestClient(app)


# ══════════════════════════════════════════════════════════
# RuntimeState 单元测试
# ══════════════════════════════════════════════════════════


class TestRuntimeStateSingleton:
    def test_singleton(self):
        s1 = RuntimeState.get()
        s2 = RuntimeState.get()
        assert s1 is s2

    def test_reset(self):
        s1 = RuntimeState.get()
        RuntimeState.reset()
        s2 = RuntimeState.get()
        assert s1 is not s2


class TestRuntimeStateMode:
    def test_set_mode(self):
        state = RuntimeState.get()
        state.set_mode(DaemonMode.POLLING)
        status = state.get_status()
        assert status.mode == DaemonMode.POLLING

    def test_default_mode(self):
        status = RuntimeState.get().get_status()
        assert status.mode == DaemonMode.WEBHOOK


class TestRuntimeStateAnalysis:
    def test_record_start_and_finish(self):
        state = RuntimeState.get()
        state.record_start("PRJ-1")

        # 活跃分析中
        status = state.get_status()
        assert "PRJ-1" in status.active_analyses

        # 完成
        state.record_finish("PRJ-1", status="success", root_cause_level="实现偏离")

        status = state.get_status()
        assert "PRJ-1" not in status.active_analyses
        assert status.total_analyzed == 1
        assert status.total_success == 1

    def test_record_failure(self):
        state = RuntimeState.get()
        state.record_start("PRJ-2")
        state.record_finish("PRJ-2", status="failed", error_summary="connection timeout")

        status = state.get_status()
        assert status.total_failed == 1

    def test_finish_without_start(self):
        """record_finish 应能处理没有 record_start 的情况。"""
        state = RuntimeState.get()
        state.record_finish("PRJ-3", status="partial")
        history = state.get_history()
        assert len(history) == 1
        assert history[0].bug_key == "PRJ-3"

    def test_history_ordered_newest_first(self):
        state = RuntimeState.get()
        for i in range(5):
            state.record_start(f"PRJ-{i}")
            state.record_finish(f"PRJ-{i}", status="success")

        history = state.get_history()
        assert history[0].bug_key == "PRJ-4"
        assert history[-1].bug_key == "PRJ-0"

    def test_history_filter_by_status(self):
        state = RuntimeState.get()
        state.record_start("PRJ-A")
        state.record_finish("PRJ-A", status="success")
        state.record_start("PRJ-B")
        state.record_finish("PRJ-B", status="failed")

        success = state.get_history(status="success")
        assert len(success) == 1
        assert success[0].bug_key == "PRJ-A"

        failed = state.get_history(status="failed")
        assert len(failed) == 1
        assert failed[0].bug_key == "PRJ-B"

    def test_history_limit(self):
        state = RuntimeState.get()
        for i in range(10):
            state.record_start(f"PRJ-{i}")
            state.record_finish(f"PRJ-{i}", status="success")

        limited = state.get_history(limit=3)
        assert len(limited) == 3

    def test_history_max_capacity(self):
        state = RuntimeState.get()
        for i in range(RuntimeState.MAX_HISTORY + 50):
            state.record_start(f"B-{i}")
            state.record_finish(f"B-{i}", status="success")

        all_h = state.get_history(limit=999)
        assert len(all_h) == RuntimeState.MAX_HISTORY


class TestRuntimeStateErrors:
    def test_record_and_retrieve(self):
        state = RuntimeState.get()
        state.record_error("poller", "Connection refused", bug_key="PRJ-5")

        errors = state.get_errors()
        assert len(errors) == 1
        assert errors[0].source == "poller"
        assert errors[0].bug_key == "PRJ-5"

    def test_errors_ordered_newest_first(self):
        state = RuntimeState.get()
        state.record_error("a", "first")
        state.record_error("b", "second")

        errors = state.get_errors()
        assert errors[0].source == "b"

    def test_errors_max_capacity(self):
        state = RuntimeState.get()
        for i in range(RuntimeState.MAX_ERRORS + 20):
            state.record_error("src", f"msg-{i}")

        all_e = state.get_errors(limit=999)
        assert len(all_e) == RuntimeState.MAX_ERRORS


class TestRuntimeStatePoller:
    def test_set_poller_status(self):
        state = RuntimeState.get()
        state.set_poller_status(running=True, processed=42)

        status = state.get_status()
        assert status.poller_running is True
        assert status.poller_processed_count == 42


# ══════════════════════════════════════════════════════════
# Admin API 端点测试
# ══════════════════════════════════════════════════════════


class TestAdminStatus:
    def test_status_endpoint(self, client):
        RuntimeState.get().set_mode(DaemonMode.WEBHOOK)
        resp = client.get("/admin/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["mode"] == "webhook"
        assert data["uptime_seconds"] >= 0
        assert data["total_analyzed"] == 0

    def test_status_reflects_analyses(self, client):
        state = RuntimeState.get()
        state.record_start("PRJ-10")
        state.record_finish("PRJ-10", status="success")

        resp = client.get("/admin/status")
        assert resp.json()["total_analyzed"] == 1
        assert resp.json()["total_success"] == 1


class TestAdminHistory:
    def test_empty(self, client):
        resp = client.get("/admin/history")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0
        assert resp.json()["records"] == []

    def test_with_records(self, client):
        state = RuntimeState.get()
        state.record_start("PRJ-1")
        state.record_finish("PRJ-1", status="success")

        resp = client.get("/admin/history")
        data = resp.json()
        assert data["total"] == 1
        assert data["records"][0]["bug_key"] == "PRJ-1"
        assert data["records"][0]["status"] == "success"

    def test_filter_by_status(self, client):
        state = RuntimeState.get()
        state.record_start("A"); state.record_finish("A", status="success")
        state.record_start("B"); state.record_finish("B", status="failed")

        resp = client.get("/admin/history?status=failed")
        assert resp.json()["total"] == 1
        assert resp.json()["records"][0]["bug_key"] == "B"

    def test_limit(self, client):
        state = RuntimeState.get()
        for i in range(10):
            state.record_start(f"X-{i}")
            state.record_finish(f"X-{i}", status="success")

        resp = client.get("/admin/history?limit=3")
        assert resp.json()["total"] == 3


class TestAdminErrors:
    def test_empty(self, client):
        resp = client.get("/admin/errors")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_with_errors(self, client):
        RuntimeState.get().record_error("webhook", "Bad request", bug_key="PRJ-99")

        resp = client.get("/admin/errors")
        data = resp.json()
        assert data["total"] == 1
        assert data["errors"][0]["source"] == "webhook"


class TestAdminConfigGet:
    def test_get_full_config(self, client):
        resp = client.get("/admin/config")
        assert resp.status_code == 200
        data = resp.json()

        # 结构完整
        assert "jira" in data
        assert "dng" in data
        assert "llm" in data
        assert "watcher" in data
        assert "rtc" in data

    def test_secrets_redacted(self, client):
        resp = client.get("/admin/config")
        data = resp.json()

        assert data["jira"]["api_token"] == "***"
        assert data["dng"]["password"] == "***"
        assert data["llm"]["api_key"] == "***"
        assert data["watcher"]["webhook_secret"] == "***"
        assert data["rtc"]["password"] == "***"

    def test_get_section(self, client):
        resp = client.get("/admin/config/watcher")
        assert resp.status_code == 200
        data = resp.json()
        assert "mode" in data
        assert "polling_interval_seconds" in data

    def test_get_nonexistent_section(self, client):
        resp = client.get("/admin/config/nonexistent")
        assert resp.status_code == 404

    def test_get_mutable_fields(self, client):
        resp = client.get("/admin/config/mutable-fields")
        assert resp.status_code == 200
        data = resp.json()
        assert "watcher" in data
        assert "polling_interval_seconds" in data["watcher"]
        assert "rtc" in data
        assert "polling_interval_seconds" in data["rtc"]
        assert "saved_query_id" in data["rtc"]

    def test_get_rtc_section(self, client):
        resp = client.get("/admin/config/rtc")
        assert resp.status_code == 200
        data = resp.json()
        assert "ccm_url" in data
        assert "password" in data
        assert data["password"] == "***"


class TestAdminConfigUpdate:
    def test_update_allowed_field(self, client, config):
        resp = client.put(
            "/admin/config",
            json={
                "section": "watcher",
                "updates": {"polling_interval_seconds": 120},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "polling_interval_seconds" in data["updated_fields"]
        assert data["rejected_fields"] == []

        # 验证配置确实被修改了
        assert config.watcher.polling_interval_seconds == 120

    def test_update_multiple_fields(self, client, config):
        resp = client.put(
            "/admin/config",
            json={
                "section": "writer",
                "updates": {
                    "analyzed_label": "auto-analyzed",
                    "auto_create_related_bugs": True,
                },
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["updated_fields"]) == 2
        assert config.writer.analyzed_label == "auto-analyzed"
        assert config.writer.auto_create_related_bugs is True

    def test_reject_immutable_section(self, client):
        resp = client.put(
            "/admin/config",
            json={
                "section": "jira",
                "updates": {"base_url": "http://new"},
            },
        )
        assert resp.status_code == 400

    def test_reject_immutable_field_in_allowed_section(self, client):
        resp = client.put(
            "/admin/config",
            json={
                "section": "watcher",
                "updates": {
                    "polling_interval_seconds": 30,
                    "mode": "polling",  # mode 不在白名单
                },
            },
        )
        data = resp.json()
        assert "polling_interval_seconds" in data["updated_fields"]
        assert "mode" in data["rejected_fields"]

    def test_llm_update_returns_restart_required(self, client, config):
        # init_admin_router 注入了默认的 _config_updater=None
        # 重新注入带回调的版本
        def updater(section, fields):
            return section == "llm"

        init_admin_router(config, updater)

        resp = client.put(
            "/admin/config",
            json={
                "section": "llm",
                "updates": {"temperature": 0.5},
            },
        )
        data = resp.json()
        assert "temperature" in data["updated_fields"]
        assert data["restart_required"] is True

    def test_update_rtc_allowed_field(self, client, config):
        resp = client.put(
            "/admin/config",
            json={
                "section": "rtc",
                "updates": {"polling_interval_seconds": 120},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "polling_interval_seconds" in data["updated_fields"]
        assert config.rtc.polling_interval_seconds == 120

    def test_update_rtc_reject_immutable(self, client):
        resp = client.put(
            "/admin/config",
            json={
                "section": "rtc",
                "updates": {"ccm_url": "http://new"},
            },
        )
        data = resp.json()
        assert "ccm_url" in data["rejected_fields"]


# ══════════════════════════════════════════════════════════
# 附件端点测试
# ══════════════════════════════════════════════════════════


class _MockBugTracker:
    """模拟 BugTrackerClient 的附件方法。"""

    source_type = "rtc"

    def __init__(self, attachments=None, download_fail=False):
        self._attachments = attachments or []
        self._download_fail = download_fail

    async def get_attachments(self, key: str) -> list[dict]:
        return self._attachments

    async def download_attachment(self, url: str, save_path: str) -> str:
        if self._download_fail:
            raise RuntimeError("download error")
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(b"fake-content")
        return save_path

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        import re
        safe = re.sub(r'[<>:"/\\|?*]', "_", name)
        safe = safe.strip(". ")
        return safe[:200] if safe else "unnamed"


@pytest.fixture
def mock_tracker():
    return _MockBugTracker(
        attachments=[
            {"name": "report.xlsx", "url": "https://rtc/att/1", "attachment_id": "1001"},
            {"name": "log.txt", "url": "https://rtc/att/2", "attachment_id": "1002"},
        ]
    )


@pytest.fixture
def app_with_tracker(config, mock_tracker):
    _app = FastAPI()
    init_admin_router(config, bug_tracker=mock_tracker)
    _app.include_router(router)
    return _app


@pytest.fixture
def client_with_tracker(app_with_tracker):
    return TestClient(app_with_tracker)


class TestAttachmentList:
    def test_list_attachments(self, client_with_tracker):
        resp = client_with_tracker.get("/admin/bug/12345/attachments")
        assert resp.status_code == 200
        data = resp.json()
        assert data["bug_key"] == "12345"
        assert data["total"] == 2
        assert data["attachments"][0]["name"] == "report.xlsx"
        assert data["attachments"][0]["attachment_id"] == "1001"
        assert data["attachments"][1]["name"] == "log.txt"

    def test_list_attachments_empty(self, config):
        tracker = _MockBugTracker(attachments=[])
        _app = FastAPI()
        init_admin_router(config, bug_tracker=tracker)
        _app.include_router(router)
        c = TestClient(_app)

        resp = c.get("/admin/bug/99999/attachments")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["attachments"] == []

    def test_list_attachments_no_tracker(self, client):
        """无 bug_tracker 注入时返回 503。"""
        resp = client.get("/admin/bug/12345/attachments")
        assert resp.status_code == 503


class TestAttachmentDownload:
    def test_download_all(self, client_with_tracker, tmp_path):
        resp = client_with_tracker.post(
            "/admin/bug/12345/attachments/download",
            json={"output_dir": str(tmp_path)},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["bug_key"] == "12345"
        assert data["total"] == 2
        assert data["downloaded"] == 2
        assert data["failed"] == 0
        assert all(r["success"] for r in data["results"])

    def test_download_by_ids(self, client_with_tracker, tmp_path):
        resp = client_with_tracker.post(
            "/admin/bug/12345/attachments/download",
            json={"output_dir": str(tmp_path), "attachment_ids": ["1002"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["downloaded"] == 1
        assert data["results"][0]["name"] == "log.txt"

    def test_download_empty_ids_match(self, config, tmp_path):
        tracker = _MockBugTracker(
            attachments=[
                {"name": "a.txt", "url": "u", "attachment_id": "100"},
            ]
        )
        _app = FastAPI()
        init_admin_router(config, bug_tracker=tracker)
        _app.include_router(router)
        c = TestClient(_app)

        resp = c.post(
            "/admin/bug/1/attachments/download",
            json={"output_dir": str(tmp_path), "attachment_ids": ["nonexistent"]},
        )
        data = resp.json()
        assert data["total"] == 0

    def test_download_failure(self, config, tmp_path):
        tracker = _MockBugTracker(
            attachments=[
                {"name": "bad.bin", "url": "u", "attachment_id": "200"},
            ],
            download_fail=True,
        )
        _app = FastAPI()
        init_admin_router(config, bug_tracker=tracker)
        _app.include_router(router)
        c = TestClient(_app)

        resp = c.post(
            "/admin/bug/1/attachments/download",
            json={"output_dir": str(tmp_path)},
        )
        data = resp.json()
        assert data["failed"] == 1
        assert data["results"][0]["success"] is False
        assert "download error" in data["results"][0]["error"]

    def test_download_no_tracker(self, client):
        """无 bug_tracker 注入时返回 503。"""
        resp = client.post("/admin/bug/12345/attachments/download", json={})
        assert resp.status_code == 503
