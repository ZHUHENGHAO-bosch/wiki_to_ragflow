# Bug 自动分析守护程序 — 工程设计文档 (LangGraph 版)

> **目标读者**：Claude Code（自动生成代码）  
> **Agent 框架**：LangGraph（状态图驱动）  
> **约束**：每个模块 ≤ 300 行，接口明确，模块间通过 State 解耦  
> **语言**：Python 3.11+，类型注解必须完整  
> **依赖**：langgraph, langchain-anthropic, FastAPI, httpx, GitPython, pydantic

---

## Part I — 设计理念与分析逻辑

> 这一部分说明"为什么这么做"。Claude Code 在实现每个 Node（尤其是 Prompt 和比对逻辑）时，必须理解这里的推理链。

---

## 1. 问题定义

### 1.1 我们要解决什么

一句话：**Bug 来了，自动告诉工程师"问题出在哪、为什么出、还有什么被波及、怎么修"。**

工具链现状：
- **需求**在 IBM DNG（DOORS Next Generation）里
- **Bug 和 Test Case** 在 Jira 里
- **代码**在 Git 里
- 三者之间的追溯关系已经建立

传统做法：工程师拿到一个 Bug，脑子里回忆"这个功能的需求是什么、测试用例验了什么、代码写在哪里"，然后一个个系统打开查，凭经验判断根因。这个过程慢（天级）、依赖经验、容易遗漏。

本系统做的事情：**把工程师脑子里的"经验性排查"变成 Agent 在已有追溯链上的"系统性遍历"** — 不遗漏、不遗忘、速度快几个数量级。

### 1.2 核心链路

```
Bug (Jira) → Test Case (Jira) → 需求 (DNG) → 代码 (Git)
```

全部是已有的关联关系，Agent 不需要猜，直接顺着跳就行。这条链路的每一段都对应一次 API 调用：

| 跳转 | 关联方式 | API |
|------|---------|-----|
| Bug → Test Case | Jira Issue Link | Jira REST API |
| Test Case → 需求 | Jira Remote Link 或自定义字段 | Jira REST API → DNG OSLC API |
| 需求 → 代码 | DNG 追溯链接 (implemented_by) | DNG OSLC API → Git grep/blame |

---

## 2. Agent 的完整动作链（七步）

### Step 0：读 Bug 单

从 Jira API 拉这个 Bug 的所有信息 — 描述、复现步骤、环境信息、严重等级。**更关键的是拉它的 link 关系：这个 Bug 关联了哪些 Test Case。**

这一步的输出是 `BugInfo`，其中 `linked_test_case_keys` 是后续所有分析的起跳点。

### Step 1：顺着 Test Case 理解"什么该对但没对"

Test Case 本身就是"期望行为"的精确描述。Agent 读这个 Test Case 的步骤和断言条件，就能清楚地知道：**系统应该做什么，但实际做了什么**。

这比读 Bug 描述准确得多，因为 Bug 描述是人写的可能有遗漏，但 Test Case 的断言是精确的。

Agent 在这一步形成的认知：
```
期望：距离 < 3m 且 车速 > 10km/h 时，100ms 内触发制动
实际：135ms 才触发
差距：超时 35ms
```

### Step 2：顺着 Test Case → DNG 需求，拿到"为什么应该这样"

Test Case 在 Jira 里关联了 DNG 的需求。Agent 通过这条链路拿到原始需求描述。

现在 Agent 手里有三层信息了：
- 需求说了什么（DNG）
- 测试怎么验的（Jira Test Case）
- 实际表现是什么（Jira Bug）

Agent 在这一步形成的认知：
```
需求 REQ-042 说：
- AEB 应在检测到障碍物后 100ms 内触发制动
- 触发条件：前方障碍物距离 < 3m 且 车速 > 10km/h
- ASIL D
- 无温度相关的特殊说明
```

### Step 3：从需求找到代码，看"实际是怎么写的"

从 DNG 的需求沿追溯关系找到对应的代码模块/文件在 Git 里的位置。Agent 去读代码逻辑。

如果追溯关系只到模块级别，Agent 可以用 Test Case 里涉及的函数名、信号名去 Git 里 grep 精确定位。

Agent 在这一步形成的认知：
```
aeb_ctrl.c 中：
- 触发条件：distance < 3.0 && speed > 10.0  ✓ 与需求一致
- 但 radar_signal.c 中有一段：
  if (temperature < -10.0) {
      apply_cold_filter(signal, &delay);  // 额外引入 ~30ms
  }
- 这段逻辑在需求中无对应描述
- 最近一次修改：2 周前，commit abc1234，作者 Zhang Wei
```

### Step 4：四层比对，自动判定根因

**这是 Agent 的核心推理步骤。**

Agent 现在同时持有四个东西：

| 层级 | 内容 | 来源 |
|------|------|------|
| 需求 | "100ms 内触发，无温度例外" | DNG |
| 测试期望 | "100ms 内触发" | Jira Test Case |
| 代码逻辑 | "低温时额外滤波，增加 30ms" | Git |
| 实际结果 | "135ms" | Jira Bug |

**Agent 按顺序比对（这是 Prompt 中必须体现的决策树）：**

```
代码逻辑和需求一致吗？
├── 不一致 → 根因 = 实现偏离需求
│            修复路径：改代码，使其符合需求
│            （上面案例命中：代码加了需求没要求的低温滤波）
│
└── 一致 → 代码和需求一致，但测试还是失败？
            ├── 测试断言与需求不一致？
            │    → 根因 = 测试用例写错了
            │      修复路径：修正 Test Case
            │
            └── 测试和需求一致，代码也一致，但实际就是不对？
                 → 根因 = 需求遗漏了某个场景
                   修复路径：补充需求，再级联更新设计和代码
```

每种根因类型的判定条件和修复路径：

| 根因类型 | 判定条件 | 修复方向 | 典型场景 |
|---------|---------|---------|---------|
| **实现偏离** | 代码逻辑与需求不符 | 改代码 | 多了未定义的分支、阈值写错 |
| **实现遗漏** | 需求有要求但代码没实现 | 补代码 | 忘了处理某个边界条件 |
| **需求遗漏** | 代码和需求都没覆盖这个场景 | 先补需求，再改代码 | 低温、高负载等特殊工况 |
| **需求歧义** | 需求可多种理解，代码按 A 理解，测试按 B 理解 | 澄清需求 | "及时"到底是多少 ms |
| **测试缺陷** | 代码和需求一致，但测试断言写错 | 改 Test Case | 期望值写反了、精度不够 |
| **回归引入** | 近期 commit 改坏了原来好的代码 | revert 或修复最近 commit | git log 显示近期变更 |

### Step 5：影响扩散 — 同一个根因还坑了谁

找到根因节点后，**不是只修一个 Bug，而是一次性找出所有被波及的地方**。

两个扩散方向：

**向上扩散（同需求的其他测试）**：在 DNG 中查这个需求还关联了哪些 Test Case → 这些 Test Case 可能也会失败。

**横向扩散（共享代码的其他功能）**：如果根因是某个公共函数的问题，在 Git 中搜所有调用该函数的文件 → 通过追溯链反查这些文件对应的需求和测试。

```
本例中：
radar_signal.c 的 apply_cold_filter() 影响了：
├── AEB 功能 → TC-AEB-087 ← 当前 Bug
├── FCW 功能 → TC-FCW-023 ← 需要验证
└── LDW 功能 → TC-LDW-015 ← 需要验证
```

### Step 6：写回 Jira 闭环

Agent 把分析结果结构化写回 Jira Bug 单：

- **根因层级**：需求 / 实现 / 测试脚本本身
- **根因描述**：具体哪个文件哪段逻辑有问题
- **关联需求**：DNG 里的需求 ID 和链接
- **影响范围**：其他可能受影响的 Test Case 列表
- **修复建议**：改什么、改完后跑哪些回归测试
- **自动创建子任务或关联 Issue**（如果影响扩散发现了新问题）

---

## 3. 一句话总结

**Bug → Test Case → 需求 → 代码，四样东西摆一起比对，不一致的地方就是根因。**

