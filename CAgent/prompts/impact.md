# 影响扩散分析 Prompt

此文件为保留模板。当前 Node 5 (analyze_impact) 通过代码分析实现，
不依赖 LLM。如需升级为 LLM 辅助分析，可启用此 Prompt。

## 用法

将以下信息注入模板后调用 LLM:
- 根因分析结果
- 受影响文件列表
- 调用关系
- 需求追溯链

## 模板

请根据以下 Bug 根因分析结果，评估影响范围:

根因: {root_cause_summary}
问题位置: {problem_location}
调用方文件: {caller_files}

请评估:
1. 每个调用方的风险等级 (high/medium/low)
2. 是否有未被测试覆盖的调用路径
3. 建议的回归测试优先级排序
