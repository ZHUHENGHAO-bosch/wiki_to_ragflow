# Wiki → RAGFlow 同步工具

一个把 **Bosch Confluence (inside-docupedia)** 页面树抓下来、转成 Markdown、再批量上传到 **RAGFlow** 知识库的 CLI 工具。

适用场景：把团队 / 项目在 Confluence 上沉淀的文档同步成 RAGFlow dataset，给下游 RAGChat 等检索 / 问答系统用。

---

## 功能特点

- **端到端管道**：一条命令完成 `下载 Confluence → 转 MD → 上传 RAGFlow → 触发解析 → 检查结果`
- **批量输入**：单个 URL / Page ID，或 CSV 批量列表
- **保留目录层级**：按页面父子关系生成嵌套目录的 `.md`，含图片本地化
- **可单独使用**：仅下载、仅上传、列 / 删 dataset 等子命令独立可调
- **失败容忍**：单页写失败不会让整棵树崩，照样输出 `_tree.json`
- **本地覆盖配置**：`config.yaml`（公共，入库）+ `config.local.yaml`（私有，gitignored）字段级深合并

---

## 项目结构

```
wiki_to_ragflow/
├── main.py                 # CLI 入口（argparse）
├── config.py               # 配置加载（pydantic + deep merge）
├── config.yaml             # 公共配置模板（无密钥，可入库）
├── config.local.yaml       # 本地覆盖（含真实 token，已 gitignored）  ← 你自己建
├── requirements.txt
├── connectors/
│   ├── confluence_client.py    # Confluence REST API 客户端 (httpx, async)
│   └── ragflow_client.py       # RAGFlow SDK 封装
└── services/
    ├── confluence_downloader.py    # BFS 抓页面树 + 写 MD/JSON + 图片
    └── confluence_html_parser.py   # Confluence storage HTML → 结构化 blocks
```

---

## 安装

需要 Python 3.10+（已在 3.14 上测试过）。

```bash
# 1. 克隆并进入目录
git clone https://github.com/ZHUHENGHAO-bosch/wiki_to_ragflow.git
cd wiki_to_ragflow

# 2. 建议建一个虚拟环境
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
```

---

## 配置

### 两个文件，一个目的

| 文件 | 用途 | 入库？ |
|---|---|---|
| `config.yaml` | 公共默认值（base_url / 默认目录 / 超时等），**不含密钥** | 入库 |
| `config.local.yaml` | 本机私有覆盖（API token / API key 等敏感字段） | **永不入库**（`.gitignore` 已覆盖） |

加载逻辑见 `config.py::load_config()`：自动探测目录下两个文件，做**字段级深合并**——你在 `config.local.yaml` 里写了哪个字段就覆盖哪个，没写的字段保留 `config.yaml` 的值。

### 第一步：复制并填写本地配置

仓库里没有 `config.local.yaml`（也不会有）。第一次使用，自己建一份：

```yaml
# config.local.yaml —— 仅本机使用，绝对不要 commit！
confluence:
  # 在 https://inside-docupedia.bosch.com 个人设置 → Personal Access Tokens 生成
  api_token: "你的-Confluence-PAT"
  # auth_method=basic 时才需要 username，bearer 模式可留空
  # username: "your.bosch.id"

ragflow:
  # 在 RAGFlow Web UI 个人设置 → API Keys 生成
  api_key: "ragflow-xxxxxxxxxxxxxxxxxx"
```

### `config.yaml` 关键字段速查

```yaml
confluence:
  base_url: "https://inside-docupedia.bosch.com"
  context_path: "/confluence"
  auth_method: "bearer"          # bearer (PAT) / basic (账号密码)
  verify_ssl: false              # 内网自签证书一般填 false
  max_depth: 5                   # BFS 最大遍历深度
  save_format: "md"              # md / json
  default_output_dir: "./confluence_downloads"
  download_attachments: false
  request_delay: 0.3             # 每次请求间隔，防服务端断连
  max_retries: 3                 # 失败重试次数（指数退避）

ragflow:
  base_url: "http://10.161.151.72:8880"  # RAGFlow API 端口（不是 Web UI 端口）
  dataset_name: "taiji_test"             # 目标 dataset，不存在自动创建
  parse_after_upload: true               # 上传后自动触发解析
  parse_timeout: 600.0                   # 等解析完成超时（秒）
```

### 高级用法

- `python main.py --config path/to/other.yaml` —— **独占模式**，只读这一个文件，**不会**再合并 `config.local.yaml`，容易踩坑
- 环境变量 `CONFIG_PATH=path/to/x.yaml` 等价于 `--config`

---

## 使用

### 模式 1：端到端管道（最常用）

