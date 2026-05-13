"""
scripts/download_bugs.py — 按 Bug ID 下载 RTC 缺陷数据（分目录存储）

输出结构:
    output/
    ├── 12345/
    │   ├── description.json    # 核心描述信息
    │   ├── summary.json        # root cause + solution 总结
    │   ├── attachments/        # 附件文件
    │   └── raw.json            # 原始 OSLC 数据
    └── download_report.json    # 下载汇总报告

用法:
    python scripts/download_bugs.py --id 12345
    python scripts/download_bugs.py --ids 12345,67890,11111
    python scripts/download_bugs.py --id-file bug_ids.txt
    python scripts/download_bugs.py --ids 12345,67890 --output-dir ./my_output --no-attachments
    python scripts/download_bugs.py --ids 12345 --config config.local.yaml
    python scripts/download_bugs.py --id 12345 --upload
    python scripts/download_bugs.py --id 12345 --upload-only
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

# 将 CAgent 根目录加入 Python 路径
_CAGENT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir))
if _CAGENT_ROOT not in sys.path:
    sys.path.insert(0, _CAGENT_ROOT)

from config import load_config
from connectors.minio_client import MinioUploader
from connectors.rtc_client import RtcClient
from scripts.parse_rtc_tickets import parse_ticket

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("download_bugs")


# ---------------------------------------------------------------------------
# 字段提取
# ---------------------------------------------------------------------------

def extract_description(parsed: dict) -> dict[str, Any]:
    """从 parse_ticket() 结果中提取精简核心字段 → description.json。"""
    basic = parsed.get("基本信息", {})
    status = parsed.get("状态信息", {})
    people = parsed.get("人员信息", {})
    time_info = parsed.get("时间信息", {})
    test_info = parsed.get("测试信息", {})

    # 测试信息子对象（仅包含非空字段）
    test = {}
    op = test_info.get("操作步骤 (Operation Schedule)", "")
    if op:
        test["operation_schedule"] = op
    actual = test_info.get("实际结果 (Actual Result)", "")
    if actual:
        test["actual_result"] = actual
    expect = test_info.get("期望结果 (Expected Result)", "")
    if expect:
        test["expected_result"] = expect

    desc: dict[str, Any] = {}
    # 基本信息
    _set(desc, "id", basic.get("ID", ""))
    _set(desc, "title", basic.get("标题 (Title)", ""))
    _set(desc, "type", basic.get("类型 (Type)", ""))
    _set(desc, "description", basic.get("描述 (Description)", ""))
    _set(desc, "priority", basic.get("优先级 (Priority)", ""))
    _set(desc, "severity", basic.get("严重程度 (Severity)", ""))
    # 状态
    _set(desc, "state", status.get("状态 (State)", ""))
    _set(desc, "resolution", status.get("Resolution", ""))
    # 人员
    _set(desc, "creator", people.get("创建者 (Creator)", ""))
    _set(desc, "owner", people.get("负责人 (Owner)", ""))
    # 时间
    _set(desc, "created", time_info.get("创建时间 (Created)", ""))
    # 测试信息
    if test:
        desc["test_info"] = test

    return desc


def extract_summary(parsed: dict) -> dict[str, Any]:
    """从 parse_ticket() 结果中提取 root cause + solution → summary.json。"""
    basic = parsed.get("基本信息", {})
    detail = parsed.get("缺陷详情", {})

    summary: dict[str, Any] = {}
    _set(summary, "id", basic.get("ID", ""))
    _set(summary, "root_cause_category", detail.get("根因分类 (Root Cause Category)", ""))
    _set(summary, "root_cause_sub_category", detail.get("根因子类 (Root Cause Sub-Category)", ""))
    # defectsolutionandresolve → RTC 界面"根本原因"
    _set(summary, "root_cause_detail", detail.get("根本原因 (Root Cause Detail)", ""))
    # defectresolve → RTC 界面"解决方案"
    _set(summary, "solution", detail.get("解决方案 (Solution)", ""))
    _set(summary, "discover_phase", detail.get("发现阶段 (Discover Phase)", ""))
    _set(summary, "introduce_phase", detail.get("引入阶段 (Introduce Phase)", ""))
    _set(summary, "issue_category", detail.get("问题分类 (Issue Category)", ""))
    _set(summary, "rejected_cause", detail.get("拒绝原因 (Rejected Cause)", ""))
    _set(summary, "pend_cause", detail.get("挂起原因 (Pend Cause)", ""))
    _set(summary, "defer_cause", detail.get("延迟原因 (Defer Cause)", ""))

    return summary


def _set(d: dict, key: str, value: Any) -> None:
    """仅在值非空时设置字段。"""
    if value:
        d[key] = value


def _save_json(path: Path, data: Any) -> None:
    """保存 JSON 文件（自动创建父目录）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# 下载逻辑
