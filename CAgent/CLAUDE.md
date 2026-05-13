# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CAgent is a **Bug Analysis Daemon** that automatically analyzes software bugs by reading bug reports from issue trackers (Jira or RTC), tracing through linked test cases → requirements → code, using Claude LLM to determine root causes, and writing analysis reports back to the tracker. It can also send notifications to Microsoft Teams.

**Language**: Python 3.11+ | **Framework**: LangGraph (state-driven DAG) | **Async**: All I/O is async (httpx, asyncio)

## Development Environment

- **Virtual environment**: `~/CAgent_env/` — 始终使用此 venv 运行命令
- **Platform**: WSL2 (Windows Subsystem for Linux)，注意 CRLF/LF 行尾差异
- No linter or formatter is configured. No pyproject.toml or setup.py — this is a standalone daemon, not a package.

## Common Commands

```bash
# 使用虚拟环境
source ~/CAgent_env/bin/activate
# 或直接使用完整路径
~/CAgent_env/bin/pytest tests/
~/CAgent_env/bin/python main.py

# Install dependencies
~/CAgent_env/bin/pip install -r requirements.txt

# Run all tests
~/CAgent_env/bin/pytest tests/

# Run a single test file
~/CAgent_env/bin/pytest tests/test_nodes.py

# Run tests matching a name pattern
~/CAgent_env/bin/pytest -k "test_success"

# Run the daemon (various modes)
~/CAgent_env/bin/python main.py                        # webhook mode (default)
~/CAgent_env/bin/python main.py --mode polling         # polling mode
~/CAgent_env/bin/python main.py --once PRJ-123         # analyze single bug (Jira)
~/CAgent_env/bin/python main.py --once 12345 --source rtc  # analyze single bug (RTC)
~/CAgent_env/bin/python main.py --teams-send "message"     # send test message to Teams

# Confluence 端到端下载测试（手动脚本，连接真实服务器）
~/CAgent_env/bin/python scripts/run_confluence_download.py <confluence_page_url>
```

## Architecture

### LangGraph Pipeline (graph.py, state.py)

The core is a LangGraph `StateGraph` with conditional routing. All nodes share `AnalysisState` (TypedDict in `state.py`):

```
read_bug → read_testcase ─────────────→ read_requirement ──────────────→ read_code
               │ (empty?)                    │ (empty?)
               └→ search_testcase ──→        └→ search_requirement ──→
                                                                        ↓
                                        write_report ← analyze_impact ← analyze_root_cause
```

**Fallback pattern**: If `read_testcase` finds no linked test cases, the graph routes to `search_testcase` as a fallback. Same for requirements.

### Node Pattern (nodes/)

Every node is a **factory function** returning an async closure:

```python
def create_read_bug_node(tracker: BugTrackerClient, config) -> Callable:
    async def read_bug(state: AnalysisState) -> dict:
        # uses tracker and config from closure
        return {"bug_info": ..., "errors": [...]}
    return read_bug
```

Only `analyze_root_cause` calls the LLM. All other nodes interact with external systems via connectors.

### Connectors (connectors/)

External system clients, all using `httpx.AsyncClient`:

- **bug_tracker.py** — `BugTrackerClient` Protocol (duck-typed, `@runtime_checkable`). Both `JiraClient` and `RtcClient` implement this protocol without explicit inheritance.
- **jira_client.py** — Jira REST API v2
- **rtc_client.py** — IBM RTC via OSLC API with Jazz form-based auth
- **dng_client.py** — DOORS Next Generation requirements via OSLC
- **git_client.py** — GitPython-based multi-repo search and blame
- **confluence_client.py** — Confluence Server/Data Center API, PDF export via Chrome CDP or Native (REST API + WeasyPrint), global rate limiting, empty-page placeholder, `extract_children_from_page()` for efficient BFS child extraction, `_sanitize_html_for_pdf()` 预处理宽表格（移除像素/百分比溢出宽度、`<col>` 宽度、`fixed-width` 类）
- **ragflow_client.py** — RAGFlow knowledge base ingestion
- **teams_client.py** — MS Teams multi-transport messaging (Graph API / Workflow Webhook / Incoming Webhook), with automatic fallback and proxy support
- **graph_auth.py** — Azure AD OAuth2 Client Credentials authentication for Microsoft Graph API, with token caching and auto-refresh
- **graph_teams_client.py** — Microsoft Graph API Teams channel client: send/reply messages, Delta Query polling for incremental message retrieval, message filtering (own messages, @mentions)
- **teams_card_builder.py** — Adaptive Card factory: analysis result, progress, approval, error, help, status, detail, history cards
- **report_formatter.py** — `ReportFormatter` Protocol with `JiraWikiFormatter` and `RtcHtmlFormatter`