---

## Part II — 技术实现

> 以下是具体的代码架构、模块拆分和接口定义。

---

## 4. 核心设计：用 LangGraph 状态图编排分析流程

传统做法是在 orchestrator 里写 if/else 串联六步。用 LangGraph 的优势是：

- **每一步是一个 Node**，输入输出通过 State 传递，天然解耦
- **条件路由**：某步失败时自动走降级路径，不需要 if/else 嵌套
- **可视化**：LangGraph 可以导出流程图，方便调试和展示
- **可扩展**：后续加新分析步骤只需加 Node + Edge，不改已有代码

```
                    ┌──────────────┐
                    │  read_bug    │  Node 0
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ read_testcase│  Node 1
                    └──────┬───────┘
                           │
                  ┌────────▼────────┐
                  │ has_test_cases? │  Conditional Edge
                  └───┬─────────┬──┘
                  yes │         │ no
                      │    ┌────▼──────────┐
                      │    │search_testcase│  Node 1b (降级)
                      │    └────┬──────────┘
                      │         │
                  ┌───▼─────────▼──┐
                  │ read_requirement│  Node 2
                  └──────┬─────────┘
                         │
                ┌────────▼────────┐
                │has_requirements?│  Conditional Edge
                └───┬─────────┬──┘
                yes │         │ no
                    │    ┌────▼────────────────┐
                    │    │search_requirement   │  Node 2b (降级)
                    │    └────┬────────────────┘
                    │         │
                ┌───▼─────────▼──┐
                │   read_code    │  Node 3
                └──────┬─────────┘
                       │
                ┌──────▼─────────┐
                │ analyze_root   │  Node 4 (LLM)
                │   _cause       │
                └──────┬─────────┘
                       │
                ┌──────▼─────────┐
                │analyze_impact  │  Node 5
                └──────┬─────────┘
                       │
                ┌──────▼─────────┐
                │ write_report   │  Node 6
                └────────────────┘
```

---

## 5. 项目结构

```
bug_analyzer/
├── main.py                       # 入口：FastAPI + 后台消费循环
├── config.py                     # 配置加载
├── state.py                      # LangGraph State 定义
├── models.py                     # Pydantic 数据模型（不含 State）
├── graph.py                      # LangGraph 图定义（组装 Node + Edge）
│
├── watcher/
│   ├── __init__.py
│   ├── webhook_handler.py        # FastAPI 路由，接收 Jira Webhook
│   ├── poller.py                 # JQL 轮询备选
│   ├── rtc_poller.py             # RTC Saved Query 轮询
│   ├── teams_webhook_handler.py  # Teams Outgoing Webhook 路由
│   └── teams_poller.py           # Teams 频道消息轮询器 (Graph API Delta Query)
│
├── connectors/
│   ├── __init__.py
│   ├── jira_client.py            # Jira REST API
│   ├── rtc_client.py             # IBM RTC OSLC API
│   ├── dng_client.py             # DNG OSLC API
│   ├── git_client.py             # Git 操作
│   ├── confluence_client.py      # Confluence REST API + 双模式 PDF 导出 (Chrome CDP / Native WeasyPrint)
│   ├── ragflow_client.py         # RAGFlow 知识库 SDK 异步包装器
│   ├── teams_client.py           # Teams 多传输通信客户端
│   ├── teams_card_builder.py     # Adaptive Card 构建工具
│   ├── graph_auth.py             # Azure AD OAuth2 认证
│   ├── graph_teams_client.py     # Graph API Teams 消息客户端
│   └── report_formatter.py       # ReportFormatter Protocol
│
├── services/
│   ├── __init__.py
│   └── confluence_downloader.py  # Confluence 页面树 BFS 下载编排
│
├── nodes/
│   ├── __init__.py
│   ├── read_bug.py               # Node 0
│   ├── read_testcase.py          # Node 1
│   ├── search_testcase.py        # Node 1b (降级)
│   ├── read_requirement.py       # Node 2
│   ├── search_requirement.py     # Node 2b (降级)
│   ├── read_code.py              # Node 3
│   ├── analyze_root_cause.py     # Node 4 (LLM)
│   ├── analyze_impact.py         # Node 5
│   └── write_report.py           # Node 6
│
├── prompts/
│   ├── root_cause.md
│   └── impact.md
│
├── config.yaml
├── requirements.txt
└── Dockerfile
```

**与上一版的关键区别**：
- 去掉了 `engine/orchestrator.py` → 用 `graph.py` 替代
- 去掉了 `engine/` 下的各 reader → 变成 `nodes/` 下的独立 Node
- 去掉了 `writer/report_formatter.py` → 合并进 `nodes/write_report.py`
- 新增 `state.py` → LangGraph 的 State 定义
- 新增 `graph.py` → 图的组装

---

## 6. LangGraph State — `state.py`

**这是整个系统的核心数据结构。所有 Node 读写同一个 State。**

```python
"""
state.py — LangGraph State 定义

所有 Node 共享这个 State。每个 Node 只更新自己负责的字段。
使用 TypedDict 定义，LangGraph 要求。
"""
from typing import TypedDict, Annotated
from models import (BugInfo, TestCaseInfo, RequirementInfo, CodeInfo,
                    RootCauseResult, ImpactResult, AnalysisStatus)

class AnalysisState(TypedDict):
    """LangGraph 状态，贯穿整个分析流程。"""

    # ── 输入 ──
    bug_key: str

    # ── Step 0: read_bug 填充 ──
    bug_info: BugInfo | None

    # ── Step 1: read_testcase / search_testcase 填充 ──
    test_cases: list[TestCaseInfo]

    # ── Step 2: read_requirement / search_requirement 填充 ──
    requirements: list[RequirementInfo]

    # ── Step 3: read_code 填充 ──
    code_info: CodeInfo | None

    # ── Step 4: analyze_root_cause 填充 ──
    root_cause: RootCauseResult | None

    # ── Step 5: analyze_impact 填充 ──
    impact: ImpactResult | None

    # ── 流程控制 ──
    status: AnalysisStatus
    errors: list[str]                 # 各步骤的错误/警告信息
    analysis_duration: float          # 总耗时（write_report 填充）
```

**LangGraph Node 的约定**：
- 每个 Node 函数签名：`async def node_name(state: AnalysisState) -> dict`
- 返回 dict 只包含要更新的字段（LangGraph 自动 merge 到 State）
- Node 内部不直接修改 state，只返回更新

---

## 7. 数据模型 — `models.py`

与上一版完全相同，不再重复。包含：
- `BugInfo`, `TestStep`, `TestCaseInfo` — Jira 数据
- `RequirementInfo` — DNG 数据
- `GitCommit`, `CodeSnippet`, `CodeInfo` — Git 数据
- `RootCauseLevel`, `RootCauseResult`, `FixSuggestion` — 根因分析结果
- `ImpactItem`, `ImpactResult` — 影响扩散结果
- `AnalysisStatus` — 枚举：success / partial / failed
- `AnalysisReport` — 最终报告（write_report Node 中组装）

---

## 8. 配置 — `config.py`

与上一版完全相同。`AppConfig` 包含 `JiraConfig`, `DngConfig`, `GitRepoConfig`, `LlmConfig`, `WatcherConfig`, `WriterConfig`。

---

## 9. Connectors — 不变

`connectors/jira_client.py`, `connectors/dng_client.py`, `connectors/git_client.py` 接口与上一版完全相同。它们是纯 API 封装，不感知 LangGraph。

Node 通过依赖注入获得 Connector 实例（见 `graph.py` 中的闭包写法）。

---

## 10. Nodes — LangGraph 的核心

**每个 Node 是一个 async 函数，签名统一：`(state) -> dict`。**

**Node 内部通过闭包捕获 Connector 实例，不从 State 中获取 Connector。**

### 10.1 `nodes/read_bug.py` — Node 0