# ---------------------------------------------------------------------------

async def download_bug(
    rtc: RtcClient,
    bug_id: str,
    output_dir: Path,
    *,
    with_attachments: bool = True,
) -> dict[str, Any]:
    """下载单个 bug 的完整数据，按分目录存储。

    Returns:
        {"id": ..., "success": True/False, "error": ..., "attachments": ...}
    """
    bug_dir = output_dir / bug_id
    result: dict[str, Any] = {"id": bug_id, "success": False}

    try:
        # 1. 获取原始 OSLC 数据 → raw.json
        detail = await rtc.get_issue(bug_id, include_raw=True)
        raw_oslc = detail.pop("_raw_oslc", None)

        if raw_oslc:
            _save_json(bug_dir / "raw.json", raw_oslc)
        else:
            logger.warning("[%s] 未获取到原始 OSLC 数据", bug_id)
            result["error"] = "未获取到原始 OSLC 数据"
            return result

        # 2. 解析 → 拆分为 description.json + summary.json
        parsed = parse_ticket(raw_oslc)
        description = extract_description(parsed)
        summary = extract_summary(parsed)

        # 3. 获取评论 → 追加到 description
        try:
            comments = await rtc.get_comments(bug_id)
            if comments:
                description["comments"] = [
                    {
                        "creator": c.get("creator", ""),
                        "created": c.get("created", ""),
                        "body": c.get("body", ""),
                    }
                    for c in comments
                ]
                logger.info("[%s] %d 条评论", bug_id, len(comments))
        except Exception as e:
            logger.warning("[%s] 评论获取失败: %s", bug_id, e)

        _save_json(bug_dir / "description.json", description)
        _save_json(bug_dir / "summary.json", summary)

        title = description.get("title", "")[:60]
        logger.info("[%s] %s — 已保存 description.json + summary.json", bug_id, title)

        # 4. 下载附件 → attachments/
        att_summary: dict[str, Any] = {"total": 0, "success": 0, "failed": 0}
        if with_attachments:
            try:
                att_dir = str(bug_dir / "attachments")
                att_results = await rtc.download_all_attachments(bug_id, output_dir=att_dir)
                att_summary["total"] = len(att_results)
                att_summary["success"] = sum(1 for r in att_results if r.get("success"))
                att_summary["failed"] = att_summary["total"] - att_summary["success"]
                if att_summary["total"] > 0:
                    logger.info(
                        "[%s] 附件: %d/%d 成功",
                        bug_id, att_summary["success"], att_summary["total"],
                    )
            except Exception as e:
                logger.warning("[%s] 附件下载失败: %s", bug_id, e)
                att_summary["error"] = str(e)

        result["success"] = True
        result["title"] = description.get("title", "")
        result["attachments"] = att_summary

    except Exception as e:
        logger.error("[%s] 下载失败: %s", bug_id, e)
        result["error"] = str(e)

    return result