### Services (services/)

- **confluence_downloader.py** — BFS page tree traversal with producer-consumer pipeline, DFS tree-order PDF merge with auto-split volumes (≤200 pages), incremental PDF cache (`{page_id}_{title}.pdf`), exponential backoff retry, RAGFlow auto-upload hook

### Data Models (models.py)

All Pydantic v2 models: `BugInfo`, `TestCaseInfo`, `RequirementInfo`, `CodeInfo`, `RootCauseResult`, `ImpactResult`, `AnalysisReport`. `RootCauseLevel` is an enum with 6 levels (IMPLEMENTATION_DEVIATION, IMPLEMENTATION_MISSING, etc.).

### Config (config.py, config.yaml)

Hierarchical Pydantic models loaded from YAML. `config.local.yaml` overrides `config.yaml` (git-ignored). Supports `${ENV_VAR}` substitution for secrets. Config priority: CLI `--config` flag → `CONFIG_PATH` env → `config.yaml`.

### Watcher / Triggers (watcher/)

- **webhook_handler.py** — FastAPI route `POST /webhook/jira` with HMAC-SHA256 validation
- **poller.py** — Periodic JQL polling loop
- **rtc_poller.py** — Periodic RTC saved-query polling
- **teams_webhook_handler.py** — Teams outgoing webhook command handler
- **teams_poller.py** — Teams channel message poller via Graph API Delta Query (for intranet environments without inbound connectivity); supports help/status/analyze commands with thread reply

### Admin API (admin/)

FastAPI routes under `/admin` prefix: config view/update, status, history, health. Web dashboard at `/dashboard`. Secrets are redacted in config responses.

## Key Conventions

- **`from __future__ import annotations`** is used in every file
- **Module decoupling**: Nodes communicate only via `AnalysisState` TypedDict fields, never import each other
- **Protocol-based abstractions**: `BugTrackerClient` and `ReportFormatter` use Python Protocols (structural typing)
- **Test pattern**: Use `unittest.mock.AsyncMock` for async API calls; each test file mirrors a source module
- **Test vs Script**: `tests/` 目录只放 pytest 自动化单元测试；手动集成测试/脚本放 `scripts/` 目录
- **Prompt templates** live in `prompts/` as Markdown files (currently only `root_cause.md` is actively used)
- **LLM model**: Default is `claude-sonnet-4-20250514`, configurable in `config.yaml` under `llm.model`
- Documentation and comments are in Chinese

## Development Notes

- **WSL CRLF/LF**：WSL 环境下 git diff 可能显示大量行尾换行符差异，提交前用 `git diff --ignore-cr-at-eol` 确认是否有实际内容变更
- **改核心参数后检查测试**：修改 pagination limit、expand 参数等核心常量后，立即审查依赖这些值的测试用例
- **Git push 前先 fetch**：在 merge/rebase 后 push 前，先 `git fetch` 确认远端状态，避免 push rejected
- **Rebase 后验证文件**：rebase/merge 后检查关键配置文件（如 config.local.yaml）是否完整
- **PDF 导出修改后清缓存**：修改 `_sanitize_html_for_pdf` / `_wrap_export_html` / CDP JS 等 PDF 导出逻辑后，必须清除 `_pdf_cache/` 目录（`find confluence_downloads -name "_pdf_cache" -type d -exec rm -rf {} +`），否则旧缓存 PDF 会被复用，修复不生效
