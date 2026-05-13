"""
watcher/poller.py — JQL 轮询模式

定期执行 JQL 查询，发现新 Bug 后触发分析。
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Coroutine

from connectors.jira_client import JiraClient
from config import WatcherConfig

logger = logging.getLogger(__name__)


class JqlPoller:
    """JQL 轮询器。"""

    def __init__(
        self,
        jira: JiraClient,
        config: WatcherConfig,
        trigger_fn: Callable[[str], Coroutine[Any, Any, None]],
    ) -> None:
        self._jira = jira
        self._config = config
        self._trigger_fn = trigger_fn
        self._running = False
        self._processed: set[str] = set()

    async def start(self) -> None:
        """启动轮询循环。每次循环重新读取配置，支持热更新。"""
        self._running = True
        logger.info(
            f"Poller 启动: interval={self._config.polling_interval_seconds}s"
        )

        while self._running:
            # 每次循环重新读取配置 (支持运行时热更新)
            interval = self._config.polling_interval_seconds
            jql = self._config.jql_filter

            try:
                await self._poll(jql)
            except Exception as e:
                logger.error(f"Poller 轮询出错: {e}")

            await asyncio.sleep(interval)

    async def stop(self) -> None:
        """停止轮询。"""
        self._running = False
        logger.info("Poller 已停止")

    async def _poll(self, jql: str) -> None:
        """执行一次轮询。"""
        issues = await self._jira.search_issues(
            jql, fields="summary,labels", max_results=10
        )

        for issue in issues:
            key = issue.get("key", "")
            if not key or key in self._processed:
                continue

            self._processed.add(key)
            logger.info(f"Poller 发现新 Bug: {key}")

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
            pass  # admin 模块未加载时静默忽略
