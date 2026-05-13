# 多 RTC 配置使用指南

## 配置格式

在 `config.yaml` 或 `config.local.yaml` 中，`rtc` 字段现在支持两种格式：

### 格式 1: 单个 RTC 配置（向后兼容）

```yaml
rtc:
  name: "MyProject"  # 可选
  ccm_url: "https://rtc.example.com/ccm"
  username: "user"
  password: "pass"
  project_area_name: "My Project Area"
  verify_ssl: false
  with_jazz: true
```

### 格式 2: 多个 RTC 配置（列表）

```yaml
rtc:
  - name: "PEEDP"
    ccm_url: "https://peedp.saic-gm.com/ccm"
    username: "user1"
    password: "pass1"
    project_area_name: ""
    verify_ssl: false
    with_jazz: true

  - name: "SGM Local 8155"
    ccm_url: "https://rb-alm-20-p.de.bosch.com/ccm"
    username: "user2"
    password: "pass2"
    project_area_name: "SGM Local 8155"
    verify_ssl: false
    with_jazz: true
```

## 使用方法

### 1. 命令行使用（CAgent）

#### 使用默认 RTC（列表中的第一个）

```bash
cd CAgent
~/CAgent_env/bin/python scripts/download_bugs.py --id 12345
```

#### 指定特定的 RTC 项目

```bash
# 使用项目名称（name 字段）
~/CAgent_env/bin/python scripts/download_bugs.py --id 12345 --project "SGM Local 8155"

# 或使用 project_area_name
~/CAgent_env/bin/python scripts/download_bugs.py --id 67890 --project "PEEDP"
```

### 2. 在 TAgent 中使用

在 TAgent 的 LLM 工具调用中：

```python
# 下载默认 RTC 的工单
download_rtc_case_tool(case_id="12345")

# 下载指定 RTC 项目的工单
download_rtc_case_tool(case_id="67890", project_name="SGM Local 8155")
```

## 配置说明

### `name` 字段

- **可选字段**，用于标识不同的 RTC 配置
- 通过 `--project` 参数或 `project_name` 参数引用
- 如果不指定 name，可以使用 `project_area_name` 来匹配

### 匹配规则

当指定 `--project` 或 `project_name` 时，系统会按以下顺序匹配：

1. 精确匹配 `name` 字段
2. 精确匹配 `project_area_name` 字段
3. 如果都不匹配，返回错误

如果不指定项目名称，默认使用：
- 列表模式：第一个配置
- 单配置模式：唯一的配置

## 示例场景

### 场景 1: 开发环境（只配置一个 RTC）

config.local.yaml:
```yaml
rtc:
  ccm_url: "https://rtc.dev.com/ccm"
  username: "dev_user"
  password: "dev_pass"
```

使用：
```bash
python scripts/download_bugs.py --id 12345
```

### 场景 2: 多项目环境

config.local.yaml:
```yaml
rtc:
  - name: "Project A"
    ccm_url: "https://rtc-a.com/ccm"
    username: "user_a"
    password: "pass_a"
    project_area_name: "ProjectA Team"

  - name: "Project B"
    ccm_url: "https://rtc-b.com/ccm"
    username: "user_b"
    password: "pass_b"
    project_area_name: "ProjectB Team"
```

使用：
```bash
# Project A 的工单
python scripts/download_bugs.py --id 12345 --project "Project A"

# Project B 的工单
python scripts/download_bugs.py --id 67890 --project "Project B"

# 不指定项目，使用第一个（Project A）
python scripts/download_bugs.py --id 11111
```

## 当前配置

当前 `config.yaml` 已配置两个 RTC：

1. **PEEDP** (默认)
   - URL: https://peedp.saic-gm.com/ccm
   - 用户: Pdoj2h

2. **SGM Local 8155**
   - URL: https://rb-alm-20-p.de.bosch.com/ccm
   - 用户: eft1sgh
   - 项目区域: SGM Local 8155

密码已配置在 `config.local.yaml` 中（不会提交到 git）。