```python
"""
read_bug.py — Node 0: 从 Jira 读取 Bug 信息

输入 State 字段: bug_key
输出 State 字段: bug_info
依赖: JiraClient
"""
from state import AnalysisState
from models import BugInfo
from connectors.jira_client import JiraClient
from config import JiraConfig

def create_read_bug_node(jira: JiraClient, config: JiraConfig):
    """
    工厂函数，返回绑定了 jira_client 的 Node 函数。

    LangGraph Node 必须是 (state) -> dict 签名，
    所以用闭包捕获外部依赖。
    """

    async def read_bug(state: AnalysisState) -> dict:
        """
        1. jira.get_issue(state["bug_key"]) 获取 Issue JSON
        2. jira.get_issue_links(key, config.test_case_link_type) 获取关联 Test Case
        3. 从 fields 提取: summary, description, priority, components,
           environment, labels, created, reporter
        4. 返回 {"bug_info": BugInfo(...)}
        
        异常处理: 如果 get_issue 失败，返回:
        {"bug_info": None, "errors": [..., "读取 Bug 失败: {error}"],
         "status": "failed"}
        """

    return read_bug
```

### 10.2 `nodes/read_testcase.py` — Node 1

```python
"""
read_testcase.py — Node 1: 读取关联的 Test Case

输入 State 字段: bug_info.linked_test_case_keys
输出 State 字段: test_cases
依赖: JiraClient
"""
from state import AnalysisState
from models import TestCaseInfo, TestStep
from connectors.jira_client import JiraClient
from config import JiraConfig

def create_read_testcase_node(jira: JiraClient, config: JiraConfig):

    async def read_testcase(state: AnalysisState) -> dict:
        """
        1. 从 state["bug_info"].linked_test_case_keys 获取 key 列表
        2. 并发 (asyncio.gather) 读取每个 Test Case:
           - jira.get_issue(key) 获取 fields
           - 解析 config.test_steps_field 为 list[TestStep]
           - jira.get_remote_links(key) 获取 DNG 需求链接
           - 或从 config.requirement_field 字段读取需求 ID
        3. 返回 {"test_cases": [...]}

        测试步骤解析:
        - JSON 数组: [{"step": "...", "expected": "...", "actual": "..."}]
        - 纯文本: 按行号拆分
        - 字段为 None: steps = []

        需求 ID 提取:
        - remote link URL 中正则提取 (如 /rm/resources/REQ-042)
        - 或自定义字段值直接作为 ID
        """

    return read_testcase
```

### 10.3 `nodes/search_testcase.py` — Node 1b (降级)

```python
"""
search_testcase.py — Node 1b: Bug 无关联 Test Case 时的降级搜索

触发条件: state["test_cases"] 为空
输入 State 字段: bug_info.components, bug_info.summary
输出 State 字段: test_cases, errors (追加)
依赖: JiraClient
"""
from state import AnalysisState
from connectors.jira_client import JiraClient
from config import JiraConfig

def create_search_testcase_node(jira: JiraClient, config: JiraConfig):

    async def search_testcase(state: AnalysisState) -> dict:
        """
        1. 从 bug_info 提取搜索关键词 (components + summary 分词)
        2. 构造 JQL:
           issuetype = "{config.test_case_issue_type}"
           AND (component in ({components}) OR summary ~ "{keywords}")
        3. jira.search_issues(jql, max_results=5)
        4. 对搜索到的 key，复用 read_testcase 的解析逻辑读取详情
        5. 返回 {"test_cases": [...], "errors": [..., "通过关键词搜索找到 N 个 Test Case"]}
        
        如果搜不到: 返回 {"test_cases": [], "errors": [..., "未找到关联 Test Case"]}
        """

    return search_testcase
```

### 10.4 `nodes/read_requirement.py` — Node 2

```python
"""
read_requirement.py — Node 2: 从 DNG 读取需求

输入 State 字段: test_cases[].linked_requirement_ids
输出 State 字段: requirements
依赖: DngClient
"""
from state import AnalysisState
from models import RequirementInfo
from connectors.dng_client import DngClient

def create_read_requirement_node(dng: DngClient):

    async def read_requirement(state: AnalysisState) -> dict:
        """
        1. 从 state["test_cases"] 收集所有 linked_requirement_ids (去重)
        2. 并发读取每个需求:
           - dng.get_requirement(req_id) 获取属性
           - dng.get_trace_links(req_id) 获取追溯链接
        3. 组装 RequirementInfo:
           - linked_module_names ← trace_links["implemented_by"]
           - linked_test_case_ids ← trace_links["validated_by"]
        4. 返回 {"requirements": [...]}
        
        如果 req_ids 为空 (test_cases 里没有关联需求):
        返回 {"requirements": []}
        """

    return read_requirement
```

### 10.5 `nodes/search_requirement.py` — Node 2b (降级)

```python
"""
search_requirement.py — Node 2b: 需求列表为空时的降级搜索

触发条件: state["requirements"] 为空
输入 State 字段: bug_info.components
输出 State 字段: requirements, errors (追加)
依赖: DngClient
"""
from state import AnalysisState
from connectors.dng_client import DngClient

def create_search_requirement_node(dng: DngClient):

    async def search_requirement(state: AnalysisState) -> dict:
        """
        1. 用 bug_info.components 作为关键词
        2. dng.search_requirements(keyword) 搜索
        3. 对搜索到的需求读取追溯链接
        4. 返回 {"requirements": [...], "errors": [..., "通过关键词搜索找到 N 个需求"]}
        """

    return search_requirement
```

### 10.6 `nodes/read_code.py` — Node 3

```python
"""
read_code.py — Node 3: 从 Git 读取相关代码

输入 State 字段: requirements[].linked_module_names, bug_info.components
输出 State 字段: code_info
依赖: GitClient
"""
from state import AnalysisState
from models import CodeInfo, CodeSnippet, GitCommit
from connectors.git_client import GitClient

def create_read_code_node(git: GitClient):

    async def read_code(state: AnalysisState) -> dict:
        """
        1. 收集搜索关键词:
           - requirements[].linked_module_names
           - bug_info.components
        2. git.search_files(keywords) 搜索相关文件
        3. 如果文件 > 10，按优先级排序取 top 5:
           - 最近有 commit 的排前
           - 命中关键词多的排前
        4. 对每个文件:
           - git.get_file_content() 读内容
           - _extract_snippets() 截取关键代码片段 (关键词上下文 ±30 行)
           - git.get_recent_commits() 读近 4 周变更
        5. 返回 {"code_info": CodeInfo(...)}
        
        如果搜不到文件: 返回 {"code_info": None, "errors": [..., "未找到相关代码文件"]}
        """

    def _extract_snippets(content: str, keywords: list[str],
                          context_lines: int = 30) -> list[tuple[int, int, str]]:
        """
        找关键词所在行，向上找函数开头 (C 函数定义模式: 
        返回类型 + 函数名 + 括号 + 花括号)，向下截取 context_lines 行。
        """

    return read_code
```

### 10.7 `nodes/analyze_root_cause.py` — Node 4 (LLM)

```python
"""
analyze_root_cause.py — Node 4: LLM 根因分析

输入 State 字段: bug_info, test_cases, requirements, code_info
输出 State 字段: root_cause
依赖: langchain-anthropic (ChatAnthropic)

这是唯一调用 LLM 的 Node。
"""
import json
from pathlib import Path
from langchain_anthropic import ChatAnthropic
from state import AnalysisState
from models import RootCauseResult, RootCauseLevel, FixSuggestion
from config import LlmConfig

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "root_cause.md"

def create_analyze_root_cause_node(llm: ChatAnthropic, config: LlmConfig):

    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")

    async def analyze_root_cause(state: AnalysisState) -> dict:
        """
        1. _build_prompt(): 将 state 中的四层信息填入 Prompt 模板
        2. llm.ainvoke(prompt) 调用 LLM
        3. _parse_response(): 解析 LLM 返回的 JSON
        4. 返回 {"root_cause": RootCauseResult(...)}
        
        Prompt 中要求 LLM 按以下逻辑分析:
        - 代码行为 vs 需求描述 → 不一致则"实现偏离"
        - 代码和需求一致但测试失败 → 检查测试断言
        - 都一致但实际就是错 → "需求遗漏"
        - 最近 commit 引入 → "回归引入"
        
        LLM 返回格式 (Prompt 中约束):
        {
          "level": "实现偏离",
          "summary": "一句话根因",
          "detail": "详细分析",
          "problem_location": "radar_signal.c:142-155",
          "introducer": "Zhang Wei",
          "introducing_commit": "abc1234",
          "fix_suggestions": [
            {"label": "方案A", "description": "...", "effort": "2h"}
          ]
        }
        
        容错:
        - 去除 markdown 代码块包裹
        - JSON 解析失败时从文本提取关键信息
        - level 不在枚举内时映射到最接近的枚举值
        
        异常: 返回 {"root_cause": None, "errors": [..., "LLM 分析失败: {error}"]}
        """

    def _build_prompt(state: AnalysisState) -> str:
        """
        填充模板。截断策略:
        - 代码片段总长 > 3000 字符 → 只保留最相关的 2 个
        - 需求描述 > 1000 字符 → 截断
        """

    def _parse_response(text: str) -> RootCauseResult:
        """解析 LLM JSON 响应。"""

    return analyze_root_cause
```

