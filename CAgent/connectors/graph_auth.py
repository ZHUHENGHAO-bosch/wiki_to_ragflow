"""
connectors/graph_auth.py — Azure AD OAuth2 认证

使用 Client Credentials Flow 获取 Microsoft Graph API 访问令牌。
自动在过期前刷新 token，无需引入额外 MSAL 依赖。
"""
from __future__ import annotations

import logging
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Azure AD token 端点模板
_TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"

# 提前刷新的缓冲时间 (秒)
_REFRESH_BUFFER = 300  # 5 分钟


class GraphAuth:
    """Azure AD OAuth2 Client Credentials 认证管理器。"""

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        proxy: str = "",
    ) -> None:
        self._tenant_id = tenant_id
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_url = _TOKEN_URL.format(tenant=tenant_id)

        transport = (
            httpx.AsyncHTTPTransport(proxy=proxy)
            if proxy
            else None
        )
        self._client = httpx.AsyncClient(
            timeout=30.0,
            transport=transport,
        )

        self._access_token: str | None = None
        self._expires_at: float = 0.0  # Unix timestamp

    @property
    def is_configured(self) -> bool:
        """检查是否已配置所有必要参数。"""
        return bool(
            self._tenant_id and self._client_id and self._client_secret
        )

    async def get_token(self) -> str:
        """
        获取有效的访问令牌。

        如果 token 已缓存且未过期，直接返回缓存。
        否则重新获取。
        """
        if self._access_token and time.time() < self._expires_at:
            return self._access_token

        await self._refresh_token()
        return self._access_token  # type: ignore[return-value]

    async def get_auth_headers(self) -> dict[str, str]:
        """返回包含 Bearer token 的请求头。"""
        token = await self.get_token()
        return {"Authorization": f"Bearer {token}"}

    async def _refresh_token(self) -> None:
        """从 Azure AD 获取新的访问令牌。"""
        data = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "scope": "https://graph.microsoft.com/.default",
        }

        try:
            resp = await self._client.post(
                self._token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            resp.raise_for_status()
            token_data: dict[str, Any] = resp.json()

            self._access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self._expires_at = time.time() + expires_in - _REFRESH_BUFFER

            logger.info(
                f"Azure AD token 获取成功，有效期 {expires_in}s"
            )
        except httpx.HTTPStatusError as e:
            error_body = e.response.text
            logger.error(
                f"Azure AD token 获取失败 (HTTP {e.response.status_code}): {error_body}"
            )
            raise
        except Exception as e:
            logger.error(f"Azure AD token 获取异常: {e}")
            raise

    async def close(self) -> None:
        """关闭 HTTP 客户端。"""
        await self._client.aclose()
