"""
graph.py — LangGraph 图定义

组装所有 Node，定义边和条件路由。
流程:
  read_bug → [read_testcase | search_testcase]
           → [read_requirement | search_requirement]
           → read_code → analyze_root_cause → analyze_impact → write_report

支持 Jira 和 RTC 双系统：通过 BugTrackerClient Protocol 抽象。
"""
from __future__ import annotations

import logging

from langchain_anthropic import ChatAnthropic
from langgraph.graph import END, StateGraph

from config import AppConfig, JiraConfig, RtcConfig
from connectors.bug_tracker import BugTrackerClient
from connectors.dng_client import DngClient
from connectors.git_client import GitClient
from connectors.report_formatter import ReportFormatter
from connectors.teams_client import TeamsClient
from nodes.analyze_impact import create_analyze_impact_node
from nodes.analyze_root_cause import create_analyze_root_cause_node
from nodes.read_bug import create_read_bug_node
from nodes.read_code import create_read_code_node
from nodes.read_requirement import create_read_requirement_node
from nodes.read_testcase import create_read_testcase_node
from nodes.search_requirement import create_search_requirement_node
from nodes.search_testcase import create_search_testcase_node
from nodes.write_report import create_write_report_node
from state import AnalysisState

logger = logging.getLogger(__name__)


def build_graph(
    config: AppConfig,
    tracker: BugTrackerClient,
    formatter: ReportFormatter,
    dng: DngClient,
    git: GitClient,
    teams_client: TeamsClient | None = None,
) -> StateGraph:
    """
    构建并返回编译好的 LangGraph StateGraph。

    调用方使用 graph.invoke({"bug_key": "PRJ-123"}) 启动分析。
    tracker 可以是 JiraClient 或 RtcClient。
    """

    # ── 确定 tracker 对应的配置 ──
    # 多 Jira / 多 RTC 时取首个作为默认（CAgent daemon 当前只跑单实例分析）
    tracker_config: JiraConfig | RtcConfig = (
        config.get_jira_config() if tracker.source_type == "jira"
        else config.get_rtc_config()
    )

    # ── 创建 LLM 实例 ──
    llm = ChatAnthropic(
        model=config.llm.model,
        api_key=config.llm.api_key,
        max_tokens=config.llm.max_tokens,
        temperature=config.llm.temperature,
    )

    # ── 创建 Node 函数 ──
    read_bug = create_read_bug_node(tracker, tracker_config)
    read_testcase = create_read_testcase_node(tracker, tracker_config)
    search_testcase = create_search_testcase_node(tracker, tracker_config)
    read_requirement = create_read_requirement_node(dng)
    search_requirement = create_search_requirement_node(dng)
    read_code = create_read_code_node(git)
    analyze_root_cause = create_analyze_root_cause_node(llm, config.llm)
    analyze_impact = create_analyze_impact_node(git, dng)
    write_report = create_write_report_node(
        tracker, config, formatter, teams_client=teams_client,
    )

    # ── 构建图 ──
    graph = StateGraph(AnalysisState)

    # 添加节点
    graph.add_node("read_bug", read_bug)
    graph.add_node("read_testcase", read_testcase)
    graph.add_node("search_testcase", search_testcase)
    graph.add_node("read_requirement", read_requirement)
    graph.add_node("search_requirement", search_requirement)
    graph.add_node("read_code", read_code)
    graph.add_node("analyze_root_cause", analyze_root_cause)
    graph.add_node("analyze_impact", analyze_impact)
    graph.add_node("write_report", write_report)

    # ── 边 ──

    # 入口 → read_bug
    graph.set_entry_point("read_bug")

    # read_bug 后检查是否失败
    graph.add_conditional_edges(
        "read_bug",
        _route_after_read_bug,
        {
            "read_testcase": "read_testcase",
            "write_report": "write_report",  # bug 读取失败直接出报告
        },
    )

    # read_testcase 后检查是否为空 → 降级搜索
    graph.add_conditional_edges(
        "read_testcase",
        _route_after_read_testcase,
        {
            "read_requirement": "read_requirement",
            "search_testcase": "search_testcase",
        },
    )

    # search_testcase → read_requirement (无论搜到没搜到)
    graph.add_edge("search_testcase", "read_requirement")

    # read_requirement 后检查是否为空 → 降级搜索
    graph.add_conditional_edges(
        "read_requirement",
        _route_after_read_requirement,
        {
            "read_code": "read_code",
            "search_requirement": "search_requirement",
        },
    )

    # search_requirement → read_code
    graph.add_edge("search_requirement", "read_code")

    # read_code → analyze_root_cause
    graph.add_edge("read_code", "analyze_root_cause")

    # analyze_root_cause → analyze_impact
    graph.add_edge("analyze_root_cause", "analyze_impact")

    # analyze_impact → write_report
    graph.add_edge("analyze_impact", "write_report")

    # write_report → END
    graph.add_edge("write_report", END)

    return graph.compile()


# ── 条件路由函数 ──


def _route_after_read_bug(state: AnalysisState) -> str:
    """read_bug 之后: 如果 bug_info 为空说明失败，直接跳到 write_report。"""
    if state.get("bug_info") is None:
        logger.warning("read_bug 失败，跳转 write_report")
        return "write_report"
    return "read_testcase"


def _route_after_read_testcase(state: AnalysisState) -> str:
    """read_testcase 之后: 如果 test_cases 为空则降级搜索。"""
    if not state.get("test_cases"):
        logger.info("无关联 Test Case，降级到 search_testcase")
        return "search_testcase"
    return "read_requirement"


def _route_after_read_requirement(state: AnalysisState) -> str:
    """read_requirement 之后: 如果 requirements 为空则降级搜索。"""
    if not state.get("requirements"):
        logger.info("无关联需求，降级到 search_requirement")
        return "search_requirement"
    return "read_code"
