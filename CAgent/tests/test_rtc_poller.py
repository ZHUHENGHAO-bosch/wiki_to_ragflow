"""RtcPoller 单元测试。"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from config import RtcConfig
from watcher.rtc_poller import RtcPoller


@pytest.fixture
def rtc_config() -> RtcConfig:
    return RtcConfig(
        ccm_url="https://rtc.test.com/ccm",
        username="user",
        password="pass",
        saved_query_id="_TestQueryID",
        polling_interval_seconds=5,
        analyzed_tag="analyzed",
    )


@pytest.fixture
def rtc_mock() -> AsyncMock:
    rtc = AsyncMock()
    rtc.source_type = "rtc"
    return rtc


class TestRtcPollerPoll:
    @pytest.mark.asyncio
    async def test_poll_triggers_new_workitem(self, rtc_mock, rtc_config):
        """新发现的 WorkItem 应触发 trigger_fn。"""
        rtc_mock.search_issues.return_value = [
            {
                "key": "501",
                "fields": {"summary": "Bug A", "labels": []},
            },
        ]

        trigger = AsyncMock()
        poller = RtcPoller(rtc_mock, rtc_config, trigger)

        await poller._poll()

        trigger.assert_called_once_with("501")

    @pytest.mark.asyncio
    async def test_poll_dedup(self, rtc_mock, rtc_config):
        """同一 WorkItem 不应重复触发。"""
        rtc_mock.search_issues.return_value = [
            {
                "key": "501",
                "fields": {"summary": "Bug A", "labels": []},
            },
        ]

        trigger = AsyncMock()
        poller = RtcPoller(rtc_mock, rtc_config, trigger)

        await poller._poll()
        await poller._poll()  # 第二次不应触发

        trigger.assert_called_once_with("501")

    @pytest.mark.asyncio
    async def test_poll_skips_analyzed(self, rtc_mock, rtc_config):
        """已含 analyzed tag 的 WorkItem 应跳过。"""
        rtc_mock.search_issues.return_value = [
            {
                "key": "502",
                "fields": {"summary": "Bug B", "labels": ["analyzed"]},
            },
        ]

        trigger = AsyncMock()
        poller = RtcPoller(rtc_mock, rtc_config, trigger)

        await poller._poll()

        trigger.assert_not_called()

    @pytest.mark.asyncio
    async def test_poll_skips_empty_key(self, rtc_mock, rtc_config):
        """key 为空的 WorkItem 应跳过。"""
        rtc_mock.search_issues.return_value = [
            {
                "key": "",
                "fields": {"summary": "No key", "labels": []},
            },
        ]

        trigger = AsyncMock()
        poller = RtcPoller(rtc_mock, rtc_config, trigger)

        await poller._poll()

        trigger.assert_not_called()

    @pytest.mark.asyncio
    async def test_poll_no_query_id(self, rtc_mock, rtc_config):
        """saved_query_id 未配置时应跳过轮询。"""
        rtc_config.saved_query_id = ""

        trigger = AsyncMock()
        poller = RtcPoller(rtc_mock, rtc_config, trigger)

        await poller._poll()

        rtc_mock.search_issues.assert_not_called()
        trigger.assert_not_called()

    @pytest.mark.asyncio
    async def test_poll_multiple_workitems(self, rtc_mock, rtc_config):
        """多个 WorkItem 应分别触发。"""
        rtc_mock.search_issues.return_value = [
            {"key": "601", "fields": {"summary": "A", "labels": []}},
            {"key": "602", "fields": {"summary": "B", "labels": []}},
            {"key": "603", "fields": {"summary": "C", "labels": ["analyzed"]}},
        ]

        trigger = AsyncMock()
        poller = RtcPoller(rtc_mock, rtc_config, trigger)

        await poller._poll()

        assert trigger.call_count == 2
        trigger.assert_any_call("601")
        trigger.assert_any_call("602")

    @pytest.mark.asyncio
    async def test_poll_trigger_failure_continues(self, rtc_mock, rtc_config):
        """trigger_fn 异常不应阻断后续处理。"""
        rtc_mock.search_issues.return_value = [
            {"key": "701", "fields": {"summary": "A", "labels": []}},
            {"key": "702", "fields": {"summary": "B", "labels": []}},
        ]

        trigger = AsyncMock(side_effect=[Exception("fail"), None])
        poller = RtcPoller(rtc_mock, rtc_config, trigger)

        await poller._poll()

        # 两个都应尝试触发
        assert trigger.call_count == 2


class TestRtcPollerProcessedGrowth:
    @pytest.mark.asyncio
    async def test_processed_set_trimming(self, rtc_mock, rtc_config):
        """_processed 集合超过 1000 时应裁剪。"""
        trigger = AsyncMock()
        poller = RtcPoller(rtc_mock, rtc_config, trigger)

        # 手动添加 1001 个条目
        for i in range(1001):
            poller._processed.add(str(i))

        rtc_mock.search_issues.return_value = []
        await poller._poll()

        assert len(poller._processed) == 500


class TestRtcPollerLifecycle:
    @pytest.mark.asyncio
    async def test_stop(self, rtc_mock, rtc_config):
        """stop 应设置 _running 为 False。"""
        trigger = AsyncMock()
        poller = RtcPoller(rtc_mock, rtc_config, trigger)

        poller._running = True
        await poller.stop()

        assert poller._running is False
