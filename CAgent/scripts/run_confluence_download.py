#!/usr/bin/env python3
"""
Confluence 下载端到端测试脚本 — 连接真实服务器，统计耗时。

Usage:
    python scripts/run_confluence_download.py <confluence_page_url>
    python scripts/run_confluence_download.py  # 使用默认 URL
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import time
import sys
from pathlib import Path

# 将项目根目录加入 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

DEFAULT_URL = (
    "https://inside-docupedia.bosch.com/confluence"
    "/spaces/GG/pages/4605261869/04-+SGM+VCU+Lite+Design"
)


async def main(target_url: str) -> None:
    logger.info(f"目标页面: {target_url}")

    # ── 1. 加载配置 ──
    t0 = time.perf_counter()
    from config import load_config

    cfg = load_config()
    confluence_cfg = cfg.confluence
    logger.info(
        f"配置加载完成: base_url={confluence_cfg.base_url}, "
        f"auth={confluence_cfg.auth_method}, "
        f"format={confluence_cfg.save_format}, "
        f"pdf_method={confluence_cfg.pdf_export_method}, "
        f"max_depth={confluence_cfg.max_depth}"
    )

    # ── 2. 解析 URL ──
    from connectors.confluence_client import ConfluenceClient

    parsed = ConfluenceClient.parse_page_url(target_url)
    page_id = parsed["page_id"]
    space_key = parsed["space_key"]
    logger.info(f"解析结果: space={space_key}, page_id={page_id}")

    if not page_id:
        logger.error("无法从 URL 解析 page_id")
        return

    # ── 3. 创建客户端 ──
    client = ConfluenceClient(confluence_cfg)

    # ── 4. 先测试 API 连通性 ──
    logger.info("测试 API 连通性...")
    t_api_start = time.perf_counter()
    try:
        page_data = await client.get_page(page_id)
        title = page_data.get("title", "?")
        version = page_data.get("version", {}).get("number", 0)
        t_api_end = time.perf_counter()
        logger.info(
            f"API 连通: 页面标题='{title}', 版本={version}, "
            f"耗时={t_api_end - t_api_start:.2f}s"
        )
    except Exception as e:
        logger.error(f"API 连接失败: {e}")
        await client.close()
        return

    # ── 5. 获取子页面数量 ──
    logger.info("获取子页面...")
    t_children_start = time.perf_counter()
    try:
        children = await client.get_all_child_pages(page_id)
        t_children_end = time.perf_counter()
        logger.info(
            f"子页面数量: {len(children)}, "
            f"耗时={t_children_end - t_children_start:.2f}s"
        )
        for child in children[:10]:
            logger.info(f"  - {child.get('title', '?')} (id={child['id']})")
        if len(children) > 10:
            logger.info(f"  ... 还有 {len(children) - 10} 个子页面")
    except Exception as e:
        logger.error(f"获取子页面失败: {e}")

    # ── 6. 启动下载任务 ──
    from services.confluence_downloader import ConfluenceDownloader

    downloader = ConfluenceDownloader(client, confluence_cfg)

    output_dir = "./confluence_downloads/test_run"
    logger.info(f"开始下载任务 (save_format={confluence_cfg.save_format})...")

    task_id = await downloader.start_download(
        page_url=target_url,
        output_dir=output_dir,
        resume=True,
    )
    logger.info(f"任务已创建: {task_id}")

    # ── 7. 轮询进度 ──
    last_status = ""
    while True:
        await asyncio.sleep(2)
        progress = downloader.get_progress(task_id)
        if progress is None:
            logger.warning("无法获取进度")
            break

        status = progress["status"]
        pages_dl = progress["pages_downloaded"]
        pages_skip = progress["pages_skipped"]
        pages_fail = progress["pages_failed"]
        total = progress["total_pages_discovered"]
        attach_dl = progress["attachments_downloaded"]
        current = progress["current_page"]
        elapsed = progress["elapsed_seconds"]

        status_line = (
            f"[{status}] 发现={total}, 下载={pages_dl}, "
            f"跳过={pages_skip}, 失败={pages_fail}, "
            f"附件={attach_dl}, 耗时={elapsed:.1f}s"
        )
        if current:
            status_line += f", 当前={current}"

        if status_line != last_status:
            logger.info(status_line)
            last_status = status_line

        if status in ("completed", "failed", "cancelled"):
            break

    # ── 8. 输出最终结果 ──
    t_download_end = time.perf_counter()
    total_time = t_download_end - t0

    progress = downloader.get_progress(task_id)
    logger.info("=" * 60)
    logger.info("下载完成，统计信息:")
    logger.info(f"  状态: {progress['status']}")
    logger.info(f"  根页面: {progress['root_page_title']}")
    logger.info(f"  发现页面: {progress['total_pages_discovered']}")
    logger.info(f"  下载成功: {progress['pages_downloaded']}")
    logger.info(f"  缓存跳过: {progress['pages_skipped']}")
    logger.info(f"  下载失败: {progress['pages_failed']}")
    logger.info(f"  附件下载: {progress['attachments_downloaded']}")
    logger.info(f"  附件失败: {progress['attachments_failed']}")
    logger.info(f"  下载耗时: {progress['elapsed_seconds']:.1f}s")
    logger.info(f"  总耗时:   {total_time:.1f}s")
    logger.info(f"  输出路径: {progress['output_dir']}")

    if progress["errors"]:
        logger.info("  错误信息:")
        for err in progress["errors"]:
            logger.info(f"    - {err}")

    # 检查输出文件
    out_path = Path(progress["output_dir"])
    if out_path.exists():
        if out_path.is_file():
            size_kb = out_path.stat().st_size / 1024
            logger.info(f"  文件大小: {size_kb:.1f} KB")
        else:
            files = list(out_path.rglob("*"))
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            logger.info(
                f"  输出文件数: {len(files)}, "
                f"总大小: {total_size / 1024:.1f} KB"
            )

    logger.info("=" * 60)

    await client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Confluence 下载端到端测试")
    parser.add_argument(
        "url",
        nargs="?",
        default=DEFAULT_URL,
        help="Confluence 页面 URL（默认使用内置 URL）",
    )
    args = parser.parse_args()
    asyncio.run(main(args.url))