**Prompt 模板 `prompts/root_cause.md`**：

```markdown
你是一个汽车电子软件 Bug 根因分析专家。

以下是从 Jira / DNG / Git 三个系统收集到的信息：

## Bug (Jira)
- 编号: {bug_key}
- 描述: {bug_description}
- 环境: {environment}
- 优先级: {priority}

## 测试用例 (Jira)
{test_cases_section}

## 需求 (DNG)
{requirements_section}

## 代码 (Git)
{code_section}

## 你的任务

逐步分析：
1. 对比代码实际行为和需求要求，是否一致？
2. 如果不一致，具体哪里不一致？（实现偏离 / 实现遗漏）
3. 如果一致，测试断言是否正确？（测试缺陷）
4. 如果都一致但还是出 Bug，是否需求遗漏了某个场景？
5. 检查 git 最近变更，是否是近期改动引入？（回归引入）
6. 给出修复建议

请只返回 JSON（无 markdown 包裹）：
{
  "level": "实现偏离 | 实现遗漏 | 需求遗漏 | 需求歧义 | 测试缺陷 | 回归引入",
  "summary": "一句话根因",
  "detail": "详细分析过程",
  "problem_location": "文件:行号 或 需求ID",
  "introducer": "作者名 或 null",
  "introducing_commit": "commit hash 或 null",
  "fix_suggestions": [
    {"label": "方案A", "description": "具体修复方法", "effort": "预估工时"}
  ]
}
```

### 10.8 `nodes/analyze_impact.py` — Node 5

```python
"""
analyze_impact.py — Node 5: 影响扩散分析

输入 State 字段: root_cause, code_info, requirements
输出 State 字段: impact
依赖: GitClient, DngClient
"""
from state import AnalysisState
from models import ImpactResult, ImpactItem
from connectors.git_client import GitClient
from connectors.dng_client import DngClient

def create_analyze_impact_node(git: GitClient, dng: DngClient):

    async def analyze_impact(state: AnalysisState) -> dict:
        """
        1. 从 root_cause.problem_location 提取问题函数名
           格式: "file.c:142-155" → 读该行范围提取函数名
           或: "apply_cold_filter" → 直接使用
        2. git.search_callers(repo, function_name) 找所有调用方
        3. 对每个调用文件:
           - 在 state["requirements"] 中匹配模块名
           - 匹配到 → 取出 linked_test_case_ids
           - 匹配不到 → 标注 "未追溯，需人工确认"
        4. 汇总 regression_test_list:
           - 当前 Bug 已关联的 Test Case (直接关联)
           - 扩散发现的 Test Case (间接关联)
           - 去重
        5. 返回 {"impact": ImpactResult(...)}
        
        如果 root_cause 或 code_info 为 None:
        返回 {"impact": None}
        """

    return analyze_impact
```

### 10.9 `nodes/write_report.py` — Node 6

```python
"""
write_report.py — Node 6: 格式化报告 + 写回 Jira

输入 State 字段: 所有字段
输出 State 字段: analysis_duration
依赖: JiraClient, AppConfig

合并了 report_formatter 和 jira_writer 的职责。
"""
import time
from state import AnalysisState
from models import AnalysisReport, AnalysisStatus
from connectors.jira_client import JiraClient
from config import AppConfig

def create_write_report_node(jira: JiraClient, config: AppConfig):

    async def write_report(state: AnalysisState) -> dict:
        """
        1. _format_report(state) 生成 Jira wiki markup
        2. jira.add_comment(state["bug_key"], comment)
        3. jira.update_labels(state["bug_key"], [config.writer.analyzed_label])
        4. 如果 config.writer.auto_create_related_bugs 且有影响扩散结果:
           对高风险项创建关联 Bug
        5. 如果 config.writer.notify_webhook:
           发送通知
        6. 返回 {"analysis_duration": elapsed}
        """

    def _format_report(state: AnalysisState) -> str:
        """
        生成 Jira wiki markup:
        
        {panel:title=🤖 Bug Analysis Agent|borderColor=#003B71}
        
        h4. 分析状态
        {status:colour=Green|title=完成} 或 {status:colour=Yellow|title=部分}
        
        h4. 根因层级
        {status:colour=Red|title=实现偏离}
        
        h4. 根因定位
        - 文件: {{file.c}} (Line xxx)
        - 问题: ...
        - 引入者: ..., commit ...
        
        h4. 关联需求
        - REQ-xxx: ... [链接|url]
        
        h4. 影响范围
        || 模块 || 测试用例 || 风险 ||
        | ... | ... | ... |
        
        h4. 修复建议
        - *方案 A*: ...
        
        h4. 回归测试清单
        - PROJ-xxxx (直接关联)
        - PROJ-yyyy (影响扩散)
        
        分析耗时: {duration}s
        {panel}
        """

    def _send_notification(state: AnalysisState) -> None:
        """POST 到 webhook URL。"""

    return write_report
```

---

## 11. Graph 组装 — `graph.py`

**这是 LangGraph 的核心：定义 Node、Edge、条件路由。**

```python
"""
graph.py — LangGraph 图定义

职责:
1. 注册所有 Node
2. 定义 Edge (包括条件路由)
3. 编译成可执行的 CompiledGraph
"""
from langgraph.graph import StateGraph, END
from state import AnalysisState
from nodes.read_bug import create_read_bug_node
from nodes.read_testcase import create_read_testcase_node
from nodes.search_testcase import create_search_testcase_node
from nodes.read_requirement import create_read_requirement_node
from nodes.search_requirement import create_search_requirement_node
from nodes.read_code import create_read_code_node
from nodes.analyze_root_cause import create_analyze_root_cause_node
from nodes.analyze_impact import create_analyze_impact_node
from nodes.write_report import create_write_report_node
from connectors.jira_client import JiraClient
from connectors.dng_client import DngClient
from connectors.git_client import GitClient
from langchain_anthropic import ChatAnthropic
from config import AppConfig


def build_graph(jira: JiraClient, dng: DngClient, git: GitClient,
                llm: ChatAnthropic, config: AppConfig):
    """
    构建完整的分析流程图。返回 CompiledGraph。
    
    使用: graph = build_graph(...); result = await graph.ainvoke({"bug_key": "PROJ-1234"})
    """

    # ── 创建 Node 函数 (闭包注入依赖) ──
    read_bug = create_read_bug_node(jira, config.jira)
    read_testcase = create_read_testcase_node(jira, config.jira)
    search_testcase = create_search_testcase_node(jira, config.jira)
    read_requirement = create_read_requirement_node(dng)
    search_requirement = create_search_requirement_node(dng)
    read_code = create_read_code_node(git)
    analyze_root_cause = create_analyze_root_cause_node(llm, config.llm)
    analyze_impact = create_analyze_impact_node(git, dng)
    write_report = create_write_report_node(jira, config)

    # ── 构建 StateGraph ──
    graph = StateGraph(AnalysisState)

    # ── 注册 Node ──
    graph.add_node("read_bug", read_bug)
    graph.add_node("read_testcase", read_testcase)
    graph.add_node("search_testcase", search_testcase)
    graph.add_node("read_requirement", read_requirement)
    graph.add_node("search_requirement", search_requirement)
    graph.add_node("read_code", read_code)
    graph.add_node("analyze_root_cause", analyze_root_cause)
    graph.add_node("analyze_impact", analyze_impact)
    graph.add_node("write_report", write_report)

    # ── 入口 ──
    graph.set_entry_point("read_bug")

    # ── Edge: read_bug → read_testcase ──
    graph.add_edge("read_bug", "read_testcase")

    # ── Conditional Edge: read_testcase 之后 ──
    def after_read_testcase(state: AnalysisState) -> str:
        """有 test_cases → 读需求; 没有 → 降级搜索"""
        if state.get("test_cases"):
            return "read_requirement"
        return "search_testcase"

    graph.add_conditional_edges(
        "read_testcase",
        after_read_testcase,
        {"read_requirement": "read_requirement",
         "search_testcase": "search_testcase"}
    )

    # ── search_testcase → read_requirement ──
    graph.add_edge("search_testcase", "read_requirement")

    # ── Conditional Edge: read_requirement 之后 ──
    def after_read_requirement(state: AnalysisState) -> str:
        """有 requirements → 读代码; 没有 → 降级搜索"""
        if state.get("requirements"):
            return "read_code"
        return "search_requirement"

    graph.add_conditional_edges(
        "read_requirement",
        after_read_requirement,
        {"read_code": "read_code",
         "search_requirement": "search_requirement"}
    )

    # ── search_requirement → read_code ──
    graph.add_edge("search_requirement", "read_code")

    # ── read_code → analyze_root_cause ──
    graph.add_edge("read_code", "analyze_root_cause")

    # ── analyze_root_cause → analyze_impact ──
    graph.add_edge("analyze_root_cause", "analyze_impact")

    # ── analyze_impact → write_report ──
    graph.add_edge("analyze_impact", "write_report")

    # ── write_report → END ──
    graph.add_edge("write_report", END)

    # ── 编译 ──
    return graph.compile()
```

