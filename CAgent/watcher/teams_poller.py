"""
watcher/teams_poller.py — Teams 频道消息轮询器

通过 Graph API Delta Query 轮询 Teams 频道新消息，
识别命令并触发相应操作。仅需出站连接，适用于企业内网环境。

设计模式与 poller.py (JqlPoller) 一致。
"""
from __future__ import annotations

import asyncio
import logging
import re
from typing import Any, Callable, Coroutine

from connectors.graph_teams_client import ChannelMessage, GraphTeamsClient
from connectors.teams_client import TeamsClient

logger = logging.getLogger(__name__)


class TeamsChannelPoller:
    """轮询 Teams 频道消息，识别并处理命令。"""

    def __init__(
        self,
        graph_client: GraphTeamsClient,
        teams_client: TeamsClient,
        trigger_fn: Callable[[str], Coroutine[Any, Any, None]],
        poll_interval: float = 10.0,
    ) -> None:
        """
        Args:
            graph_client: Graph API Teams 客户端
            teams_client: Teams 通信客户端 (用于发送响应)
            trigger_fn: 分析触发函数 (async, 接收 bug_key)
            poll_interval: 轮询间隔 (秒)
        """
        self._graph = graph_client
        self._teams = teams_client
        self._trigger_fn = trigger_fn
        self._interval = poll_interval
        self._running = False
        self._initialized = False

    async def start(self) -> None:
        """启动轮询循环。"""
        self._running = True
        logger.info(
            f"Teams Channel Poller 启动: interval={self._interval}s"
        )

        # 首次 Delta Query: 获取 deltaLink，不处理历史消息
        if not self._initialized:
            try:
                await self._graph.get_channel_messages_delta()
                self._initialized = True
                logger.info("Teams Channel Poller 初始化完成 (已跳过历史消息)")
            except Exception as e:
                logger.error(f"Teams Channel Poller 初始化失败: {e}")
                # 继续运行，下次循环重试

        while self._running:
            try:
                await self._poll()
            except Exception as e:
                logger.error(f"Teams Channel Poller 轮询出错: {e}")

            await asyncio.sleep(self._interval)

    async def stop(self) -> None:
        """停止轮询。"""
        self._running = False
        logger.info("Teams Channel Poller 已停止")

    async def _poll(self) -> None:
        """执行一次轮询，处理新消息。"""
        messages = await self._graph.get_channel_messages_delta()

        for msg in messages:
            # 跳过自己发的消息
            if self._graph.is_own_message(msg):
                continue

            # 检查是否是命令
            if not self._graph.is_mention_or_command(msg):
                continue

            try:
                await self._handle_message(msg)
            except Exception as e:
                logger.error(f"处理 Teams 消息失败: {e} (msg_id={msg.id})")

    async def _handle_message(self, msg: ChannelMessage) -> None:
        """处理单条命令消息。"""
        # 使用 TeamsClient.parse_command 解析命令
        parsed = TeamsClient.parse_command(msg.content)

        if parsed is None:
            # 无法识别的命令，发送帮助
            await self._reply(
                msg,
                "未识别的命令。支持的命令:\n"
                "- **analyze BUG-123** — 触发 Bug 分析\n"
                "- **status** — 查看系统状态\n"
                "- **help** — 显示帮助",
            )
            return

        command, argument = parsed

        if command == "help":
            await self._reply(
                msg,
                "Bug Analysis Agent 命令:\n"
                "- **analyze BUG-123** — 触发指定 Bug 的自动分析\n"
                "- **status** — 查看守护进程状态\n"
                "- **help** — 显示此帮助信息",
            )

        elif command == "status":
            await self._handle_status(msg)

        elif command == "analyze":
            await self._handle_analyze(msg, argument)

    async def _handle_status(self, msg: ChannelMessage) -> None:
        """处理 status 命令。"""
        try:
            from admin.runtime_state import RuntimeState

            rt = RuntimeState.get()
            status = rt.get_status()
            text = (
                f"守护进程状态:\n"
                f"- 模式: {status.mode}\n"
                f"- 运行中: {'是' if status.is_healthy else '否'}\n"
                f"- 已分析: {status.total_analyzed}\n"
                f"- 成功: {status.total_success}\n"
                f"- 失败: {status.total_failed}\n"
                f"- 运行时长: {status.uptime_seconds:.0f}s"
            )
        except Exception as e:
            text = f"获取状态失败: {e}"

        await self._reply(msg, text)

    async def _handle_analyze(self, msg: ChannelMessage, argument: str) -> None:
        """处理 analyze 命令。"""
        if not argument:
            await self._reply(msg, "请指定 Bug Key，例如: analyze BUG-123")
            return

        bug_key = argument.split()[0].upper()

        # 发送确认回复
        await self._reply(
            msg, f"已触发 **{bug_key}** 的分析，完成后将发送结果通知。"
        )

        # 异步触发分析 (不阻塞轮询)
        asyncio.create_task(self._run_analysis(bug_key))
        logger.info(f"Teams Poller 触发分析: {bug_key}")

    async def _run_analysis(self, bug_key: str) -> None:
        """执行分析任务。"""
        try:
            await self._trigger_fn(bug_key)
        except Exception as e:
            logger.error(f"Teams Poller 分析触发失败: {bug_key}, {e}")

    async def _reply(self, msg: ChannelMessage, text: str) -> None:
        """回复消息 (在同一线程中)。"""
        try:
            await self._graph.reply_to_message(msg.id, content=text)
        except Exception as e:
            logger.warning(f"Teams 回复失败，尝试直接发送: {e}")
            # 降级: 直接发送到频道
            try:
                await self._teams.send_message(text)
            except Exception as e2:
                logger.error(f"Teams 消息发送也失败: {e2}")

    # ── RuntimeState 集成 ──

    def _update_poller_status(self) -> None:
        """更新 RuntimeState 指标。"""
        try:
            from admin.runtime_state import RuntimeState
            RuntimeState.get().set_poller_status(running=self._running)
        except Exception:
            pass
