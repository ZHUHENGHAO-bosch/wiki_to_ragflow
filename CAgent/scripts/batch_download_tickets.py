"""
scripts/batch_download_tickets.py — 批量下载 RTC 项目中的 Ticket 信息

用法:
    python scripts/batch_download_tickets.py \
        --query-id _M1DbkPUZEfCCDJnEYT0R8Q \
        --batch-size 50 \
        --sleep 10

    # 或按条件过滤 (不使用 saved query):
    python scripts/batch_download_tickets.py \
        --filter 'type/id="defect"' \
        --batch-size 50 \
        --sleep 10

功能:
    1. 通过 Reportable REST API 分页获取 WorkItem ID 列表
    2. 分批获取完整 ticket 信息 (OSLC API):
       a. get_issue() — 完整 WorkItem 数据
       b. get_comments() — Discussion 评论
    3. 使用 parse_rtc_tickets 解析为结构化格式
    4. 可选下载附件 (--with-attachments)，按 ticket ID 分目录存放
    5. 批次间 sleep 指定秒数
    6. 结果写入:
       - rtc_ticket_pages/ticket_*.json — 原始 OSLC 数据
       - rtc_ticket_pages/discussions.json — 全部评论
       - rtc_ticket_pages/tickets_structured.json — 结构化格式 (含评论)

注: 代理环境下 /oslc/queries/ 路径可能被拦截，本脚本使用
    /rpt/repository/workitem 路径绕过此限制。
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import xmltodict

# 将 CAgent 根目录加入 Python 路径
_CAGENT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir))
if _CAGENT_ROOT not in sys.path:
    sys.path.insert(0, _CAGENT_ROOT)

from config import load_config
from connectors.rtc_client import RtcClient
from scripts.parse_rtc_tickets import parse_ticket

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("batch_download")


def _fetch_workitem_ids_via_rpt(
    rtc: RtcClient,
    project_area_name: str,
    wi_filter: str = 'type/id="defect"',
    page_size: int = 50,
    sleep_seconds: int = 10,
    max_count: int = 0,
    saved_query_id: str | None = None,
) -> list[dict[str, str]]:
    """通过 Reportable REST API 分页获取 WorkItem ID 列表。

    支持两种模式:
    1. saved_query_id: 使用 savedQuery 参数执行已保存的查询
    2. wi_filter: 使用 fields 条件过滤

    返回 [{"id": "12345", "summary": "...", "state": "..."}, ...]
    """
    rtc._ensure_session()
    session = rtc._session
    ccm_url = rtc._ccm_url

    # 构造初始 URL
    if saved_query_id:
        # 使用 Saved Query
        fields_param = "workitem/workItem/(id|summary|state/name|priority/name)"
        base_url = f"{ccm_url}/rpt/repository/workitem?savedQuery={saved_query_id}&fields={fields_param}&size={page_size}"
        logger.info("使用 Saved Query: %s", saved_query_id)
    else:
        # 使用条件过滤
        pa_filter = f'projectArea/name="{project_area_name}"'
        condition = f"{pa_filter} and {wi_filter}" if wi_filter else pa_filter
        fields_param = f"workitem/workItem[{condition}]/(id|summary|state/name|priority/name)"
        base_url = f"{ccm_url}/rpt/repository/workitem?fields={fields_param}&size={page_size}"

    results: list[dict[str, str]] = []
    url = base_url
    page = 0

    while url:
        page += 1
        logger.info("Reportable REST 第 %d 页 (已获取 %d 条)...", page, len(results))

        try:
            resp = session.get(
                url,
                headers={"Accept": "text/xml", "Connection": "close"},
                timeout=120,
            )
            resp.raise_for_status()
        except Exception as e:
            logger.error("Reportable REST 请求失败: %s", e)
            break

        raw = xmltodict.parse(resp.content)
        root = raw.get("workitem", {})
        entries = root.get("workItem", [])
        if isinstance(entries, dict):
            entries = [entries]

        if not entries:
            break

        for entry in entries:
            wi_id = entry.get("id", "")
            summary = entry.get("summary", "")
            state = ""
            if isinstance(entry.get("state"), dict):
                state = entry["state"].get("name", "")
            priority = ""
            if isinstance(entry.get("priority"), dict):
                priority = entry["priority"].get("name", "")

            results.append({
                "id": str(wi_id),
                "summary": summary,
                "state": state,
                "priority": priority,
            })

        logger.info("  本页 %d 条，累计 %d 条", len(entries), len(results))

        # 达到 max_count 提前停止
        if max_count > 0 and len(results) >= max_count:
            results = results[:max_count]
            logger.info("已达 max_count=%d，停止获取 ID", max_count)
            break

        # 检查是否有下一页
        next_href = root.get("@href", "")
        rel = root.get("@rel", "")
        if rel == "next" and next_href:
            url = next_href
            if page > 1:
                import time
                time.sleep(sleep_seconds)
        else:
            break

    return results


async def batch_download(
    query_id: str | None = None,
    wi_filter: str = 'type/id="defect"',
    batch_size: int = 50,
    sleep_seconds: int = 10,
    config_path: str | None = None,
    output_dir: str | None = None,
    with_discussions: bool = True,
    max_count: int = 0,
    with_attachments: bool = False,
) -> str:
    """批量下载 RTC Ticket 信息 + Discussion。

    1. 通过 Reportable REST API 获取 WorkItem ID 列表
    2. 分批获取: get_issue() + get_comments()
    3. 保存原始 OSLC 数据 + 结构化解析结果

    Returns:
        输出目录路径。
    """
    # 加载配置（多 RTC 时取首个作为默认）
    config = load_config(config_path)
    rtc_cfg = config.get_rtc_config()
    if not rtc_cfg:
        raise ValueError("未配置 RTC（请检查 config.local.yaml 的 rtc 段）")
    rtc = RtcClient(rtc_cfg)
    project_area = rtc_cfg.project_area_name

    # 输出目录
    out_dir = output_dir or os.path.join(_CAGENT_ROOT, "rtc_ticket_pages")
    os.makedirs(out_dir, exist_ok=True)

    # Step 1: 获取 WorkItem ID 列表
    logger.info("通过 Reportable REST API 获取 WorkItem 列表...")
    logger.info("  项目: %s, 过滤: %s", project_area, wi_filter)

    id_list = await asyncio.to_thread(
        _fetch_workitem_ids_via_rpt,
        rtc, project_area, wi_filter, batch_size, sleep_seconds, max_count,
        query_id,
    )
    # 限制数量
    if max_count > 0 and len(id_list) > max_count:
        logger.info("限制下载数量: %d -> %d", len(id_list), max_count)
        id_list = id_list[:max_count]

    total = len(id_list)
    logger.info("共获取 %d 个 WorkItem ID", total)

    if total == 0:
        logger.warning("查询结果为空，退出")
        return ""

    # Step 2: 分批获取详细信息 + 评论
    raw_tickets: list[dict] = []
    all_discussions: dict[str, dict] = {}
    failed: list[dict] = []
    total_batches = (total + batch_size - 1) // batch_size

    for batch_idx in range(total_batches):
        start = batch_idx * batch_size
        end = min(start + batch_size, total)
        batch = id_list[start:end]

        logger.info(
            "=== 批次 %d/%d (items %d-%d / %d) ===",
            batch_idx + 1, total_batches, start + 1, end, total,
        )

        for i, item in enumerate(batch):
            key = item["id"]
            try:
                # 获取 OSLC 完整数据 (含原始 RDF)
                detail = await rtc.get_issue(key, include_raw=True)
                raw_tickets.append({"key": key, "oslc_data": detail})

                # 保存原始 OSLC JSON
                raw_oslc = detail.pop("_raw_oslc", None)
                raw_path = os.path.join(out_dir, f"ticket_{key}.json")
                if raw_oslc:
                    with open(raw_path, "w", encoding="utf-8") as f:
                        json.dump(raw_oslc, f, ensure_ascii=False, indent=2)

                summary = detail.get("fields", {}).get("summary", "")[:60]
                logger.info(
                    "  [%d/%d] %s - %s",
                    start + i + 1, total, key, summary,
                )

                # 获取评论
                if with_discussions:
                    try:
                        comments = await rtc.get_comments(key)
                        all_discussions[key] = {
                            "workitem_id": key,
                            "total_comments": len(comments),
                            "comments": comments,
                        }
                        if comments:
                            logger.info("    -> %d 条评论", len(comments))
                    except Exception as ce:
                        logger.warning("    -> 评论获取失败: %s", ce)
                        all_discussions[key] = {
                            "workitem_id": key,
                            "total_comments": 0,
                            "comments": [],
                            "error": str(ce),
                        }

                # 下载附件
                if with_attachments:
                    try:
                        att_dir = os.path.join(out_dir, "attachments", key)
                        att_results = await rtc.download_all_attachments(
                            key, output_dir=att_dir,
                        )
                        ok = [r for r in att_results if r.get("success")]
                        skip = [r for r in att_results if not r.get("success")]
                        if ok:
                            logger.info("    -> %d 个附件已下载", len(ok))
                        if skip:
                            for r in skip:
                                logger.warning(
                                    "    -> 附件跳过: %s (%s)",
                                    r.get("name", "?"), r.get("error", ""),
                                )
                    except Exception as ae:
                        logger.warning("    -> 附件下载失败: %s", ae)

            except Exception as e:
                logger.error("  [%d/%d] %s - 失败: %s", start + i + 1, total, key, e)
                failed.append({"key": key, "error": str(e)})

        # 批次间 sleep（最后一批不 sleep）
        if batch_idx < total_batches - 1:
            logger.info("Sleep %ds ...", sleep_seconds)
            await asyncio.sleep(sleep_seconds)

    # Step 3: 解析为结构化格式
    logger.info("解析为结构化格式...")
    structured_tickets = []

    # 从已保存的原始 JSON 文件中解析
    json_files = sorted(Path(out_dir).glob("ticket_*.json"))
    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                raw = json.load(f)
            ticket = parse_ticket(raw)

            # 添加 Discussion
            wi_id = ticket.get("基本信息", {}).get("ID", "")
            disc = all_discussions.get(wi_id, {})
            if disc.get("comments"):
                ticket["讨论 (Discussion)"] = [
                    {
                        "评论者": c["creator"],
                        "时间": c["created"],
                        "内容": c["body"],
                    }
                    for c in disc["comments"]
                ]

            structured_tickets.append(ticket)
        except Exception as e:
            logger.warning("解析 %s 失败: %s", jf.name, e)

    # Step 4: 写入输出文件
    # 4a. discussions.json
    if all_discussions:
        disc_path = os.path.join(out_dir, "discussions.json")
        with open(disc_path, "w", encoding="utf-8") as f:
            json.dump(all_discussions, f, ensure_ascii=False, indent=2)
        logger.info("评论 -> %s", disc_path)

    # 4b. tickets_structured.json
    structured_path = os.path.join(out_dir, "tickets_structured.json")
    with open(structured_path, "w", encoding="utf-8") as f:
        json.dump(structured_tickets, f, ensure_ascii=False, indent=2)
    logger.info("结构化 -> %s", structured_path)

    # 4c. 汇总信息
    summary_path = os.path.join(out_dir, "download_summary.json")
    total_comments = sum(d.get("total_comments", 0) for d in all_discussions.values())
    summary: dict[str, Any] = {
        "query_id": query_id,
        "filter": wi_filter,
        "project_area": project_area,
        "total_found": total,
        "total_downloaded": len(structured_tickets),
        "total_failed": len(failed),
        "total_comments": total_comments,
        "downloaded_at": datetime.now().isoformat(),
        "output_dir": out_dir,
        "failed": failed,
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    logger.info(
        "完成! 成功 %d / 失败 %d / 评论 %d / 总计 %d | 输出: %s",
        len(structured_tickets), len(failed), total_comments, total, out_dir,
    )
    return out_dir


async def download_by_ids(
    bug_ids: list[str],
    config_path: str | None = None,
    output_dir: str | None = None,
    with_discussions: bool = True,
    with_attachments: bool = False,
) -> str:
    """按 ID 列表下载 WorkItem，输出与 batch_download 相同的结构化格式。

    支持单个或多个 ID。

    Returns:
        输出目录路径。
    """
    config = load_config(config_path)
    rtc_cfg = config.get_rtc_config()
    if not rtc_cfg:
        raise ValueError("未配置 RTC（请检查 config.local.yaml 的 rtc 段）")
    rtc = RtcClient(rtc_cfg)

    out_dir = output_dir or os.path.join(_CAGENT_ROOT, "rtc_ticket_pages")
    os.makedirs(out_dir, exist_ok=True)

    total = len(bug_ids)
    logger.info("下载 %d 个 WorkItem: %s", total, ", ".join(bug_ids))

    all_tickets: list[dict] = []
    all_discussions: dict[str, dict] = {}
    failed: list[dict] = []

    for idx, bug_id in enumerate(bug_ids):
        try:
            # 获取 OSLC 完整数据
            detail = await rtc.get_issue(bug_id, include_raw=True)
            raw_oslc = detail.pop("_raw_oslc", None)

            # 保存原始 OSLC JSON
            if raw_oslc:
                raw_path = os.path.join(out_dir, f"ticket_{bug_id}.json")
                with open(raw_path, "w", encoding="utf-8") as f:
                    json.dump(raw_oslc, f, ensure_ascii=False, indent=2)

            summary = detail.get("fields", {}).get("summary", "")[:60]
            logger.info("  [%d/%d] %s - %s", idx + 1, total, bug_id, summary)

            # 解析为结构化格式
            ticket: dict[str, Any] = {}
            if raw_oslc:
                ticket = parse_ticket(raw_oslc)

            # 获取评论
            if with_discussions:
                try:
                    comments = await rtc.get_comments(bug_id)
                    all_discussions[bug_id] = {
                        "workitem_id": bug_id,
                        "total_comments": len(comments),
                        "comments": comments,
                    }
                    if comments:
                        ticket["讨论 (Discussion)"] = [
                            {
                                "评论者": c["creator"],
                                "时间": c["created"],
                                "内容": c["body"],
                            }
                            for c in comments
                        ]
                        logger.info("    -> %d 条评论", len(comments))
                except Exception as ce:
                    logger.warning("    -> 评论获取失败: %s", ce)

            # 下载附件
            if with_attachments:
                try:
                    att_dir = os.path.join(out_dir, "attachments", bug_id)
                    att_results = await rtc.download_all_attachments(
                        bug_id, output_dir=att_dir,
                    )
                    ok = [r for r in att_results if r.get("success")]
                    skip = [r for r in att_results if not r.get("success")]
                    if ok:
                        logger.info("    -> %d 个附件已下载", len(ok))
                    for r in skip:
                        logger.warning(
                            "    -> 附件跳过: %s (%s)",
                            r.get("name", "?"), r.get("error", ""),
                        )
                except Exception as ae:
                    logger.warning("    -> 附件下载失败: %s", ae)

            all_tickets.append(ticket)

        except Exception as e:
            logger.error("  [%d/%d] %s - 失败: %s", idx + 1, total, bug_id, e)
            failed.append({"key": bug_id, "error": str(e)})

    # 保存评论
    if all_discussions:
        disc_path = os.path.join(out_dir, "discussions.json")
        with open(disc_path, "w", encoding="utf-8") as f:
            json.dump(all_discussions, f, ensure_ascii=False, indent=2)
        logger.info("评论 -> %s", disc_path)

    # 保存结构化结果
    structured_path = os.path.join(out_dir, "tickets_structured.json")
    with open(structured_path, "w", encoding="utf-8") as f:
        json.dump(all_tickets, f, ensure_ascii=False, indent=2)
    logger.info("结构化 -> %s", structured_path)

    logger.info(
        "完成! 成功 %d / 失败 %d / 总计 %d | 输出: %s",
        len(all_tickets), len(failed), total, out_dir,
    )
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="批量下载 RTC Ticket 信息 + Discussion")
    parser.add_argument(
        "--id", default=None,
        help="单个 WorkItem ID，直接下载该 ticket",
    )
    parser.add_argument(
        "--ids", default=None,
        help="多个 WorkItem ID，逗号分隔，如: 111,222,333",
    )
    parser.add_argument(
        "--query-id", default=None,
        help="RTC Saved Query ID",
    )
    parser.add_argument(
        "--filter", default='type/id="defect"',
        help='WorkItem 过滤条件 (默认: type/id=\"defect\")',
    )
    parser.add_argument(
        "--batch-size", type=int, default=50,
        help="每批下载数量 (默认 50)",
    )
    parser.add_argument(
        "--sleep", type=int, default=10,
        help="批次间 sleep 秒数 (默认 10)",
    )
    parser.add_argument(
        "--config", default=None,
        help="配置文件路径 (默认自动探测 config.local.yaml > config.yaml)",
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="输出目录 (默认 rtc_ticket_pages/)",
    )
    parser.add_argument(
        "--no-discussions", action="store_true",
        help="不下载评论 (Discussion)",
    )
    parser.add_argument(
        "--max-count", type=int, default=0,
        help="最大下载数量 (默认 0 = 不限)",
    )
    parser.add_argument(
        "--with-attachments", action="store_true",
        help="同时下载附件 (存放在 attachments/<ticket_id>/ 目录)",
    )
    args = parser.parse_args()

    if args.id or args.ids:
        # 按 ID 下载模式（单个或多个）
        if args.ids:
            id_list = [x.strip() for x in args.ids.split(",") if x.strip()]
        else:
            id_list = [args.id]
        asyncio.run(
            download_by_ids(
                bug_ids=id_list,
                config_path=args.config,
                output_dir=args.output_dir,
                with_discussions=not args.no_discussions,
                with_attachments=args.with_attachments,
            )
        )
    else:
        # 批量下载模式 (query)
        asyncio.run(
            batch_download(
                query_id=args.query_id,
                wi_filter=args.filter,
                batch_size=args.batch_size,
                sleep_seconds=args.sleep,
                config_path=args.config,
                output_dir=args.output_dir,
                with_discussions=not args.no_discussions,
                max_count=args.max_count,
                with_attachments=args.with_attachments,
            )
        )


if __name__ == "__main__":
    main()
