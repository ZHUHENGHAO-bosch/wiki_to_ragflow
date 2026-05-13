"""
watcher/teams_webhook_handler.py — Teams Outgoing Webhook 路由

接收 Teams Outgoing Webhook 回调，验证 HMAC 签名，
解析命令并触发 Bug 分析或返回状态信息。
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Coroutine

from fastapi import APIRouter, HTTPException, Request

from admin.runtime_state import RuntimeState
from connectors.teams_client import TeamsClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/teams", tags=["teams"])

# 将在 main.py 中通过 set_teams_trigger 注入
_trigger_fn: Callable[[str], Coroutine[Any, Any, None]] | None = None
_webhook_secret: str = ""


def set_teams_trigger(
    fn: Callable[[str], Coroutine[Any, Any, None]],
    secret: str = "",
) -> None:
    """注入分析触发函数和 Outgoing Webhook secret。"""
    global _trigger_fn, _webhook_secret
    _trigger_fn = fn
    _webhook_secret = secret


@router.post("/webhook")
async def handle_teams_webhook(request: Request) -> dict[str, str]:
    """
    处理 Teams Outgoing Webhook 回调。

    Teams 在频道中 @mention bot 时 POST JSON 到此端点。
    必须在 5 秒内响应，因此分析任务通过 asyncio.create_task 异步触发。

    响应格式: {"type": "message", "text": "..."}
    """
    body = await request.body()

    # HMAC 验证 (如果配置了 secret)
    if _webhook_secret:
        auth_header = request.headers.get("Authorization", "")
        if not TeamsClient.verify_hmac(body, auth_header, _webhook_secret):
            raise HTTPException(status_code=401, detail="HMAC verification failed")

    payload = await request.json()
    text = payload.get("text", "")

    parsed = TeamsClient.parse_command(text)
    if parsed is None:
        return _teams_response(
            "未识别的命令。支持的命令:\n"
            "- **analyze BUG-123** — 触发 Bug 分析\n"
            "- **status** — 查看系统状态\n"
            "- **help** — 显示帮助"
        )

    command, argument = parsed

    if command == "help":
        return _teams_response(
            "Bug Analysis Agent 命令:\n"
            "- **analyze BUG-123** — 触发指定 Bug 的自动分析\n"
            "- **status** — 查看守护进程状态\n"
            "- **help** — 显示此帮助信息"
        )

    if command == "status":
        return _handle_status()

    if command == "analyze":
        return await _handle_analyze(argument)

    return _teams_response(f"未知命令: {command}")


@router.get("/health")
async def teams_health() -> dict[str, str]:
    """Teams 路由健康检查。"""
    return {"status": "ok", "service": "teams-webhook"}


# ── 命令处理 ──


def _handle_status() -> dict[str, str]:
    """返回系统运行状态。"""
    try:
        rt = RuntimeState.get()
        status = rt.get_status()
        text = (
            f"守护进程状态:\n"
            f"- 模式: {status.mode}\n"
            f"- 运行中: {'是' if status.is_running else '否'}\n"
            f"- 已分析: {status.total_analyzed}\n"
            f"- 成功: {status.total_success}\n"
            f"- 失败: {status.total_failed}\n"
            f"- 启动时间: {status.uptime}"
        )
    except Exception as e:
        text = f"获取状态失败: {e}"
    return _teams_response(text)


async def _handle_analyze(argument: str) -> dict[str, str]:
    """触发 Bug 分析。"""
    if not argument:
        return _teams_response("请指定 Bug Key，例如: analyze BUG-123")

    bug_key = argument.split()[0].upper()

    if _trigger_fn is None:
        return _teams_response("分析服务未就绪，请稍后重试")

    # 异步触发分析 (不等待完成，确保 5 秒内响应)
    asyncio.create_task(_trigger_fn(bug_key))
    logger.info(f"Teams 触发分析: {bug_key}")

    return _teams_response(
        f"已触发 **{bug_key}** 的分析，完成后将发送结果通知。"
    )


def _teams_response(text: str) -> dict[str, str]:
    """构造 Teams Outgoing Webhook 响应。"""
    return {"type": "message", "text": text}
