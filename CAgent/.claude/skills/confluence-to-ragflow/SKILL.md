---
name: confluence-to-ragflow
description: 下载 Confluence 页面并上传到 RAGFlow 知识库。当用户要求下载 Confluence 页面、上传到 RAGFlow、或同时执行两者时触发。
disable-model-invocation: true
user-invocable: true
allowed-tools: Bash, Read, Grep, Glob
argument-hint: <confluence_url> [--dataset <知识库名称>]
---

# Confluence → RAGFlow 端到端管道

将 Confluence 页面树下载为 PDF 并上传到 RAGFlow 知识库进行解析。

## 参数解析

用户输入格式: `/confluence-to-ragflow <url_or_page_id> [--dataset <dataset_name>]`

- `$ARGUMENTS[0]` — Confluence 页面 URL 或 Page ID（必填）
- 如果用户通过 `--dataset` 指定了知识库名称，提取该值；否则使用配置文件默认值

## 执行步骤

1. **解析参数**：从 `$ARGUMENTS` 中提取 URL 和可选的 dataset 名称
2. **构建命令**：

```bash
~/CAgent_env/bin/python3 main.py --config config.local.yaml \
  --confluence-to-ragflow "<url_or_id>" \
  [--ragflow-dataset "<dataset_name>"]
```

3. **执行命令**：使用 Bash 工具运行，设置 `timeout: 600000`（10 分钟），因为下载+上传+解析耗时较长
4. **报告结果**：汇总下载页数、上传状态、解析结果

## 注意事项

- 工作目录必须是项目根目录 `/mnt/c/workspace/02_tagent/CAgent`
- 使用 `config.local.yaml` 配置文件（含 Confluence 和 RAGFlow 凭据）
- PDF 导出后若修改过 sanitize 逻辑，需先清缓存：`find confluence_downloads -name "_pdf_cache" -type d -exec rm -rf {} +`
- RAGFlow 最后阶段（解析）可能耗时较长，耐心等待
- 如果 RAGFlow 解析个别页出错（如 NaN 错误），属于服务端问题，不影响其余页面

## 示例

```
/confluence-to-ragflow https://inside-docupedia.bosch.com/confluence/spaces/XX/pages/12345/PageTitle --dataset KB-MyProject
/confluence-to-ragflow https://inside-docupedia.bosch.com/confluence/spaces/XX/pages/12345/PageTitle
/confluence-to-ragflow 12345 --dataset MyDataset
```