---

## 12. 入口 — `main.py`

```python
"""
main.py — 守护程序入口

1. 加载配置
2. 初始化 Connectors + LLM
3. build_graph() 构建 LangGraph
4. 启动 FastAPI (Webhook) + 后台消费循环

运行: uvicorn main:app --host 0.0.0.0 --port 8000
"""
import asyncio, logging
from fastapi import FastAPI
from langchain_anthropic import ChatAnthropic
from config import load_config
from connectors.jira_client import JiraClient
from connectors.dng_client import DngClient
from connectors.git_client import GitClient
from graph import build_graph
from watcher.webhook_handler import create_webhook_handler
from watcher.poller import JiraPoller

app = FastAPI(title="Bug Analysis Daemon")
logger = logging.getLogger("main")

@app.on_event("startup")
async def startup():
    config = load_config()
    queue = asyncio.Queue()

    # Connectors
    jira = JiraClient(config.jira)
    dng = DngClient(config.dng)
    git = GitClient(config.git_repos)
    await git.pull_all()
    await dng.authenticate()

    # LLM
    llm = ChatAnthropic(
        model=config.llm.model,
        api_key=config.llm.api_key,
        max_tokens=config.llm.max_tokens,
    )

    # LangGraph
    analysis_graph = build_graph(jira, dng, git, llm, config)

    # Webhook
    app.include_router(create_webhook_handler(config, queue))

    # Polling (if configured)
    if config.watcher.mode == "polling":
        asyncio.create_task(JiraPoller(jira, config, queue).start())

    # Consumer
    asyncio.create_task(_consumer_loop(queue, analysis_graph))

    app.state.jira = jira
    app.state.dng = dng

@app.on_event("shutdown")
async def shutdown():
    await app.state.jira.close()
    await app.state.dng.close()

async def _consumer_loop(queue: asyncio.Queue, graph):
    """从 queue 取 bug_key，调用 LangGraph 执行分析。"""
    while True:
        bug_key = await queue.get()
        logger.info(f"Analyzing {bug_key}...")
        try:
            # 初始 State
            initial_state = {
                "bug_key": bug_key,
                "bug_info": None,
                "test_cases": [],
                "requirements": [],
                "code_info": None,
                "root_cause": None,
                "impact": None,
                "status": "success",
                "errors": [],
                "analysis_duration": 0.0,
            }
            result = await graph.ainvoke(initial_state)
            logger.info(f"Done {bug_key}: status={result['status']}")
        except Exception as e:
            logger.error(f"Failed {bug_key}: {e}", exc_info=True)
        finally:
            queue.task_done()

@app.get("/health")
async def health():
    return {"status": "running"}
```

---

## 13. Watcher 模块 — 不变

`watcher/webhook_handler.py` 和 `watcher/poller.py` 与上一版接口完全相同。它们只负责把 `bug_key` 放入 `asyncio.Queue`，不感知 LangGraph。

---

## 14. 模块行数估算

| 模块 | 预估行数 | 说明 |
|------|---------|------|
| `models.py` | ~150 | 纯数据模型 |
| `state.py` | ~30 | LangGraph State TypedDict |
| `config.py` | ~80 | 配置加载 |
| `graph.py` | ~100 | 图定义 + 条件路由 |
| `connectors/jira_client.py` | ~200 | Jira API |
| `connectors/dng_client.py` | ~150 | DNG OSLC API |
| `connectors/git_client.py` | ~200 | Git 操作 |
| `nodes/read_bug.py` | ~60 | Node 0 |
| `nodes/read_testcase.py` | ~120 | Node 1 含步骤解析 |
| `nodes/search_testcase.py` | ~80 | Node 1b 降级 |
| `nodes/read_requirement.py` | ~90 | Node 2 |
| `nodes/search_requirement.py` | ~70 | Node 2b 降级 |
| `nodes/read_code.py` | ~180 | Node 3 含代码提取 |
| `nodes/analyze_root_cause.py` | ~160 | Node 4 LLM |
| `nodes/analyze_impact.py` | ~150 | Node 5 扩散 |
| `nodes/write_report.py` | ~200 | Node 6 格式化+写回 |
| `watcher/webhook_handler.py` | ~60 | Webhook |
| `watcher/poller.py` | ~70 | 轮询 |
| `main.py` | ~80 | 入口 |

**总计 19 个文件，所有模块 ≤ 300 行，总代码量约 2230 行。**

---

## 15. Claude Code 实现顺序

| # | 文件 | 原因 | 可独立测试 |
|---|------|------|----------|
| 1 | `models.py` | 数据契约 | ✅ pydantic 校验 |
| 2 | `state.py` | LangGraph State | ✅ TypedDict 检查 |
| 3 | `config.py` | 全局依赖 | ✅ yaml 加载 |
| 4 | `connectors/jira_client.py` | 被多数 Node 依赖 | ✅ mock HTTP |
| 5 | `connectors/dng_client.py` | Node 2/2b/5 依赖 | ✅ mock HTTP |
| 6 | `connectors/git_client.py` | Node 3/5 依赖 | ✅ mock git |
| 7 | `nodes/read_bug.py` | 最简单的 Node | ✅ mock JiraClient |
| 8 | `nodes/read_testcase.py` | Node 1 | ✅ mock JiraClient |
| 9 | `nodes/search_testcase.py` | Node 1b | ✅ mock JiraClient |
| 10 | `nodes/read_requirement.py` | Node 2 | ✅ mock DngClient |
| 11 | `nodes/search_requirement.py` | Node 2b | ✅ mock DngClient |
| 12 | `nodes/read_code.py` | Node 3 | ✅ mock GitClient |
| 13 | `nodes/analyze_root_cause.py` | Node 4 核心 | ✅ mock LLM |
| 14 | `nodes/analyze_impact.py` | Node 5 | ✅ mock Connectors |
| 15 | `nodes/write_report.py` | Node 6 | ✅ mock JiraClient |
| 16 | `graph.py` | 组装所有 Node | ✅ 用 mock Node 测试路由 |
| 17 | `watcher/webhook_handler.py` | HTTP 入口 | ✅ TestClient |
| 18 | `watcher/poller.py` | 备选入口 | ✅ mock JiraClient |
| 19 | `main.py` | 启动组装 | ✅ 集成测试 |

