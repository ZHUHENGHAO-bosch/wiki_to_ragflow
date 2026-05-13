"""
admin/admin_router.py — 管理 API 路由

提供系统配置查看/修改、运行状态查询、分析历史查询等端点。
"""
from __future__ import annotations

import logging
from typing import Any, Callable

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from admin.runtime_state import (
    AnalysisRecord,
    DaemonStatus,
    ErrorRecord,
    RuntimeState,
)
from config import AppConfig
from connectors.bug_tracker import BugTrackerClient
from services.confluence_downloader import ConfluenceDownloader

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

# 将在 main.py 中通过 init_admin_router 注入
_config: AppConfig | None = None
_config_updater: Callable[[str, list[str]], bool] | None = None
_confluence_downloader: ConfluenceDownloader | None = None
_bug_tracker: BugTrackerClient | None = None


# ── 安全可编辑字段白名单 ──

MUTABLE_FIELDS: dict[str, set[str]] = {
    "watcher": {"polling_interval_seconds", "jql_filter"},
    "writer": {"analyzed_label", "auto_create_related_bugs", "notify_webhook"},
    "llm": {"max_tokens", "temperature"},
    "git_repos": {"search_extensions", "recent_commit_weeks"},
    "confluence": {
        "max_concurrent_requests",
        "default_output_dir",
        "download_attachments",
        "max_depth",
        "timeout",
        "save_format",
    },
    "teams": {"enabled", "notify_on_analysis_complete", "timeout"},
    "rtc": {"polling_interval_seconds", "saved_query_id", "analyzed_tag", "verify_ssl"},
}

# 永不暴露的字段
SECRET_FIELDS: set[str] = {
    "api_token",
    "password",
    "api_key",
    "webhook_secret",
    "outgoing_webhook_secret",
}


def init_admin_router(
    config: AppConfig,
    config_updater: Callable[[str, list[str]], bool] | None = None,
    confluence_downloader: ConfluenceDownloader | None = None,
    bug_tracker: BugTrackerClient | None = None,
) -> None:
    """注入配置对象、更新回调、Confluence 下载器和 Bug 跟踪器。"""
    global _config, _config_updater, _confluence_downloader, _bug_tracker
    _config = config
    _config_updater = config_updater
    _confluence_downloader = confluence_downloader
    _bug_tracker = bug_tracker


# ── 请求/响应模型 ──


class ConfigUpdateRequest(BaseModel):
    """配置更新请求。"""

    section: str  # e.g. "watcher", "writer", "llm"
    updates: dict[str, Any]  # e.g. {"polling_interval_seconds": 120}


class ConfigUpdateResponse(BaseModel):
    """配置更新响应。"""

    updated_fields: list[str]
    rejected_fields: list[str] = Field(default_factory=list)
    restart_required: bool = False
    message: str = ""


class HistoryResponse(BaseModel):
    """分析历史响应。"""

    total: int
    records: list[AnalysisRecord]


class ErrorsResponse(BaseModel):
    """错误日志响应。"""

    total: int
    errors: list[ErrorRecord]


# ── 端点: 系统状态 ──


@router.get("/status", response_model=DaemonStatus)
async def get_status() -> DaemonStatus:
    """获取守护进程当前运行状态。"""
    return RuntimeState.get().get_status()


# ── 端点: 分析历史 ──


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    limit: int = Query(50, ge=1, le=200, description="返回记录数"),
    status: str | None = Query(
        None, description="按状态过滤: success|partial|failed"
    ),
) -> HistoryResponse:
    """查询分析历史记录。"""
    state = RuntimeState.get()
    records = state.get_history(limit=limit, status=status)
    return HistoryResponse(total=len(records), records=records)


# ── 端点: 错误日志 ──


@router.get("/errors", response_model=ErrorsResponse)
async def get_errors(
    limit: int = Query(50, ge=1, le=100, description="返回记录数"),
) -> ErrorsResponse:
    """查询最近的错误日志。"""
    state = RuntimeState.get()
    errors = state.get_errors(limit=limit)
    return ErrorsResponse(total=len(errors), errors=errors)


# ── 端点: 配置查看 ──


@router.get("/config")
async def get_config() -> dict[str, Any]:
    """
    获取当前配置 (敏感字段已脱敏)。

    密码、Token 等字段显示为 "***"。
    """
    if _config is None:
        raise HTTPException(status_code=500, detail="配置未初始化")

    raw = _config.model_dump()
    return _redact_secrets(raw)


@router.get("/config/mutable-fields")
async def get_mutable_fields() -> dict[str, list[str]]:
    """返回所有可运行时修改的配置字段。"""
    return {section: sorted(fields) for section, fields in MUTABLE_FIELDS.items()}


