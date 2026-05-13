"""connectors/graph_teams_client.py 单元测试。"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from connectors.graph_auth import GraphAuth
from connectors.graph_teams_client import ChannelMessage, GraphTeamsClient


@pytest.fixture
def mock_auth() -> GraphAuth:
    auth = MagicMock(spec=GraphAuth)
    auth.get_auth_headers = AsyncMock(
        return_value={"Authorization": "Bearer test-token"}
    )
    return auth


@pytest.fixture
def client(mock_auth: GraphAuth) -> GraphTeamsClient:
    return GraphTeamsClient(
        auth=mock_auth,
        team_id="team-123",
        channel_id="19:channel@thread.tacv2",
        bot_name="CAgent",
    )


class TestSendChannelMessage:
    @pytest.mark.asyncio
    async def test_send_text(self, client: GraphTeamsClient) -> None:
        """发送纯文本消息。"""
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"id": "msg-001"}

        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_resp
        ) as mock_post:
            msg_id = await client.send_channel_message(content="Hello Teams!")

            assert msg_id == "msg-001"
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            assert payload["body"]["content"] == "Hello Teams!"
            assert payload["body"]["contentType"] == "html"

    @pytest.mark.asyncio
    async def test_send_adaptive_card(self, client: GraphTeamsClient) -> None:
        """发送 Adaptive Card。"""
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"id": "msg-002"}

        card = {"type": "AdaptiveCard", "body": [], "version": "1.4"}

        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_resp
        ) as mock_post:
            msg_id = await client.send_channel_message(card=card)

            assert msg_id == "msg-002"
            payload = mock_post.call_args[1]["json"]
            assert "attachments" in payload
            assert payload["attachments"][0]["contentType"] == "application/vnd.microsoft.card.adaptive"

    @pytest.mark.asyncio
    async def test_send_with_auth_headers(self, client: GraphTeamsClient, mock_auth: GraphAuth) -> None:
        """验证请求包含 Authorization 头。"""
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"id": "msg-003"}

        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_resp
        ) as mock_post:
            await client.send_channel_message(content="test")

            headers = mock_post.call_args[1]["headers"]
            assert headers["Authorization"] == "Bearer test-token"
            mock_auth.get_auth_headers.assert_called_once()


class TestReplyToMessage:
    @pytest.mark.asyncio
    async def test_reply_text(self, client: GraphTeamsClient) -> None:
        """回复纯文本。"""
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"id": "reply-001"}

        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_resp
        ) as mock_post:
            reply_id = await client.reply_to_message("msg-parent", content="Reply text")

            assert reply_id == "reply-001"
            url = mock_post.call_args[0][0]
            assert "msg-parent/replies" in url

    @pytest.mark.asyncio
    async def test_reply_with_card(self, client: GraphTeamsClient) -> None:
        """回复 Adaptive Card。"""
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"id": "reply-002"}

        card = {"type": "AdaptiveCard", "body": [], "version": "1.4"}

        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_resp
        ) as mock_post:
            reply_id = await client.reply_to_message("msg-parent", card=card)

            assert reply_id == "reply-002"
            payload = mock_post.call_args[1]["json"]
            assert "attachments" in payload


class TestListMessageReplies:
    @pytest.mark.asyncio
    async def test_list_replies(self, client: GraphTeamsClient) -> None:
        """获取消息回复列表。"""
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "value": [
                {
                    "id": "reply-1",
                    "body": {"content": "Reply 1", "contentType": "text"},
                    "from": {"user": {"displayName": "Alice", "id": "user-1"}},
                    "createdDateTime": "2025-01-01T12:00:00Z",
                },
                {
                    "id": "reply-2",
                    "body": {"content": "Reply 2", "contentType": "text"},
                    "from": {"user": {"displayName": "Bob", "id": "user-2"}},
                    "createdDateTime": "2025-01-01T12:01:00Z",
                },
            ]
        }

        with patch.object(
            client._client, "get", new_callable=AsyncMock, return_value=mock_resp
        ):
            replies = await client.list_message_replies("msg-parent")

            assert len(replies) == 2
            assert replies[0].id == "reply-1"
            assert replies[0].from_name == "Alice"
            assert replies[1].content == "Reply 2"

    @pytest.mark.asyncio
    async def test_list_replies_empty(self, client: GraphTeamsClient) -> None:
        """无回复时返回空列表。"""
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"value": []}

        with patch.object(
            client._client, "get", new_callable=AsyncMock, return_value=mock_resp
        ):
            replies = await client.list_message_replies("msg-parent")
            assert replies == []


class TestDeltaQuery:
    @pytest.mark.asyncio
    async def test_initial_delta(self, client: GraphTeamsClient) -> None:
        """首次 Delta Query 返回消息并保存 deltaLink。"""
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "value": [
                {
                    "id": "msg-1",
                    "body": {"content": "Hello", "contentType": "text"},
                    "from": {"user": {"displayName": "Alice", "id": "u1"}},
                    "createdDateTime": "2025-01-01T10:00:00Z",
                },
            ],
            "@odata.deltaLink": "https://graph.microsoft.com/delta?token=abc",
        }

        with patch.object(
            client._client, "get", new_callable=AsyncMock, return_value=mock_resp
        ):
            messages = await client.get_channel_messages_delta()

            assert len(messages) == 1
            assert messages[0].id == "msg-1"
            assert client._delta_link == "https://graph.microsoft.com/delta?token=abc"

    @pytest.mark.asyncio
    async def test_subsequent_delta(self, client: GraphTeamsClient) -> None:
        """后续 Delta Query 使用 deltaLink。"""
        client._delta_link = "https://graph.microsoft.com/delta?token=existing"

        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "value": [
                {
                    "id": "msg-new",
                    "body": {"content": "New msg", "contentType": "text"},
                    "from": {"user": {"displayName": "Bob", "id": "u2"}},
                    "createdDateTime": "2025-01-01T11:00:00Z",
                },
            ],
            "@odata.deltaLink": "https://graph.microsoft.com/delta?token=updated",
        }

        with patch.object(
            client._client, "get", new_callable=AsyncMock, return_value=mock_resp
        ) as mock_get:
            messages = await client.get_channel_messages_delta()

            assert len(messages) == 1
            # 验证使用了 deltaLink
            url = mock_get.call_args[0][0]
            assert "token=existing" in url
            # deltaLink 已更新
            assert client._delta_link == "https://graph.microsoft.com/delta?token=updated"

    @pytest.mark.asyncio
    async def test_delta_pagination(self, client: GraphTeamsClient) -> None:
        """Delta Query 分页。"""
        page1 = MagicMock()
        page1.raise_for_status = MagicMock()
        page1.json.return_value = {
            "value": [
                {
                    "id": "msg-p1",
                    "body": {"content": "Page 1", "contentType": "text"},
                    "from": {"user": {"displayName": "A", "id": "u1"}},
                    "createdDateTime": "2025-01-01T10:00:00Z",
                },
            ],
            "@odata.nextLink": "https://graph.microsoft.com/next?page=2",
        }

        page2 = MagicMock()
        page2.raise_for_status = MagicMock()
        page2.json.return_value = {
            "value": [
                {
                    "id": "msg-p2",
                    "body": {"content": "Page 2", "contentType": "text"},
                    "from": {"user": {"displayName": "B", "id": "u2"}},
                    "createdDateTime": "2025-01-01T10:01:00Z",
                },
            ],
            "@odata.deltaLink": "https://graph.microsoft.com/delta?token=final",
        }

        with patch.object(
            client._client, "get", new_callable=AsyncMock,
            side_effect=[page1, page2]
        ):
            messages = await client.get_channel_messages_delta()

            assert len(messages) == 2
            assert messages[0].id == "msg-p1"
            assert messages[1].id == "msg-p2"
            assert client._delta_link == "https://graph.microsoft.com/delta?token=final"

    @pytest.mark.asyncio
    async def test_delta_empty(self, client: GraphTeamsClient) -> None:
        """无新消息时返回空列表。"""
        client._delta_link = "https://graph.microsoft.com/delta?token=x"

        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "value": [],
            "@odata.deltaLink": "https://graph.microsoft.com/delta?token=x2",
        }

        with patch.object(
            client._client, "get", new_callable=AsyncMock, return_value=mock_resp
        ):
            messages = await client.get_channel_messages_delta()
            assert messages == []


class TestMessageFiltering:
    def test_is_own_message(self, client: GraphTeamsClient) -> None:
        """识别 Bot 自己的消息。"""
        msg = ChannelMessage(id="1", from_name="CAgent")
        assert client.is_own_message(msg) is True

    def test_is_own_message_case_insensitive(self, client: GraphTeamsClient) -> None:
        """Bot 名称大小写不敏感。"""
        msg = ChannelMessage(id="1", from_name="cagent")
        assert client.is_own_message(msg) is True

    def test_is_not_own_message(self, client: GraphTeamsClient) -> None:
        """其他用户的消息。"""
        msg = ChannelMessage(id="1", from_name="Alice")
        assert client.is_own_message(msg) is False

    def test_is_mention(self, client: GraphTeamsClient) -> None:
        """包含 @mention 的消息被识别为命令。"""
        msg = ChannelMessage(
            id="1",
            content="analyze BUG-123",
            mentions=["CAgent"],
        )
        assert client.is_mention_or_command(msg) is True

    def test_is_command_by_name_prefix(self, client: GraphTeamsClient) -> None:
        """以 Bot 名称开头的消息被识别为命令。"""
        msg = ChannelMessage(
            id="1",
            content="CAgent analyze BUG-123",
        )
        assert client.is_mention_or_command(msg) is True

    def test_not_command(self, client: GraphTeamsClient) -> None:
        """普通消息不被识别为命令。"""
        msg = ChannelMessage(
            id="1",
            content="Just a normal message",
        )
        assert client.is_mention_or_command(msg) is False


class TestParseMessage:
    def test_parse_user_message(self, client: GraphTeamsClient) -> None:
        """解析用户消息。"""
        data = {
            "id": "msg-123",
            "body": {"content": "Hello!", "contentType": "text"},
            "from": {
                "user": {"displayName": "Alice", "id": "user-alice"},
            },
            "createdDateTime": "2025-01-01T12:00:00Z",
            "mentions": [],
        }
        msg = client._parse_message(data)

        assert msg.id == "msg-123"
        assert msg.content == "Hello!"
        assert msg.from_name == "Alice"
        assert msg.from_id == "user-alice"
        assert msg.created_at == "2025-01-01T12:00:00Z"

    def test_parse_message_with_mentions(self, client: GraphTeamsClient) -> None:
        """解析包含 @mention 的消息。"""
        data = {
            "id": "msg-456",
            "body": {"content": "<at>CAgent</at> analyze BUG-1", "contentType": "html"},
            "from": {
                "user": {"displayName": "Bob", "id": "user-bob"},
            },
            "createdDateTime": "2025-01-01T13:00:00Z",
            "mentions": [
                {"mentioned": {"user": {"displayName": "CAgent"}}},
            ],
        }
        msg = client._parse_message(data)

        assert msg.id == "msg-456"
        assert "CAgent" in msg.mentions
        assert msg.content_type == "html"

    def test_parse_application_message(self, client: GraphTeamsClient) -> None:
        """解析应用 (Bot) 发的消息。"""
        data = {
            "id": "msg-789",
            "body": {"content": "Bot reply", "contentType": "text"},
            "from": {
                "application": {"displayName": "CAgent", "id": "app-1"},
            },
            "createdDateTime": "2025-01-01T14:00:00Z",
        }
        msg = client._parse_message(data)

        assert msg.from_name == "CAgent"
        assert msg.from_id == "app-1"

    def test_parse_empty_from(self, client: GraphTeamsClient) -> None:
        """from 字段为空时不崩溃。"""
        data = {
            "id": "msg-empty",
            "body": {"content": "", "contentType": "text"},
            "from": {},
            "createdDateTime": "",
        }
        msg = client._parse_message(data)
        assert msg.from_name == ""


class TestClose:
    @pytest.mark.asyncio
    async def test_close(self, client: GraphTeamsClient) -> None:
        """close() 正常关闭。"""
        with patch.object(
            client._client, "aclose", new_callable=AsyncMock
        ) as mock_close:
            await client.close()
            mock_close.assert_called_once()