---

## 16. requirements.txt

```
langgraph>=0.2.0
langchain-anthropic>=0.3.0
langchain-core>=0.3.0
fastapi>=0.115.0
uvicorn>=0.32.0
httpx>=0.27.0
pydantic>=2.9.0
pydantic-settings>=2.6.0
pyyaml>=6.0
gitpython>=3.1.0
pypdf>=4.0.0
websockets>=12.0
weasyprint>=62.0
ragflow-sdk>=0.24.0
```

---

## 17. Confluence 下载与 RAGFlow 知识库集成

### 17.1 功能概述

本模块为 Bug 分析系统提供 **知识库自动构建** 能力：

1. **Confluence 批量下载** — 通过 BFS 遍历 Confluence 页面树，将内容导出为 PDF（支持 Chrome CDP 或 Native REST API + WeasyPrint 双模式），按页面层级 DFS 前序遍历合并为 PDF 文件（超过 200 页自动分卷）
2. **RAGFlow 上传解析** — 将导出的 PDF 自动上传到 RAGFlow 知识库并触发 chunking 解析

两种触发方式：
- **自动模式**：Confluence 下载完成后自动上传到 RAGFlow（`auto_upload_after_confluence: true`）
- **手动模式**：独立 `--upload-ragflow` CLI 命令，上传任意本地文件

### 17.2 Confluence 下载架构

```
┌──────────────────────────────────────────────────────────────┐
│                     ConfluenceDownloader                      │
│                                                              │
│   ┌──────────────────┐    asyncio.Queue    ┌──────────────┐ │
│   │  BFS Producer    │──── page_id ────▶  │  PDF Consumer │ │
│   │  (轻量 expand)    │──── page_id ────▶  │  (双模式导出) │ │
│   │  + 版本缓存检查   │──── None ──────▶   │              │ │
│   │  + children 提取  │   (sentinel)       └──────┬───────┘ │
│   └──────┬───────────┘                           │          │
│          │                                        │          │
│   children_order   _pdf_cache/            pdf_map: dict      │
│   (树结构记录)     {pid}_{title}.pdf              │          │
│          │         {pid}_{title}.json              │          │
│          ▼                                        │          │
│   ┌──────────────┐                       ┌────────▼───────┐ │
│   │  _dfs_order  │                       │  PdfWriter     │ │
│   │  (DFS 前序   │──── 层级顺序 ────▶   │  (DFS 合并)    │ │
│   │   遍历)      │                       └────────┬───────┘ │
│   └──────────────┘                                │         │
│                                       ┌───────────▼───────┐ │
│                                       │ 自动分卷 (≤200页) │ │
│                                       │ vol1.pdf vol2.pdf │ │
│                                       └───────────┬───────┘ │
│                                                   │         │
│                                       ┌───────────▼───────┐ │
│                                       │ RAGFlow 上传      │ │
│                                       │ (可选钩子)         │ │
│                                       └───────────────────┘ │
└──────────────────────────────────────────────────────────────┘

PDF 导出双模式 (pdf_export_method):
  ┌─────────────────────┐     ┌─────────────────────────────┐
  │  "chrome" (CDP)     │     │  "native" (REST + WeasyPrint)│
  │  Windows SPNEGO     │     │  PAT / Basic Auth           │
  │  Kerberos 环境      │     │  无需 Chrome                │
  │  networkIdle 检测   │     │  body.export_view → PDF     │
  └─────────────────────┘     └─────────────────────────────┘
```

**核心组件：**

| 模块 | 职责 |
|------|------|
| `connectors/confluence_client.py` | Confluence REST API + 双模式 PDF 导出（Chrome CDP / Native WeasyPrint）、全局限流（`_throttle`）、空页面占位 PDF、`extract_children_from_page` 子页面提取 |
| `services/confluence_downloader.py` | BFS 页面树遍历、Pipeline 生产者-消费者并行下载、PDF 增量缓存（含标题命名）、DFS 层级合并与自动分卷、指数退避重试、RAGFlow 上传钩子 |
| `connectors/ragflow_client.py` | RAGFlow SDK 异步包装器，负责 dataset 查找/创建、文件上传、解析触发 |

### 17.3 Confluence 配置 — ConfluenceConfig

```python
class ConfluenceConfig(BaseModel):
    base_url: str = ""                        # e.g. "https://inside-docupedia.bosch.com"
    context_path: str = "/confluence"         # Server/DC 默认上下文路径
    username: str = ""
    api_token: str = ""                       # PAT 或密码
    auth_method: Literal["basic", "bearer"] = "basic"  # "bearer" 用于 PAT
    verify_ssl: bool = True
    timeout: float = 30.0
    max_concurrent_requests: int = 5
    default_output_dir: str = "./confluence_downloads"
    download_attachments: bool = True
    max_depth: int = 10                       # BFS 遍历深度限制
    save_format: Literal["html", "pdf"] = "html"
    pdf_concurrency: int = 6                  # 并行导出线程数
    pdf_export_method: Literal["chrome", "native"] = "chrome"  # native = REST API + WeasyPrint
    request_delay: float = 0.2                # 请求间隔（秒），全局限流防止服务器断连
    max_retries: int = 2                      # 失败重试次数（指数退避）
```

**关键设计决策：**

- **`pdf_export_method`**：双模式选择。`"chrome"` 使用 Chrome CDP + Windows SPNEGO 适合 Kerberos 环境；`"native"` 使用 REST API `body.export_view` + WeasyPrint 转 PDF，无需 Chrome，适合 PAT 认证
- **`request_delay`**：全局限流器 `_throttle()` 使用 `asyncio.Lock` 序列化所有并发请求的发送时机，确保请求间隔不低于此值，防止 Confluence 服务器因请求过密而断连
- **`max_retries`**：指数退避重试（`base_delay × 2^attempt`），应对瞬时网络错误和服务器限流
- **空页面占位**：当 `export_view` 返回空 body 时（如仅含子页面链接的父页面），生成仅含标题的占位 PDF 而非报错，保证页面树完整性
- **DFS 层级合并**：PDF 合并按 Confluence 页面树的 DFS 前序遍历顺序排列，而非 BFS 发现顺序。BFS 遍历时记录 `children_order: dict[parent_id → [child_ids]]` 树结构，合并前通过 `_dfs_order()` 计算正确的层级展开顺序
- **自动分卷**：合并后 PDF 超过 200 页时自动拆分为多个卷（`{title}_{date}_vol1.pdf`, `vol2.pdf`, ...），避免单文件过大
- **缓存命名**：`_pdf_cache/{page_id}_{safe_title}.pdf` 包含页面标题，便于人工查找；兼容旧命名格式（按前缀匹配）
- **性能优化**：BFS 使用轻量 expand `"version,children.page"` 而非 `"body.storage,version,ancestors,children.page"`，并通过 `extract_children_from_page()` 从 `get_page` 响应直接提取子页面，消除冗余的 `get_all_child_pages` API 调用，分页 limit 从 25 提升至 100

### 17.4 配置 — RAGFlowConfig

在 `config.py` 的 `AppConfig` 中新增 `ragflow` 字段：

```python
class RAGFlowConfig(BaseModel):
    """RAGFlow 知识库配置。"""
    base_url: str = ""                          # e.g. "http://ragflow-host:9380"
    api_key: str = ""                           # Bearer token
    dataset_name: str = "confluence_docs"       # 目标 dataset 名称
    auto_upload_after_confluence: bool = False   # 下载后自动上传
    parse_after_upload: bool = True             # 上传后自动触发解析
```

### 17.5 RAGFlowClient 设计

`ragflow-sdk` 是同步库（基于 `requests`），用 `asyncio.loop.run_in_executor()` 包装为 async 接口。

