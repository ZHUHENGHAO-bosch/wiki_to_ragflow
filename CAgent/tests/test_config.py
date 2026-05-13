"""config.py 单元测试。"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

import config as config_module
from config import AppConfig, JiraConfig, DngConfig, LlmConfig, RtcConfig, load_config
from config import _deep_merge


SAMPLE_YAML = """\
jira:
  base_url: "https://jira.test.com"
  username: "user"
  api_token: "token123"
  project_key: "PRJ"

dng:
  base_url: "https://dng.test.com"
  username: "user"
  password: "pass"
  project_area: "https://dng.test.com/rm/project/area1"

git_repos:
  repos:
    - name: "fw"
      path: "/tmp/fw"
      branch: "main"
  search_extensions:
    - ".c"
    - ".h"

llm:
  model: "claude-sonnet-4-20250514"
  api_key: "sk-test"
  max_tokens: 2048

watcher:
  mode: "polling"
  polling_interval_seconds: 30

writer:
  analyzed_label: "done"
"""


class TestLoadConfig:
    def test_load_valid_yaml(self, tmp_path: Path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text(SAMPLE_YAML, encoding="utf-8")

        cfg = load_config(config_file)

        assert isinstance(cfg, AppConfig)
        assert cfg.jira.base_url == "https://jira.test.com"
        assert cfg.jira.api_token == "token123"
        assert cfg.dng.base_url == "https://dng.test.com"
        assert cfg.llm.model == "claude-sonnet-4-20250514"
        assert cfg.llm.max_tokens == 2048
        assert cfg.watcher.mode == "polling"
        assert cfg.watcher.polling_interval_seconds == 30
        assert cfg.writer.analyzed_label == "done"

    def test_git_repos_parsed(self, tmp_path: Path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text(SAMPLE_YAML, encoding="utf-8")

        cfg = load_config(config_file)

        assert len(cfg.git_repos.repos) == 1
        assert cfg.git_repos.repos[0].name == "fw"
        assert cfg.git_repos.repos[0].branch == "main"
        assert cfg.git_repos.search_extensions == [".c", ".h"]

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/path/config.yaml")

    def test_defaults(self, tmp_path: Path):
        minimal = """\
jira:
  base_url: "https://jira.test.com"
dng:
  base_url: "https://dng.test.com"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(minimal, encoding="utf-8")

        cfg = load_config(config_file)

        # 检查默认值
        assert cfg.llm.temperature == 0.0
        assert cfg.watcher.mode == "webhook"
        assert cfg.jira.verify_ssl is True


class TestJiraConfig:
    def test_defaults(self):
        cfg = JiraConfig(base_url="https://j.com")
        assert cfg.bug_issue_type == "Bug"
        assert cfg.test_case_issue_type == "Test Case"
        assert cfg.verify_ssl is True