@router.get("/config/{section}")
async def get_config_section(section: str) -> dict[str, Any]:
    """获取指定配置段 (敏感字段已脱敏)。"""
    if _config is None:
        raise HTTPException(status_code=500, detail="配置未初始化")

    if not hasattr(_config, section):
        raise HTTPException(
            status_code=404, detail=f"配置段 '{section}' 不存在"
        )

    sub = getattr(_config, section)
    raw = sub.model_dump() if hasattr(sub, "model_dump") else sub
    return _redact_secrets(raw) if isinstance(raw, dict) else raw


# ── 端点: 配置修改 ──


@router.put("/config", response_model=ConfigUpdateResponse)
async def update_config(req: ConfigUpdateRequest) -> ConfigUpdateResponse:
    """
    运行时更新配置 (仅限白名单字段)。

    - 连接地址、认证信息等不可修改 (需重启)
    - 轮询间隔、JQL、LLM 参数等可热更新
    """
    if _config is None:
        raise HTTPException(status_code=500, detail="配置未初始化")

    allowed = MUTABLE_FIELDS.get(req.section)
    if allowed is None:
        raise HTTPException(
            status_code=400,
            detail=f"配置段 '{req.section}' 不允许运行时修改",
        )

    if not hasattr(_config, req.section):
        raise HTTPException(
            status_code=404,
            detail=f"配置段 '{req.section}' 不存在",
        )

    sub_config = getattr(_config, req.section)
    updated: list[str] = []
    rejected: list[str] = []

    for key, value in req.updates.items():
        if key not in allowed:
            rejected.append(key)
            continue
        if key in SECRET_FIELDS:
            rejected.append(key)
            continue
        if not hasattr(sub_config, key):
            rejected.append(key)
            continue

        setattr(sub_config, key, value)
        updated.append(key)
        logger.info(f"配置已更新: {req.section}.{key} = {value}")

    # 调用更新回调 (如需要热重载客户端)
    restart_required = False
    if _config_updater and updated:
        try:
            restart_required = _config_updater(req.section, updated)
        except Exception as e:
            logger.warning(f"配置更新回调失败: {e}")

    message = ""
    if rejected:
        message = f"以下字段不允许运行时修改: {', '.join(rejected)}"

    return ConfigUpdateResponse(
        updated_fields=updated,
        rejected_fields=rejected,
        restart_required=restart_required,
        message=message,
    )


# ── Confluence 下载端点 ──


class ConfluenceDownloadRequest(BaseModel):
    """Confluence 下载请求。"""

    page_url: str = ""
    page_id: str = ""
    output_dir: str = ""
    max_depth: int | None = None
    download_attachments: bool | None = None
    save_format: str | None = None  # "html" or "pdf"
    resume: bool = True
    output_filename: str | None = None  # 自定义输出文件名


class ConfluenceDownloadResponse(BaseModel):
    """Confluence 下载响应。"""

    task_id: str
    message: str