def _create_minio_uploader(config) -> MinioUploader | None:
    """根据配置创建 MinIO 上传客户端（endpoint 为空则返回 None）。"""
    minio_cfg = config.minio
    if not minio_cfg.endpoint:
        logger.error("MinIO endpoint 未配置，无法上传")
        return None
    return MinioUploader(
        endpoint=minio_cfg.endpoint,
        access_key=minio_cfg.access_key,
        secret_key=minio_cfg.secret_key,
        bucket=minio_cfg.bucket,
        prefix=minio_cfg.prefix,
        secure=minio_cfg.secure,
    )


def upload_bugs(
    bug_ids: list[str],
    output_dir: Path,
    uploader: MinioUploader,
) -> dict[str, Any]:
    """将已下载的 bug 产物上传到 MinIO。

    Returns:
        {"total": N, "success": N, "failed": N, "bugs": [...]}
    """
    total = len(bug_ids)
    logger.info("开始上传 %d 个 bug → MinIO", total)

    results: list[dict[str, Any]] = []
    for idx, bug_id in enumerate(bug_ids):
        bug_dir = output_dir / bug_id
        if not bug_dir.is_dir():
            logger.warning("[%d/%d] Bug %s 目录不存在，跳过: %s", idx + 1, total, bug_id, bug_dir)
            results.append({"id": bug_id, "success": False, "error": "目录不存在"})
            continue

        logger.info("=== [%d/%d] 上传 Bug %s ===", idx + 1, total, bug_id)
        r = uploader.upload_bug(bug_dir, bug_id)
        results.append({"id": bug_id, "success": r["failed"] == 0, **r})

    success_count = sum(1 for r in results if r.get("success"))
    logger.info("上传完成! 成功 %d / 失败 %d / 总计 %d", success_count, total - success_count, total)
    return {"total": total, "success": success_count, "failed": total - success_count, "bugs": results}