class TestRtcConfig:
    def test_defaults(self):
        cfg = RtcConfig()
        assert cfg.ccm_url == ""
        assert cfg.with_jazz is True
        assert cfg.old_auth is False
        assert cfg.verify_ssl is True
        assert cfg.polling_interval_seconds == 60
        assert cfg.analyzed_tag == "analyzed"
        assert cfg.bug_work_item_type == "defect"

    def test_field_mapping_defaults(self):
        cfg = RtcConfig()
        assert "summary" in cfg.field_mapping
        assert cfg.field_mapping["summary"] == "dcterms:title"
        assert cfg.field_mapping["priority"] == "oslc_cm:priority"

    def test_custom_values(self):
        cfg = RtcConfig(
            ccm_url="https://rtc.test.com/ccm",
            username="user",
            password="pass",
            project_area_name="MyProject",
            saved_query_id="_QueryABC",
            polling_interval_seconds=120,
        )
        assert cfg.ccm_url == "https://rtc.test.com/ccm"
        assert cfg.saved_query_id == "_QueryABC"
        assert cfg.polling_interval_seconds == 120

    def test_rtc_in_appconfig(self):
        cfg = AppConfig(
            jira=JiraConfig(base_url="https://j.com"),
            dng=DngConfig(base_url="https://d.com"),
            rtc=RtcConfig(ccm_url="https://rtc.com/ccm"),
        )
        assert cfg.rtc.ccm_url == "https://rtc.com/ccm"

    def test_rtc_defaults_in_appconfig(self):
        """AppConfig 不提供 rtc 时应使用默认值。"""
        cfg = AppConfig(
            jira=JiraConfig(base_url="https://j.com"),
            dng=DngConfig(base_url="https://d.com"),
        )
        assert cfg.rtc.ccm_url == ""
        assert isinstance(cfg.rtc, RtcConfig)

    def test_load_yaml_with_rtc(self, tmp_path):
        yaml_content = """\
jira:
  base_url: "https://jira.test.com"
dng:
  base_url: "https://dng.test.com"
rtc:
  ccm_url: "https://rtc.test.com/ccm"
  username: "rtc_user"
  password: "rtc_pass"
  project_area_name: "TestArea"
  saved_query_id: "_TestQuery123"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content, encoding="utf-8")

        cfg = load_config(config_file)
        assert cfg.rtc.ccm_url == "https://rtc.test.com/ccm"
        assert cfg.rtc.username == "rtc_user"
        assert cfg.rtc.saved_query_id == "_TestQuery123"


class TestMultiJiraConfig:
    """多 Jira 配置场景（FEATURE-554）。"""

    def test_single_jira_get_default(self):
        cfg = AppConfig(
            jira=JiraConfig(base_url="https://j.com"),
            dng=DngConfig(base_url="https://d.com"),
        )
        got = cfg.get_jira_config()
        assert got is not None
        assert got.base_url == "https://j.com"

    def test_single_jira_get_by_name(self):
        cfg = AppConfig(
            jira=JiraConfig(name="Bosch_Jira", base_url="https://j.com"),
            dng=DngConfig(base_url="https://d.com"),
        )
        assert cfg.get_jira_config("Bosch_Jira") is not None
        assert cfg.get_jira_config("Patac_Jira") is None

    def test_list_jira_get_default(self):
        cfg = AppConfig(
            jira=[
                JiraConfig(name="Bosch_Jira", base_url="https://b.com"),
                JiraConfig(name="Patac_Jira", base_url="https://p.com"),
            ],
            dng=DngConfig(base_url="https://d.com"),
        )
        first = cfg.get_jira_config()
        assert first is not None
        assert first.name == "Bosch_Jira"

    def test_list_jira_get_by_name(self):
        cfg = AppConfig(
            jira=[
                JiraConfig(name="Bosch_Jira", base_url="https://b.com"),
                JiraConfig(name="Patac_Jira", base_url="https://p.com"),
            ],
            dng=DngConfig(base_url="https://d.com"),
        )
        patac = cfg.get_jira_config("Patac_Jira")
        assert patac is not None
        assert patac.base_url == "https://p.com"

    def test_list_jira_get_unknown_returns_none(self):
        cfg = AppConfig(
            jira=[JiraConfig(name="Bosch_Jira", base_url="https://b.com")],
            dng=DngConfig(base_url="https://d.com"),
        )
        assert cfg.get_jira_config("Unknown") is None

    def test_list_jira_configs_single(self):
        cfg = AppConfig(
            jira=JiraConfig(base_url="https://j.com"),
            dng=DngConfig(base_url="https://d.com"),
        )
        all_jiras = cfg.list_jira_configs()
        assert len(all_jiras) == 1

    def test_list_jira_configs_multi(self):
        cfg = AppConfig(
            jira=[
                JiraConfig(name="Bosch_Jira", base_url="https://b.com"),
                JiraConfig(name="Patac_Jira", base_url="https://p.com"),
            ],
            dng=DngConfig(base_url="https://d.com"),
        )
        all_jiras = cfg.list_jira_configs()
        assert len(all_jiras) == 2
        names = [j.name for j in all_jiras]
        assert "Bosch_Jira" in names
        assert "Patac_Jira" in names

    def test_load_yaml_with_multi_jira(self, tmp_path: Path):
        yaml_content = """\
