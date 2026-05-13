"""
config.py — 配置加载

从 config.yaml 和环境变量加载配置。
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class JiraConfig(BaseModel):
    """Jira 连接配置。"""

    name: str = ""  # 配置名称/标识符（用于多 Jira 配置场景，如 Bosch_Jira / Patac_Jira）
    base_url: str
    username: str = ""
    api_token: str = ""
    project_key: str = ""
    bug_issue_type: str = "Bug"
    test_case_issue_type: str = "Test Case"
    test_case_link_type: str = "is tested by"
    test_steps_field: str = "customfield_10100"
    requirement_field: str = "customfield_10200"
    auth_method: Literal["", "basic", "bearer"] = ""  # 认证方式覆盖（空=自动检测）
    verify_ssl: bool = True


class DngConfig(BaseModel):
    """DNG (DOORS Next Generation) OSLC 连接配置。"""

    base_url: str
    username: str = ""
    password: str = ""
    project_area: str = ""
    implemented_by_link_type: str = "implemented_by"
    validated_by_link_type: str = "validated_by"
    verify_ssl: bool = True


class GitRepoConfig(BaseModel):
    """Git 仓库配置。"""

    repos: list[RepoEntry] = Field(default_factory=list)
    search_extensions: list[str] = Field(
        default_factory=lambda: [".c", ".h", ".cpp", ".py"]
    )
    recent_commit_weeks: int = 4


class RepoEntry(BaseModel):
    """单个 Git 仓库条目。"""

    name: str
    path: str
    branch: str = "main"


# 修正前向引用
GitRepoConfig.model_rebuild()


class LlmConfig(BaseModel):
    """LLM 配置。"""

    model: str = "claude-sonnet-4-20250514"
    api_key: str = ""
    max_tokens: int = 4096
    temperature: float = 0.0


class WatcherConfig(BaseModel):
    """Bug 监控方式配置。"""

    mode: Literal["webhook", "polling"] = "webhook"
    polling_interval_seconds: int = 60
    jql_filter: str = (
        'issuetype = Bug AND status = Open AND labels not in ("analyzed")'
    )
    webhook_secret: str = ""


class WriterConfig(BaseModel):
    """报告写回配置。"""

    analyzed_label: str = "analyzed"
    auto_create_related_bugs: bool = False
    notify_webhook: str = ""


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
    save_format: Literal["html", "pdf", "json"] = "html"
    pdf_concurrency: int = 6  # 并行 CDP Tab 数（PDF 模式）
    pdf_export_method: Literal["chrome", "native"] = "chrome"  # native = REST API + WeasyPrint
    request_delay: float = 0.2  # 请求间隔（秒），防止服务器断连
    max_retries: int = 2  # 失败重试次数


class RAGFlowConfig(BaseModel):
    """RAGFlow 知识库配置。"""

    base_url: str = ""  # e.g. "http://ragflow-host:9380"
    api_key: str = ""
    dataset_name: str = "confluence_docs"
    auto_upload_after_confluence: bool = False
    parse_after_upload: bool = True
    parse_timeout: float = 600.0  # 解析最大等待时间（秒）
    parse_poll_interval: float = 5.0  # 解析轮询间隔（秒）


class TeamsConfig(BaseModel):
    """Microsoft Teams 连接配置。"""

    webhook_url: str = ""  # Incoming Webhook URL（发送通知，降级方案）
    outgoing_webhook_secret: str = ""  # Outgoing Webhook HMAC secret（接收命令）
    enabled: bool = False
    notify_on_analysis_complete: bool = True
    timeout: float = 30.0
    # Webhook 类型: auto=自动检测, connector=O365 MessageCard, power_automate=格式化文本
    webhook_type: Literal["auto", "connector", "power_automate"] = "auto"

    # 企业代理
    proxy: str = ""  # HTTP 代理 (如 "http://proxy:8080")

    # Power Automate Workflow Webhook（替代 Incoming Webhook）
    workflow_webhook_url: str = ""

    # Graph API 相关（双向通信）
    graph_tenant_id: str = ""  # Azure AD 租户 ID
    graph_client_id: str = ""  # 应用 (客户端) ID
    graph_client_secret: str = ""  # 客户端密钥
    graph_team_id: str = ""  # Teams 团队 ID
    graph_channel_id: str = ""  # 频道 ID
    graph_poll_interval: float = 10.0  # 轮询间隔 (秒)
    graph_bot_name: str = "CAgent"  # Bot 显示名 (用于过滤 @mention)



class RtcConfig(BaseModel):
    """RTC (Rational Team Concert) 连接配置。"""

    name: str = ""  # 配置名称/标识符（用于多 RTC 配置场景）
    ccm_url: str = ""  # e.g. "https://rb-alm-20-p.de.bosch.com/ccm"
    username: str = ""
    password: str = ""
    project_area_name: str = ""
    project_area_id: str = ""  # PA UUID，用于 OSLC context
    with_jazz: bool = True  # Jazz Form-based Auth
    old_auth: bool = False
    verify_ssl: bool = True
    # 字段映射 (参考 refer/RTC_Api 的 attribs_fetcher)
    field_mapping: dict[str, str] = Field(
        default_factory=lambda: {
            "summary": "dcterms:title",
            "identifier": "dcterms:identifier",
            "description": "dcterms:description",
            "state": "rtc_cm:state",
            "priority": "oslc_cm:priority",
            "tags": "dcterms:subject",
            "filed_against": "rtc_cm:filedAgainst",
            "modified": "dcterms:modified",
            "created": "dcterms:created",
            "creator": "dcterms:creator",
            "contributor": "dcterms:contributor",
            "comments": "rtc_cm:comments",
        }
    )
    # 轮询配置
    saved_query_id: str = ""  # Saved Query UUID
    polling_interval_seconds: int = 60
    analyzed_tag: str = "analyzed"  # 标记已分析的 tag (dc:subject)
    bug_work_item_type: str = "defect"
    # 附件下载配置
    attachments_output_dir: str = "./rtc_attachments"  # 附件下载目录
    max_attachment_size_mb: int = 500  # 单文件大小限制 (MB)


class MinioConfig(BaseModel):
    """MinIO 对象存储配置。"""

    endpoint: str = ""
    access_key: str = ""
    secret_key: str = ""
    bucket: str = "agent"
    prefix: str = "tagent"
    secure: bool = False


class AppConfig(BaseModel):
    """应用总配置。"""

    jira: JiraConfig | list[JiraConfig]
    dng: DngConfig
    git_repos: GitRepoConfig = Field(default_factory=GitRepoConfig)
    llm: LlmConfig = Field(default_factory=LlmConfig)
    watcher: WatcherConfig = Field(default_factory=WatcherConfig)
    writer: WriterConfig = Field(default_factory=WriterConfig)
    confluence: ConfluenceConfig = Field(default_factory=ConfluenceConfig)
    ragflow: RAGFlowConfig = Field(default_factory=RAGFlowConfig)
    teams: TeamsConfig = Field(default_factory=TeamsConfig)
    rtc: RtcConfig | list[RtcConfig] = Field(default_factory=RtcConfig)
    minio: MinioConfig = Field(default_factory=MinioConfig)

    def get_jira_config(self, name: str | None = None) -> JiraConfig | None:
        """获取指定的 Jira 配置。

        Args:
            name: Jira 配置名称（如 "Bosch_Jira" / "Patac_Jira"），为 None 返回首个

        Returns:
            匹配的 JiraConfig，未找到返回 None
        """
        if isinstance(self.jira, JiraConfig):
            if name is None or not name:
                return self.jira
            if self.jira.name == name:
                return self.jira
            return None
        else:
            if not self.jira:
                return None
            if name is None or not name:
                return self.jira[0]
            for cfg in self.jira:
                if cfg.name == name:
                    return cfg
            return None

    def list_jira_configs(self) -> list[JiraConfig]:
        """列出所有 Jira 配置。"""
        if isinstance(self.jira, JiraConfig):
            return [self.jira]
        else:
            return self.jira

    def get_rtc_config(self, name: str | None = None) -> RtcConfig | None:
        """获取指定的 RTC 配置。

        Args:
            name: RTC 配置名称，如果为 None 则返回第一个配置

        Returns:
            匹配的 RtcConfig，未找到返回 None
        """
        if isinstance(self.rtc, RtcConfig):
            # 单配置模式
            if name is None or not name:
                return self.rtc
            # 检查是否匹配（通过 name 或 project_area_name）
            if self.rtc.name == name or self.rtc.project_area_name == name:
                return self.rtc
            return None
        else:
            # 列表模式
            if not self.rtc:
                return None
            if name is None or not name:
                # 返回第一个
                return self.rtc[0]
            # 按 name 或 project_area_name 匹配
            for cfg in self.rtc:
                if cfg.name == name or cfg.project_area_name == name:
                    return cfg
            return None

    def list_rtc_configs(self) -> list[RtcConfig]:
        """列出所有 RTC 配置。"""
        if isinstance(self.rtc, RtcConfig):
            return [self.rtc]
        else:
            return self.rtc


def _deep_merge(base: object, override: object) -> object:
    """深度合并两份 YAML 解析结果，override 覆盖 base。

    合并规则：
    - 两边都是 dict：递归合并；override 中存在的键覆盖 base 中相同键
      （仅当 base 也是 dict 时递归，否则 override 直接替换该键）
    - 两边都是 list 且元素全是含 ``name`` 字段的 dict（典型如 ``jira``、``rtc``、
      ``git_repos.repos``）：按 ``name`` 做 by-key 合并，base 中的条目按原顺序保留，
      若 override 中存在同名条目则字段级深合并；override 中独有的条目追加在尾部
    - 其他 list 或类型不一致：override 整体替换 base

    这套语义让 ``config.local.yaml`` 对每个命名条目（如 ``Patac_Jira``）只填想覆盖
    的字段（如 ``api_token``）即可，避免把 ``base_url`` 等公共字段重复抄一遍。
    """
    if isinstance(base, dict) and isinstance(override, dict):
        merged: dict = dict(base)
        for k, v in override.items():
            if k in merged:
                merged[k] = _deep_merge(merged[k], v)
            else:
                merged[k] = v
        return merged

    if isinstance(base, list) and isinstance(override, list):
        # 仅当两边都是「dict 列表且每个 dict 都带 name」时才按 name 合并
        if (
            base
            and override
            and all(isinstance(x, dict) and "name" in x for x in base)
            and all(isinstance(x, dict) and "name" in x for x in override)
        ):
            override_by_name: dict[str, dict] = {x["name"]: x for x in override}
            seen: set[str] = set()
            result: list = []
            for item in base:
                name = item["name"]
                if name in override_by_name:
                    result.append(_deep_merge(item, override_by_name[name]))
                else:
                    result.append(item)
                seen.add(name)
            for item in override:
                if item["name"] not in seen:
                    result.append(item)
            return result
        return override

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
       - 任一存在即可工作；两个都存在时 local 按字段级 / by-name 覆盖 default
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
