"""
scripts/download_discussions.py — 下载已有 ticket 的 Discussion (评论)

为 rtc_ticket_pages/ 中已下载的 ticket 获取评论，将结果保存到各 ticket JSON 中。

用法:
    python scripts/download_discussions.py [--input-dir rtc_ticket_pages] [--sleep 2]
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import sys
from pathlib import Path

_CAGENT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir))
if _CAGENT_ROOT not in sys.path:
    sys.path.insert(0, _CAGENT_ROOT)

from config import load_config
from connectors.rtc_client import RtcClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("download_discussions")


async def download_discussions(
    input_dir: str | None = None,
    sleep_seconds: int = 2,
    config_path: str | None = None,
) -> None:
    """为已下载的 ticket 获取 Discussion/Comments。"""
    config = load_config(config_path)
    rtc_cfg = config.get_rtc_config()
    if not rtc_cfg:
        raise ValueError("未配置 RTC（请检查 config.local.yaml 的 rtc 段）")
    rtc = RtcClient(rtc_cfg)

    ticket_dir = input_dir or os.path.join(_CAGENT_ROOT, "rtc_ticket_pages")
    json_files = sorted(Path(ticket_dir).glob("ticket_*.json"))

    if not json_files:
        logger.warning("目录 %s 中没有 ticket_*.json 文件", ticket_dir)
        return

    logger.info("共 %d 个 ticket 文件，开始获取评论...", len(json_files))

    all_discussions = {}

    for i, jf in enumerate(json_files):
        # 从文件名提取 ID
        m = re.search(r'ticket_(\d+)\.json', jf.name)
        if not m:
            continue
        wi_id = m.group(1)

        logger.info("[%d/%d] 获取 WorkItem %s 的评论...", i + 1, len(json_files), wi_id)

        try:
            comments = await rtc.get_comments(wi_id)
            all_discussions[wi_id] = {
                "workitem_id": wi_id,
                "total_comments": len(comments),
                "comments": comments,
            }
            logger.info("  -> %d 条评论", len(comments))
        except Exception as e:
            logger.error("  -> 失败: %s", e)
            all_discussions[wi_id] = {
                "workitem_id": wi_id,
                "total_comments": 0,
                "comments": [],
                "error": str(e),
            }

        if i < len(json_files) - 1 and sleep_seconds > 0:
            await asyncio.sleep(sleep_seconds)

    # 保存到 discussions.json
    output_path = os.path.join(ticket_dir, "discussions.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_discussions, f, ensure_ascii=False, indent=2)

    total_comments = sum(d["total_comments"] for d in all_discussions.values())
    logger.info(
        "完成! %d 个 ticket, %d 条评论 -> %s",
        len(all_discussions), total_comments, output_path,
    )


def main():
    import argparse
    parser = argparse.ArgumentParser(description="下载 RTC ticket 评论")
    parser.add_argument("--input-dir", default=None)
    parser.add_argument("--sleep", type=int, default=2)
    parser.add_argument("--config", default=None)
    args = parser.parse_args()

    asyncio.run(download_discussions(
        input_dir=args.input_dir,
        sleep_seconds=args.sleep,
        config_path=args.config,
    ))


if __name__ == "__main__":
    main()
