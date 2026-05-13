"""
connectors/report_formatter.py — 报告格式化策略

ReportFormatter Protocol + Jira Wiki / RTC HTML 两种实现。
从 write_report.py 中提取格式化逻辑，使 write_report 节点可用于两种系统。
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from state import AnalysisState

# 根因层级对应的颜色
LEVEL_COLORS: dict[str, str] = {
    "实现偏离": "Red",
    "实现遗漏": "Red",
    "需求遗漏": "Yellow",
    "需求歧义": "Yellow",
    "测试缺陷": "Blue",
    "回归引入": "Red",
}


@runtime_checkable
class ReportFormatter(Protocol):
    """报告格式化协议。"""

    def format_report(self, state: AnalysisState, status: str) -> str:
        ...


class JiraWikiFormatter:
    """Jira Wiki Markup 格式化器。"""

    def format_report(self, state: AnalysisState, status: str) -> str:
        lines: list[str] = []

        lines.append(
            "{panel:title=🤖 Bug Analysis Agent|borderColor=#003B71}"
        )
        lines.append("")

        # 分析状态
        if status == "success":
            status_markup = "{status:colour=Green|title=完成}"
        elif status == "partial":
            status_markup = "{status:colour=Yellow|title=部分完成}"
        else:
            status_markup = "{status:colour=Red|title=失败}"

        lines.append("h4. 分析状态")
        lines.append(status_markup)
        lines.append("")

        # 根因
        root_cause = state.get("root_cause")
        if root_cause:
            level_str = root_cause.level.value
            color = LEVEL_COLORS.get(level_str, "Gray")
            lines.append("h4. 根因层级")
            lines.append(f"{{status:colour={color}|title={level_str}}}")
            lines.append("")

            lines.append("h4. 根因定位")
            if root_cause.problem_location:
                lines.append(f"- 文件: {{{{{root_cause.problem_location}}}}}")
            lines.append(f"- 问题: {root_cause.summary}")
            if root_cause.detail:
                lines.append(f"- 详细: {root_cause.detail}")
            if root_cause.introducer:
                commit = root_cause.introducing_commit or "未知"
                lines.append(
                    f"- 引入者: {root_cause.introducer}, commit {commit}"
                )
            lines.append("")

            if root_cause.fix_suggestions:
                lines.append("h4. 修复建议")
                for fs in root_cause.fix_suggestions:
                    effort = f" ({fs.effort})" if fs.effort else ""
                    lines.append(f"- *{fs.label}*{effort}: {fs.description}")
                lines.append("")
        else:
            lines.append("h4. 根因分析")
            lines.append("未能完成自动分析，请人工排查。")
            lines.append("")

        # 关联需求
        requirements = state.get("requirements", [])
        if requirements:
            lines.append("h4. 关联需求")
            for req in requirements:
                link = f"[{req.req_id}|{req.url}]" if req.url else req.req_id
                lines.append(f"- {link}: {req.title}")
            lines.append("")

        # 影响范围
        impact = state.get("impact")
        if impact and impact.affected_items:
            lines.append("h4. 影响范围")
            lines.append("|| 模块 || 测试用例 || 风险 || 备注 ||")
            for item in impact.affected_items:
                tcs = ", ".join(item.related_test_cases[:5]) or "-"
                lines.append(
                    f"| {item.module_name} | {tcs} "
                    f"| {item.risk_level} | {item.note} |"
                )
            lines.append("")

        # 回归测试清单
        if impact and impact.regression_test_list:
            lines.append("h4. 回归测试清单")
            direct_tests = {
                tc.key for tc in state.get("test_cases", [])
            }
            for tc_id in impact.regression_test_list:
                tag = "(直接关联)" if tc_id in direct_tests else "(影响扩散)"
                lines.append(f"- {tc_id} {tag}")
            lines.append("")

        # 错误/警告
        errors = state.get("errors", [])
        if errors:
            lines.append("h4. 分析过程说明")
            for err in errors:
                lines.append(f"- {err}")
            lines.append("")

        # 耗时
        duration = state.get("analysis_duration", 0.0)
        lines.append(f"分析耗时: {duration:.1f}s")
        lines.append("{panel}")

        return "\n".join(lines)


class RtcHtmlFormatter:
    """RTC HTML 格式化器 (用于 RTC WorkItem 评论)。"""

    def format_report(self, state: AnalysisState, status: str) -> str:
        lines: list[str] = []

        lines.append('<div style="border:2px solid #003B71;padding:10px;margin:5px 0;">')
        lines.append("<h3>🤖 Bug Analysis Agent</h3>")

        # 分析状态
        color_map = {"success": "green", "partial": "orange", "failed": "red"}
        color = color_map.get(status, "gray")
        label_map = {"success": "完成", "partial": "部分完成", "failed": "失败"}
        label = label_map.get(status, status)
        lines.append(f'<h4>分析状态</h4><span style="color:{color};font-weight:bold;">{label}</span>')

        # 根因
        root_cause = state.get("root_cause")
        if root_cause:
            level_str = root_cause.level.value
            level_color = {"Red": "red", "Yellow": "orange", "Blue": "blue"}.get(
                LEVEL_COLORS.get(level_str, "Gray"), "gray"
            )
            lines.append(f'<h4>根因层级</h4><span style="color:{level_color};font-weight:bold;">{level_str}</span>')

            lines.append("<h4>根因定位</h4><ul>")
            if root_cause.problem_location:
                lines.append(f"<li>文件: <code>{root_cause.problem_location}</code></li>")
            lines.append(f"<li>问题: {root_cause.summary}</li>")
            if root_cause.detail:
                lines.append(f"<li>详细: {root_cause.detail}</li>")
            if root_cause.introducer:
                commit = root_cause.introducing_commit or "未知"
                lines.append(f"<li>引入者: {root_cause.introducer}, commit {commit}</li>")
            lines.append("</ul>")

            if root_cause.fix_suggestions:
                lines.append("<h4>修复建议</h4><ul>")
                for fs in root_cause.fix_suggestions:
                    effort = f" ({fs.effort})" if fs.effort else ""
                    lines.append(f"<li><b>{fs.label}</b>{effort}: {fs.description}</li>")
                lines.append("</ul>")
        else:
            lines.append("<h4>根因分析</h4><p>未能完成自动分析，请人工排查。</p>")

        # 关联需求
        requirements = state.get("requirements", [])
        if requirements:
            lines.append("<h4>关联需求</h4><ul>")
            for req in requirements:
                if req.url:
                    lines.append(f'<li><a href="{req.url}">{req.req_id}</a>: {req.title}</li>')
                else:
                    lines.append(f"<li>{req.req_id}: {req.title}</li>")
            lines.append("</ul>")

        # 影响范围
        impact = state.get("impact")
        if impact and impact.affected_items:
            lines.append("<h4>影响范围</h4>")
            lines.append('<table border="1" cellpadding="4"><tr><th>模块</th><th>测试用例</th><th>风险</th><th>备注</th></tr>')
            for item in impact.affected_items:
                tcs = ", ".join(item.related_test_cases[:5]) or "-"
                lines.append(f"<tr><td>{item.module_name}</td><td>{tcs}</td><td>{item.risk_level}</td><td>{item.note}</td></tr>")
            lines.append("</table>")

        # 回归测试清单
        if impact and impact.regression_test_list:
            lines.append("<h4>回归测试清单</h4><ul>")
            direct_tests = {tc.key for tc in state.get("test_cases", [])}
            for tc_id in impact.regression_test_list:
                tag = "(直接关联)" if tc_id in direct_tests else "(影响扩散)"
                lines.append(f"<li>{tc_id} {tag}</li>")
            lines.append("</ul>")

        # 错误/警告
        errors = state.get("errors", [])
        if errors:
            lines.append("<h4>分析过程说明</h4><ul>")
            for err in errors:
                lines.append(f"<li>{err}</li>")
            lines.append("</ul>")

        # 耗时
        duration = state.get("analysis_duration", 0.0)
        lines.append(f"<p>分析耗时: {duration:.1f}s</p>")
        lines.append("</div>")

        return "\n".join(lines)
