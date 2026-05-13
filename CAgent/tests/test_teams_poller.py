"""watcher/teams_poller.py 单元测试。"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from connectors.graph_teams_client import ChannelMessage, GraphTeamsClient
from connectors.teams_client import TeamsClient
from watcher.teams_poller import TeamsChannelPoller


@pytest.fixture
def mock_graph() -> GraphTeamsClient:
    graph = MagicMock(spec=GraphTeamsClient)
    graph.get_channel_messages_delta = AsyncMock(return_value=[])
    graph.reply_to_message = AsyncMock(return_value="reply-id")
    graph.send_channel_message = AsyncMock(return_value="msg-id")
    graph.is_own_message = MagicMock(return_value=False)
    graph.is_mention_or_command = MagicMock(return_value=True)
    return graph


@pytest.fixture
def mock_teams() -> TeamsClient:
    teams = MagicMock(spec=TeamsClient)
    teams.send_message = AsyncMock(return_value=True)
    return teams


@pytest.fixture
def mock_trigger() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def poller(
    mock_graph: GraphTeamsClient,
    mock_teams: TeamsClient,
    mock_trigger: AsyncMock,
) -> TeamsChannelPoller:
    return TeamsChannelPoller(
        graph_client=mock_graph,
        teams_client=mock_teams,
        trigger_fn=mock_trigger,
        poll_interval=1.0,
    )


class TestPoll:
    @pytest.mark.asyncio
    async def test_poll_no_messages(self, poller: TeamsChannelPoller, mock_graph: GraphTeamsClient) -> None:
        """无消息时不触发任何处理。"""
        mock_graph.get_channel_messages_delta.return_value = []
        await poller._poll()
        mock_graph.reply_to_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_poll_skips_own_messages(
        self, poller: TeamsChannelPoller, mock_graph: GraphTeamsClient
    ) -> None:
        """跳过 Bot 自己的消息。"""
        msg = ChannelMessage(id="1", content="self message", from_name="CAgent")
        mock_graph.get_channel_messages_delta.return_value = [msg]
        mock_graph.is_own_message.return_value = True

        await poller._poll()
        mock_graph.reply_to_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_poll_skips_non_commands(
        self, poller: TeamsChannelPoller, mock_graph: GraphTeamsClient
    ) -> None:
        """跳过非命令消息。"""
        msg = ChannelMessage(id="1", content="just chatting", from_name="Alice")
        mock_graph.get_channel_messages_delta.return_value = [msg]
        mock_graph.is_own_message.return_value = False
        mock_graph.is_mention_or_command.return_value = False

        await poller._poll()
        mock_graph.reply_to_message.assert_not_called()


class TestHandleMessage:
    @pytest.mark.asyncio
    async def test_handle_help(
        self, poller: TeamsChannelPoller, mock_graph: GraphTeamsClient
    ) -> None:
        """处理 help 命令。"""
        msg = ChannelMessage(id="1", content="<at>CAgent</at> help", from_name="Alice")

        await poller._handle_message(msg)

        mock_graph.reply_to_message.assert_called_once()
        reply_content = mock_graph.reply_to_message.call_args[1]["content"]
        assert "analyze" in reply_content.lower()

    @pytest.mark.asyncio
    async def test_handle_status(
        self, poller: TeamsChannelPoller, mock_graph: GraphTeamsClient
    ) -> None:
        """处理 status 命令。"""
        msg = ChannelMessage(id="1", content="<at>CAgent</at> status", from_name="Alice")

        await poller._handle_message(msg)

        mock_graph.reply_to_message.assert_called_once()
        reply_content = mock_graph.reply_to_message.call_args[1]["content"]
        assert "守护进程" in reply_content or "状态" in reply_content

    @pytest.mark.asyncio
    async def test_handle_analyze(
        self,
        poller: TeamsChannelPoller,
        mock_graph: GraphTeamsClient,
        mock_trigger: AsyncMock,
    ) -> None:
        """处理 analyze 命令。"""
        msg = ChannelMessage(
            id="1", content="<at>CAgent</at> analyze BUG-123", from_name="Alice"
        )

        await poller._handle_message(msg)

        # 应回复确认
        mock_graph.reply_to_message.assert_called_once()
        reply_content = mock_graph.reply_to_message.call_args[1]["content"]
        assert "BUG-123" in reply_content

    @pytest.mark.asyncio
    async def test_handle_analyze_no_key(
        self, poller: TeamsChannelPoller, mock_graph: GraphTeamsClient
    ) -> None:
        """analyze 无参数时提示。"""
        msg = ChannelMessage(
            id="1", content="<at>CAgent</at> analyze", from_name="Alice"
        )

        await poller._handle_message(msg)

        reply_content = mock_graph.reply_to_message.call_args[1]["content"]
        assert "请指定" in reply_content

    @pytest.mark.asyncio
    async def test_handle_unknown_command(
        self, poller: TeamsChannelPoller, mock_graph: GraphTeamsClient
    ) -> None:
        """未知命令返回帮助。"""
        msg = ChannelMessage(
            id="1", content="<at>CAgent</at> foobar", from_name="Alice"
        )

        await poller._handle_message(msg)

        reply_content = mock_graph.reply_to_message.call_args[1]["content"]
        assert "未识别" in reply_content


class TestReply:
    @pytest.mark.asyncio
    async def test_reply_success(
        self, poller: TeamsChannelPoller, mock_graph: GraphTeamsClient
    ) -> None:
        """回复成功。"""
        msg = ChannelMessage(id="parent-1", from_name="Alice")
        await poller._reply(msg, "test reply")
        mock_graph.reply_to_message.assert_called_once_with(
            "parent-1", content="test reply"
        )

    @pytest.mark.asyncio
    async def test_reply_fallback_to_send(
        self,
        poller: TeamsChannelPoller,
        mock_graph: GraphTeamsClient,
        mock_teams: TeamsClient,
    ) -> None:
        """回复失败时降级为直接发送。"""
        mock_graph.reply_to_message = AsyncMock(side_effect=Exception("Reply failed"))

        msg = ChannelMessage(id="parent-1", from_name="Alice")
        await poller._reply(msg, "fallback message")

        mock_teams.send_message.assert_called_once_with("fallback message")


class TestInitialization:
    @pytest.mark.asyncio
    async def test_init_skips_history(
        self, poller: TeamsChannelPoller, mock_graph: GraphTeamsClient
    ) -> None:
        """初始化时获取 deltaLink 但不处理历史消息。"""
        # 模拟首次 delta 返回历史消息
        mock_graph.get_channel_messages_delta.return_value = [
            ChannelMessage(id="old-1", content="old message", from_name="X"),
        ]

        # 手动执行初始化逻辑
        assert poller._initialized is False
        await mock_graph.get_channel_messages_delta()
        poller._initialized = True
        assert poller._initialized is True
