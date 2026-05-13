"""
analyze_root_cause.py — Node 4: LLM 根因分析

输入 State 字段: bug_info, test_cases, requirements, code_info
输出 State 字段: root_cause
依赖: langchain-anthropic (ChatAnthropic)

这是唯一调用 LLM 的 Node。
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from langchain_anthropic import ChatAnthropic

from config import LlmConfig
from models import FixSuggestion, RootCauseLevel, RootCauseResult
from state import AnalysisState

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "root_cause.md"

# 中文 level 到枚举的映射
LEVEL_MAP: dict[str, RootCauseLevel] = {
    "实现偏离": RootCauseLevel.IMPLEMENTATION_DEVIATION,
    "实现遗漏": RootCauseLevel.IMPLEMENTATION_MISSING,
    "需求遗漏": RootCauseLevel.REQUIREMENT_MISSING,
    "需求歧义": RootCauseLevel.REQUIREMENT_AMBIGUITY,
    "测试缺陷": RootCauseLevel.TEST_DEFECT,
    "回归引入": RootCauseLevel.REGRESSION,
}

MAX_CODE_CHARS = 3000
MAX_REQ_CHARS = 1000


def create_analyze_root_cause_node(llm: ChatAnthropic, config: LlmConfig):

    prompt_template = ""
    if PROMPT_PATH.exists():
        prompt_template = PROMPT_PATH.read_text(encoding="utf-8")

    async def analyze_root_cause(state: AnalysisState) -> dict[str, Any]:
        logger.info("[Node 4] 开始 LLM 根因分析")

        prompt = _build_prompt(state, prompt_template)

        try:
            response = await llm.ainvoke(prompt)
            text = (
                response.content
                if isinstance(response.content, str)
                else str(response.content)
            )
            logger.debug(f"[Node 4] LLM 响应长度: {len(text)}")

            root_cause = _parse_response(text)
            logger.info(f"[Node 4] 根因层级: {root_cause.level.value}")
            return {"root_cause": root_cause}

        except Exception as e:
            logger.error(f"[Node 4] LLM 分析失败: {e}")
            return {
                "root_cause": None,
                "errors": state.get("errors", []) + [f"LLM 分析失败: {e}"],
            }

    return analyze_root_cause


def _build_prompt(state: AnalysisState, template: str) -> str:
    """填充 Prompt 模板，截断过长内容。"""
    bug_info = state.get("bug_info")
    test_cases = state.get("test_cases", [])
    requirements = state.get("requirements", [])
    code_info = state.get("code_info")

    # Bug 部分
    bug_key = state.get("bug_key", "")
    bug_desc = ""
    environment = ""
    priority = ""
    if bug_info:
        bug_desc = bug_info.description[:2000]
        environment = bug_info.environment
        priority = bug_info.priority

    # Test Case 部分
    tc_lines: list[str] = []
    for tc in test_cases:
        tc_lines.append(f"### {tc.key}: {tc.summary}")
        if tc.description:
            tc_lines.append(tc.description[:500])
        for i, step in enumerate(tc.steps, 1):
            tc_lines.append(f"  步骤 {i}: {step.step}")
            if step.expected:
                tc_lines.append(f"    期望: {step.expected}")
            if step.actual:
                tc_lines.append(f"    实际: {step.actual}")
    tc_section = "\n".join(tc_lines) if tc_lines else "无关联 Test Case"

    # 需求部分
    req_lines: list[str] = []
    for req in requirements:
        desc = req.description
        if len(desc) > MAX_REQ_CHARS:
            desc = desc[:MAX_REQ_CHARS] + "...(已截断)"
        req_lines.append(f"### {req.req_id}: {req.title}")
        if desc:
            req_lines.append(desc)
        if req.asil_level:
            req_lines.append(f"ASIL: {req.asil_level}")
    req_section = "\n".join(req_lines) if req_lines else "无关联需求"

    # 代码部分
    code_lines: list[str] = []
    total_chars = 0
    if code_info:
        for snippet in code_info.snippets:
            snippet_text = (
                f"### {snippet.file_path} "
                f"(Line {snippet.start_line}-{snippet.end_line})\n"
                f"```{snippet.language}\n{snippet.content}\n```"
            )
            if total_chars + len(snippet_text) > MAX_CODE_CHARS:
                code_lines.append("...(更多代码已省略)")
                break
            code_lines.append(snippet_text)
            total_chars += len(snippet_text)

        if code_info.recent_commits:
            code_lines.append("\n### 近期 Git 变更")
            for c in code_info.recent_commits[:5]:
                code_lines.append(
                    f"- {c.hash} ({c.author}, {c.date}): {c.message}"
                )

    code_section = "\n".join(code_lines) if code_lines else "未找到相关代码"

    # 填充模板
    if template:
        return (
            template.replace("{bug_key}", bug_key)
            .replace("{bug_description}", bug_desc)
            .replace("{environment}", environment)
            .replace("{priority}", priority)
            .replace("{test_cases_section}", tc_section)
            .replace("{requirements_section}", req_section)
            .replace("{code_section}", code_section)
        )

    # fallback: 直接拼接
    return (
        f"分析以下 Bug 的根因:\n\n"
        f"## Bug: {bug_key}\n{bug_desc}\n"
        f"环境: {environment}\n优先级: {priority}\n\n"
        f"## 测试用例\n{tc_section}\n\n"
        f"## 需求\n{req_section}\n\n"
        f"## 代码\n{code_section}\n\n"
        f"请按 JSON 格式返回根因分析结果。"
    )


def _parse_response(text: str) -> RootCauseResult:
    """解析 LLM JSON 响应。"""
    # 去除 markdown 代码块包裹
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # 尝试从文本中提取 JSON 块
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                return _fallback_parse(text)
        else:
            return _fallback_parse(text)

    # 解析 level
    level_str = data.get("level", "")
    level = LEVEL_MAP.get(level_str)
    if not level:
        # 模糊匹配
        level_lower = level_str.lower()
        for key, val in LEVEL_MAP.items():
            if key in level_lower or level_lower in key:
                level = val
                break
        if not level:
            level = RootCauseLevel.IMPLEMENTATION_DEVIATION

    # 解析 fix_suggestions
    suggestions: list[FixSuggestion] = []
    for s in data.get("fix_suggestions", []):
        if isinstance(s, dict):
            suggestions.append(
                FixSuggestion(
                    label=s.get("label", ""),
                    description=s.get("description", ""),
                    effort=s.get("effort", ""),
                )
            )

    return RootCauseResult(
        level=level,
        summary=data.get("summary", ""),
        detail=data.get("detail", ""),
        problem_location=data.get("problem_location", ""),
        introducer=data.get("introducer"),
        introducing_commit=data.get("introducing_commit"),
        fix_suggestions=suggestions,
    )


def _fallback_parse(text: str) -> RootCauseResult:
    """JSON 解析失败时从文本提取关键信息。"""
    logger.warning("[Node 4] JSON 解析失败，使用 fallback 解析")

    # 尝试识别 level
    level = RootCauseLevel.IMPLEMENTATION_DEVIATION
    for key, val in LEVEL_MAP.items():
        if key in text:
            level = val
            break

    return RootCauseResult(
        level=level,
        summary=text[:200] if text else "LLM 响应解析失败",
        detail=text[:1000] if text else "",
    )