@router.post("/confluence/download", response_model=ConfluenceDownloadResponse)
async def start_confluence_download(
    req: ConfluenceDownloadRequest,
) -> ConfluenceDownloadResponse:
    """启动 Confluence 页面树下载任务。"""
    if _confluence_downloader is None:
        raise HTTPException(
            status_code=503,
            detail="Confluence 未配置或未初始化",
        )

    try:
        task_id = await _confluence_downloader.start_download(
            page_url=req.page_url or None,
            page_id=req.page_id or None,
            output_dir=req.output_dir or None,
            max_depth=req.max_depth,
            download_attachments=req.download_attachments,
            save_format=req.save_format,
            resume=req.resume,
            output_filename=req.output_filename,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ConfluenceDownloadResponse(
        task_id=task_id,
        message=f"Download started: {task_id}",
    )


@router.get("/confluence/progress")
async def get_confluence_progress() -> dict[str, Any]:
    """获取所有 Confluence 下载任务的进度。"""
    if _confluence_downloader is None:
        return {"tasks": []}
    return {"tasks": _confluence_downloader.list_tasks()}


@router.get("/confluence/progress/{task_id}")
async def get_confluence_task_progress(task_id: str) -> dict[str, Any]:
    """获取单个下载任务的进度。"""
    if _confluence_downloader is None:
        raise HTTPException(status_code=503, detail="Confluence 未配置")

    progress = _confluence_downloader.get_progress(task_id)
    if progress is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return progress


@router.post("/confluence/cancel/{task_id}")
async def cancel_confluence_download(task_id: str) -> dict[str, str]:
    """取消正在运行的下载任务。"""
    if _confluence_downloader is None:
        raise HTTPException(status_code=503, detail="Confluence 未配置")

    if _confluence_downloader.cancel_download(task_id):
        return {"message": f"Cancellation requested for {task_id}"}
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


# ── 附件下载端点 ──


class AttachmentItem(BaseModel):
    """附件元数据。"""

    name: str
    url: str = ""
    attachment_id: str = ""


class AttachmentListResponse(BaseModel):
    """附件列表响应。"""

    bug_key: str
    total: int
    attachments: list[AttachmentItem]


class AttachmentDownloadRequest(BaseModel):
    """附件下载请求。"""

    output_dir: str = ""  # 自定义输出目录 (空则使用默认)
    attachment_ids: list[str] = Field(
        default_factory=list,
        description="指定要下载的附件 ID 列表 (空则下载全部)",
    )


class AttachmentDownloadResult(BaseModel):
    """单个附件下载结果。"""

    name: str
    path: str = ""
    success: bool
    error: str = ""


class AttachmentDownloadResponse(BaseModel):
    """附件下载响应。"""

    bug_key: str
    total: int
    downloaded: int
    failed: int
    results: list[AttachmentDownloadResult]


@router.get("/bug/{bug_key}/attachments", response_model=AttachmentListResponse)
async def list_attachments(bug_key: str) -> AttachmentListResponse:
    """获取 Bug/WorkItem 的附件列表 (仅元数据，不下载)。"""
    if _bug_tracker is None:
        raise HTTPException(
            status_code=503,
            detail="Bug 跟踪器未配置或未初始化",
        )

    try:
        attachments = await _bug_tracker.get_attachments(bug_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取附件列表失败: {e}")

    items = [
        AttachmentItem(
            name=att.get("name", ""),
            url=att.get("url", ""),
            attachment_id=att.get("attachment_id", ""),
        )
        for att in attachments
    ]
    return AttachmentListResponse(
        bug_key=bug_key, total=len(items), attachments=items,
    )


@router.post(
    "/bug/{bug_key}/attachments/download",
    response_model=AttachmentDownloadResponse,
)
async def download_attachments(
    bug_key: str,
    req: AttachmentDownloadRequest | None = None,
) -> AttachmentDownloadResponse:
    """下载 Bug/WorkItem 的附件。

    - 不指定 attachment_ids 则下载全部附件
    - 指定 attachment_ids 则仅下载对应附件
    - 已存在的同名文件会被跳过
    """
    if _bug_tracker is None:
        raise HTTPException(
            status_code=503,
            detail="Bug 跟踪器未配置或未初始化",
        )

    body = req or AttachmentDownloadRequest()

    try:
        # 获取附件列表
        all_attachments = await _bug_tracker.get_attachments(bug_key)

        # 按 ID 过滤
        if body.attachment_ids:
            id_set = set(body.attachment_ids)
            target_attachments = [
                att for att in all_attachments
                if att.get("attachment_id", "") in id_set
            ]
        else:
            target_attachments = all_attachments

        if not target_attachments:
            return AttachmentDownloadResponse(
                bug_key=bug_key, total=0, downloaded=0, failed=0, results=[],
            )

        # 确定输出目录
        output_dir = body.output_dir or None

        # 使用 download_all_attachments 的逻辑逐个下载
        import os
        from pathlib import Path
        if hasattr(_bug_tracker, '_config'):
            default_base = getattr(_bug_tracker._config, 'attachments_output_dir', './attachments')
        else:
            default_base = './attachments'

        base_dir = Path(output_dir) if output_dir else Path(default_base) / str(bug_key)

        results: list[AttachmentDownloadResult] = []
        for att in target_attachments:
            name = att.get("name", "unnamed")
            att_url = att.get("url", "")
            # 简单文件名清理
            safe_name = name
            if hasattr(_bug_tracker, '_sanitize_filename'):
                safe_name = _bug_tracker._sanitize_filename(name)
            save_path = str(base_dir / safe_name)

            # 跳过已存在
            if os.path.exists(save_path):
                results.append(AttachmentDownloadResult(
                    name=name, path=save_path, success=True,
                ))
                continue

            try:
                path = await _bug_tracker.download_attachment(att_url, save_path)
                results.append(AttachmentDownloadResult(
                    name=name, path=path, success=True,
                ))
            except Exception as e:
                logger.error("下载附件 '%s' 失败: %s", name, e)
                results.append(AttachmentDownloadResult(
                    name=name, path=save_path, success=False, error=str(e),
                ))

        downloaded = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)

        return AttachmentDownloadResponse(
            bug_key=bug_key,
            total=len(results),
            downloaded=downloaded,
            failed=failed,
            results=results,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"附件下载失败: {e}")


# ── 内部工具 ──


def _redact_secrets(data: dict[str, Any]) -> dict[str, Any]:
    """递归脱敏敏感字段。"""
    result: dict[str, Any] = {}
    for key, value in data.items():
        if key in SECRET_FIELDS:
            result[key] = "***"
        elif isinstance(value, dict):
            result[key] = _redact_secrets(value)
        else:
            result[key] = value
    return result