jira:
  - name: "Bosch_Jira"
    base_url: "https://rb-tracker.bosch.com/tracker08"
    username: "u1"
  - name: "Patac_Jira"
    base_url: "https://jira-patac.apps.saic-gm.com"
    username: "u2"
dng:
  base_url: "https://dng.test.com"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content, encoding="utf-8")

        cfg = load_config(config_file)
        bosch = cfg.get_jira_config("Bosch_Jira")
        patac = cfg.get_jira_config("Patac_Jira")
        assert bosch is not None and bosch.username == "u1"
        assert patac is not None and patac.base_url == "https://jira-patac.apps.saic-gm.com"


class TestLlmConfig:
    def test_defaults(self):
        cfg = LlmConfig()
        assert cfg.model == "claude-sonnet-4-20250514"
        assert cfg.max_tokens == 4096
        assert cfg.temperature == 0.0


class TestDeepMerge:
    """`_deep_merge` 的 dict / by-name list 合并语义。"""

    def test_dict_simple_override(self):
        base = {"a": 1, "b": 2}
        override = {"b": 20, "c": 3}
        assert _deep_merge(base, override) == {"a": 1, "b": 20, "c": 3}

    def test_dict_nested_merge(self):
        base = {"jira": {"base_url": "https://j.com", "api_token": ""}}
        override = {"jira": {"api_token": "secret"}}
        merged = _deep_merge(base, override)
        # 嵌套字段级合并：base_url 保留，api_token 被覆盖
        assert merged == {"jira": {"base_url": "https://j.com", "api_token": "secret"}}

    def test_list_with_name_merged_by_name(self):
        base = [
            {"name": "Bosch_Jira", "base_url": "https://b.com", "api_token": ""},
            {"name": "Patac_Jira", "base_url": "https://p.com", "api_token": ""},
        ]
        override = [
            {"name": "Patac_Jira", "api_token": "secret-p"},
            {"name": "Bosch_Jira", "api_token": "secret-b"},
        ]
        merged = _deep_merge(base, override)
        # base 的顺序保留；同名条目字段级合并
        assert isinstance(merged, list)
        assert merged[0] == {
            "name": "Bosch_Jira",
            "base_url": "https://b.com",
            "api_token": "secret-b",
        }
        assert merged[1] == {
            "name": "Patac_Jira",
            "base_url": "https://p.com",
            "api_token": "secret-p",
        }

    def test_list_with_name_appends_new_entries(self):
        base = [{"name": "A", "v": 1}]
        override = [{"name": "B", "v": 2}]
        merged = _deep_merge(base, override)
        assert merged == [{"name": "A", "v": 1}, {"name": "B", "v": 2}]

    def test_plain_list_replaced(self):
        # 不含 name 的 list 整体替换，而非合并
        base = [".c", ".h", ".py"]
        override = [".rs"]
        assert _deep_merge(base, override) == [".rs"]

    def test_type_mismatch_override_wins(self):
        # 类型不一致时 override 整体替换
        assert _deep_merge({"a": 1}, [1, 2]) == [1, 2]
        assert _deep_merge([1, 2], {"a": 1}) == {"a": 1}
        assert _deep_merge("str", 42) == 42


