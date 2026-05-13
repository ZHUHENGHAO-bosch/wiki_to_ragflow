"""connectors/graph_auth.py 单元测试。"""
from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from connectors.graph_auth import GraphAuth


@pytest.fixture
def auth() -> GraphAuth:
    return GraphAuth(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
    )


@pytest.fixture
def auth_with_proxy() -> GraphAuth:
    return GraphAuth(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
        proxy="http://proxy:8080",
    )


class TestGraphAuth:
    def test_is_configured(self, auth: GraphAuth) -> None:
        """正确配置时返回 True。"""
        assert auth.is_configured is True

    def test_not_configured_missing_tenant(self) -> None:
        """缺少 tenant_id 时返回 False。"""
        auth = GraphAuth("", "client-id", "secret")
        assert auth.is_configured is False

    def test_not_configured_missing_client(self) -> None:
        """缺少 client_id 时返回 False。"""
        auth = GraphAuth("tenant", "", "secret")
        assert auth.is_configured is False

    def test_not_configured_missing_secret(self) -> None:
        """缺少 client_secret 时返回 False。"""
        auth = GraphAuth("tenant", "client", "")
        assert auth.is_configured is False

    @pytest.mark.asyncio
    async def test_get_token_success(self, auth: GraphAuth) -> None:
        """成功获取 token。"""
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "access_token": "test-token-abc",
            "expires_in": 3600,
            "token_type": "Bearer",
        }

        with patch.object(
            auth._client, "post", new_callable=AsyncMock, return_value=mock_resp
        ) as mock_post:
            token = await auth.get_token()

            assert token == "test-token-abc"
            mock_post.assert_called_once()

            # 验证请求参数
            call_kwargs = mock_post.call_args
            assert "login.microsoftonline.com" in call_kwargs[0][0]
            assert call_kwargs[1]["data"]["grant_type"] == "client_credentials"
            assert call_kwargs[1]["data"]["client_id"] == "test-client-id"
            assert call_kwargs[1]["data"]["scope"] == "https://graph.microsoft.com/.default"

    @pytest.mark.asyncio
    async def test_get_token_cached(self, auth: GraphAuth) -> None:
        """token 未过期时使用缓存。"""
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "access_token": "cached-token",
            "expires_in": 3600,
        }

        with patch.object(
            auth._client, "post", new_callable=AsyncMock, return_value=mock_resp
        ) as mock_post:
            # 第一次获取
            token1 = await auth.get_token()
            # 第二次获取 (应使用缓存)
            token2 = await auth.get_token()

            assert token1 == "cached-token"
            assert token2 == "cached-token"
            # 只应调用一次 POST
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_token_refresh_on_expiry(self, auth: GraphAuth) -> None:
        """token 过期后重新获取。"""
        mock_resp1 = MagicMock()
        mock_resp1.raise_for_status = MagicMock()
        mock_resp1.json.return_value = {
            "access_token": "token-1",
            "expires_in": 3600,
        }

        mock_resp2 = MagicMock()
        mock_resp2.raise_for_status = MagicMock()
        mock_resp2.json.return_value = {
            "access_token": "token-2",
            "expires_in": 3600,
        }

        with patch.object(
            auth._client, "post", new_callable=AsyncMock,
            side_effect=[mock_resp1, mock_resp2]
        ) as mock_post:
            token1 = await auth.get_token()
            assert token1 == "token-1"

            # 模拟过期
            auth._expires_at = time.time() - 1

            token2 = await auth.get_token()
            assert token2 == "token-2"
            assert mock_post.call_count == 2

    @pytest.mark.asyncio
    async def test_get_token_http_error(self, auth: GraphAuth) -> None:
        """HTTP 错误时抛出异常。"""
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"
        mock_resp.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "Unauthorized", request=MagicMock(), response=mock_resp
            )
        )

        with patch.object(
            auth._client, "post", new_callable=AsyncMock, return_value=mock_resp
        ):
            with pytest.raises(httpx.HTTPStatusError):
                await auth.get_token()

    @pytest.mark.asyncio
    async def test_get_auth_headers(self, auth: GraphAuth) -> None:
        """get_auth_headers 返回正确的 Bearer 头。"""
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "access_token": "my-bearer-token",
            "expires_in": 3600,
        }

        with patch.object(
            auth._client, "post", new_callable=AsyncMock, return_value=mock_resp
        ):
            headers = await auth.get_auth_headers()
            assert headers == {"Authorization": "Bearer my-bearer-token"}

    def test_proxy_configured(self, auth_with_proxy: GraphAuth) -> None:
        """代理配置时客户端创建成功。"""
        assert auth_with_proxy._client is not None

    @pytest.mark.asyncio
    async def test_close(self, auth: GraphAuth) -> None:
        """close() 正常关闭。"""
        with patch.object(
            auth._client, "aclose", new_callable=AsyncMock
        ) as mock_close:
            await auth.close()
            mock_close.assert_called_once()
