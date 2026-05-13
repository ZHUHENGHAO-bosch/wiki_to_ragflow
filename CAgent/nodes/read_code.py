"""
read_code.py — Node 3: 从 Git 读取相关代码

输入 State 字段: requirements[].linked_module_names, bug_info.components
输出 State 字段: code_info
依赖: GitClient
"""
from __future__ import annotations

import logging
import re
from typing import Any

from connectors.git_client import GitClient
from models import CodeInfo, CodeSnippet, GitCommit
from state import AnalysisState

logger = logging.getLogger(__name__)

MAX_FILES = 5
CONTEXT_LINES = 30


def create_read_code_node(git: GitClient):

    async def read_code(state: AnalysisState) -> dict[str, Any]:
        requirements = state.get("requirements", [])
        bug_info = state.get("bug_info")

        # 收集搜索关键词
        keywords: list[str] = []
        for req in requirements:
            keywords.extend(req.linked_module_names)
        if bug_info:
            keywords.extend(bug_info.components)

        # 去重
        keywords = list(dict.fromkeys(kw for kw in keywords if kw))

        if not keywords:
            logger.warning("[Node 3] 无搜索关键词")
            return {
                "code_info": None,
                "errors": state.get("errors", []) + ["未找到代码搜索关键词"],
            }

        logger.info(f"[Node 3] 搜索关键词: {keywords}")

        # 搜索相关文件
        all_files = git.search_files(keywords)

        if not all_files:
            logger.info("[Node 3] 未搜索到相关文件")
            return {
                "code_info": None,
                "errors": state.get("errors", []) + ["未找到相关代码文件"],
            }

        # 如果文件过多，取 top N (按匹配数排序，search_files 已排序)
        top_files = all_files[:MAX_FILES]

        logger.info(
            f"[Node 3] 找到 {len(all_files)} 个文件，取前 {len(top_files)} 个"
        )

        file_paths: list[str] = []
        all_snippets: list[CodeSnippet] = []
        all_commits: list[GitCommit] = []

        for finfo in top_files:
            repo_name = finfo["repo_name"]
            file_path = finfo["file_path"]
            file_paths.append(f"{repo_name}/{file_path}")

            # 读取文件内容
            content = git.get_file_content(repo_name, file_path)
            if content:
                snippets = _extract_snippets(content, keywords, file_path)
                all_snippets.extend(snippets)

            # 读取最近 commit
            commits_raw = git.get_recent_commits(repo_name, file_path)
            for c in commits_raw:
                gc = GitCommit(
                    hash=c["hash"],
                    author=c["author"],
                    date=c["date"],
                    message=c["message"],
                )
                if not any(
                    existing.hash == gc.hash for existing in all_commits
                ):
                    all_commits.append(gc)

        code_info = CodeInfo(
            files=file_paths,
            snippets=all_snippets,
            recent_commits=all_commits,
        )

        logger.info(
            f"[Node 3] 提取 {len(all_snippets)} 个代码片段, "
            f"{len(all_commits)} 个近期 commit"
        )
        return {"code_info": code_info}

    return read_code


def _extract_snippets(
    content: str,
    keywords: list[str],
    file_path: str,
    context_lines: int = CONTEXT_LINES,
) -> list[CodeSnippet]:
    """
    找关键词所在行，向上找函数开头 (C/C++ 函数定义模式)，
    向下截取 context_lines 行。
    """
    lines = content.split("\n")
    total_lines = len(lines)

    # C 函数定义的正则: 返回类型 + 函数名 + 括号
    func_pattern = re.compile(
        r"^[a-zA-Z_]\w*[\s*]+[a-zA-Z_]\w*\s*\("
    )

    # 找到所有命中行
    hit_lines: set[int] = set()
    for i, line in enumerate(lines):
        line_lower = line.lower()
        for kw in keywords:
            if kw.lower() in line_lower:
                hit_lines.add(i)
                break

    if not hit_lines:
        return []

    # 聚合相近的命中行为区域
    regions: list[tuple[int, int]] = []
    for hit in sorted(hit_lines):
        # 向上找函数开头
        start = hit
        for j in range(hit, max(hit - 50, -1), -1):
            if j < 0:
                break
            if func_pattern.match(lines[j]):
                start = j
                break

        end = min(start + context_lines, total_lines)

        # 合并重叠区域
        if regions and start <= regions[-1][1]:
            regions[-1] = (regions[-1][0], max(regions[-1][1], end))
        else:
            regions.append((start, end))

    # 推断语言
    lang = _infer_language(file_path)

    snippets: list[CodeSnippet] = []
    for start, end in regions[:3]:  # 最多 3 个片段
        snippet_content = "\n".join(lines[start:end])
        snippets.append(
            CodeSnippet(
                file_path=file_path,
                start_line=start + 1,
                end_line=end,
                content=snippet_content,
                language=lang,
            )
        )

    return snippets


def _infer_language(file_path: str) -> str:
    """根据文件扩展名推断语言。"""
    ext_map = {
        ".c": "c",
        ".h": "c",
        ".cpp": "cpp",
        ".hpp": "cpp",
        ".py": "python",
        ".java": "java",
        ".rs": "rust",
        ".go": "go",
    }
    for ext, lang in ext_map.items():
        if file_path.endswith(ext):
            return lang
    return ""
