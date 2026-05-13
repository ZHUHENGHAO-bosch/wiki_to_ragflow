# Bug 根因分析

你是一个嵌入式软件 Bug 分析专家。请根据以下信息分析 Bug 的根因。

## Bug 信息
- **Bug Key**: {bug_key}
- **优先级**: {priority}
- **环境**: {environment}
- **描述**:
{bug_description}

## 关联测试用例
{test_cases_section}

## 关联需求
{requirements_section}

## 相关代码
{code_section}

---

## 分析要求

请完成以下分析并以 **JSON** 格式返回：

1. **根因层级 (level)**，必须为以下之一：
   - `实现偏离`：代码实现与需求不一致
   - `实现遗漏`：需求已定义但代码未实现
   - `需求遗漏`：需求本身缺失该场景
   - `需求歧义`：需求描述模糊导致实现理解偏差
   - `测试缺陷`：测试用例未覆盖该场景
   - `回归引入`：近期代码变更引入

2. **根因摘要 (summary)**：一句话描述根因

3. **详细分析 (detail)**：详细描述为什么会出现该 Bug

4. **问题定位 (problem_location)**：具体到文件名和行号（如 `module.c:142-155`），或函数名

5. **引入者 (introducer)**：如果能从 Git 记录判断，给出引入者姓名

6. **引入 commit (introducing_commit)**：对应的 commit hash

7. **修复建议 (fix_suggestions)**：数组，每项包含:
   - `label`: 修复方案名称
   - `description`: 具体修复方法
   - `effort`: 预估工作量（small / medium / large）

## 输出格式

```json
{
  "level": "实现偏离",
  "summary": "...",
  "detail": "...",
  "problem_location": "file.c:42-50",
  "introducer": "张三",
  "introducing_commit": "abc1234",
  "fix_suggestions": [
    {
      "label": "方案A",
      "description": "...",
      "effort": "small"
    }
  ]
}
```

请直接返回 JSON，不要添加其他文字。
