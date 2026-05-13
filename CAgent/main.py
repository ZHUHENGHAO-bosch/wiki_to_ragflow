"""
main.py — Bug Analysis Daemon 入口

支持多种运行模式:
1. webhook: 启动 FastAPI 服务，接收 Jira Webhook
2. polling: 定期 JQL 轮询
3. once: 单次分析指定 Bug (调试用)
4. download-confluence: 下载 Confluence 页面树（支持单个 URL/ID 或 CSV 批量）
5. upload-ragflow: 上传文件到 RAGFlow 知识库
6. teams-send: 发送测试消息到 Teams 频道

用法:
    python main.py                          # 使用 config.yaml 默认模式
    python main.py --config path/to/config  # 指定配置文件
    python main.py --mode polling           # 强制轮询模式
    python main.py --once PRJ-123           # 单次分析（调试用，自动选择源）
    python main.py --once 12345 --source rtc # 单次分析 RTC WorkItem
    python main.py --download-confluence URL # 下载 Confluence 页面
    python main.py --download-confluence batch.csv  # CSV 批量下载
    python main.py --upload-ragflow f1.pdf f2.pdf   # 上传到 RAGFlow
    python main.py --teams-send "测试消息"   # 发送 Teams 测试消息
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import logging
import sys
import time

import uvicorn
from fastapi import FastAPI

from admin.admin_router import router as admin_router, init_admin_router
from admin.dashboard import dashboard_router
from admin.runtime_state import DaemonMode, RuntimeState
from config import AppConfig, load_config
from connectors.confluence_client import ConfluenceClient
from connectors.dng_client import DngClient
from connectors.git_client import GitClient
from connectors.jira_client import JiraClient
from connectors.ragflow_client import RAGFlowClient
from connectors.report_formatter import JiraWikiFormatter, RtcHtmlFormatter
from connectors.rtc_client import RtcClient
from connectors.graph_auth import GraphAuth
from connectors.graph_teams_client import GraphTeamsClient
from connectors.teams_client import TeamsClient
from graph import build_graph
from services.confluence_downloader import ConfluenceDownloader
from watcher.poller import JqlPoller
from watcher.rtc_poller import RtcPoller
from watcher.teams_poller import TeamsChannelPoller
from watcher.teams_webhook_handler import (
    router as teams_router,
    set_teams_trigger,
)
from watcher.webhook_handler import router as webhook_router, set_trigger_fn

logger = logging.getLogger("bug_analyzer")


def main() -> None:
    args = _parse_args()
    _setup_logging(verbose=args.verbose)

    logger.info("加载配置...")
    config = load_config(args.config)

    if args.teams_send:
        asyncio.run(_run_teams_send(config, args.teams_send))
    elif args.upload_ragflow:
        asyncio.run(_run_ragflow_upload(config, args.upload_ragflow))
    elif args.confluence_to_ragflow:
        asyncio.run(
            _run_confluence_to_ragflow(
                config,
                args.confluence_to_ragflow,
                args.confluence_output,
                args.confluence_depth,
                args.confluence_format,
                args.ragflow_dataset,
            )
        )
    elif args.download_confluence:
        asyncio.run(
            _run_confluence_download(
                config,
                args.download_confluence,
                args.confluence_output,
                args.confluence_depth,
                args.confluence_format,
            )
        )
    elif args.once:
        asyncio.run(_run_once(config, args.once, source=args.source))
    elif (args.mode or config.watcher.mode) == "polling":
        asyncio.run(_run_polling(config))
    else:
        _run_webhook(config)


# ── 三种运行模式 ──


async def _run_once(
    config: AppConfig, bug_key: str, source: str | None = None
) -> None:
    """单次分析一个 Bug（调试用）。"""
    jira, rtc, dng, git = await _create_clients(config)
    teams = _create_teams_client(config)

    # Graph API 集成
    graph_auth, graph_client = _create_graph_clients(config)
    if teams and graph_client:
        teams.set_graph_client(graph_client)

    # 选择 tracker: 如果指定了 --source 则强制使用
    if source == "rtc":
        tracker = rtc
        if tracker is None:
            logger.error("指定了 --source rtc 但 RTC 未配置 (config.rtc.ccm_url 为空)")
            return
    elif source == "jira":
        tracker = jira
        if tracker is None:
            logger.error("指定了 --source jira 但 Jira 未配置 (config.jira.base_url 为空)")
            return
    else:
        # 自动选择: 优先 Jira，若未配置则用 RTC
        tracker = jira or rtc
        if tracker is None:
            logger.error("未配置任何 Bug 管理系统 (Jira 或 RTC)")
            return

    formatter = (
        JiraWikiFormatter() if tracker.source_type == "jira" else RtcHtmlFormatter()
    )

    try:
        compiled_graph = build_graph(
            config, tracker, formatter, dng, git, teams_client=teams,
        )

        logger.info(f"开始分析: {bug_key} (source={tracker.source_type})")
        start = time.monotonic()

        result = await compiled_graph.ainvoke(
            {
                "bug_key": bug_key,
                "bug_info": None,
                "test_cases": [],
                "requirements": [],
                "code_info": None,
                "root_cause": None,
                "impact": None,
                "bug_source": tracker.source_type,
                "status": "success",
                "errors": [],
                "analysis_duration": 0.0,
            }
        )

        elapsed = time.monotonic() - start
        status = result.get("status", "unknown")
        logger.info(f"分析完成: {bug_key}, 状态={status}, 耗时={elapsed:.1f}s")

        if result.get("errors"):
            for err in result["errors"]:
                logger.warning(f"  - {err}")

    finally:
        if jira:
            await jira.close()
        if rtc:
            await rtc.close()
        await dng.close()
        if teams:
            await teams.close()
        if graph_client:
            await graph_client.close()
        if graph_auth:
            await graph_auth.close()


def _run_webhook(config: AppConfig) -> None:
    """Webhook 模式: 启动 FastAPI 服务。"""
    app = FastAPI(title="Bug Analysis Daemon", version="1.0.0")

    # 共享客户端 (在 lifespan 中管理)
    clients: dict = {}

    @app.on_event("startup")
    async def startup() -> None:
        jira, rtc, dng, git = await _create_clients(config)
        clients["jira"] = jira
        clients["rtc"] = rtc
        clients["dng"] = dng
        clients["git"] = git

        # Teams 客户端 (optional)
        teams = _create_teams_client(config)
        if teams:
            clients["teams"] = teams

        # Graph API 集成
        graph_auth, graph_client = _create_graph_clients(config)
        if graph_auth:
            clients["graph_auth"] = graph_auth
        if graph_client:
            clients["graph_client"] = graph_client
            if teams:
                teams.set_graph_client(graph_client)

        # Jira graph (默认 webhook 触发)
        if jira:
            jira_graph = build_graph(
                config, jira, JiraWikiFormatter(), dng, git, teams_client=teams,
            )
            clients["jira_graph"] = jira_graph

            async def jira_trigger(bug_key: str) -> None:
                await _run_analysis(jira_graph, bug_key, source="jira")

            set_trigger_fn(jira_trigger, config.watcher.webhook_secret)

        # Confluence downloader (optional)
        confluence_dl = _create_confluence_downloader(config)
        if confluence_dl:
            clients["confluence"] = confluence_dl[0]  # client
            clients["confluence_dl"] = confluence_dl[1]  # downloader

        # Teams Outgoing Webhook (使用 Jira graph 或 RTC graph)
        if config.teams.enabled:
            trigger_graph = clients.get("jira_graph")
            if trigger_graph:
                async def teams_trigger(bug_key: str) -> None:
                    await _run_analysis(trigger_graph, bug_key, source="jira")
                set_teams_trigger(teams_trigger, config.teams.outgoing_webhook_secret)

        # 选择活跃的 bug tracker (优先 RTC，其次 Jira)
        active_tracker = clients.get("rtc") or clients.get("jira")

        init_admin_router(
            config,
            _config_updater,
            confluence_downloader=confluence_dl[1] if confluence_dl else None,
            bug_tracker=active_tracker,
        )
        RuntimeState.get().set_mode(DaemonMode.WEBHOOK)
        logger.info("Webhook 模式启动完成")

    @app.on_event("shutdown")
    async def shutdown() -> None:
        if clients.get("jira"):
            await clients["jira"].close()
        if clients.get("rtc"):
            await clients["rtc"].close()
        if clients.get("dng"):
            await clients["dng"].close()
        if clients.get("confluence"):
            await clients["confluence"].close()
        if clients.get("teams"):
            await clients["teams"].close()
        if clients.get("graph_client"):
            await clients["graph_client"].close()
        if clients.get("graph_auth"):
            await clients["graph_auth"].close()
        logger.info("服务关闭")

    app.include_router(webhook_router)
    app.include_router(admin_router)
    app.include_router(dashboard_router)
    if config.teams.enabled:
        app.include_router(teams_router)

    uvicorn.run(app, host="0.0.0.0", port=8000)


async def _run_polling(config: AppConfig) -> None:
    """Polling 模式: 定期轮询 (Jira JQL + RTC Saved Query + Teams Channel) + Admin HTTP 服务。"""
    jira, rtc, dng, git = await _create_clients(config)
    teams = _create_teams_client(config)

    # Graph API 集成
    graph_auth, graph_client = _create_graph_clients(config)
    if teams and graph_client:
        teams.set_graph_client(graph_client)

    try:
        poll_tasks: list[Any] = []

        # Jira Poller
        if jira:
            jira_graph = build_graph(
                config, jira, JiraWikiFormatter(), dng, git, teams_client=teams,
            )

            async def jira_trigger(bug_key: str) -> None:
                await _run_analysis(jira_graph, bug_key, source="jira")

            jira_poller = JqlPoller(jira, config.watcher, jira_trigger)
            poll_tasks.append(jira_poller.start())
            logger.info("Jira Poller 已配置")

        # RTC Poller（多 RTC 时取首个作为默认）
        rtc_cfg_default = config.get_rtc_config()
        if rtc and rtc_cfg_default and rtc_cfg_default.saved_query_id:
            rtc_graph = build_graph(
                config, rtc, RtcHtmlFormatter(), dng, git, teams_client=teams,
            )

            async def rtc_trigger(bug_key: str) -> None:
                await _run_analysis(rtc_graph, bug_key, source="rtc")

            rtc_poller = RtcPoller(rtc, rtc_cfg_default, rtc_trigger)
            poll_tasks.append(rtc_poller.start())
            logger.info("RTC Poller 已配置")

        # Teams Channel Poller (Graph API Delta Query)
        if graph_client and teams and config.teams.enabled:
            # 选择触发函数: 优先 Jira，否则 RTC
            trigger_graph_for_teams = None
            if jira:
                jira_graph_for_teams = build_graph(
                    config, jira, JiraWikiFormatter(), dng, git, teams_client=teams,
                )

                async def teams_analysis_trigger(bug_key: str) -> None:
                    await _run_analysis(jira_graph_for_teams, bug_key, source="jira")

                trigger_graph_for_teams = teams_analysis_trigger
            elif rtc:
                rtc_graph_for_teams = build_graph(
                    config, rtc, RtcHtmlFormatter(), dng, git, teams_client=teams,
                )

                async def teams_rtc_trigger(bug_key: str) -> None:
                    await _run_analysis(rtc_graph_for_teams, bug_key, source="rtc")

                trigger_graph_for_teams = teams_rtc_trigger

            if trigger_graph_for_teams:
                teams_poller = TeamsChannelPoller(
                    graph_client=graph_client,
                    teams_client=teams,
                    trigger_fn=trigger_graph_for_teams,
                    poll_interval=config.teams.graph_poll_interval,
                )
                poll_tasks.append(teams_poller.start())
                logger.info("Teams Channel Poller 已配置")

        if not poll_tasks:
            logger.error("未配置任何 Poller (Jira 或 RTC)")
            return

        # Confluence downloader (optional)
        confluence_dl = _create_confluence_downloader(config)

        # Admin HTTP 服务 (Polling 模式下也启动)
        app = FastAPI(title="Bug Analysis Daemon (Admin)", version="1.0.0")

        # Teams Outgoing Webhook
        if config.teams.enabled and jira:
            jira_graph_ref = build_graph(
                config, jira, JiraWikiFormatter(), dng, git, teams_client=teams,
            )

            async def teams_trigger(bug_key: str) -> None:
                await _run_analysis(jira_graph_ref, bug_key, source="jira")

            set_teams_trigger(teams_trigger, config.teams.outgoing_webhook_secret)
            app.include_router(teams_router)

        # 选择活跃的 bug tracker (优先 RTC，其次 Jira)
        active_tracker = rtc or jira

        init_admin_router(
            config,
            _config_updater,
            confluence_downloader=confluence_dl[1] if confluence_dl else None,
            bug_tracker=active_tracker,
        )
        app.include_router(admin_router)
        app.include_router(dashboard_router)

        RuntimeState.get().set_mode(DaemonMode.POLLING)

        uv_config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="warning")
        server = uvicorn.Server(uv_config)

        logger.info(
            f"Polling 模式启动完成 (Admin API on :8000), "
            f"{len(poll_tasks)} 个 Poller 活跃"
        )

        # 并发运行所有 poller 和 admin HTTP
        await asyncio.gather(
            *poll_tasks,
            server.serve(),
        )

    finally:
        if jira:
            await jira.close()
        if rtc:
            await rtc.close()
        await dng.close()
        if teams:
            await teams.close()
        if graph_client:
            await graph_client.close()
        if graph_auth:
            await graph_auth.close()


# ── 公共工具 ──


async def _create_clients(
    config: AppConfig,
) -> tuple[JiraClient | None, RtcClient | None, DngClient, GitClient]:
    """创建并初始化所有连接器。"""
    # Jira (仅在配置了 base_url 时创建)，多 Jira 时取首个作为默认
    jira_cfg = config.get_jira_config()
    jira = JiraClient(jira_cfg) if jira_cfg and jira_cfg.base_url else None

    # RTC (仅在配置了 ccm_url 时创建)，多 RTC 时取首个作为默认
    rtc_cfg = config.get_rtc_config()
    rtc = RtcClient(rtc_cfg) if rtc_cfg and rtc_cfg.ccm_url else None

    dng = DngClient(config.dng)
    git = GitClient(config.git_repos)

    # DNG 需要先认证
    try:
        await dng.authenticate()
    except Exception as e:
        logger.warning(f"DNG 认证失败 (可能无需 DNG): {e}")

    return jira, rtc, dng, git


async def _run_analysis(
    compiled_graph, bug_key: str, source: str = "jira"
) -> None:
    """执行一次 Bug 分析。"""
    rt = RuntimeState.get()
    rt.record_start(bug_key)

    logger.info(f"开始分析: {bug_key} (source={source})")
    start = time.monotonic()

    try:
        result = await compiled_graph.ainvoke(
            {
                "bug_key": bug_key,
                "bug_info": None,
                "test_cases": [],
                "requirements": [],
                "code_info": None,
                "root_cause": None,
                "impact": None,
                "bug_source": source,
                "status": "success",
                "errors": [],
                "analysis_duration": 0.0,
            }
        )

        elapsed = time.monotonic() - start
        status = result.get("status", "unknown")
        root_cause = result.get("root_cause")

        logger.info(
            f"分析完成: {bug_key}, 状态={status}, 耗时={elapsed:.1f}s"
        )

        rt.record_finish(
            bug_key,
            status=status,
            root_cause_level=root_cause.level.value if root_cause else None,
        )

    except Exception as e:
        elapsed = time.monotonic() - start
        logger.error(f"分析异常: {bug_key}, 耗时={elapsed:.1f}s, 错误={e}")
        rt.record_finish(bug_key, status="failed", error_summary=str(e))
        rt.record_error("analysis", str(e), bug_key=bug_key)


def _create_confluence_downloader(
    config: AppConfig,
    ragflow_client: RAGFlowClient | None = None,
) -> tuple[ConfluenceClient, ConfluenceDownloader] | None:
    """创建 Confluence 客户端和下载器 (如果已配置)。"""
    if not config.confluence.base_url:
        logger.debug("Confluence 未配置，跳过")
        return None

    client = ConfluenceClient(config.confluence)
    downloader = ConfluenceDownloader(
        client, config.confluence, ragflow_client=ragflow_client,
    )
    logger.info(f"Confluence 客户端就绪: {config.confluence.base_url}")
    return client, downloader


async def _create_ragflow_client(config: AppConfig) -> RAGFlowClient | None:
    """创建并初始化 RAGFlow 客户端 (如果已配置)。"""
    if not config.ragflow.base_url or not config.ragflow.api_key:
        return None

    client = RAGFlowClient(config.ragflow)
    await client.init()
    return client


def _create_teams_client(config: AppConfig) -> TeamsClient | None:
    """创建 Teams 客户端 (如果已配置且启用)。"""
    if not config.teams.enabled:
        return None

    client = TeamsClient(config.teams)
    logger.info("Teams 客户端已创建")
    return client


def _create_graph_clients(
    config: AppConfig,
) -> tuple[GraphAuth | None, GraphTeamsClient | None]:
    """创建 Graph API 认证和 Teams 客户端 (如果已配置)。"""
    tc = config.teams
    if not (tc.graph_tenant_id and tc.graph_client_id and tc.graph_client_secret):
        return None, None
    if not (tc.graph_team_id and tc.graph_channel_id):
        logger.warning("Graph API 认证已配置，但缺少 team_id/channel_id")
        return None, None

    auth = GraphAuth(
        tenant_id=tc.graph_tenant_id,
        client_id=tc.graph_client_id,
        client_secret=tc.graph_client_secret,
        proxy=tc.proxy,
    )
    graph_client = GraphTeamsClient(
        auth=auth,
        team_id=tc.graph_team_id,
        channel_id=tc.graph_channel_id,
        bot_name=tc.graph_bot_name,
        proxy=tc.proxy,
    )
    logger.info("Graph API Teams 客户端已创建")
    return auth, graph_client


async def _run_teams_send(config: AppConfig, text: str) -> None:
    """CLI 模式: 发送测试消息到 Teams 频道。"""
    has_any_transport = (
        config.teams.webhook_url
        or config.teams.workflow_webhook_url
        or (config.teams.graph_tenant_id and config.teams.graph_team_id)
    )
    if not has_any_transport:
        logger.error(
            "Teams 未配置任何发送方式。"
            "请设置 webhook_url、workflow_webhook_url 或 Graph API 参数"
        )
        sys.exit(1)

    client = TeamsClient(config.teams)

    # 注入 Graph API 客户端 (如已配置)
    graph_auth, graph_client = _create_graph_clients(config)
    if graph_client:
        client.set_graph_client(graph_client)

    try:
        ok = await client.send_message(text)
        if ok:
            logger.info("Teams 消息发送成功")
        else:
            logger.error("Teams 消息发送失败")
            sys.exit(1)
    finally:
        await client.close()
        if graph_client:
            await graph_client.close()
        if graph_auth:
            await graph_auth.close()


async def _run_ragflow_upload(
    config: AppConfig, file_paths: list[str],
) -> None:
    """CLI 模式: 上传文件到 RAGFlow 知识库。"""
    from pathlib import Path

    if not config.ragflow.base_url or not config.ragflow.api_key:
        logger.error(
            "RAGFlow 未配置。请在配置文件中设置 ragflow.base_url 和 ragflow.api_key"
        )
        sys.exit(1)

    paths = [Path(p) for p in file_paths]
    missing = [p for p in paths if not p.exists()]
    if missing:
        for m in missing:
            logger.warning(f"文件不存在: {m}")

    client = RAGFlowClient(config.ragflow)
    try:
        await client.init()
        result = await client.upload_and_parse(paths)
        logger.info(
            f"RAGFlow 上传完成: {len(result['uploaded'])} 个文件上传, "
            f"{result['parse_count']} 个文件解析中"
        )
    finally:
        await client.close()


async def _run_confluence_download(
    config: AppConfig,
    target: str,
    output: str | None,
    depth: int | None,
    save_format: str | None = None,
) -> None:
    """CLI 模式: 下载 Confluence 页面树，支持单个 URL/ID 或 CSV 批量。"""
    if not config.confluence.base_url:
        logger.error("Confluence 未配置。请在 config.yaml 中设置 confluence.base_url")
        sys.exit(1)

    # 自动创建 RAGFlow 客户端 (如果配置了自动上传)
    ragflow_client: RAGFlowClient | None = None
    if config.ragflow.auto_upload_after_confluence:
        ragflow_client = await _create_ragflow_client(config)
        if ragflow_client:
            logger.info("RAGFlow 自动上传已启用")
        else:
            logger.warning(
                "ragflow.auto_upload_after_confluence=true 但 RAGFlow 未正确配置"
            )

    try:
        # 自动检测 CSV 文件
        if target.lower().endswith(".csv"):
            await _run_confluence_csv_batch(
                config, target, output, depth, save_format,
                ragflow_client=ragflow_client,
            )
        else:
            client = ConfluenceClient(config.confluence)
            downloader = ConfluenceDownloader(
                client, config.confluence, ragflow_client=ragflow_client,
            )
            try:
                await _run_confluence_single(
                    downloader, target, output, depth, save_format,
                )
            finally:
                await client.close()
    finally:
        if ragflow_client:
            await ragflow_client.close()


async def _run_confluence_single(
    downloader: ConfluenceDownloader,
    target: str,
    output: str | None,
    depth: int | None,
    save_format: str | None = None,
    output_filename: str | None = None,
    download_attachments: bool | None = None,
) -> bool:
    """下载单个 Confluence 页面树。返回 True 表示成功。"""
    task_id = await downloader.start_download(
        page_url=target if target.startswith("http") else None,
        page_id=target if not target.startswith("http") else None,
        output_dir=output,
        max_depth=depth,
        save_format=save_format,
        output_filename=output_filename,
        download_attachments=download_attachments,
    )
    logger.info(f"下载任务已启动: {task_id}")

    # 等待完成并打印进度
    while True:
        await asyncio.sleep(2)
        progress = downloader.get_progress(task_id)
        if not progress:
            break
        status = progress["status"]
        logger.info(
            f"进度: {progress['pages_downloaded']}/{progress['total_pages_discovered']} pages, "
            f"{progress['pages_skipped']} skipped, "
            f"{progress['attachments_downloaded']} attachments"
        )
        if status in ("completed", "failed", "cancelled"):
            break

    final = downloader.get_progress(task_id)
    if final:
        logger.info(f"下载完成: {final['status']}, 输出: {final['output_dir']}")
        if final.get("errors"):
            for err in final["errors"]:
                logger.warning(f"  - {err}")
        return final["status"] == "completed"
    return False


async def _run_confluence_csv_batch(
    config: AppConfig,
    csv_path: str,
    output: str | None,
    depth: int | None,
    save_format: str | None = None,
    ragflow_client: RAGFlowClient | None = None,
) -> None:
    """从 CSV 文件批量下载 Confluence 页面树。

    CSV 格式:
        file_name,link
        新人手册,https://confluence.example.com/pages/12345
        设计文档,67890
    """
    import os

    if not os.path.isfile(csv_path):
        logger.error(f"CSV 文件不存在: {csv_path}")
        sys.exit(1)

    # 解析 CSV（自动检测分隔符：逗号或 Tab）
    entries: list[dict[str, str]] = []
    with open(csv_path, encoding="utf-8-sig") as f:  # utf-8-sig 处理 Excel BOM
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",\t;")
        except csv.Error:
            dialect = None  # fallback to default (comma)
        reader = csv.DictReader(f, dialect=dialect) if dialect else csv.DictReader(f)
        # 验证必须列
        if not reader.fieldnames or not {"file_name", "link"}.issubset(
            set(reader.fieldnames)
        ):
            logger.error(
                f"CSV 缺少必要列。需要: file_name, link。"
                f"实际列: {reader.fieldnames}"
            )
            sys.exit(1)

        for i, row in enumerate(reader, start=2):  # 行号从 2 开始（第 1 行是表头）
            file_name = (row.get("file_name") or "").strip()
            link = (row.get("link") or "").strip()
            if not link:
                logger.warning(f"CSV 第 {i} 行: link 为空，跳过")
                continue
            if not file_name:
                logger.warning(f"CSV 第 {i} 行: file_name 为空，将使用页面标题")
            entries.append({"file_name": file_name or None, "link": link})

    if not entries:
        logger.error("CSV 中没有有效条目")
        sys.exit(1)

    logger.info(f"CSV 共 {len(entries)} 个下载任务")

    # 逐个下载（避免 Chrome 并发问题）
    client = ConfluenceClient(config.confluence)
    downloader = ConfluenceDownloader(
        client, config.confluence, ragflow_client=ragflow_client,
    )

    succeeded = 0
    failed = 0

    try:
        for idx, entry in enumerate(entries, start=1):
            link = entry["link"]
            fname = entry["file_name"]
            logger.info(
                f"── [{idx}/{len(entries)}] "
                f"{fname or '(auto)'} ← {link} ──"
            )
            try:
                ok = await _run_confluence_single(
                    downloader,
                    target=link,
                    output=output,
                    depth=depth,
                    save_format=save_format,
                    output_filename=None,  # 使用页面自身标题
                )
                if ok:
                    succeeded += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"下载失败: {link} — {e}")
                failed += 1

        logger.info(
            f"CSV 批量下载完成: {succeeded} 成功, {failed} 失败, "
            f"共 {len(entries)} 个"
        )
    finally:
        await client.close()


async def _run_confluence_to_ragflow(
    config: AppConfig,
    target: str,
    output: str | None,
    depth: int | None,
    save_format: str | None,
    ragflow_dataset: str | None,
) -> None:
    """端到端管道: 下载 Confluence → 上传 RAGFlow → 解析 → 检查结果。"""
    from pathlib import Path

    # ── 校验前置条件 ──
    if not config.confluence.base_url:
        logger.error("Confluence 未配置。请在 config.yaml 中设置 confluence.base_url")
        sys.exit(1)
    if not config.ragflow.base_url or not config.ragflow.api_key:
        logger.error(
            "RAGFlow 未配置。请在配置文件中设置 ragflow.base_url 和 ragflow.api_key"
        )
        sys.exit(1)

    # ── 阶段 1: 下载 ──
    logger.info("═══ 阶段 1/4: 下载 Confluence 页面 ═══")

    # 默认 JSON 格式，支持 pdf/json，不注入 ragflow_client（管道自己控制上传）
    effective_format = save_format or "json"
    if effective_format not in ("pdf", "json"):
        logger.warning(
            f"端到端管道仅支持 pdf/json 格式，已忽略 --confluence-format={save_format}，使用 json"
        )
        effective_format = "json"

    # 确定输出目录
    output_dir = output or config.confluence.default_output_dir
    output_path = Path(output_dir)

    # 记录下载前已有的文件（含 mtime），用于识别新增/更新的文件
    file_ext = f".{effective_format}"
    cache_dir = f"_{effective_format}_cache"
    # RAGFlow 可解析的附件扩展名
    _RAGFLOW_ATTACHMENT_EXTS = {
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".txt", ".csv", ".md", ".html", ".htm",
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff",
    }
    existing_files: dict[Path, float] = {}
    if output_path.exists():
        for p in output_path.rglob(f"*{file_ext}"):
            if cache_dir not in p.parts and "_tree.json" not in p.name:
                existing_files[p] = p.stat().st_mtime
        # 同时记录 _attachments 下已有的附件
        for p in output_path.rglob("_attachments/**/*"):
            if p.is_file() and p.suffix.lower() in _RAGFLOW_ATTACHMENT_EXTS:
                existing_files[p] = p.stat().st_mtime

    if target.lower().endswith(".csv"):
        await _run_confluence_csv_batch(
            config, target, output_dir, depth, effective_format,
            ragflow_client=None,
        )
    else:
        client = ConfluenceClient(config.confluence)
        downloader = ConfluenceDownloader(
            client, config.confluence, ragflow_client=None,
        )
        try:
            await _run_confluence_single(
                downloader, target, output_dir, depth, effective_format,
                download_attachments=True if effective_format == "json" else None,
            )
        finally:
            await client.close()

    # ── 阶段 1→2 衔接: 收集本次新增/更新的文件 ──
    new_files = sorted(
        p for p in output_path.rglob(f"*{file_ext}")
        if cache_dir not in p.parts
        and "_tree.json" not in p.name
        and (p not in existing_files or p.stat().st_mtime > existing_files[p])
    )

    # 收集 _attachments 目录下新增/更新的可解析附件
    new_attachments = sorted(
        p for p in output_path.rglob("_attachments/**/*")
        if p.is_file()
        and p.suffix.lower() in _RAGFLOW_ATTACHMENT_EXTS
        and (p not in existing_files or p.stat().st_mtime > existing_files[p])
    )

    all_files = new_files + new_attachments

    if not all_files:
        logger.error(f"输出目录中未找到可上传文件: {output_path}")
        sys.exit(1)

    logger.info(
        f"收集到 {len(new_files)} 个 {effective_format.upper()} 文件"
        + (f", {len(new_attachments)} 个附件" if new_attachments else "")
    )

    # ── 阶段 2: 上传 ──
    logger.info("═══ 阶段 2/4: 上传到 RAGFlow ═══")

    ragflow_client = RAGFlowClient(config.ragflow)
    try:
        await ragflow_client.init(dataset_name=ragflow_dataset)
        doc_ids = await ragflow_client.upload_documents(all_files)

        if not doc_ids:
            logger.error("没有文件上传成功")
            sys.exit(1)

        logger.info(f"上传完成: {len(doc_ids)} 个文档")

        # ── 阶段 3: 触发解析 ──
        logger.info("═══ 阶段 3/4: 触发解析 ═══")
        await ragflow_client.parse_documents(doc_ids)

        # ── 阶段 4: 等待解析完成 ──
        logger.info("═══ 阶段 4/4: 等待解析完成 ═══")

        def _on_progress(docs: list[dict]) -> None:
            done = sum(1 for d in docs if d["run"] == "DONE")
            running = sum(1 for d in docs if d["run"] == "RUNNING")
            fail = sum(1 for d in docs if d["run"] in ("FAIL", "CANCEL"))
            logger.info(
                f"  解析进度: {done} 完成, {running} 进行中, {fail} 失败 "
                f"(共 {len(docs)})"
            )

        result = await ragflow_client.wait_for_parsing(
            doc_ids, on_progress=_on_progress,
        )

        # ── 汇总报告 ──
        logger.info("═══ 端到端管道完成 ═══")
        logger.info(
            f"  完成: {len(result['completed'])} 个文档, "
            f"{result['total_chunks']} chunks, "
            f"{result['total_tokens']} tokens"
        )
        logger.info(f"  耗时: {result['elapsed_seconds']:.1f}s")

        if result["failed"]:
            for doc in result["failed"]:
                logger.warning(
                    f"  解析失败: {doc['name']} — {doc['progress_msg']}"
                )

        if result["timed_out"]:
            for doc in result["timed_out"]:
                logger.warning(f"  解析超时: {doc['name']} (run={doc['run']})")

        if result["failed"] or result["timed_out"]:
            sys.exit(1)

    finally:
        await ragflow_client.close()


def _config_updater(section: str, updated_fields: list[str]) -> bool:
    """配置更新回调。返回 True 表示需要重启才能完全生效。"""
    # LLM 参数修改需要重建 graph
    if section == "llm":
        return True
    return False


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bug Analysis Daemon")
    parser.add_argument(
        "--config", type=str, default=None, help="配置文件路径"
    )
    parser.add_argument(
        "--mode",
        choices=["webhook", "polling"],
        default=None,
        help="运行模式 (覆盖配置文件)",
    )
    parser.add_argument(
        "--once",
        type=str,
        default=None,
        help="单次分析指定 Bug Key (调试用)",
    )
    parser.add_argument(
        "--source",
        choices=["jira", "rtc"],
        default=None,
        help="指定 Bug 来源系统 (配合 --once 使用，默认自动选择)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="详细日志"
    )
    # Confluence 下载参数
    parser.add_argument(
        "--download-confluence",
        type=str,
        default=None,
        metavar="URL_OR_ID_OR_CSV",
        help="下载 Confluence 页面树 (URL、Page ID 或 CSV 文件路径)",
    )
    parser.add_argument(
        "--confluence-output",
        type=str,
        default=None,
        help="Confluence 下载输出目录",
    )
    parser.add_argument(
        "--confluence-depth",
        type=int,
        default=None,
        help="Confluence 最大遍历深度",
    )
    parser.add_argument(
        "--confluence-format",
        type=str,
        choices=["html", "pdf", "json"],
        default=None,
        help="Confluence 页面保存格式 (html、pdf 或 json)",
    )
    # Confluence → RAGFlow 端到端管道
    parser.add_argument(
        "--confluence-to-ragflow",
        type=str,
        default=None,
        metavar="URL_OR_ID_OR_CSV",
        help="端到端管道: 下载 Confluence → 上传 RAGFlow → 解析 → 检查结果",
    )
    parser.add_argument(
        "--ragflow-dataset",
        type=str,
        default=None,
        help="RAGFlow dataset 名称 (覆盖 config 中的 ragflow.dataset_name)",
    )
    # RAGFlow 上传参数
    parser.add_argument(
        "--upload-ragflow",
        type=str,
        nargs="+",
        metavar="FILE",
        help="上传文件到 RAGFlow 知识库",
    )
    # Teams 测试发送
    parser.add_argument(
        "--teams-send",
        type=str,
        default=None,
        metavar="TEXT",
        help="发送测试消息到 Teams 频道",
    )
    return parser.parse_args()


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # httpx 太啰嗦
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


if __name__ == "__main__":
    main()
