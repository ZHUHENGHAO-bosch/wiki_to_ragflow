"""
watcher/webhook_handler.py — Jira Webhook 路由

接收 Jira Webhook 事件，提取 Bug key 并触发分析流程。
"""
from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any, Callable, Coroutine

from fastapi import APIRouter, Header, HTTPException, Request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])

# 将在 main.py 中通过 set_trigger_fn 注入
_trigger_fn: Callable[[str], Coroutine[Any, Any, None]] | None = None
_webhook_secret: str = ""


def set_trigger_fn(
    fn: Callable[[str], Coroutine[Any, Any, None]],
    secret: str = "",
) -> None:
    """注入分析触发函数和 webhook secret。"""
    global _trigger_fn, _webhook_secret
    _trigger_fn = fn
    _webhook_secret = secret


@router.post("/jira")
async def handle_jira_webhook(
    request: Request,
    x_hub_signature: str | None = Header(None, alias="X-Hub-Signature"),
) -> dict[str, str]:
    """
    处理 Jira Webhook 回调。

    Jira 会在 Issue 创建/更新时 POST 到此端点。
    """
    body = await request.body()

    # 验证签名 (如果配置了 secret)
    if _webhook_secret:
        if not x_hub_signature:
            raise HTTPException(status_code=401, detail="Missing signature")
        if not _verify_signature(body, x_hub_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()

    # 提取事件类型
    event = payload.get("webhookEvent", "")
    issue = payload.get("issue", {})
    issue_key = issue.get("key", "")
    issue_type = (
        issue.get("fields", {}).get("issuetype", {}).get("name", "")
    )

    logger.info(
        f"Webhook 事件: {event}, issue: {issue_key}, type: {issue_type}"
    )

    # 只处理 Bug 类型
    if issue_type != "Bug":
        return {"status": "ignored", "reason": "not a Bug"}

    # 只处理 created 和 updated 事件
    if event not in ("jira:issue_created", "jira:issue_updated"):
        return {"status": "ignored", "reason": f"event {event}"}

    # 检查是否已被分析过 (通过 label)
    labels = issue.get("fields", {}).get("labels", [])
    if "analyzed" in labels:
        return {"status": "ignored", "reason": "already analyzed"}

    # 触发分析
    if _trigger_fn is None:
        raise HTTPException(
            status_code=500, detail="Trigger function not configured"
        )

    logger.info(f"触发分析: {issue_key}")
    await _trigger_fn(issue_key)

    return {"status": "triggered", "bug_key": issue_key}


@router.get("/health")
async def health() -> dict[str, str]:
    """健康检查端点。"""
    return {"status": "ok"}


def _verify_signature(body: bytes, signature: str) -> bool:
    """验证 HMAC-SHA256 签名。"""
    expected = hmac.new(
        _webhook_secret.encode(), body, hashlib.sha256
    ).hexdigest()

    # 支持 sha256=xxx 和直接 xxx 格式
    actual = signature
    if actual.startswith("sha256="):
        actual = actual[7:]

    return hmac.compare_digest(expected, actual)