```python
class RAGFlowClient:
    """RAGFlow 知识库异步客户端（包装 ragflow-sdk）。"""

    def __init__(self, config: RAGFlowConfig):
        self._config = config
        self._rag = None       # ragflow_sdk.RAGFlow 实例
        self._dataset = None   # 当前 dataset

    async def init(self) -> None:
        """初始化 SDK 连接 + 查找/创建 dataset。"""
        # RAGFlow(api_key, base_url) → 同步，需 executor
        # list_datasets(name=...) → 找到则复用，否则 create_dataset(name)

    async def upload_documents(self, file_paths: list[Path]) -> list[str]:
        """上传文件到 dataset，返回 doc_id 列表。"""
        # 构造 [{"display_name": name, "blob": bytes}]
        # dataset.upload_documents(docs) → 同步，需 executor

    async def parse_all_documents(self) -> int:
        """触发 dataset 中所有文档的解析。返回解析文档数。"""
        # dataset.list_documents() → 取 doc_ids
        # dataset.async_parse_documents(doc_ids)

    async def upload_and_parse(self, file_paths: list[Path]) -> dict:
        """组合方法：上传 + 解析。返回 {"uploaded": [...], "parse_count": N}"""

    async def close(self) -> None:
        """清理引用。"""
```

**关键设计决策：**
- `init()` 与 `__init__` 分离：SDK 初始化需要网络 I/O（验证 API key、查找 dataset），不适合在构造函数中执行
- 所有 SDK 调用通过 `loop.run_in_executor(None, sync_fn)` 异步化，避免阻塞事件循环
- dataset 按名字查找/创建：首次运行自动建立，后续复用
- **内网代理绕过**：`_ensure_no_proxy()` 静态方法在 `init()` 时自动将 RAGFlow 主机加入 `NO_PROXY` / `no_proxy` 环境变量，防止 `requests` 库将内网请求路由到公司代理

```python
@staticmethod
def _ensure_no_proxy(base_url: str) -> None:
    """将 RAGFlow 主机加入 NO_PROXY，防止内网请求走代理。"""
    host = urlparse(base_url).hostname
    if not host:
        return
    for var in ("no_proxy", "NO_PROXY"):
        current = os.environ.get(var, "")
        if host not in current:
            os.environ[var] = f"{host},{current}" if current else host
```

### 17.6 自动上传钩子

在 `ConfluenceDownloader.__init__` 中接受可选的 `ragflow_client` 参数：

```python
def __init__(self, client, config, ragflow_client=None):
    self._ragflow = ragflow_client
```

在 `_download_tree_pdf()` 的 PDF 合并写入之后插入上传逻辑（支持多卷）：

```python
# 写入 merged PDF(s) 之后...
if self._ragflow is not None:
    try:
        result = await self._ragflow.upload_and_parse(merged_paths)  # 支持多卷
        logger.info(
            f"RAGFlow: {len(result['uploaded'])} uploaded, "
            f"{result['parse_count']} parsing"
        )
    except Exception as e:
        logger.error(f"RAGFlow auto-upload failed: {e}")
        progress.errors.append(f"RAGFlow upload: {e}")
```

**重要原则**：RAGFlow 上传失败 **不影响** 下载任务状态（status 仍为 "completed"）。

### 17.7 CLI 命令

**A. 独立上传命令：**
```bash
python main.py --config config.local.yaml --upload-ragflow file1.pdf file2.pdf
```

**B. 下载 + 自动上传（配置文件中设置）：**
```yaml
ragflow:
  base_url: "http://<ragflow-host>:8880"   # RAGFlow API 端口（非 Web UI 端口）
  api_key: "ragflow-xxx"
  dataset_name: "confluence_docs"
  auto_upload_after_confluence: true
  parse_after_upload: true
```

```bash
python main.py --config config.local.yaml --download-confluence batch.csv
# PDF 下载完成后自动上传到 RAGFlow
```

### 17.8 模块行数估算

| 模块 | 预估行数 | 说明 |
|------|---------|------|
| `connectors/confluence_client.py` | ~810 | Confluence REST API + 双模式 PDF 导出 + 全局限流 + `extract_children_from_page` |
| `connectors/ragflow_client.py` | ~140 | RAGFlow SDK 异步包装 + 代理绕过 |
| `services/confluence_downloader.py` | ~870 | BFS + Pipeline + DFS 层级合并 + 自动分卷 + PDF 增量缓存 + 指数退避 + RAGFlow 钩子 |

### 17.9 部署注意事项

#### 端口区分

RAGFlow 部署通常暴露两个端口：

| 端口 | 用途 | SDK 使用 |
|------|------|---------|
| 80 / 443 | Web UI（管理界面） | ✗ |
| **8880** | **HTTP API**（`/api/v1/*`） | ✓ `base_url` 应指向此端口 |

`ragflow-sdk` 在 `base_url` 基础上拼接 `/api/v1` 路径，因此 `base_url` 必须指向 API 端口而非 Web UI 端口。

> 示例：`base_url: "http://10.161.151.72:8880"` → SDK 实际请求 `http://10.161.151.72:8880/api/v1/datasets`

#### 内网代理绕过

企业环境下，`http_proxy` / `https_proxy` 环境变量通常指向公司代理（如 `http://127.0.0.1:3128`）。`ragflow-sdk` 底层使用 `requests` 库，会自动走代理，导致内网 RAGFlow 请求被错误路由。

**解决方案**：`RAGFlowClient._ensure_no_proxy()` 在 `init()` 时自动从 `base_url` 提取主机名，追加到 `NO_PROXY` 和 `no_proxy` 环境变量：

```
init() 前: no_proxy = "localhost,127.0.0.*"
init() 后: no_proxy = "10.161.151.72,localhost,127.0.0.*"
```

此方案对进程全局生效，仅追加不覆盖，幂等安全（重复调用不会重复追加）。

#### 配置示例（实际部署）

```yaml
ragflow:
  base_url: "http://10.161.151.72:8880"
  api_key: "ragflow-ViMjBkODVlMTJjNjExZjE5NDBiYzJlMW"
  dataset_name: "taiji1.0"
  auto_upload_after_confluence: false
  parse_after_upload: true
```

#### 验证连通性

可用 curl 快速验证 API 可达性：

```bash
curl -H "Authorization: Bearer <api_key>" \
     "http://<host>:8880/api/v1/datasets?page=1&page_size=1"
# 正常返回: {"code": 0, "data": [...]}
```

## 18. Microsoft Teams 集成

### 18.1 功能概述

CAgent 支持与 Microsoft Teams 频道进行交互，适配**企业内网**环境（无公网入站连接）。

**核心设计**：所有通信均由 CAgent 主动发起（仅出站），通过多种传输方式实现消息发送和接收。

| 方向 | 机制 | 说明 |
|------|------|------|
| **发送** (CAgent→Teams) | ① Graph API ② Workflow Webhook ③ Incoming Webhook | 按优先级自动选择，高优失败自动降级 |
| **接收** (Teams→CAgent) | ① Graph API Delta Query 轮询 ② Outgoing Webhook | 轮询仅需出站连接，适配内网 |

**消息格式**：Adaptive Card（Microsoft 推荐格式），降级时自动转为文本或 O365 MessageCard。

### 18.2 架构

