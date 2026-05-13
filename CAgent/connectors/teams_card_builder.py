"""
connectors/teams_card_builder.py — Adaptive Card 构建工具

替代 O365 MessageCard，使用 Microsoft 推荐的 Adaptive Card 格式。
支持分析结果、进度、审批、错误等多种卡片模板。
"""
from __future__ import annotations

from typing import Any


# Adaptive Card schema 版本
SCHEMA = "http://adaptivecards.io/schemas/adaptive-card.json"
CARD_VERSION = "1.4"


def _base_card() -> dict[str, Any]:
    """创建 Adaptive Card 基础结构。"""
    return {
        "type": "AdaptiveCard",
        "$schema": SCHEMA,
        "version": CARD_VERSION,
        "body": [],
        "actions": [],
    }


def _header_block(text: str, color: str = "default") -> dict[str, Any]:
    """标题块。"""
    return {
        "type": "TextBlock",
        "text": text,
        "size": "large",
        "weight": "bolder",
        "color": color,
        "wrap": True,
    }


def _fact_set(facts: list[tuple[str, str]]) -> dict[str, Any]:
    """事实表（key-value 列表）。"""
    return {
        "type": "FactSet",
        "facts": [{"title": k, "value": v} for k, v in facts if v],
    }


def _text_block(text: str, **kwargs: Any) -> dict[str, Any]:
    """文本块。"""
    block: dict[str, Any] = {
        "type": "TextBlock",
        "text": text,
        "wrap": True,
    }
    block.update(kwargs)
    return block


# ── 状态颜色映射 ──

_STATUS_COLOR: dict[str, str] = {
    "success": "good",
    "partial": "warning",
    "failed": "attention",
}

_STATUS_TEXT: dict[str, str] = {
    "success": "分析完成",
    "partial": "部分完成",
    "failed": "分析失败",
}

_STATUS_EMOJI: dict[str, str] = {
    "success": "\u2705",
    "partial": "\u26a0\ufe0f",
    "failed": "\u274c",
}


def build_analysis_result_card(state: dict[str, Any]) -> dict[str, Any]:
    """
    构建分析结果通知卡片。

    Args:
        state: AnalysisState 字典，包含 bug_key, status, root_cause 等字段。
    """
    bug_key = state.get("bug_key", "UNKNOWN")
    status = state.get("status", "unknown")
    root_cause = state.get("root_cause")
    duration = state.get("analysis_duration", 0.0)
    errors = state.get("errors", [])

    status_text = _STATUS_TEXT.get(status, status)
    status_color = _STATUS_COLOR.get(status, "default")
    emoji = _STATUS_EMOJI.get(status, "")

    card = _base_card()

    # 标题
    card["body"].append(
        _header_block(f"{emoji} Bug 分析: {bug_key} — {status_text}", status_color)
    )

    # 基础信息
    facts: list[tuple[str, str]] = [
        ("Bug", bug_key),
        ("状态", status_text),
    ]

    if root_cause:
        level = getattr(root_cause, "level", None)
        if level:
            level_str = level.value if hasattr(level, "value") else str(level)
            facts.append(("根因层级", level_str))

        summary = getattr(root_cause, "summary", None)
        if summary:
            facts.append(("根因摘要", summary))

        fix_suggestions = getattr(root_cause, "fix_suggestions", None)
        if fix_suggestions:
            fix_text = "; ".join(
                f"{fs.label}: {fs.description}" for fs in fix_suggestions[:3]
            )
            facts.append(("修复建议", fix_text))

    facts.append(("耗时", f"{duration:.1f}s"))

    card["body"].append(_fact_set(facts))

    # 错误信息
    if errors:
        card["body"].append(_text_block("**分析过程说明**", spacing="medium"))
        error_lines = "\n".join(f"- {e}" for e in errors[:5])
        card["body"].append(_text_block(error_lines, size="small"))

    # 根因详情（折叠）
    if root_cause:
        detail = getattr(root_cause, "detail", None)
        if detail:
            card["body"].append(
                _text_block(
                    f"**根因详情**: {detail[:500]}",
                    spacing="medium",
                    isSubtle=True,
                )
            )

    return card


def build_progress_card(
    bug_key: str,
    step: int,
    total_steps: int,
    step_name: str = "",
    completed_steps: list[str] | None = None,
) -> dict[str, Any]:
    """
    构建分析进度卡片。

    Args:
        bug_key: Bug 标识
        step: 当前步骤编号 (1-based)
        total_steps: 总步骤数
        step_name: 当前步骤名称
        completed_steps: 已完成步骤名称列表
    """
    card = _base_card()

    card["body"].append(
        _header_block(f"\u23f3 {bug_key} 分析进度 ({step}/{total_steps})")
    )

    # 已完成步骤
    if completed_steps:
        lines = [f"\u2705 {s}" for s in completed_steps]
        if step_name:
            lines.append(f"\u23f3 {step_name}...")
        card["body"].append(_text_block("\n".join(lines)))

    # 进度条（用文本模拟）
    filled = step
    empty = total_steps - step
    bar = "\u2588" * filled + "\u2591" * empty
    card["body"].append(
        _text_block(f"`{bar}` {step}/{total_steps}", isSubtle=True)
    )

    return card


