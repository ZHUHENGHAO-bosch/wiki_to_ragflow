"""
watcher/rtc_poller.py — RTC Saved Query 轮询模式

定期执行 RTC Saved Query，发现新 WorkItem 后触发分析。
参照 JqlPoller 模式实现。
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Coroutine

from config import RtcConfig
from connectors.rtc_client import RtcClient

logger = logging.getLogger(__name__)


class RtcPoller:
    """RTC Saved Query 轮询器。"""

    def __init__(
        self,
        rtc: RtcClient,
        config: RtcConfig,
        trigger_fn: Callable[[str], Coroutine[Any, Any, None]],
    ) -> None:
        self._rtc = rtc
        self._config = config
        self._trigger_fn = trigger_fn
        self._running = False
        self._processed: set[str] = set()

    async def start(self) -> None:
        """启动轮询循环。"""
        self._running = True
        logger.info(
            f"RTC Poller 启动: interval={self._config.polling_interval_seconds}s, "
            f"query_id={self._config.saved_query_id}"
        )

        while self._running:
            interval = self._config.polling_interval_seconds

            try:
                await self._poll()
            except Exception as e:
                logger.error(f"RTC Poller 轮询出错: {e}")

            await asyncio.sleep(interval)

    async def stop(self) -> None:
        """停止轮询。"""
        self._running = False
        logger.info("RTC Poller 已停止")

    async def _poll(self) -> None:
        """执行一次轮询。"""
        query_id = self._config.saved_query_id
        if not query_id:
            logger.warning("RTC Poller: saved_query_id 未配置，跳过")
            return

        issues = await self._rtc.search_issues(
            query_id, fields="summary,status", max_results=10
        )

        analyzed_tag = self._config.analyzed_tag

        for issue in issues:
            key = issue.get("key", "")
            if not key or key in self._processed:
                continue

            # 检查是否已含 analyzed tag
            labels = issue.get("fields", {}).get("labels", [])
            if analyzed_tag and analyzed_tag in labels:
                self._processed.add(key)
                continue

            self._processed.add(key)
            logger.info(f"RTC Poller 发现新 WorkItem: {key}")

            try:
                await self._trigger_fn(key)
            except Exception as e:
                logger.error(f"触发分析 {key} 失败: {e}")

        # 防止 processed 集合无限增长
        if len(self._processed) > 1000:
            self._processed = set(list(self._processed)[-500:])

        # 更新 RuntimeState 指标
        try:
            from admin.runtime_state import RuntimeState
            RuntimeState.get().set_poller_status(
                running=self._running,
                processed=len(self._processed),
            )
        except Exception:
            pass
