"""
main.py — Wiki → RAGFlow 同步入口

支持五种模式：
1. download-confluence:    仅下载 Confluence 页面树（不上传）
2. upload-ragflow:         仅上传本地文件到 RAGFlow 知识库
3. confluence-to-ragflow:  端到端管道：下载 → 上传 → 解析 → 检查结果（推荐）
4. list-datasets:          列出 RAGFlow 上所有可见 dataset（运维）
5. delete-dataset:         删除指定 dataset（运维，默认要二次确认）

用法：
    python main.py --confluence-to-ragflow URL     # 端到端管道（单 URL/Page ID）
    python main.py --confluence-to-ragflow batch.csv  # 端到端管道（CSV 批量）
    python main.py --download-confluence URL       # 仅下载
    python main.py --upload-ragflow f1.md f2.pdf   # 仅上传
    python main.py --list-datasets                 # 查看所有 dataset
    python main.py --delete-dataset taiji1.0_test  # 按名字删 dataset
    python main.py --delete-dataset <id> --delete-by-id -y  # 按 id 强删

    --config path/to/config.yaml   # 指定配置文件
    --confluence-format md|json           # 输出格式（覆盖 config）
    --confluence-output ./dir      # 输出目录（覆盖 config）
    --confluence-depth 5           # 最大遍历深度
    --ragflow-dataset NAME         # RAGFlow dataset 名称（覆盖 config）
    --yes / -y                     # 跳过删除确认（用于脚本/CI）
    --verbose                      # 详细日志
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import logging
import os
import re
import sys
from pathlib import Path

from config import AppConfig, load_config
from connectors.confluence_client import ConfluenceClient
from connectors.ragflow_client import RAGFlowClient
from services.confluence_downloader import ConfluenceDownloader

logger = logging.getLogger("wiki_to_ragflow")


def main() -> None:
    args = _parse_args()
    _setup_logging(verbose=args.verbose)

    logger.info("加载配置...")
    config = load_config(args.config)

    if args.list_datasets:
        asyncio.run(_run_list_datasets(config))
    elif args.delete_dataset:
        asyncio.run(
            _run_delete_dataset(
                config, args.delete_dataset,
                by_id=args.delete_by_id,
                yes=args.yes,
            )
        )
    elif args.merge_md:
        merged = _merge_tree_to_single_md(Path(args.merge_md))
        print(f"\n合并后单文件: {merged}")
        if args.then_upload:
            logger.info("继续：把合并文件上传到 RAGFlow...")
            asyncio.run(
                _run_ragflow_upload(
                    config, [str(merged)], args.ragflow_dataset,
                )
            )
    elif args.upload_ragflow:
        asyncio.run(
            _run_ragflow_upload(
                config, args.upload_ragflow, args.ragflow_dataset,
            )
        )
    elif args.confluence_to_ragflow:
        asyncio.run(
            _run_confluence_to_ragflow(
                config,
                args.confluence_to_ragflow,
                args.confluence_output,
                args.confluence_depth,
                args.confluence_format,
                args.ragflow_dataset,
                merge=args.merge,
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
                discover_only=args.discover_only,
            )
        )
    else:
        logger.error(
            "未指定运行模式。可选: --confluence-to-ragflow / --download-confluence / "
            "--upload-ragflow / --list-datasets / --delete-dataset。"
            "运行 python main.py -h 查看帮助。"
        )
        sys.exit(1)


# ── 公共工具 ──


async def _create_ragflow_client(config: AppConfig) -> RAGFlowClient | None:
    """创建并初始化 RAGFlow 客户端 (如果已配置)。"""
    if not config.ragflow.base_url or not config.ragflow.api_key:
        return None

    client = RAGFlowClient(config.ragflow)
    await client.init()
    return client


# ── 模式 4: RAGFlow 运维 (list / delete dataset) ──


async def _run_list_datasets(config: AppConfig) -> None:
    """CLI 模式: 列出当前 API key 可见的所有 dataset。"""
    if not config.ragflow.base_url or not config.ragflow.api_key:
        logger.error(
            "RAGFlow 未配置。请在配置文件中设置 ragflow.base_url 和 ragflow.api_key"
        )
        sys.exit(1)

    client = RAGFlowClient(config.ragflow)
    try:
        datasets = await client.list_all_datasets()
    finally:
        await client.close()

    if not datasets:
        print("(没有可见的 dataset)")
        return

    name_w = max(len("name"), max(len(d["name"]) for d in datasets))
    print(
        f"{'name'.ljust(name_w)}  "
        f"{'docs':>5}  {'chunks':>6}  "
        f"{'chunk_method'.ljust(12)}  id"
    )
    print("-" * (name_w + 5 + 6 + 12 + 32 + 12))
    for d in datasets:
        print(
            f"{d['name'].ljust(name_w)}  "
            f"{d['document_count']:>5}  {d['chunk_count']:>6}  "
            f"{(d['chunk_method'] or '').ljust(12)}  {d['id']}"
        )
    print(f"\n共 {len(datasets)} 个 dataset")


async def _run_delete_dataset(
    config: AppConfig,
    name_or_id: str,
    by_id: bool = False,
    yes: bool = False,
) -> None:
    """CLI 模式: 删除指定 dataset。默认按名称匹配，传 --delete-by-id 用 id。"""
    if not config.ragflow.base_url or not config.ragflow.api_key:
        logger.error(
            "RAGFlow 未配置。请在配置文件中设置 ragflow.base_url 和 ragflow.api_key"
        )
        sys.exit(1)

    client = RAGFlowClient(config.ragflow)
    try:
        # 先解析出 dataset，给用户看一下 chunk_count / doc_count 再决定
        datasets = await client.list_all_datasets()
        if by_id:
            matched = [d for d in datasets if d["id"] == name_or_id]
        else:
            matched = [d for d in datasets if d["name"] == name_or_id]

        if not matched:
            logger.error(
                f"未找到 dataset (按 {'id' if by_id else 'name'}='{name_or_id}')。"
                f"当前可见: {[d['name'] for d in datasets]}"
            )
            sys.exit(1)
        if len(matched) > 1:
            logger.error(
                f"匹配到多个 dataset: {[(d['name'], d['id']) for d in matched]}。"
                "请使用 --delete-by-id 精确指定。"
            )
            sys.exit(1)

        target = matched[0]
        logger.warning(
            f"即将删除 dataset:\n"
            f"  name      = {target['name']}\n"
            f"  id        = {target['id']}\n"
            f"  documents = {target['document_count']}\n"
            f"  chunks    = {target['chunk_count']}\n"
            f"此操作不可恢复。"
        )

        if not yes:
            ans = input("输入 'yes' 确认删除: ").strip().lower()
            if ans != "yes":
                logger.info("已取消")
                return

        await client.delete_dataset(target["id"], by_id=True)
        logger.info(
            f"删除成功: name={target['name']} id={target['id']}"
        )
    finally:
        await client.close()


# ── 模式 1: 仅上传到 RAGFlow ──


async def _run_ragflow_upload(
    config: AppConfig,
    file_paths: list[str],
    ragflow_dataset: str | None = None,
) -> None:
    """CLI 模式: 上传文件到 RAGFlow 知识库。

    Args:
        file_paths: 可以是文件或目录混合。目录会递归扫描出所有
            ``_RAGFLOW_ATTACHMENT_EXTS`` 白名单内的文件；自动跳过
            ``_json_cache`` / ``_images`` / ``_pdf_cache`` 这类内部目录。
        ragflow_dataset: 覆盖 config 中的 dataset_name；None 则用 config 默认。
    """
    from pathlib import Path

    if not config.ragflow.base_url or not config.ragflow.api_key:
        logger.error(
            "RAGFlow 未配置。请在配置文件中设置 ragflow.base_url 和 ragflow.api_key"
        )
        sys.exit(1)

    # 把混合输入（目录/文件）展平为"实际要上传的文件列表"
    paths = _expand_to_uploadable_files([Path(p) for p in file_paths])
    if not paths:
        logger.error("没有可上传的文件，退出")
        sys.exit(1)
    logger.info(f"准备上传 {len(paths)} 个文件到 RAGFlow")

    client = RAGFlowClient(config.ragflow)
    try:
        await client.init(dataset_name=ragflow_dataset)
        result = await client.upload_and_parse(paths)
        logger.info(
            f"RAGFlow 上传完成: {len(result['uploaded'])} 个文件上传, "
            f"{result['parse_count']} 个文件解析中"
        )
    finally:
        await client.close()


# 可上传到 RAGFlow 的附件扩展名（含有可检索的文本内容）。
# 注意：图片类（.png/.jpg/...）刻意排除——它们只是 MD 的内嵌资源，
# 已通过 _images/ 目录被 MD 文件引用，不应作为独立文档进入 RAG 索引。
_RAGFLOW_ATTACHMENT_EXTS: set[str] = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".csv", ".md", ".html", ".htm",
}

# 扫描目录时要跳过的内部目录（缓存/中间产物，不该进 RAG）。
_RAGFLOW_SKIP_DIRS: set[str] = {
    "_json_cache", "_pdf_cache", "_images", "_attachments",
}


def _expand_to_uploadable_files(inputs: list[Path]) -> list[Path]:
    """把目录展开为目录内所有可上传文件，过滤不存在/不支持的项。

    规则：
    - 不存在路径 → warning 跳过
    - 文件：扩展名在白名单内即收，否则跳过并 warning
    - 目录：``rglob("*")`` 取所有白名单扩展名文件，跳过 ``_RAGFLOW_SKIP_DIRS``
      内的内部目录（缓存/图片资源）和 ``_tree.json``。
    """
    from pathlib import Path
    out: list[Path] = []
    seen: set[Path] = set()
    for p in inputs:
        if not p.exists():
            logger.warning(f"路径不存在，跳过: {p}")
            continue
        if p.is_file():
            if p.suffix.lower() in _RAGFLOW_ATTACHMENT_EXTS:
                rp = p.resolve()
                if rp not in seen:
                    seen.add(rp)
                    out.append(p)
            else:
                logger.warning(
                    f"扩展名 {p.suffix} 不在 RAGFlow 上传白名单内，跳过: {p}"
                )
            continue
        # 目录：递归
        for f in p.rglob("*"):
            if not f.is_file():
                continue
            if f.suffix.lower() not in _RAGFLOW_ATTACHMENT_EXTS:
                continue
            # 跳过任何一级祖先是内部目录的（如 _json_cache 下的 .json）
            if any(part in _RAGFLOW_SKIP_DIRS for part in f.parts):
                continue
            if f.name == "_tree.json":
                continue
            rp = f.resolve()
            if rp in seen:
                continue
            seen.add(rp)
            out.append(f)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Tree → 单文件合并
#
# 把 ``--download-confluence ... --confluence-format md`` 生成的树状 MD 目录，
# 按父子层级合并为单一 MD 文件，文件名 = 根页面标题。
# 用途：方便整体作为一份知识库文档上传到 RAGFlow（避免几十个小文件污染索引）。
# ─────────────────────────────────────────────────────────────────────────────


_MD_HEADER_SPLIT_RE = re.compile(r"^---\s*$", re.MULTILINE)
_MD_IMG_REF_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def _strip_md_self_header(md_text: str) -> str:
    """剥掉单页 MD 顶部的"# 标题 + > Source/Last modified + ---"那一块。

    生成时 ``blocks_to_markdown`` 总会写出：

        # <title>
        > Source: ...
        > Last modified: ...
        ---
        <正文>

    合并时上层会重新生成更合适层级的标题，所以这块要去掉，避免重复。
    """
    parts = _MD_HEADER_SPLIT_RE.split(md_text, maxsplit=1)
    if len(parts) == 2:
        body = parts[1]
    else:
        body = md_text
    return body.lstrip("\n")


def _rewrite_image_refs_for_merge(
    md_text: str,
    src_md_dir: Path,
    merged_md_dir: Path,
) -> str:
    """把"相对原 MD 父目录"的图片引用 → 改写为"相对合并后 MD 父目录"。

    例：合并前 ``out/A/B/page.md`` 引用 ``../../_images/Foo/x.png``；
        合并后 ``out/<root>.md`` 引用 ``_images/Foo/x.png``。
    """
    src_abs = src_md_dir.resolve()
    dst_abs = merged_md_dir.resolve()

    def _rewrite(match: re.Match[str]) -> str:
        from urllib.parse import quote, unquote
        alt, path = match.group(1), match.group(2)
        decoded = unquote(path)
        # 外部 URL 不动
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", decoded):
            return match.group(0)
        abs_target = (src_abs / decoded).resolve()
        try:
            new_rel = Path(os.path.relpath(abs_target, dst_abs)).as_posix()
        except ValueError:
            return match.group(0)
        encoded = quote(new_rel, safe="/:?&=#%~+")
        return f"![{alt}]({encoded})"

    return _MD_IMG_REF_RE.sub(_rewrite, md_text)


def _merge_tree_to_single_md(output_dir: Path) -> Path:
    """读取 ``<output_dir>/_tree.json``，按 DFS 父子顺序合并所有 .md 为单文件。

    Returns
    -------
    Path
        合并后产物的绝对路径：``<output_dir>/<根标题>.md``。
    """
    import json
    tree_path = output_dir / "_tree.json"
    if not tree_path.exists():
        raise FileNotFoundError(
            f"未找到 {tree_path}。请先用 --download-confluence --confluence-format md "
            f"生成树状 MD 目录。"
        )

    tree = json.loads(tree_path.read_text(encoding="utf-8"))
    pages: dict = tree.get("pages", {})
    root_id: str | None = tree.get("root_page_id")
    root_title: str = tree.get("root_page_title", "merged") or "merged"
    if not root_id or root_id not in pages:
        raise ValueError(f"_tree.json 缺少 root_page_id 或根页面信息: {root_id}")

    # 合并文件名 = root_title 做安全清洗
    safe_root = re.sub(r'[<>:"/\\|?*]', "_", root_title).strip(". ") or "merged"
    merged_path = output_dir / f"{safe_root}.md"

    out_lines: list[str] = []
    visited: set[str] = set()
    counts = {"with_content": 0, "folder_only": 0, "missing_file": 0}

    # 顶部一段元信息
    out_lines.append(f"# {root_title}")
    out_lines.append("")
    out_lines.append(
        f"> Merged from {len(pages)} Confluence pages "
        f"（自动生成，请勿手工编辑）"
    )
    out_lines.append("")
    out_lines.append("---")
    out_lines.append("")

    def visit(pid: str, depth: int) -> None:
        if pid in visited:
            return
        visited.add(pid)
        info = pages.get(pid)
        if not info:
            return

        title = info.get("title") or f"page_{pid}"
        # 根 (depth=0) = H1 已经在顶部写过；
        # 根的直接子 (depth=1) → H2；再往下递增；H6 兜底。
        level = max(2, min(6, depth + 1))

        # 不重复写根标题
        if pid != root_id:
            out_lines.append("#" * level + " " + title)
            out_lines.append("")

        md_rel = info.get("path")
        if md_rel:
            md_file = output_dir / md_rel
            if md_file.exists():
                raw = md_file.read_text(encoding="utf-8")
                body = _strip_md_self_header(raw)
                body = _rewrite_image_refs_for_merge(
                    body, md_file.parent, output_dir,
                )
                body = body.rstrip() + "\n"
                if body.strip():
                    out_lines.append(body)
                    out_lines.append("")
                    counts["with_content"] += 1
            else:
                counts["missing_file"] += 1
                out_lines.append(f"> _(文件不存在: {md_rel})_")
                out_lines.append("")
        else:
            counts["folder_only"] += 1
            # 仅目录节点 → 给一个轻提示，避免 ChatGPT 类读起来突兀
            if pid != root_id:
                out_lines.append(
                    "> _(分类目录，无独立正文)_"
                )
                out_lines.append("")

        for cid in info.get("children", []) or []:
            visit(cid, depth + 1)

    visit(root_id, 0)

    merged_path.write_text("\n".join(out_lines), encoding="utf-8")
    logger.info(
        f"合并完成 → {merged_path.name}  "
        f"({counts['with_content']} 个含正文页，"
        f"{counts['folder_only']} 个目录，"
        f"{counts['missing_file']} 个文件缺失)"
    )
    return merged_path


def _print_tree_summary(output_dir: str) -> None:
    """读取 _tree.json，打印树概览（页数、深度分布、Top hub 页）。

    用于 --discover-only 后给用户一个全局印象，决定是否做完整下载。
    """
    import json as _json
    from collections import Counter
    from pathlib import Path

    tree_path = Path(output_dir) / "_tree.json"
    if not tree_path.exists():
        logger.warning(f"未找到 {tree_path}，跳过摘要")
        return

    try:
        tree = _json.loads(tree_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(f"解析 _tree.json 失败: {e}")
        return

    pages: dict = tree.get("pages", {})
    if not pages:
        logger.info("(未发现任何页面)")
        return

    depth_hist = Counter(p.get("depth", -1) for p in pages.values())
    by_children = sorted(
        pages.items(),
        key=lambda kv: len(kv[1].get("children", [])),
        reverse=True,
    )

    # 粗略估算正文下载耗时:
    # request_delay 0.3s + 平均 1-2 张图 + 并发 5 → 每页约 1-2s 实际墙钟
    n = len(pages)
    eta_min = max(1, int(n * 1.2 / 60))
    eta_max = max(1, int(n * 2.5 / 60))

    print()
    print("═" * 60)
    print(f"  Discover-only 完成: 共发现 {n} 个页面")
    print(f"  根: {tree.get('root_page_title', '?')} (id={tree.get('root_page_id', '?')})")
    print("═" * 60)
    print()
    print("  深度分布 (depth=0 是根页):")
    for d in sorted(depth_hist):
        bar = "█" * min(40, depth_hist[d])
        print(f"    depth {d:2d}  {depth_hist[d]:5d}  {bar}")
    print()
    print(f"  Top 10 hub 页 (直接子页最多的):")
    for pid, p in by_children[:10]:
        children = p.get("children", [])
        if not children:
            break
        print(
            f"    [{len(children):3d} children]  "
            f"depth={p.get('depth','?'):>2}  "
            f"{p.get('title','?')}"
        )
    print()
    print(f"  做完整下载预计耗时: 约 {eta_min}-{eta_max} 分钟")
    print(
        f"  命令: python main.py --download-confluence <URL> "
        f"--confluence-format md --confluence-depth 999 "
        f"--confluence-output {output_dir}"
    )
    print("═" * 60)


# ── 模式 2: 仅下载 Confluence ──


async def _run_confluence_download(
    config: AppConfig,
    target: str,
    output: str | None,
    depth: int | None,
    save_format: str | None = None,
    discover_only: bool = False,
) -> None:
    """CLI 模式: 下载 Confluence 页面树，支持单个 URL/ID 或 CSV 批量。

    discover_only: 仅 BFS 发现整棵树，不抓正文。完成后打印树概览，
    并生成 _tree.json 方便用户决定是否做完整下载。
    """
    if not config.confluence.base_url:
        logger.error("Confluence 未配置。请在 config.yaml 中设置 confluence.base_url")
        sys.exit(1)

    # 自动创建 RAGFlow 客户端 (如果配置了自动上传)
    # discover_only 模式下不需要 RAGFlow，避免无谓的连接。
    ragflow_client: RAGFlowClient | None = None
    if config.ragflow.auto_upload_after_confluence and not discover_only:
        ragflow_client = await _create_ragflow_client(config)
        if ragflow_client:
            logger.info("RAGFlow 自动上传已启用")
        else:
            logger.warning(
                "ragflow.auto_upload_after_confluence=true 但 RAGFlow 未正确配置"
            )

    try:
        if target.lower().endswith(".csv"):
            if discover_only:
                logger.error("--discover-only 暂不支持 CSV 批量模式")
                sys.exit(1)
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
                ok = await _run_confluence_single(
                    downloader, target, output, depth, save_format,
                    discover_only=discover_only,
                )
                if ok and discover_only:
                    _print_tree_summary(output or config.confluence.default_output_dir)
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
    discover_only: bool = False,
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
        discover_only=discover_only,
    )
    logger.info(f"下载任务已启动: {task_id}")

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

    entries: list[dict[str, str]] = []
    with open(csv_path, encoding="utf-8-sig") as f:  # utf-8-sig 处理 Excel BOM
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",\t;")
        except csv.Error:
            dialect = None
        reader = csv.DictReader(f, dialect=dialect) if dialect else csv.DictReader(f)
        if not reader.fieldnames or not {"file_name", "link"}.issubset(
            set(reader.fieldnames)
        ):
            logger.error(
                f"CSV 缺少必要列。需要: file_name, link。"
                f"实际列: {reader.fieldnames}"
            )
            sys.exit(1)

        for i, row in enumerate(reader, start=2):
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
                    output_filename=None,
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


# ── 模式 3: 端到端管道 (推荐) ──


async def _run_confluence_to_ragflow(
    config: AppConfig,
    target: str,
    output: str | None,
    depth: int | None,
    save_format: str | None,
    ragflow_dataset: str | None,
    merge: bool = False,
) -> None:
    """端到端管道: 下载 Confluence → 上传 RAGFlow → 解析 → 检查结果。

    当 ``merge=True`` 时，在上传前会先把树状 MD 合并为单个文件，再仅上传该合并文件。
    仅在 ``save_format == "md"`` 时生效。
    """
    from pathlib import Path

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

    # 默认 md 格式，端到端管道仅支持 md / json（html 不会触发 RAGFlow 路径）
    effective_format = save_format or config.confluence.save_format or "md"
    if effective_format not in ("md", "json"):
        logger.warning(
            f"端到端管道仅支持 md/json 格式，已忽略 "
            f"--confluence-format={save_format}，使用 md"
        )
        effective_format = "md"

    output_dir = output or config.confluence.default_output_dir
    output_path = Path(output_dir)

    # 记录下载前已有的文件（含 mtime），用于识别新增/更新的文件
    file_ext = f".{effective_format}"
    # md 与 json 共用 _json_cache（缓存的中间数据是 JSON）
    cache_dir_name = "_json_cache"
    existing_files: dict[Path, float] = {}
    if output_path.exists():
        for p in output_path.rglob(f"*{file_ext}"):
            if cache_dir_name not in p.parts and "_tree.json" not in p.name:
                existing_files[p] = p.stat().st_mtime
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
                # MD 模式下内嵌图片由 _download_content_images 单独处理到
                # _images/，无需再走 _attachments/ 路径。是否下载其它附件
                # （PDF/Excel 等）尊重 config.confluence.download_attachments。
                download_attachments=None,
            )
        finally:
            await client.close()

    # ── 阶段 1→2 衔接: 收集本次新增/更新的文件 ──
    new_files = sorted(
        p for p in output_path.rglob(f"*{file_ext}")
        if cache_dir_name not in p.parts
        and "_tree.json" not in p.name
        and (p not in existing_files or p.stat().st_mtime > existing_files[p])
    )

    new_attachments = sorted(
        p for p in output_path.rglob("_attachments/**/*")
        if p.is_file()
        and p.suffix.lower() in _RAGFLOW_ATTACHMENT_EXTS
        and (p not in existing_files or p.stat().st_mtime > existing_files[p])
    )

    all_files = new_files + new_attachments

    # ── 可选: 合并所有 MD 为单文件，仅上传该文件 ──
    if merge:
        if effective_format != "md":
            logger.warning(
                f"--merge 仅在 md 格式下生效，已忽略 (当前 format={effective_format})"
            )
        else:
            logger.info("═══ 阶段 1.5/4: 合并树状 MD 为单文件 ═══")
            try:
                merged_file = _merge_tree_to_single_md(output_path)
            except Exception as exc:
                logger.error(f"合并失败: {exc}")
                sys.exit(1)
            logger.info(f"合并完成 → {merged_file}")
            # 合并模式只上传这一个文件，绕开增量识别
            all_files = [merged_file]

    if not all_files:
        logger.error(f"输出目录中未找到可上传文件: {output_path}")
        sys.exit(1)

    if not merge:
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


# ── CLI 参数 / 日志 ──


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Wiki → RAGFlow 同步工具：抓取 Confluence 页面，转 Markdown，"
                    "上传到 RAGFlow 知识库，更新供 RAGChat 检索的 dataset。"
    )
    parser.add_argument(
        "--config", type=str, default=None, help="配置文件路径"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="详细日志"
    )
    # 模式 1: 端到端管道（推荐）
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
    # 模式 2: 仅下载
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
        choices=["json", "md"],
        default=None,
        help="Confluence 页面保存格式 (md / json)",
    )
    parser.add_argument(
        "--discover-only",
        action="store_true",
        help="仅 BFS 发现整棵树并打印摘要，不抓正文/图片 "
             "(快速估算页数和层级，决定要不要完整下载)",
    )
    # 模式 3: 仅上传
    parser.add_argument(
        "--upload-ragflow",
        type=str,
        nargs="+",
        metavar="FILE_OR_DIR",
        help="上传文件或目录到 RAGFlow 知识库（目录会递归扫描白名单扩展名）",
    )
    parser.add_argument(
        "--merge-md",
        type=str,
        default=None,
        metavar="OUTPUT_DIR",
        help="把 <OUTPUT_DIR>/_tree.json 下整棵树合并成单个 .md "
             "(文件名 = 根页面标题)；可与 --then-upload 串联",
    )
    parser.add_argument(
        "--then-upload",
        action="store_true",
        help="配合 --merge-md：合并完直接把单文件上传到 RAGFlow",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="配合 --confluence-to-ragflow：在上传前把整棵树合并成单个 .md，"
             "再仅上传该合并文件（仅 md 格式生效）",
    )
    # 模式 4: RAGFlow 运维 (list / delete dataset)
    parser.add_argument(
        "--list-datasets",
        action="store_true",
        help="列出 RAGFlow 上当前 API key 可见的所有 dataset",
    )
    parser.add_argument(
        "--delete-dataset",
        type=str,
        default=None,
        metavar="NAME_OR_ID",
        help="删除指定 dataset (默认按 name 匹配, 加 --delete-by-id 用 id)",
    )
    parser.add_argument(
        "--delete-by-id",
        action="store_true",
        help="配合 --delete-dataset 使用，按 dataset id 而非 name 删除",
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="跳过删除确认提示 (用于脚本/CI)",
    )
    return parser.parse_args()


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


if __name__ == "__main__":
    main()