```bash
# 单个页面（URL 或 pageId 都行）
python main.py --confluence-to-ragflow https://inside-docupedia.bosch.com/confluence/pages/viewpage.action?pageId=1234567

# CSV 批量（CSV 第一列是 URL / pageId）
python main.py --confluence-to-ragflow batch.csv

# 上传前合并整棵树为单个 .md 再上传（适合小型文档集）
python main.py --confluence-to-ragflow URL --merge
```

### 模式 2：仅下载

```bash
# 抓整棵子树到 ./confluence_downloads（按 config.yaml 配置）
python main.py --download-confluence URL --confluence-format md

# 只看页数 / 层级，不抓正文 / 图片（快速估算用）
python main.py --download-confluence URL --discover-only

# 覆盖输出目录 + 最大深度
python main.py --download-confluence URL \
  --confluence-output ./out/proj_x \
  --confluence-depth 3
```

### 模式 3：仅上传

```bash
# 上传若干文件 / 目录到 RAGFlow（目录递归扫白名单扩展名）
python main.py --upload-ragflow ./out/proj_x ./extra/doc.pdf

# 指定 dataset 名（覆盖 config.yaml 里的 dataset_name）
python main.py --upload-ragflow ./out/proj_x --ragflow-dataset proj_x_kb
```

### 模式 4：把已抓的树合并成单个 MD

```bash
# 用之前 --download-confluence --confluence-format md 生成的输出目录
python main.py --merge-md ./out/proj_x

# 合并后顺便上传到 RAGFlow
python main.py --merge-md ./out/proj_x --then-upload
```

### 模式 5：RAGFlow 运维

```bash
# 列出当前 API key 可见的所有 dataset（顺便验证配置是否生效）
python main.py --list-datasets

# 按名字删（默认会二次确认）
python main.py --delete-dataset taiji_test

# 按 id 强删，跳过确认（脚本 / CI 用）
python main.py --delete-dataset a9764d5c502011f1bb944ed3f5edef51 --delete-by-id -y
```

### 全局参数

| 参数 | 作用 |
|---|---|
| `--config <path>` | 显式指定单一配置文件（**不再**合并 local） |
| `-v` / `--verbose` | DEBUG 级别日志 |
| `-y` / `--yes` | 跳过破坏性操作的确认提示 |

---

## 输出文件

执行 `--download-confluence --confluence-format md` 后，输出目录大致是：

```
confluence_downloads/
└── 根页面标题/
    ├── README.md                  # 根页面正文
    ├── 子页面 A/
    │   ├── README.md
    │   └── 子子页面/
    │       └── README.md
    ├── _images/                   # 集中存放页面图片
    │   └── <attachment-id>.png
    └── _tree.json                 # 整棵树的元数据（标题、url、path、parent）
```

`_tree.json` 是 `--merge-md` 模式的输入；任何分析 / 二次加工脚本也可以直接读它，不用再爬 Confluence。

---

## 故障排查

### 1. `UnicodeEncodeError: 'charmap' codec can't encode character ...`

Windows 终端默认非 UTF-8。两种解决方案任选其一：

```powershell
# A. 当前会话临时
$env:PYTHONIOENCODING = "utf-8"

# B. 永久设到 PowerShell profile
Add-Content $PROFILE '$env:PYTHONIOENCODING = "utf-8"'
```

### 2. `RAGFlow 未配置` / 401 / 403

检查 `config.local.yaml` 中 `ragflow.api_key` 是否正确，运行 `python main.py --list-datasets` 验证。

### 3. `SSL: CERTIFICATE_VERIFY_FAILED`

内网 Confluence 自签证书。`config.yaml` 已默认 `verify_ssl: false`。如需打开，请把内部 CA 加到系统信任链或 Python `certifi`。

### 4. 下载到一半卡住 / 频繁断连

调大 `config.yaml` 里的 `request_delay`（如 `0.5`）并适当降低 `max_concurrent_requests`（如 `3`）。

---

## 安全须知

- **永远不要** 把真实 API token / PAT / API key 写进 `config.yaml`、commit message、issue、聊天截图。
- 实际密钥只放在本机的 `config.local.yaml`（已 gitignored）或环境变量里。
- 如果发现密钥泄露，**立即去对应后台撤销并重新生成**，然后用 `git filter-repo --replace-text` 清洗历史，最后强推。Git 历史里的密钥即便从最新 commit 删掉，也依然能从旧 commit 里恢复出来。
- Bosch GitHub 启用了 Push Protection（GH013），会在 push 时扫描并拦截可疑 token —— 配合上述规范，不要试图通过 unblock 链接放行真实密钥。

---

## 开发约定

- Python 风格：标准库优先，依赖最小化（详见 `requirements.txt`）
- 异步 IO：Confluence / RAGFlow 客户端均基于 `httpx` async
- 类型：`pydantic v2` 做配置 schema 校验
- 日志：标准 `logging`，所有模块用 `logger = logging.getLogger(...)`，不用 `print` 调试