def build_approval_card(
    bug_key: str,
    summary: str,
    root_cause_level: str = "",
    timeout_seconds: float = 3600.0,
) -> dict[str, Any]:
    """
    构建审批确认卡片。

    Args:
        bug_key: Bug 标识
        summary: 分析摘要
        root_cause_level: 根因层级
        timeout_seconds: 审批超时时间
    """
    card = _base_card()

    card["body"].append(
        _header_block(f"\U0001f4cb {bug_key} — 等待审批确认")
    )

    facts: list[tuple[str, str]] = [
        ("Bug", bug_key),
        ("根因层级", root_cause_level),
        ("分析摘要", summary),
        ("超时", f"{timeout_seconds / 60:.0f} 分钟后自动处理"),
    ]
    card["body"].append(_fact_set(facts))

    card["body"].append(
        _text_block(
            "请回复以下命令确认:\n"
            f"- `approve {bug_key}` — 确认并写入报告\n"
            f"- `reject {bug_key}` — 拒绝写入",
            spacing="medium",
        )
    )

    return card


def build_error_card(
    bug_key: str,
    errors: list[str],
    context: str = "",
) -> dict[str, Any]:
    """
    构建错误通知卡片。

    Args:
        bug_key: Bug 标识
        errors: 错误消息列表
        context: 额外上下文信息
    """
    card = _base_card()

    card["body"].append(
        _header_block(f"\u274c {bug_key} — 分析错误", "attention")
    )

    if context:
        card["body"].append(_text_block(context))

    if errors:
        error_lines = "\n".join(f"- {e}" for e in errors[:10])
        card["body"].append(_text_block(error_lines))

    return card


def build_help_card() -> dict[str, Any]:
    """构建帮助信息卡片。"""
    card = _base_card()

    card["body"].append(_header_block("CAgent 命令帮助"))

    commands = [
        ("analyze <key>", "触发 Bug 分析"),
        ("status", "查看系统状态"),
        ("detail <key>", "查看分析详情"),
        ("history [n]", "最近 n 条分析记录"),
        ("reanalyze <key>", "重新分析"),
        ("approve <key>", "审批确认"),
        ("reject <key>", "拒绝审批"),
        ("help", "显示此帮助"),
    ]
    card["body"].append(_fact_set(commands))

    return card


def build_status_card(
    mode: str,
    is_running: bool,
    total_analyzed: int,
    total_success: int,
    total_failed: int,
    uptime: str = "",
    active_analyses: list[str] | None = None,
) -> dict[str, Any]:
    """构建系统状态卡片。"""
    card = _base_card()

    card["body"].append(_header_block("\U0001f4ca CAgent 守护进程状态"))

    facts: list[tuple[str, str]] = [
        ("模式", mode),
        ("运行中", "是" if is_running else "否"),
        ("已分析", str(total_analyzed)),
        ("成功", str(total_success)),
        ("失败", str(total_failed)),
        ("运行时长", uptime),
    ]
    card["body"].append(_fact_set(facts))

    if active_analyses:
        card["body"].append(
            _text_block(
                "**正在分析**: " + ", ".join(active_analyses),
                spacing="medium",
            )
        )

    return card


def build_detail_card(record: dict[str, Any]) -> dict[str, Any]:
    """构建分析详情卡片。"""
    card = _base_card()

    bug_key = record.get("bug_key", "UNKNOWN")
    card["body"].append(_header_block(f"\U0001f50d {bug_key} 分析详情"))

    facts: list[tuple[str, str]] = [
        ("Bug", bug_key),
        ("状态", record.get("status", "unknown")),
        ("根因层级", record.get("root_cause_level", "N/A")),
        ("开始时间", record.get("started_at", "")),
        ("完成时间", record.get("finished_at", "")),
        ("耗时", f"{record.get('duration_seconds', 0):.1f}s"),
    ]
    card["body"].append(_fact_set(facts))

    error_summary = record.get("error_summary")
    if error_summary:
        card["body"].append(
            _text_block(f"**错误**: {error_summary}", color="attention")
        )

    return card


def build_history_card(records: list[dict[str, Any]]) -> dict[str, Any]:
    """构建分析历史卡片。"""
    card = _base_card()

    card["body"].append(_header_block(f"\U0001f4dc 最近 {len(records)} 条分析记录"))

    if not records:
        card["body"].append(_text_block("暂无分析记录"))
        return card

    for r in records:
        emoji = _STATUS_EMOJI.get(r.get("status", ""), "")
        line = f"{emoji} **{r.get('bug_key', '?')}** — {r.get('status', '?')}"
        root_level = r.get("root_cause_level")
        if root_level:
            line += f" ({root_level})"
        duration = r.get("duration_seconds", 0)
        if duration:
            line += f" [{duration:.1f}s]"
        card["body"].append(_text_block(line))

    return card


def wrap_for_workflow_webhook(card: dict[str, Any]) -> dict[str, Any]:
    """
    将 Adaptive Card 包装为 Power Automate Workflow Webhook payload。

    Workflow Webhook 要求的格式与 Incoming Webhook 不同。
    """
    return {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card,
            }
        ],
    }


def wrap_for_graph_api(card: dict[str, Any], text: str = "") -> dict[str, Any]:
    """
    将 Adaptive Card 包装为 Graph API chatMessage payload。

    用于 POST /teams/{id}/channels/{id}/messages。
    """
    return {
        "body": {
            "contentType": "html",
            "content": text or "<attachment id=\"card\"></attachment>",
        },
        "attachments": [
            {
                "id": "card",
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card,
            }
        ],
    }
