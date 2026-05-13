"""
connectors/git_client.py — Git 操作封装

使用 GitPython 进行 Git 操作。纯工具封装，不感知 LangGraph。
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from git import Repo

from config import GitRepoConfig, RepoEntry

logger = logging.getLogger(__name__)


class GitClient:
    """Git 仓库操作客户端。"""

    def __init__(self, config: GitRepoConfig) -> None:
        self._config = config
        self._repos: dict[str, Repo] = {}

        for entry in config.repos:
            try:
                repo = Repo(entry.path)
                self._repos[entry.name] = repo
                logger.info(f"加载 Git 仓库: {entry.name} ({entry.path})")
            except Exception as e:
                logger.error(f"无法加载 Git 仓库 {entry.name}: {e}")

    async def pull_all(self) -> None:
        """拉取所有仓库的最新代码。"""
        for name, repo in self._repos.items():
            try:
                entry = self._get_entry(name)
                if entry and not repo.bare:
                    origin = repo.remotes.origin
                    origin.pull(entry.branch)
                    logger.info(f"拉取 {name}/{entry.branch} 成功")
            except Exception as e:
                logger.warning(f"拉取 {name} 失败: {e}")

    def search_files(
        self, keywords: list[str], repo_name: str | None = None
    ) -> list[dict[str, Any]]:
        """
        在 Git 仓库中搜索包含关键词的文件。

        返回列表，每项包含: repo_name, file_path, match_count
        """
        results: list[dict[str, Any]] = []
        repos = (
            {repo_name: self._repos[repo_name]}
            if repo_name and repo_name in self._repos
            else self._repos
        )

        extensions = set(self._config.search_extensions)

        for rname, repo in repos.items():
            try:
                tree = repo.head.commit.tree
                for blob in tree.traverse():
                    if not hasattr(blob, "path"):
                        continue
                    fpath = str(blob.path)
                    suffix = Path(fpath).suffix
                    if suffix not in extensions:
                        continue

                    try:
                        content = blob.data_stream.read().decode(
                            "utf-8", errors="replace"
                        )
                    except Exception:
                        continue

                    content_lower = content.lower()
                    match_count = sum(
                        content_lower.count(kw.lower()) for kw in keywords if kw
                    )
                    if match_count > 0:
                        results.append(
                            {
                                "repo_name": rname,
                                "file_path": fpath,
                                "match_count": match_count,
                            }
                        )
            except Exception as e:
                logger.warning(f"搜索 {rname} 失败: {e}")

        results.sort(key=lambda x: x["match_count"], reverse=True)
        return results

    def get_file_content(self, repo_name: str, file_path: str) -> str | None:
        """读取指定仓库中文件的内容。"""
        repo = self._repos.get(repo_name)
        if not repo:
            return None
        try:
            blob = repo.head.commit.tree[file_path]
            return blob.data_stream.read().decode("utf-8", errors="replace")
        except (KeyError, Exception) as e:
            logger.warning(f"读取 {repo_name}/{file_path} 失败: {e}")
            return None

    def get_recent_commits(
        self, repo_name: str, file_path: str | None = None, weeks: int | None = None
    ) -> list[dict[str, str]]:
        """
        获取最近的 commit 列表。

        如果指定 file_path，只返回涉及该文件的 commit。
        """
        repo = self._repos.get(repo_name)
        if not repo:
            return []

        weeks = weeks or self._config.recent_commit_weeks
        since = datetime.now() - timedelta(weeks=weeks)
        since_str = since.strftime("%Y-%m-%d")

        try:
            args = ["--since", since_str, "--max-count", "20"]
            if file_path:
                args.extend(["--", file_path])
            commits = list(repo.iter_commits("HEAD", **_parse_git_args(args)))
        except Exception as e:
            logger.warning(f"获取 {repo_name} commit 失败: {e}")
            return []

        return [
            {
                "hash": str(c.hexsha)[:8],
                "author": str(c.author),
                "date": c.committed_datetime.isoformat(),
                "message": c.message.strip().split("\n")[0],
            }
            for c in commits
        ]

    def search_callers(
        self, repo_name: str, function_name: str
    ) -> list[dict[str, Any]]:
        """
        搜索调用了指定函数的所有文件。

        通过 grep 函数名在所有源码文件中查找。
        """
        results: list[dict[str, Any]] = []
        repo = self._repos.get(repo_name)
        if not repo:
            return results

        extensions = set(self._config.search_extensions)
        pattern = re.compile(re.escape(function_name) + r"\s*\(")

        try:
            tree = repo.head.commit.tree
            for blob in tree.traverse():
                if not hasattr(blob, "path"):
                    continue
                fpath = str(blob.path)
                if Path(fpath).suffix not in extensions:
                    continue

                try:
                    content = blob.data_stream.read().decode(
                        "utf-8", errors="replace"
                    )
                except Exception:
                    continue

                lines = content.split("\n")
                call_lines: list[int] = []
                for i, line in enumerate(lines, start=1):
                    if pattern.search(line):
                        call_lines.append(i)

                if call_lines:
                    results.append(
                        {
                            "repo_name": repo_name,
                            "file_path": fpath,
                            "call_lines": call_lines,
                            "call_count": len(call_lines),
                        }
                    )
        except Exception as e:
            logger.warning(f"搜索调用方失败: {e}")

        return results

    def get_blame(
        self, repo_name: str, file_path: str, start_line: int, end_line: int
    ) -> list[dict[str, str]]:
        """获取指定行范围的 blame 信息。"""
        repo = self._repos.get(repo_name)
        if not repo:
            return []

        try:
            blame = repo.blame("HEAD", file_path)
        except Exception as e:
            logger.warning(f"blame {repo_name}/{file_path} 失败: {e}")
            return []

        results: list[dict[str, str]] = []
        current_line = 1
        for commit, lines in blame:
            for _line in lines:
                if start_line <= current_line <= end_line:
                    results.append(
                        {
                            "line": str(current_line),
                            "hash": str(commit.hexsha)[:8],
                            "author": str(commit.author),
                            "date": commit.committed_datetime.isoformat(),
                        }
                    )
                current_line += 1
                if current_line > end_line:
                    break
            if current_line > end_line:
                break

        return results

    # ── 内部 ──

    def _get_entry(self, name: str) -> RepoEntry | None:
        for e in self._config.repos:
            if e.name == name:
                return e
        return None


def _parse_git_args(args: list[str]) -> dict[str, Any]:
    """将 git 命令行参数转为 GitPython kwargs。"""
    kwargs: dict[str, Any] = {}
    i = 0
    while i < len(args):
        if args[i] == "--since" and i + 1 < len(args):
            kwargs["since"] = args[i + 1]
            i += 2
        elif args[i] == "--max-count" and i + 1 < len(args):
            kwargs["max_count"] = int(args[i + 1])
            i += 2
        elif args[i] == "--":
            if i + 1 < len(args):
                kwargs["paths"] = args[i + 1]
            i += 2
        else:
            i += 1
    return kwargs
