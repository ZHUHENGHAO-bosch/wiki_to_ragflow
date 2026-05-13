"""
connectors/teams_client.py — Microsoft Teams 通信客户端

支持多种传输方式（按优先级）：
1. Graph API（双向通信，推荐）
2. Power Automate Workflow Webhook（官方替代方案）
3. Incoming Webhook（降级方案，已宣布退役）

同时保留 Outgoing Webhook HMAC 验证和命令解析工具方法。
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import re
from typing import Any

import httpx

from config import TeamsConfig
from connectors.teams_card_builder import (
    build_analysis_result_card,
    wrap_for_workflow_webhook,
)

logger = logging.getLogger(__name__)


class TeamsClient:
    """Microsoft Teams 通信客户端。"""

    def __init__(self, config: TeamsConfig) -> None:
        self._config = config
        self._graph_client: Any | None = None  # GraphTeamsClient (Phase 2 注入)

        # 配置代理
        transport = (
            httpx.AsyncHTTPTransport(proxy=config.proxy)
            if config.proxy
            else None
        )
        self._client = httpx.AsyncClient(
            timeout=config.timeout,
            transport=transport,
        )

    def set_graph_client(self, graph_client: Any) -> None:
        """注入 Graph API 客户端 (Phase 2)。"""
        self._graph_client = graph_client

    # ── 统一发送接口 ──

    async def send_adaptive_card(self, card: dict[str, Any]) -> bool:
        """
        发送 Adaptive Card，自动选择最优传输方式。

        优先级: Graph API > Workflow Webhook > Incoming Webhook (降级 MessageCard)
        """
        # 1. Graph API
        if self._graph_client is not None:
            try:
                await self._graph_client.send_channel_message(card=card)
                logger.info("Teams 消息通过 Graph API 发送成功")
                return True
            except Exception as e:
                logger.warning(f"Graph API 发送失败，尝试降级: {e}")

        # 2. Workflow Webhook
        if self._config.workflow_webhook_url:
            return await self._post_workflow_webhook(card)

        # 3. Incoming Webhook (将 Adaptive Card 信息降级为文本)
        if self._config.webhook_url:
            return await self._post_adaptive_card_via_webhook(card)

        logger.debug("Teams 未配置任何发送方式，跳过")
        return False

    async def send_message(self, text: str) -> bool:
        """
        发送简单文本消息到 Teams 频道。

        如果任何发送方式均未配置，静默跳过并返回 False。
        """
        # Graph API
        if self._graph_client is not None:
            try:
                await self._graph_client.send_channel_message(content=text)
                logger.info("Teams 消息通过 Graph API 发送成功")
                return True
            except Exception as e:
                logger.warning(f"Graph API 发送失败，尝试降级: {e}")

        # Workflow Webhook (简单文本包装为 card)
        if self._config.workflow_webhook_url:
            payload = {
                "type": "message",
                "attachments": [{
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "type": "AdaptiveCard",
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "version": "1.4",
                        "body": [{"type": "TextBlock", "text": text, "wrap": True}],
                    },
                }],
            }
            return await self._post_to_url(
                self._config.workflow_webhook_url, payload, "Workflow Webhook"
            )

        # Incoming Webhook
        if not self._config.webhook_url:
            logger.debug("Teams 未配置任何发送方式，跳过发送")
            return False

        payload = {"text": text}
        return await self._post_webhook(payload)

    async def send_card(
        self,
        title: str,
        summary: str,
        theme_color: str = "0076D7",
        sections: list[dict[str, Any]] | None = None,
        actions: list[dict[str, Any]] | None = None,
    ) -> bool:
        """
        发送 O365 Connector Card 到 Teams 频道（保留向后兼容）。

        仅通过 Incoming Webhook 发送，不支持其他传输方式。
        如需使用新传输方式，请使用 send_adaptive_card()。
        """
        if not self._config.webhook_url:
            logger.debug("Teams webhook_url 未配置，跳过发送")
            return False

        payload: dict[str, Any] = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "themeColor": theme_color,
            "summary": summary,
            "title": title,
        }
        if sections:
            payload["sections"] = sections
        if actions:
            payload["potentialAction"] = actions

        return await self._post_webhook(payload)

    async def send_analysis_result(self, state: dict[str, Any]) -> bool:
        """
        将 Bug 分析结果发送到 Teams 频道。

        优先使用 Adaptive Card + 最优传输方式。
        如果无法使用新方式，降级为 O365 MessageCard。
        """
        # 优先尝试 Adaptive Card
        card = build_analysis_result_card(state)
        if await self.send_adaptive_card(card):
            return True

        # 降级: O365 MessageCard (仅 Incoming Webhook)
        return await self._send_analysis_result_legacy(state)

    # ── HMAC 验证 (Outgoing Webhook) ──

    @staticmethod
    def verify_hmac(body: bytes, auth_header: str, secret: str) -> bool:
        """
        验证 Teams Outgoing Webhook 的 HMAC-SHA256 签名。

        Teams 发送的 Authorization 头格式: "HMAC <base64-signature>"
        secret 是 Teams 提供的 base64 编码密钥。
        """
        if not auth_header or not auth_header.startswith("HMAC "):
            return False

        try:
            provided_sig = auth_header[5:]  # 去掉 "HMAC " 前缀
            secret_bytes = base64.b64decode(secret)
            expected_mac = hmac.new(secret_bytes, body, hashlib.sha256).digest()
            expected_sig = base64.b64encode(expected_mac).decode()
            return hmac.compare_digest(provided_sig, expected_sig)
        except Exception:
            logger.warning("HMAC 验证异常", exc_info=True)
            return False

    # ── 命令解析 (Outgoing Webhook) ──

    @staticmethod
    def parse_command(text: str | None) -> tuple[str, str] | None:
        """
        解析 Teams 消息中的命令。

        Teams Outgoing Webhook 消息格式:
            "<at>BotName</at> analyze BUG-123"

        返回 (command, argument) 或 None。
        支持命令: analyze, status, help, detail, history, reanalyze, approve, reject
        """
        if not text:
            return None

        # 去除 <at>...</at> 标签
        cleaned = re.sub(r"<at>.*?</at>\s*", "", text).strip()

        if not cleaned:
            return None

        parts = cleaned.split(None, 1)
        command = parts[0].lower()
        argument = parts[1].strip() if len(parts) > 1 else ""

        valid_commands = {"analyze", "status", "help"}
        if command not in valid_commands:
            return None

        return command, argument

    # ── 内部传输方法 ──

    async def _post_workflow_webhook(self, card: dict[str, Any]) -> bool:
        """通过 Power Automate Workflow Webhook 发送 Adaptive Card。"""
        payload = wrap_for_workflow_webhook(card)
        return await self._post_to_url(
            self._config.workflow_webhook_url, payload, "Workflow Webhook"
        )

    async def _post_adaptive_card_via_webhook(self, card: dict[str, Any]) -> bool:
        """
        通过 Incoming Webhook 发送 Adaptive Card (降级)。

        O365 Incoming Webhook 对 Adaptive Card 的支持有限，
        提取文本内容作为降级。
        """
        # 从 card body 提取文本
        texts = []
        for item in card.get("body", []):
            text = item.get("text", "")
            if text:
                texts.append(text)
            # FactSet
            for fact in item.get("facts", []):
                texts.append(f"**{fact.get('title', '')}**: {fact.get('value', '')}")

        fallback_text = "\n\n".join(texts) if texts else "Adaptive Card"
        payload = {"text": fallback_text}
        return await self._post_webhook(payload)

    async def _post_webhook(self, payload: dict[str, Any]) -> bool:
        """POST 到 Incoming Webhook URL。"""
        return await self._post_to_url(
            self._config.webhook_url, payload, "Incoming Webhook"
        )

    async def _post_to_url(
        self, url: str, payload: dict[str, Any], transport_name: str
    ) -> bool:
        """通用 POST 方法。"""
        try:
            resp = await self._client.post(url, json=payload)
            resp.raise_for_status()
            logger.info(f"Teams 消息通过 {transport_name} 发送成功")
            return True
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Teams {transport_name} 发送失败 (HTTP {e.response.status_code}): {e}"
            )
            return False
        except Exception as e:
            logger.error(f"Teams {transport_name} 发送异常: {e}")
            return False

    async def _send_analysis_result_legacy(self, state: dict[str, Any]) -> bool:
        """降级: 使用 O365 MessageCard 发送分析结果。"""
        if not self._config.webhook_url:
            return False

        bug_key = state.get("bug_key", "UNKNOWN")
        status = state.get("status", "unknown")
        root_cause = state.get("root_cause")

        color_map = {
            "success": "2DC72D",
            "partial": "FFA500",
            "failed": "FF0000",
        }
        color = color_map.get(status, "808080")

        status_text = {
            "success": "分析完成",
            "partial": "部分完成",
            "failed": "分析失败",
        }.get(status, status)

        facts: list[dict[str, str]] = [
            {"name": "Bug", "value": bug_key},
            {"name": "状态", "value": status_text},
        ]

        if root_cause:
            level = getattr(root_cause, "level", None)
            if level:
                facts.append(
                    {"name": "根因层级", "value": level.value if hasattr(level, "value") else str(level)}
                )
            summary = getattr(root_cause, "summary", None)
            if summary:
                facts.append({"name": "根因摘要", "value": summary})
            fix_suggestions = getattr(root_cause, "fix_suggestions", None)
            if fix_suggestions:
                fix_text = "; ".join(
                    f"{fs.label}: {fs.description}" for fs in fix_suggestions[:3]
                )
                facts.append({"name": "修复建议", "value": fix_text})

        duration = state.get("analysis_duration", 0.0)
        facts.append({"name": "耗时", "value": f"{duration:.1f}s"})

        sections = [
            {
                "activityTitle": f"Bug 分析结果: {bug_key}",
                "facts": facts,
                "markdown": True,
            }
        ]

        errors = state.get("errors", [])
        if errors:
            error_text = "\n".join(f"- {e}" for e in errors[:5])
            sections.append(
                {
                    "title": "分析过程说明",
                    "text": error_text,
                    "markdown": True,
                }
            )

        return await self.send_card(
            title=f"Bug 分析: {bug_key} — {status_text}",
            summary=f"{bug_key} 分析{status_text}",
            theme_color=color,
            sections=sections,
        )

    # ── 生命周期 ──

    async def close(self) -> None:
        """关闭 HTTP 客户端。"""
        await self._client.aclose()