class TestLoadConfigAutoDetect:
    """自动探测分支：config.yaml + config.local.yaml 深合并行为（修复 BUG）。"""

    @pytest.fixture
    def fake_cagent_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
        """把 config_module.__file__ 指到 tmp_path，让 load_config 的自动探测
        从 tmp_path 读 config.yaml / config.local.yaml。"""
        fake_module_file = tmp_path / "config.py"
        fake_module_file.write_text("# placeholder", encoding="utf-8")
        monkeypatch.setattr(config_module, "__file__", str(fake_module_file))
        # 同时清除可能干扰的环境变量
        monkeypatch.delenv("CONFIG_PATH", raising=False)
        return tmp_path

    def test_only_default_works(self, fake_cagent_dir: Path):
        """只有 config.yaml、没有 config.local.yaml：照常加载（与旧行为一致）。"""
        (fake_cagent_dir / "config.yaml").write_text(
            """
jira:
  base_url: "https://default.com"
  api_token: "default-token"
dng:
  base_url: "https://dng.com"
""",
            encoding="utf-8",
        )

        cfg = load_config()
        assert isinstance(cfg.jira, JiraConfig)
        assert cfg.jira.base_url == "https://default.com"
        assert cfg.jira.api_token == "default-token"

    def test_local_overrides_default_field_level(self, fake_cagent_dir: Path):
        """关键修复：config.local.yaml 只填敏感字段，其他字段从 config.yaml 继承。"""
        (fake_cagent_dir / "config.yaml").write_text(
            """
jira:
  - name: "Patac_Jira"
    base_url: "https://jira-patac.example.com"
    username: "user1"
    api_token: ""
    project_key: "VCU"
    auth_method: "basic"
    verify_ssl: false
dng:
  base_url: "https://dng.com"
""",
            encoding="utf-8",
        )
        (fake_cagent_dir / "config.local.yaml").write_text(
            """
jira:
  - name: "Patac_Jira"
    api_token: "REAL-SECRET"
""",
            encoding="utf-8",
        )

        cfg = load_config()
        patac = cfg.get_jira_config("Patac_Jira")
        assert patac is not None, "deep-merge 后 Patac_Jira 必须仍然可被解析到"
        # 来自 config.yaml 的字段应保留
        assert patac.base_url == "https://jira-patac.example.com"
        assert patac.username == "user1"
        assert patac.project_key == "VCU"
        assert patac.auth_method == "basic"
        assert patac.verify_ssl is False
        # 来自 config.local.yaml 的字段应覆盖
        assert patac.api_token == "REAL-SECRET"

    def test_local_only_jira_segment_keeps_other_sections(self, fake_cagent_dir: Path):
        """config.local.yaml 缺失 dng/llm 等字段时，应回退到 config.yaml。"""
        (fake_cagent_dir / "config.yaml").write_text(
            """
jira:
  base_url: "https://j.com"
dng:
  base_url: "https://dng-from-default.com"
  username: "default_user"
llm:
  model: "claude-sonnet-4-20250514"
  max_tokens: 1234
""",
            encoding="utf-8",
        )
        (fake_cagent_dir / "config.local.yaml").write_text(
            """
jira:
  api_token: "secret"
""",
            encoding="utf-8",
        )

        cfg = load_config()
        assert cfg.jira.api_token == "secret"
        assert cfg.dng.base_url == "https://dng-from-default.com"
        assert cfg.dng.username == "default_user"
        assert cfg.llm.max_tokens == 1234

    def test_local_only_works(self, fake_cagent_dir: Path):
        """只有 config.local.yaml、没有 config.yaml：仍可加载。"""
        (fake_cagent_dir / "config.local.yaml").write_text(
            """
jira:
  base_url: "https://only-local.com"
  api_token: "tok"
dng:
  base_url: "https://dng.com"
""",
            encoding="utf-8",
        )
        cfg = load_config()
        assert cfg.jira.base_url == "https://only-local.com"

    def test_neither_file_raises(self, fake_cagent_dir: Path):
        with pytest.raises(FileNotFoundError):
            load_config()

    def test_list_jira_merged_by_name_appends_unknown(self, fake_cagent_dir: Path):
        """config.local.yaml 中独有的命名条目应被追加，而非整体替换 base list。"""
        (fake_cagent_dir / "config.yaml").write_text(
            """
jira:
  - name: "Bosch_Jira"
    base_url: "https://b.com"
    api_token: ""
dng:
  base_url: "https://dng.com"
""",
            encoding="utf-8",
        )
        (fake_cagent_dir / "config.local.yaml").write_text(
            """
jira:
  - name: "Bosch_Jira"
    api_token: "tok-b"
  - name: "Patac_Jira"
    base_url: "https://p.com"
    api_token: "tok-p"
""",
            encoding="utf-8",
        )

        cfg = load_config()
        names = [j.name for j in cfg.list_jira_configs()]
        assert "Bosch_Jira" in names
        assert "Patac_Jira" in names
        assert cfg.get_jira_config("Bosch_Jira").api_token == "tok-b"
        assert cfg.get_jira_config("Patac_Jira").api_token == "tok-p"
