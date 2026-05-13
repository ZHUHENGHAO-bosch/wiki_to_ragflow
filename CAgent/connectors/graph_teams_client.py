"""
connectors/graph_teams_client.py — Microsoft Graph API Teams 消息客户端

通过 Graph API 实现频道消息的发送、回复和增量读取 (Delta Query)。
所有通信均由 CAgent 主动发起（仅出站），适用于企业内网环境。
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import httpx

from connectors.graph_auth import GraphAuth
from connectors.teams_card_builder import wrap_for_graph_api

logger = logging.getLogger(__name__)

# Graph API 基础 URL
_GRAPH_BASE = "https://graph.microsoft.com/v1.0"
_GRAPH_BETA = "https://graph.microsoft.com/beta"


@dataclass
class ChannelMessage:
    """Teams 频道消息。"""

    id: str
    content: str = ""
    content_type: str = "text"  # "text" | "html"
    from_name: str = ""
    from_id: str = ""
    created_at: str = ""
    reply_to_id: str | None = None
    mentions: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


class GraphTeamsClient:
    """通过 Microsoft Graph API 与 Teams 频道交互。"""

    def __init__(
        self,
        auth: GraphAuth,
        team_id: str,
        channel_id: str,
        bot_name: str = "CAgent",
        proxy: str = "",
    ) -> None:
        self._auth = auth
        self._team_id = team_id
        self._channel_id = channel_id
        self._bot_name = bot_name

        transport = (
            httpx.AsyncHTTPTransport(proxy=proxy)
            if proxy
            else None
        )
        self._client = httpx.AsyncClient(
            timeout=30.0,
            transport=transport,
        )

        # Delta Query 状态
        self._delta_link: str | None = None

        # API 路径
        self._messages_path = (
            f"{_GRAPH_BETA}/teams/{team_id}/channels/{channel_id}/messages"
        )

    async def send_channel_message(
        self,
        content: str = "",
        card: dict[str, Any] | None = None,
    ) -> str:
        """
        发送消息到频道，返回 message_id。

        Args:
            content: 文本内容 (HTML)
            card: Adaptive Card 字典 (可选)
        """
        if card:
            payload = wrap_for_graph_api(card, text=content)
        else:
            payload = {
                "body": {
                    "contentType": "html",
                    "content": content,
                },
            }

        headers = await self._auth.get_auth_headers()
        headers["Content-Type"] = "application/json"

        resp = await self._client.post(
            self._messages_path,
            json=payload,
            headers=headers,
        )
        resp.raise_for_status()

        data = resp.json()
        message_id = data.get("id", "")
        logger.info(f"Graph API 消息发送成功: {message_id}")
        return message_id

    async def reply_to_message(
        self,
        message_id: str,
        content: str = "",
        card: dict[str, Any] | None = None,
    ) -> str:
        """
        回复指定消息 (线程内回复)，返回 reply_id。

        Args:
            message_id: 父消息 ID
            content: 回复文本 (HTML)
            card: Adaptive Card 字典 (可选)
        """
        url = f"{self._messages_path}/{message_id}/replies"

        if card:
            payload = wrap_for_graph_api(card, text=content)
        else:
            payload = {
                "body": {
                    "contentType": "html",
                    "content": content,
                },
            }

        headers = await self._auth.get_auth_headers()
        headers["Content-Type"] = "application/json"

        resp = await self._client.post(url, json=payload, headers=headers)
        resp.raise_for_status()

        data = resp.json()
        reply_id = data.get("id", "")
        logger.info(f"Graph API 回复发送成功: {reply_id} (parent={message_id})")
        return reply_id

    async def list_message_replies(self, message_id: str) -> list[ChannelMessage]:
        """
        读取消息的回复列表 (用于审批流程等)。

        Args:
            message_id: 父消息 ID
        """
        url = f"{self._messages_path}/{message_id}/replies"
        headers = await self._auth.get_auth_headers()

        resp = await self._client.get(url, headers=headers)
        resp.raise_for_status()

        data = resp.json()
        return [self._parse_message(m) for m in data.get("value", [])]

    async def get_channel_messages_delta(self) -> list[ChannelMessage]:
        """
        增量获取频道新消息 (Delta Query)。

        首次调用返回所有最近消息并建立 deltaLink。
        后续调用仅返回新增/修改的消息。
        """
        if self._delta_link:
            url = self._delta_link
        else:
            url = f"{self._messages_path}/delta"

        headers = await self._auth.get_auth_headers()

        all_messages: list[ChannelMessage] = []

        while url:
            resp = await self._client.get(url, headers=headers)
            resp.raise_for_status()

            data = resp.json()

            for msg_data in data.get("value", []):
                msg = self._parse_message(msg_data)
                all_messages.append(msg)

            # 分页: @odata.nextLink
            url = data.get("@odata.nextLink")

            # 增量标记: @odata.deltaLink
            delta_link = data.get("@odata.deltaLink")
            if delta_link:
                self._delta_link = delta_link

        logger.debug(f"Delta Query 返回 {len(all_messages)} 条消息")
        return all_messages

    def is_own_message(self, msg: ChannelMessage) -> bool:
        """判断消息是否是 Bot 自己发的（避免处理自己的消息）。"""
        return msg.from_name.lower() == self._bot_name.lower()

    def is_mention_or_command(self, msg: ChannelMessage) -> bool:
        """
        判断消息是否是发给 Bot 的命令。

        条件: 包含 @mention Bot 名称，或消息以 Bot 名称开头。
        """
        bot_lower = self._bot_name.lower()

        # 检查 mentions
        if any(bot_lower in m.lower() for m in msg.mentions):
            return True

        # 检查消息内容是否以 bot 名称开头
        content_lower = msg.content.lower().strip()
        if content_lower.startswith(bot_lower):
            return True

        return False

    def _parse_message(self, data: dict[str, Any]) -> ChannelMessage:
        """解析 Graph API 消息响应为 ChannelMessage。"""
        from_info = data.get("from", {})
        user_info = from_info.get("user") or from_info.get("application") or {}

        mentions = []
        for m in data.get("mentions", []):
            mentioned = m.get("mentioned", {})
            name = mentioned.get("user", {}).get("displayName", "")
            if not name:
                name = mentioned.get("application", {}).get("displayName", "")
            if name:
                mentions.append(name)

        body = data.get("body", {})

        return ChannelMessage(
            id=data.get("id", ""),
            content=body.get("content", ""),
            content_type=body.get("contentType", "text"),
            from_name=user_info.get("displayName", ""),
            from_id=user_info.get("id", ""),
            created_at=data.get("createdDateTime", ""),
            reply_to_id=None,  # Delta Query 不直接提供
            mentions=mentions,
            raw=data,
        )

    async def close(self) -> None:
        """关闭 HTTP 客户端。"""
        await self._client.aclose()
