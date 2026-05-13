"""
admin/runtime_state.py — 运行时状态追踪

提供守护进程运行状态、分析历史记录、错误日志的内存存储。
使用固定大小 deque 防止内存无限增长。
"""
from __future__ import annotations

import threading
import time
from collections import deque
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DaemonMode(str, Enum):
    """守护进程运行模式。"""

    WEBHOOK = "webhook"
    POLLING = "polling"
    ONCE = "once"


class AnalysisRecord(BaseModel):
    """单次分析的历史记录。"""

    bug_key: str
    status: str = "running"  # running | success | partial | failed
    started_at: datetime
    finished_at: datetime | None = None
    duration_seconds: float = 0.0
    root_cause_level: str | None = None
    error_summary: str | None = None


class ErrorRecord(BaseModel):
    """错误日志记录。"""

    timestamp: datetime
    source: str  # 来源模块 (e.g. "poller", "webhook", "analysis")
    message: str
    bug_key: str | None = None


class DaemonStatus(BaseModel):
    """守护进程当前状态快照。"""

    mode: DaemonMode
    started_at: datetime
    uptime_seconds: float
    is_healthy: bool = True
    active_analyses: list[str] = Field(default_factory=list)
    total_analyzed: int = 0
    total_success: int = 0
    total_failed: int = 0
    poller_running: bool = False
    poller_processed_count: int = 0


class RuntimeState:
    """
    全局运行时状态 (线程安全单例)。

    分析历史和错误日志使用 deque(maxlen=N) 实现环形缓冲区，
    无需数据库，自动淘汰旧记录。
    """

    _instance: RuntimeState | None = None
    _lock = threading.Lock()

    MAX_HISTORY: int = 200
    MAX_ERRORS: int = 100
    MAX_DOWNLOADS: int = 50

    def __init__(self) -> None:
        self._mode: DaemonMode = DaemonMode.WEBHOOK
        self._started_at: float = time.time()
        self._history: deque[AnalysisRecord] = deque(maxlen=self.MAX_HISTORY)
        self._errors: deque[ErrorRecord] = deque(maxlen=self.MAX_ERRORS)
        self._download_history: deque[dict[str, Any]] = deque(maxlen=self.MAX_DOWNLOADS)
        self._active: dict[str, AnalysisRecord] = {}  # bug_key -> record
        self._total_analyzed: int = 0
        self._total_success: int = 0
        self._total_failed: int = 0
        self._poller_running: bool = False
        self._poller_processed_count: int = 0
        self._lock_state = threading.Lock()

    @classmethod
    def get(cls) -> RuntimeState:
        """获取或创建单例实例。"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """重置单例 (测试用)。"""
        with cls._lock:
            cls._instance = None

    def set_mode(self, mode: DaemonMode) -> None:
        """设置守护进程运行模式。"""
        self._mode = mode
        self._started_at = time.time()

    def record_start(self, bug_key: str) -> None:
        """记录分析开始。"""
        with self._lock_state:
            record = AnalysisRecord(
                bug_key=bug_key,
                status="running",
                started_at=datetime.now(),
            )
            self._active[bug_key] = record

    def record_finish(
        self,
        bug_key: str,
        status: str,
        root_cause_level: str | None = None,
        error_summary: str | None = None,
    ) -> None:
        """记录分析结束。"""
        with self._lock_state:
            record = self._active.pop(bug_key, None)
            if record is None:
                record = AnalysisRecord(
                    bug_key=bug_key,
                    started_at=datetime.now(),
                )
            record.status = status
            record.finished_at = datetime.now()
            record.duration_seconds = (
                record.finished_at - record.started_at
            ).total_seconds()
            record.root_cause_level = root_cause_level
            record.error_summary = error_summary

            self._history.append(record)
            self._total_analyzed += 1
            if status == "success":
                self._total_success += 1
            elif status == "failed":
                self._total_failed += 1

    def record_error(
        self, source: str, message: str, bug_key: str | None = None
    ) -> None:
        """记录一条错误。"""
        with self._lock_state:
            self._errors.append(
                ErrorRecord(
                    timestamp=datetime.now(),
                    source=source,
                    message=message,
                    bug_key=bug_key,
                )
            )

    def set_poller_status(self, running: bool, processed: int = 0) -> None:
        """更新 Poller 状态指标。"""
        self._poller_running = running
        self._poller_processed_count = processed

    def get_status(self) -> DaemonStatus:
        """生成当前状态快照。"""
        with self._lock_state:
            return DaemonStatus(
                mode=self._mode,
                started_at=datetime.fromtimestamp(self._started_at),
                uptime_seconds=time.time() - self._started_at,
                is_healthy=True,
                active_analyses=list(self._active.keys()),
                total_analyzed=self._total_analyzed,
                total_success=self._total_success,
                total_failed=self._total_failed,
                poller_running=self._poller_running,
                poller_processed_count=self._poller_processed_count,
            )

    def get_history(
        self, limit: int = 50, status: str | None = None
    ) -> list[AnalysisRecord]:
        """获取分析历史 (最新在前)。"""
        with self._lock_state:
            items = list(reversed(self._history))
            if status:
                items = [r for r in items if r.status == status]
            return items[:limit]

    def get_errors(self, limit: int = 50) -> list[ErrorRecord]:
        """获取错误日志 (最新在前)。"""
        with self._lock_state:
            return list(reversed(self._errors))[:limit]

    # ── Confluence 下载任务跟踪 ──

    def record_download(self, task_data: dict[str, Any]) -> None:
        """记录一次已完成的 Confluence 下载任务。"""
        with self._lock_state:
            self._download_history.append(task_data)

    def get_downloads(self, limit: int = 20) -> list[dict[str, Any]]:
        """获取下载历史 (最新在前)。"""
        with self._lock_state:
            return list(reversed(self._download_history))[:limit]