```
┌─────────────────────────────────────────────────────────┐
│                    CAgent (内网)                          │
│                                                          │
│  ┌──────────┐   ┌──────────────┐   ┌─────────────────┐  │
│  │ LangGraph │──→│ TeamsClient  │──→│ TransportLayer  │──┼──→ MS Cloud
│  │ Pipeline  │   │  (统一接口)   │←──│  (可插拔传输)   │←─┼──  (仅出站)
│  └──────────┘   └──────────────┘   │                 │  │
│                        │           │ ┌─Webhook────┐  │  │
│  ┌──────────┐          │           │ │(降级方案)  │  │  │
│  │ Teams    │←─────────┘           │ ├─Workflow───┤  │  │
│  │ Poller   │                      │ │(替代方案)  │  │  │
│  └──────────┘                      │ ├─Graph API──┤  │  │
│       │                            │ │(推荐,读+写)│  │  │
│  命令处理                           │ └────────────┘  │  │
│  (analyze/status/help)             └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 18.3 传输方式对比

| 能力 | Graph API | Workflow Webhook | Incoming Webhook |
|------|-----------|-----------------|-----------------|
| 发送消息 | ✅ | ✅ | ✅ |
| 接收命令 | ✅ (轮询) | ❌ | ❌ |
| Adaptive Card | ✅ | ✅ | ❌ (降级为文本) |
| 线程回复 | ✅ | ❌ | ❌ |
| 需要 Azure AD | 是 (Admin Consent) | 是 (Premium 许可) | 否 |
| 内网可用 | ✅ 仅出站 | ✅ 仅出站 | ✅ 仅出站 |
| 微软退役计划 | 无 | 无 | ⚠️ 已宣布退役 |

可同时配置多种方式，系统自动按优先级选择并支持降级。

### 18.4 配置 — TeamsConfig

```python
class TeamsConfig(BaseModel):
    webhook_url: str = ""               # Incoming Webhook URL（降级方案）
    outgoing_webhook_secret: str = ""   # Outgoing Webhook HMAC secret
    enabled: bool = False
    notify_on_analysis_complete: bool = True
    timeout: float = 30.0
    proxy: str = ""                     # HTTP 代理 (如 "http://proxy:8080")
    workflow_webhook_url: str = ""      # Power Automate Workflow URL
    # Graph API
    graph_tenant_id: str = ""           # Azure AD 租户 ID
    graph_client_id: str = ""           # 应用 (客户端) ID
    graph_client_secret: str = ""       # 客户端密钥
    graph_team_id: str = ""             # Teams 团队 ID
    graph_channel_id: str = ""          # 频道 ID
    graph_poll_interval: float = 10.0   # 轮询间隔 (秒)
    graph_bot_name: str = "CAgent"      # Bot 显示名
```

配置示例：
```yaml
teams:
  enabled: true
  proxy: "http://corporate-proxy:8080"  # 企业代理，无则留空

  # 发送方式 (按优先级: graph > workflow > webhook)
  webhook_url: ""
  workflow_webhook_url: "https://prod-xx.logic.azure.com:443/workflows/..."

  # Graph API (双向通信)
  graph_tenant_id: "${AZURE_TENANT_ID}"
  graph_client_id: "${AZURE_CLIENT_ID}"
  graph_client_secret: "${AZURE_CLIENT_SECRET}"
  graph_team_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  graph_channel_id: "19:xxxxx@thread.tacv2"
  graph_poll_interval: 10.0
  graph_bot_name: "CAgent"

  # Outgoing Webhook (有入站连接时可用)
  outgoing_webhook_secret: ""
  notify_on_analysis_complete: true
```

### 18.5 模块设计

#### TeamsClient (`connectors/teams_client.py`)

统一通信客户端，自动选择传输方式：

| 方法 | 说明 |
|------|------|
| `send_adaptive_card(card)` | 发送 Adaptive Card，自动选择最优传输 |
| `send_message(text)` | 发送文本消息，支持全部传输方式 |
| `send_analysis_result(state)` | 发送分析结果（优先 Adaptive Card，降级 MessageCard） |
| `send_card(title, summary, ...)` | 发送 O365 MessageCard（向后兼容） |
| `set_graph_client(client)` | 注入 Graph API 客户端 |
| `verify_hmac(body, token, secret)` | 静态方法，验证 HMAC-SHA256 |
| `parse_command(text)` | 静态方法，解析命令 |

**传输优先级**：Graph API → Workflow Webhook → Incoming Webhook（降级为文本）。

**代理支持**：通过 `httpx.AsyncHTTPTransport(proxy=...)` 实现，所有出站请求自动走代理。

#### Adaptive Card 构建器 (`connectors/teams_card_builder.py`)

工厂方法生成各类 Adaptive Card：

| 方法 | 用途 |
|------|------|
| `build_analysis_result_card(state)` | 分析结果（状态颜色、根因、修复建议） |
| `build_progress_card(bug_key, step, total)` | 分析进度 |
| `build_error_card(bug_key, errors)` | 错误通知 |
| `build_status_card(...)` | 系统状态 |
| `build_help_card()` | 命令帮助 |
| `wrap_for_workflow_webhook(card)` | 包装为 Workflow payload |
| `wrap_for_graph_api(card)` | 包装为 Graph API payload |

#### Graph API 认证 (`connectors/graph_auth.py`)

Azure AD OAuth2 Client Credentials Flow：
- 自动获取 access_token，过期前 5 分钟自动刷新
- 基于 httpx，无额外 MSAL 依赖
- 所需权限：`ChannelMessage.Read.All`（Application，需 Admin Consent）
- 发送权限：`ChannelMessage.Send`（需 RSC 或 Bot 注册，可选）

#### Graph API Teams 客户端 (`connectors/graph_teams_client.py`)

| 方法 | 说明 |
|------|------|
| `send_channel_message(content, card)` | 发送消息/卡片到频道 |
| `reply_to_message(message_id, content, card)` | 线程内回复 |
| `get_channel_messages_delta()` | 增量获取新消息 (Delta Query) |
| `list_message_replies(message_id)` | 读取消息回复 |
| `is_own_message(msg)` | 判断是否为 Bot 自己的消息 |
| `is_mention_or_command(msg)` | 判断是否为命令消息 |

**Delta Query**：首次调用获取 deltaLink，后续只返回新消息，高效低开销。

#### Teams 频道轮询器 (`watcher/teams_poller.py`)

设计模式与 `JqlPoller` 一致：
- 轮询间隔可配置（默认 10 秒）
- 首次启动跳过历史消息（仅建立 deltaLink）
- 过滤自己发的消息，识别 @mention 或命令前缀
- 命令回复在同一线程中，失败时降级为频道直接发送
- 支持命令：`analyze <key>`、`status`、`help`

### 18.6 集成钩子

在 `write_report` 节点中，分析完成后自动发送 Teams 通知：

```python
# nodes/write_report.py
if teams_client and config.teams.notify_on_analysis_complete:
    try:
        await teams_client.send_analysis_result(state)
    except Exception as e:
        logger.warning(f"Teams 通知失败: {e}")
```

**重要**：Teams 通知失败 **不影响** 分析流程状态。

### 18.7 main.py 集成

三种运行模式均支持 Teams 集成：

- **`--once`**：创建 TeamsClient + GraphTeamsClient，分析完成后发送通知
- **`--mode webhook`**：启动时创建客户端，注入到 LangGraph pipeline
- **`--mode polling`**：额外启动 `TeamsChannelPoller`，与 Jira/RTC Poller 并发运行

```python
# main.py 中的初始化流程
teams = _create_teams_client(config)          # TeamsClient
graph_auth, graph_client = _create_graph_clients(config)  # Graph API
if teams and graph_client:
    teams.set_graph_client(graph_client)       # 注入 Graph 传输
```

### 18.8 CLI 命令

```bash
# 测试发送（自动选择可用传输方式）
python main.py --teams-send "测试消息"

# Polling 模式（同时启动 Teams Channel Poller）
python main.py --mode polling
```

### 18.9 模块清单

| 模块 | 行数 | 说明 |
|------|------|------|
| `connectors/teams_client.py` | ~280 | 多传输通信客户端 |
| `connectors/teams_card_builder.py` | ~300 | Adaptive Card 构建工具 |
| `connectors/graph_auth.py` | ~100 | Azure AD OAuth2 认证 |
| `connectors/graph_teams_client.py` | ~230 | Graph API Teams 消息客户端 |
| `watcher/teams_poller.py` | ~170 | 频道消息轮询器 |
| `watcher/teams_webhook_handler.py` | ~130 | Outgoing Webhook 路由（保留） |
| `tests/test_teams_client.py` | ~640 | TeamsClient 单元测试 (62 tests) |
| `tests/test_teams_card_builder.py` | ~220 | Card 构建器测试 (18 tests) |
| `tests/test_graph_auth.py` | ~140 | OAuth2 认证测试 (11 tests) |
| `tests/test_graph_teams_client.py` | ~290 | Graph API 客户端测试 (22 tests) |
| `tests/test_teams_poller.py` | ~160 | 轮询器测试 (11 tests) |