async def download_bugs(
    bug_ids: list[str],
    config_path: str | None = None,
    output_dir: str | None = None,
    with_attachments: bool = True,
    max_attachment_size_mb: int | None = None,
    upload: bool = False,
    project_name: str | None = None,
) -> str:
    """批量下载 bug 数据，生成 download_report.json。

    Args:
        upload: 下载完成后是否上传到 MinIO。
        project_name: RTC 项目名称（用于多 RTC 配置场景）。

    Returns:
        输出目录路径。
    """
    config = load_config(config_path)
    logger.info("配置来源: %s", config_path or "(自动探测)")

    # 获取指定的 RTC 配置
    rtc_config = config.get_rtc_config(project_name)
    if not rtc_config:
        if project_name:
            logger.error("未找到名为 %r 的 RTC 配置", project_name)
            raise ValueError(f"未找到名为 {project_name!r} 的 RTC 配置")
        else:
            logger.error("未配置任何 RTC")
            raise ValueError("未配置任何 RTC")

    logger.info(
        "RTC 配置: name=%r, ccm_url=%r, username=%r, project_area=%r, verify_ssl=%s",
        rtc_config.name or "(默认)",
        rtc_config.ccm_url,
        rtc_config.username,
        rtc_config.project_area_name,
        rtc_config.verify_ssl,
    )
    if not rtc_config.ccm_url:
        logger.error("RTC ccm_url 为空！请检查配置文件中 rtc.ccm_url 字段")
    if max_attachment_size_mb is not None:
        rtc_config.max_attachment_size_mb = max_attachment_size_mb
    rtc = RtcClient(rtc_config)

    out = Path(output_dir) if output_dir else Path(_CAGENT_ROOT) / "output"
    out.mkdir(parents=True, exist_ok=True)

    total = len(bug_ids)
    logger.info("开始下载 %d 个 bug → %s", total, out)

    results: list[dict[str, Any]] = []
    for idx, bug_id in enumerate(bug_ids):
        logger.info("=== [%d/%d] Bug %s ===", idx + 1, total, bug_id)
        r = await download_bug(rtc, bug_id, out, with_attachments=with_attachments)
        results.append(r)

    # 生成 download_report.json
    success_count = sum(1 for r in results if r.get("success"))
    failed_count = total - success_count
    report = {
        "downloaded_at": datetime.now().isoformat(),
        "output_dir": str(out),
        "total": total,
        "success": success_count,
        "failed": failed_count,
        "bugs": results,
    }
    _save_json(out / "download_report.json", report)

    logger.info(
        "完成! 成功 %d / 失败 %d / 总计 %d | 输出: %s",
        success_count, failed_count, total, out,
    )

    try:
        await rtc.close()
    except Exception:
        pass

    # 可选: 上传到 MinIO
    if upload:
        uploader = _create_minio_uploader(config)
        if uploader:
            successful_ids = [r["id"] for r in results if r.get("success")]
            if successful_ids:
                upload_bugs(successful_ids, out, uploader)
            else:
                logger.warning("没有成功下载的 bug，跳过上传")

    return str(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_id_file(path: str) -> list[str]:
    """从文件逐行读取 bug ID（忽略空行和 # 开头的注释）。"""
    ids: list[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                ids.append(line)
    return ids


def main() -> None:
    parser = argparse.ArgumentParser(
        description="按 Bug ID 下载 RTC 缺陷数据（分目录存储）",
    )
    parser.add_argument(
        "--id", default=None,
        help="单个 Bug ID",
    )
    parser.add_argument(
        "--ids", default=None,
        help="多个 Bug ID，逗号分隔 (如 12345,67890)",
    )
    parser.add_argument(
        "--id-file", default=None,
        help="从文件读取 Bug ID 列表（每行一个）",
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="输出目录 (默认 ./output)",
    )
    parser.add_argument(
        "--no-attachments", action="store_true",
        help="不下载附件",
    )
    parser.add_argument(
        "--config", default=None,
        help="配置文件路径 (默认自动探测 config.local.yaml > config.yaml)",
    )
    parser.add_argument(
        "--max-attachment-size", type=int, default=None,
        help="附件大小上限 (MB)，超过则跳过 (如 --max-attachment-size 10)",
    )
    parser.add_argument(
        "--upload", action="store_true",
        help="下载完成后上传到 MinIO",
    )
    parser.add_argument(
        "--upload-only", action="store_true",
        help="仅上传已有产物到 MinIO（不重新下载）",
    )
    parser.add_argument(
        "--project", default=None,
        help="RTC 项目名称（用于多 RTC 配置场景，匹配 config 中的 name 或 project_area_name）",
    )
    args = parser.parse_args()

    # 收集 bug ID
    bug_ids: list[str] = []
    if args.id:
        bug_ids.append(args.id)
    if args.ids:
        bug_ids.extend(x.strip() for x in args.ids.split(",") if x.strip())
    if args.id_file:
        bug_ids.extend(_parse_id_file(args.id_file))

    if not bug_ids:
        parser.error("请提供 --id, --ids 或 --id-file 中的至少一个")

    # 去重保持顺序
    seen: set[str] = set()
    unique_ids: list[str] = []
    for bid in bug_ids:
        if bid not in seen:
            seen.add(bid)
            unique_ids.append(bid)

    if args.upload_only:
        # 仅上传模式：不下载，直接上传已有产物
        config = load_config(args.config)
        uploader = _create_minio_uploader(config)
        if not uploader:
            sys.exit(1)
        out = Path(args.output_dir) if args.output_dir else Path(_CAGENT_ROOT) / "output"
        upload_bugs(unique_ids, out, uploader)
    else:
        asyncio.run(
            download_bugs(
                bug_ids=unique_ids,
                config_path=args.config,
                output_dir=args.output_dir,
                with_attachments=not args.no_attachments,
                max_attachment_size_mb=args.max_attachment_size,
                upload=args.upload,
                project_name=args.project,
            )
        )


if __name__ == "__main__":
    main()
