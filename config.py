"""
config.py — Wiki → RAGFlow 配置加载

从 config.yaml 加载配置。只包含 Confluence 下载和 RAGFlow 上传所需字段。
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class ConfluenceConfig(BaseModel):
    """Confluence Server/Data Center 连接配置。"""

    base_url: str = ""
    context_path: str = "/confluence"
    username: str = ""
    api_token: str = ""  # PAT 或密码
    auth_method: Literal["basic", "bearer"] = "basic"
    verify_ssl: bool = True
    timeout: float = 30.0
    max_concurrent_requests: int = 5
    default_output_dir: str = "./confluence_downloads"
    download_attachments: bool = True
    max_depth: int = 10
    save_format: Literal["json", "md"] = "md"
    request_delay: float = 0.2
    max_retries: int = 2


class RAGFlowConfig(BaseModel):
    """RAGFlow 知识库配置。"""

    base_url: str = ""
    api_key: str = ""
    dataset_name: str = "confluence_docs"
    auto_upload_after_confluence: bool = False
    parse_after_upload: bool = True
    parse_timeout: float = 600.0
    parse_poll_interval: float = 5.0


class AppConfig(BaseModel):
    """应用总配置。"""

    confluence: ConfluenceConfig = Field(default_factory=ConfluenceConfig)
    ragflow: RAGFlowConfig = Field(default_factory=RAGFlowConfig)


def _deep_merge(base: object, override: object) -> object:
    """深度合并两份 YAML 解析结果，override 覆盖 base。

    合并规则：
    - 两边都是 dict：递归合并；override 中存在的键覆盖 base 中相同键
    - 其他类型：override 整体替换 base

    用途：让 ``config.local.yaml`` 只填想覆盖的字段（如 ``api_token``），
    避免把 ``base_url`` 等公共字段重复抄一遍。
    """
    if isinstance(base, dict) and isinstance(override, dict):
        merged: dict = dict(base)
        for k, v in override.items():
            if k in merged:
                merged[k] = _deep_merge(merged[k], v)
            else:
                merged[k] = v
        return merged
    return override


def _load_yaml(path: Path) -> dict:
    """读取并校验 YAML 配置文件，返回顶层 dict。空文件返回空 dict。"""
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError(f"配置文件内容格式错误（顶层应为 mapping）: {path}")
    return raw


def load_config(path: str | Path | None = None) -> AppConfig:
    """
    从 YAML 文件加载配置。

    优先级（从高到低）：
    1. ``path`` 参数（显式指定，如 ``--config``）
    2. 环境变量 ``CONFIG_PATH``
    3. 自动探测：``config.yaml``（基础） + ``config.local.yaml``（覆盖）做深合并
       - 两个文件都不存在则报错
       - 任一存在即可工作；两个都存在时 local 按字段级覆盖 base
    """
    import os

    config_dir = Path(__file__).parent

    if path is not None:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"指定的配置文件不存在: {path}")
        raw = _load_yaml(path)
        if not raw:
            raise ValueError(f"配置文件内容为空: {path}")
        return AppConfig(**raw)

    if os.environ.get("CONFIG_PATH"):
        env_path = Path(os.environ["CONFIG_PATH"])
        if not env_path.exists():
            raise FileNotFoundError(f"CONFIG_PATH 指定的配置文件不存在: {env_path}")
        raw = _load_yaml(env_path)
        if not raw:
            raise ValueError(f"配置文件内容为空: {env_path}")
        return AppConfig(**raw)

    default_path = config_dir / "config.yaml"
    local_path = config_dir / "config.local.yaml"

    if not default_path.exists() and not local_path.exists():
        raise FileNotFoundError(
            f"未找到配置文件，请创建 {default_path} 或 {local_path}"
        )

    base: dict = _load_yaml(default_path) if default_path.exists() else {}
    override: dict = _load_yaml(local_path) if local_path.exists() else {}
    merged = _deep_merge(base, override)

    if not merged or not isinstance(merged, dict):
        sources = []
        if default_path.exists():
            sources.append(str(default_path))
        if local_path.exists():
            sources.append(str(local_path))
        raise ValueError(f"配置文件内容为空或格式错误: {', '.join(sources)}")

    return AppConfig(**merged)
