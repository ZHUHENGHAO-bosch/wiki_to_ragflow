"""connectors/teams_client.py + watcher/teams_webhook_handler.py 单元测试。"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from config import TeamsConfig
from connectors.teams_client import TeamsClient


@pytest.fixture
def teams_config() -> TeamsConfig:
    return TeamsConfig(
        webhook_url="https://outlook.office.com/webhook/test-url",
        outgoing_webhook_secret=base64.b64encode(b"test-secret-key").decode(),
        enabled=True,
        notify_on_analysis_complete=True,
        timeout=10.0,
    )


@pytest.fixture
def workflow_config() -> TeamsConfig:
    """Workflow Webhook 配置（无 Incoming Webhook）。"""
    return TeamsConfig(
        workflow_webhook_url="https://prod-123.logic.azure.com/workflows/test",
        enabled=True,
        timeout=10.0,
    )


@pytest.fixture
def proxy_config() -> TeamsConfig:
    """带代理的配置。"""
    return TeamsConfig(
        webhook_url="https://outlook.office.com/webhook/test-url",
        proxy="http://corporate-proxy:8080",
        enabled=True,
        timeout=10.0,
    )


@pytest.fixture
def empty_config() -> TeamsConfig:
    return TeamsConfig()


@pytest.fixture
def client(teams_config: TeamsConfig) -> TeamsClient:
    return TeamsClient(teams_config)


# ── SendMessage Tests ──


class TestSendMessage:
    @pytest.mark.asyncio
    async def test_send_message_success(self, client: TeamsClient) -> None:
        """成功发送文本消息。"""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_response
        ) as mock_post:
            result = await client.send_message("Hello Teams!")
            assert result is True
            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args
            assert call_kwargs[1]["json"] == {"text": "Hello Teams!"}

    @pytest.mark.asyncio
    async def test_send_message_no_webhook_url(self, empty_config: TeamsConfig) -> None:
        """webhook_url 为空时跳过发送。"""
        client = TeamsClient(empty_config)
        result = await client.send_message("test")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_message_http_error(self, client: TeamsClient) -> None:
        """HTTP 错误时返回 False。"""
        import httpx

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "Bad Request", request=MagicMock(), response=mock_response
            )
        )

        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await client.send_message("test")
            assert result is False


# ── SendCard Tests ──


class TestSendCard:
    @pytest.mark.asyncio
    async def test_send_card_structure(self, client: TeamsClient) -> None:
        """验证 Card 的 JSON 结构。"""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_response
        ) as mock_post:
            await client.send_card(
                title="Test Card",
                summary="Test Summary",
                theme_color="FF0000",
                sections=[{"title": "Section1", "text": "Content"}],
                actions=[{"@type": "OpenUri", "name": "View"}],
            )

            payload = mock_post.call_args[1]["json"]
            assert payload["@type"] == "MessageCard"
            assert payload["title"] == "Test Card"
            assert payload["summary"] == "Test Summary"
            assert payload["themeColor"] == "FF0000"
            assert len(payload["sections"]) == 1
            assert len(payload["potentialAction"]) == 1

    @pytest.mark.asyncio
    async def test_send_card_minimal(self, client: TeamsClient) -> None:
        """最小卡片（无 sections/actions）。"""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_response
        ) as mock_post:
            await client.send_card(title="Minimal", summary="Min")
            payload = mock_post.call_args[1]["json"]
            assert "sections" not in payload
            assert "potentialAction" not in payload


# ── SendAnalysisResult Tests ──


class TestSendAnalysisResult:
    @pytest.mark.asyncio
    async def test_success_state(self, client: TeamsClient) -> None:
        """成功状态发送成功。"""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        state = {
            "bug_key": "BUG-123",
            "status": "success",
            "root_cause": None,
            "analysis_duration": 5.2,
            "errors": [],
        }

        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await client.send_analysis_result(state)
            assert result is True

    @pytest.mark.asyncio
    async def test_partial_state(self, client: TeamsClient) -> None:
        """部分完成发送成功。"""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        state = {
            "bug_key": "BUG-456",
            "status": "partial",
            "root_cause": None,
            "analysis_duration": 3.0,
            "errors": ["Some warning"],
        }

        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await client.send_analysis_result(state)
            assert result is True

    @pytest.mark.asyncio
    async def test_failed_state(self, client: TeamsClient) -> None:
        """失败状态发送成功。"""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        state = {
            "bug_key": "BUG-789",
            "status": "failed",
            "root_cause": None,
            "analysis_duration": 1.0,
            "errors": [],
        }

        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await client.send_analysis_result(state)
            assert result is True

    @pytest.mark.asyncio
    async def test_no_transport_skips(self, empty_config: TeamsConfig) -> None:
        """无任何传输配置时跳过。"""
        client = TeamsClient(empty_config)
        state = {"bug_key": "BUG-1", "status": "success"}
        result = await client.send_analysis_result(state)
        assert result is False

    @pytest.mark.asyncio
    async def test_with_root_cause(self, client: TeamsClient) -> None:
        """包含 root_cause 的分析结果发送成功。"""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        root_cause = MagicMock()
        root_cause.level.value = "实现偏离"
        root_cause.summary = "空指针解引用"
        root_cause.fix_suggestions = []
        root_cause.detail = ""

        state = {
            "bug_key": "BUG-100",
            "status": "success",
            "root_cause": root_cause,
            "analysis_duration": 10.5,
            "errors": [],
        }

        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await client.send_analysis_result(state)
            assert result is True

    @pytest.mark.asyncio
    async def test_legacy_fallback(self, teams_config: TeamsConfig) -> None:
        """send_analysis_result 在 Adaptive Card 降级时使用 legacy MessageCard。"""
        client = TeamsClient(teams_config)
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        state = {
            "bug_key": "BUG-LEGACY",
            "status": "success",
            "root_cause": None,
            "analysis_duration": 2.0,
            "errors": [],
        }

        # Adaptive Card 通过 webhook 降级发送，第一次 post 成功
        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_response
        ) as mock_post:
            result = await client.send_analysis_result(state)
            assert result is True
            # 验证 POST 到 webhook URL
            url = mock_post.call_args[0][0]
            assert "outlook.office.com" in url


# ── HMAC Verification Tests ──


class TestHmacVerification:
    def test_valid_signature(self) -> None:
        """正确签名验证通过。"""
        secret = base64.b64encode(b"my-secret-key").decode()
        body = b'{"text": "hello"}'

        # 计算正确签名
        secret_bytes = base64.b64decode(secret)
        mac = hmac.new(secret_bytes, body, hashlib.sha256).digest()
        sig = base64.b64encode(mac).decode()
        auth_header = f"HMAC {sig}"

        assert TeamsClient.verify_hmac(body, auth_header, secret) is True

    def test_invalid_signature(self) -> None:
        """错误签名验证失败。"""
        secret = base64.b64encode(b"my-secret-key").decode()
        body = b'{"text": "hello"}'
        auth_header = "HMAC invalidbase64signature=="

        assert TeamsClient.verify_hmac(body, auth_header, secret) is False

    def test_tampered_body(self) -> None:
        """篡改 body 后签名失效。"""
        secret = base64.b64encode(b"my-secret-key").decode()
        original_body = b'{"text": "hello"}'

        secret_bytes = base64.b64decode(secret)
        mac = hmac.new(secret_bytes, original_body, hashlib.sha256).digest()
        sig = base64.b64encode(mac).decode()
        auth_header = f"HMAC {sig}"

        tampered_body = b'{"text": "hacked"}'
        assert TeamsClient.verify_hmac(tampered_body, auth_header, secret) is False

    def test_missing_hmac_prefix(self) -> None:
        """缺少 HMAC 前缀时失败。"""
        assert TeamsClient.verify_hmac(b"body", "Bearer token", "secret") is False

    def test_empty_auth_header(self) -> None:
        """空 auth header 失败。"""
        assert TeamsClient.verify_hmac(b"body", "", "secret") is False

    def test_none_auth_header(self) -> None:
        """None auth header 失败。"""
        assert TeamsClient.verify_hmac(b"body", None, "secret") is False


# ── ParseCommand Tests ──


class TestParseCommand:
    def test_analyze_command(self) -> None:
        """解析 analyze 命令。"""
        text = "<at>Bot</at> analyze BUG-123"
        result = TeamsClient.parse_command(text)
        assert result == ("analyze", "BUG-123")

    def test_status_command(self) -> None:
        """解析 status 命令。"""
        text = "<at>Bot Name</at> status"
        result = TeamsClient.parse_command(text)
        assert result == ("status", "")

    def test_help_command(self) -> None:
        """解析 help 命令。"""
        text = "<at>Analysis Bot</at> help"
        result = TeamsClient.parse_command(text)
        assert result == ("help", "")

    def test_empty_text(self) -> None:
        """空消息返回 None。"""
        assert TeamsClient.parse_command("") is None
        assert TeamsClient.parse_command(None) is None

    def test_no_mention(self) -> None:
        """无 @mention 的命令也能解析。"""
        result = TeamsClient.parse_command("analyze BUG-456")
        assert result == ("analyze", "BUG-456")

    def test_unknown_command(self) -> None:
        """未知命令返回 None。"""
        text = "<at>Bot</at> unknown_command arg"
        assert TeamsClient.parse_command(text) is None

    def test_case_insensitive(self) -> None:
        """命令大小写不敏感。"""
        text = "<at>Bot</at> ANALYZE BUG-789"
        result = TeamsClient.parse_command(text)
        assert result == ("analyze", "BUG-789")

    def test_only_mention(self) -> None:
        """只有 @mention 没有命令。"""
        text = "<at>Bot</at>"
        assert TeamsClient.parse_command(text) is None

    def test_whitespace_only(self) -> None:
        """只有空白。"""
        text = "<at>Bot</at>   "
        assert TeamsClient.parse_command(text) is None


# ── TeamsWebhookHandler Tests ──


class TestTeamsWebhookHandler:
    """测试 Teams Outgoing Webhook 路由。"""

    @pytest.fixture
    def app(self) -> FastAPI:
        from watcher.teams_webhook_handler import router, set_teams_trigger
        app = FastAPI()
        app.include_router(router)

        async def mock_trigger(bug_key: str) -> None:
            pass

        set_teams_trigger(mock_trigger, "")
        return app

    @pytest.fixture
    def http_client(self, app: FastAPI) -> TestClient:
        return TestClient(app)

    def test_health(self, http_client: TestClient) -> None:
        """健康检查端点。"""
        resp = http_client.get("/teams/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"

    def test_analyze_command(self, http_client: TestClient) -> None:
        """analyze 命令触发分析。"""
        payload = {"text": "<at>Bot</at> analyze BUG-999"}
        resp = http_client.post("/teams/webhook", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "message"
        assert "BUG-999" in data["text"]

    def test_help_command(self, http_client: TestClient) -> None:
        """help 命令返回帮助信息。"""
        payload = {"text": "<at>Bot</at> help"}
        resp = http_client.post("/teams/webhook", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "analyze" in data["text"].lower()

    def test_status_command(self, http_client: TestClient) -> None:
        """status 命令返回系统状态。"""
        payload = {"text": "<at>Bot</at> status"}
        resp = http_client.post("/teams/webhook", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "message"

    def test_unknown_command(self, http_client: TestClient) -> None:
        """未知命令返回帮助提示。"""
        payload = {"text": "<at>Bot</at> foobar"}
        resp = http_client.post("/teams/webhook", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "未识别" in data["text"]

    def test_analyze_no_key(self, http_client: TestClient) -> None:
        """analyze 不带 key 时提示。"""
        payload = {"text": "<at>Bot</at> analyze"}
        resp = http_client.post("/teams/webhook", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "请指定" in data["text"]

    def test_hmac_verification_enabled(self) -> None:
        """启用 HMAC 时，无签名返回 401。"""
        from watcher.teams_webhook_handler import router, set_teams_trigger

        app = FastAPI()
        app.include_router(router)

        secret = base64.b64encode(b"test-key").decode()

        async def mock_trigger(bug_key: str) -> None:
            pass

        set_teams_trigger(mock_trigger, secret)

        tc = TestClient(app)
        payload = {"text": "<at>Bot</at> help"}
        resp = tc.post("/teams/webhook", json=payload)
        assert resp.status_code == 401

    def test_hmac_verification_valid(self) -> None:
        """有效 HMAC 签名通过验证。"""
        from watcher.teams_webhook_handler import router, set_teams_trigger

        app = FastAPI()
        app.include_router(router)

        secret = base64.b64encode(b"test-key").decode()

        async def mock_trigger(bug_key: str) -> None:
            pass

        set_teams_trigger(mock_trigger, secret)

        body = json.dumps({"text": "<at>Bot</at> help"}).encode()
        secret_bytes = base64.b64decode(secret)
        mac = hmac.new(secret_bytes, body, hashlib.sha256).digest()
        sig = base64.b64encode(mac).decode()

        tc = TestClient(app)
        resp = tc.post(
            "/teams/webhook",
            content=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"HMAC {sig}",
            },
        )
        assert resp.status_code == 200


# ── Proxy Tests ──


class TestProxySupport:
    def test_proxy_configured(self, proxy_config: TeamsConfig) -> None:
        """代理配置时 transport 被设置。"""
        client = TeamsClient(proxy_config)
        # 验证 client 创建成功（proxy transport 已注入）
        assert client._client is not None
        assert client._config.proxy == "http://corporate-proxy:8080"

    def test_no_proxy(self, teams_config: TeamsConfig) -> None:
        """无代理时正常创建。"""
        client = TeamsClient(teams_config)
        assert client._client is not None
        assert client._config.proxy == ""


# ── Workflow Webhook Tests ──


class TestWorkflowWebhook:
    @pytest.mark.asyncio
    async def test_send_message_via_workflow(self, workflow_config: TeamsConfig) -> None:
        """通过 Workflow Webhook 发送文本消息。"""
        client = TeamsClient(workflow_config)
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_response
        ) as mock_post:
            result = await client.send_message("Hello via Workflow!")
            assert result is True
            # 验证 POST 到 Workflow URL
            call_args = mock_post.call_args
            assert "logic.azure.com" in call_args[0][0]
            # Workflow payload 包含 Adaptive Card
            payload = call_args[1]["json"]
            assert payload["type"] == "message"
            assert payload["attachments"][0]["contentType"] == "application/vnd.microsoft.card.adaptive"

    @pytest.mark.asyncio
    async def test_send_adaptive_card_via_workflow(self, workflow_config: TeamsConfig) -> None:
        """通过 Workflow Webhook 发送 Adaptive Card。"""
        client = TeamsClient(workflow_config)
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        card = {
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [{"type": "TextBlock", "text": "Test"}],
        }

        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_response
        ) as mock_post:
            result = await client.send_adaptive_card(card)
            assert result is True
            payload = mock_post.call_args[1]["json"]
            assert payload["type"] == "message"
            assert payload["attachments"][0]["content"] is card


# ── Transport Priority Tests ──


class TestTransportPriority:
    @pytest.mark.asyncio
    async def test_graph_api_first(self, teams_config: TeamsConfig) -> None:
        """Graph API 优先于其他传输方式。"""
        client = TeamsClient(teams_config)

        mock_graph = AsyncMock()
        mock_graph.send_channel_message = AsyncMock()
        client.set_graph_client(mock_graph)

        card = {"type": "AdaptiveCard", "body": [], "version": "1.4"}
        result = await client.send_adaptive_card(card)
        assert result is True
        mock_graph.send_channel_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_graph_api_fallback_to_webhook(self, teams_config: TeamsConfig) -> None:
        """Graph API 失败时降级到 Incoming Webhook。"""
        client = TeamsClient(teams_config)

        mock_graph = AsyncMock()
        mock_graph.send_channel_message = AsyncMock(side_effect=Exception("API Error"))
        client.set_graph_client(mock_graph)

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        card = {"type": "AdaptiveCard", "body": [{"type": "TextBlock", "text": "test"}], "version": "1.4"}
        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await client.send_adaptive_card(card)
            assert result is True

    @pytest.mark.asyncio
    async def test_workflow_before_incoming_webhook(self) -> None:
        """同时配置 Workflow 和 Incoming Webhook 时优先用 Workflow。"""
        config = TeamsConfig(
            webhook_url="https://outlook.office.com/webhook/test",
            workflow_webhook_url="https://prod-123.logic.azure.com/workflows/test",
            enabled=True,
        )
        client = TeamsClient(config)

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        card = {"type": "AdaptiveCard", "body": [], "version": "1.4"}
        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_response
        ) as mock_post:
            result = await client.send_adaptive_card(card)
            assert result is True
            # 验证 POST 到 Workflow URL 而非 Incoming Webhook
            url = mock_post.call_args[0][0]
            assert "logic.azure.com" in url

    @pytest.mark.asyncio
    async def test_no_transport_configured(self, empty_config: TeamsConfig) -> None:
        """无任何传输配置时返回 False。"""
        client = TeamsClient(empty_config)
        card = {"type": "AdaptiveCard", "body": [], "version": "1.4"}
        result = await client.send_adaptive_card(card)
        assert result is False

    @pytest.mark.asyncio
    async def test_send_analysis_result_adaptive_card(self) -> None:
        """send_analysis_result 优先使用 Adaptive Card。"""
        config = TeamsConfig(
            workflow_webhook_url="https://prod-123.logic.azure.com/test",
            enabled=True,
        )
        client = TeamsClient(config)

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        state = {
            "bug_key": "BUG-123",
            "status": "success",
            "root_cause": None,
            "analysis_duration": 5.0,
            "errors": [],
        }

        with patch.object(
            client._client, "post", new_callable=AsyncMock, return_value=mock_response
        ) as mock_post:
            result = await client.send_analysis_result(state)
            assert result is True
            payload = mock_post.call_args[1]["json"]
            # Workflow Webhook payload 格式
            assert payload["type"] == "message"
            assert payload["attachments"][0]["contentType"] == "application/vnd.microsoft.card.adaptive"


# ── Close Tests ──


class TestClose:
    @pytest.mark.asyncio
    async def test_close(self, client: TeamsClient) -> None:
        """close() 正常关闭。"""
        with patch.object(
            client._client, "aclose", new_callable=AsyncMock
        ) as mock_close:
            await client.close()
            mock_close.assert_called_once()
