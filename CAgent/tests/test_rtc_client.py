"""RtcClient 单元测试 — 使用 mock 避免真实 RTC 调用。"""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Any

import pytest

from config import RtcConfig
from connectors.rtc_client import RtcClient


@pytest.fixture
def rtc_config() -> RtcConfig:
    return RtcConfig(
        ccm_url="https://rtc.test.com/ccm",
        username="user",
        password="pass",
        project_area_name="TestProject",
        project_area_id="pa-uuid-123",
        with_jazz=True,
        old_auth=False,
        verify_ssl=False,
        saved_query_id="_TestQueryID",
        analyzed_tag="analyzed",
    )


@pytest.fixture
def client(rtc_config: RtcConfig) -> RtcClient:
    return RtcClient(rtc_config)


def _mock_resp(content: bytes, etag: str = '"etag-1"') -> MagicMock:
    """创建模拟的 requests.Response。"""
    resp = MagicMock()
    resp.content = content
    resp.headers = {"etag": etag}
    resp.status_code = 200
    resp.raise_for_status = MagicMock()
    return resp


# ── 基本属性 ──


class TestRtcClientBasic:
    def test_source_type(self, client: RtcClient):
        assert client.source_type == "rtc"

    def test_init_sets_fields(self, client: RtcClient):
        assert client._ccm_url == "https://rtc.test.com/ccm"
        assert client._session is None  # 延迟初始化


# ── _normalize_workitem ──


class TestNormalizeWorkitem:
    def test_basic_mapping(self, client: RtcClient):
        raw = {
            "dcterms:title": "Crash on boot",
            "dcterms:identifier": {"@rdf:datatype": "xsd:string", "#text": "12345"},
            "dcterms:description": {"@rdf:parseType": "Literal", "#text": "ECU crashes on cold start"},
            "rtc_cm:state": {"@rdf:resource": "http://rtc/state/New"},
            "oslc_cm:priority": {"@rdf:resource": "http://rtc/priority/High"},
            "dcterms:subject": "regression, safety",
            "rtc_cm:filedAgainst": {"@rdf:resource": "http://rtc/fa/ModuleA"},
            "dcterms:modified": "2025-06-01T10:00:00Z",
        }
        result = client._normalize_workitem("12345", raw)

        assert result["key"] == "12345"
        assert result["fields"]["summary"] == "Crash on boot"
        assert result["fields"]["description"] == "ECU crashes on cold start"
        assert result["fields"]["labels"] == ["regression", "safety"]
        assert result["fields"]["components"] == []

    def test_empty_fields(self, client: RtcClient):
        result = client._normalize_workitem("999", {})
        assert result["key"] == "999"
        assert result["fields"]["summary"] == ""
        assert result["fields"]["labels"] == []

    def test_text_value_extraction(self, client: RtcClient):
        raw = {
            "dcterms:title": {"#text": "Title via text node"},
            "dcterms:identifier": "42",
        }
        result = client._normalize_workitem("42", raw)
        assert result["fields"]["summary"] == "Title via text node"

    def test_resource_link_extraction(self, client: RtcClient):
        raw = {
            "oslc_cm:priority": {"@rdf:resource": "http://rtc/priority/Critical"},
            "dcterms:identifier": "55",
        }
        result = client._normalize_workitem("55", raw)
        assert result["fields"]["priority"]["name"] == "http://rtc/priority/Critical"

    def test_state_url_shortened(self, client: RtcClient):
        """state 为完整 URL 时，应提取末尾名称。"""
        raw = {
            "rtc_cm:state": {"@rdf:resource": "https://rtc/workflows/wf1/states/InProgress"},
        }
        result = client._normalize_workitem("1", raw)
        assert result["fields"]["status"]["name"] == "InProgress"


# ── _extract_description ──


class TestExtractDescription:
    def test_single_description(self):
        raw = {"rdf:RDF": {"rdf:Description": {"dcterms:title": "Bug A"}}}
        result = RtcClient._extract_description(raw)
        assert result["dcterms:title"] == "Bug A"

    def test_multiple_descriptions_select_workitem(self):
        """多个 Description 节点时，应选择包含 /workitems/ 的主条目。"""
        raw = {"rdf:RDF": {"rdf:Description": [
            {"@rdf:nodeID": "A0", "dcterms:title": "Attachment info"},
            {"@rdf:about": "https://rtc/oslc/workitems/100", "dcterms:title": "Main Bug"},
            {"@rdf:nodeID": "A1", "dcterms:title": "Another attachment"},
        ]}}
        result = RtcClient._extract_description(raw)
        assert result["dcterms:title"] == "Main Bug"

    def test_fallback_to_dcterms_identifier(self):
        """无 /workitems/ URL 时，回退到含 dcterms:identifier 的节点。"""
        raw = {"rdf:RDF": {"rdf:Description": [
            {"@rdf:nodeID": "A0"},
            {"dcterms:identifier": "200", "dcterms:title": "Found by ID"},
        ]}}
        result = RtcClient._extract_description(raw)
        assert result["dcterms:title"] == "Found by ID"

    def test_empty_description(self):
        raw = {"rdf:RDF": {"rdf:Description": None}}
        result = RtcClient._extract_description(raw)
        assert result == {}

    def test_no_description_key(self):
        raw = {"oslc_cm:ChangeRequest": {"dcterms:title": "Direct CR"}}
        result = RtcClient._extract_description(raw)
        assert result["dcterms:title"] == "Direct CR"


# ── _extract_value ──


class TestExtractValue:
    def test_string(self):
        assert RtcClient._extract_value("hello") == "hello"

    def test_none(self):
        assert RtcClient._extract_value(None) == ""

    def test_dict_with_text(self):
        assert RtcClient._extract_value({"#text": "val", "@attr": "x"}) == "val"

    def test_dict_with_resource(self):
        assert RtcClient._extract_value({"@rdf:resource": "http://x"}) == "http://x"

    def test_dict_empty(self):
        assert RtcClient._extract_value({}) == ""

    def test_int(self):
        assert RtcClient._extract_value(42) == "42"


# ── get_issue ──


class TestGetIssue:
    @pytest.mark.asyncio
    async def test_get_issue_success(self, client: RtcClient):
        resp = _mock_resp(b"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:dcterms="http://purl.org/dc/terms/"
         xmlns:oslc_cm="http://open-services.net/ns/cm#"
         xmlns:rtc_cm="http://jazz.net/xmlns/prod/jazz/rtc/cm/1.0/">
  <rdf:Description rdf:about="https://rtc.test.com/ccm/oslc/workitems/100">
    <dcterms:title>Test Bug</dcterms:title>
    <dcterms:identifier rdf:datatype="xsd:string">100</dcterms:identifier>
    <dcterms:description>A test bug</dcterms:description>
    <dcterms:subject>tag1, tag2</dcterms:subject>
  </rdf:Description>
</rdf:RDF>""")

        with patch.object(client, "_oslc_get", return_value=resp):
            result = await client.get_issue("100")

        assert result["key"] == "100"
        assert result["fields"]["summary"] == "Test Bug"
        assert result["fields"]["description"] == "A test bug"
        assert result["fields"]["labels"] == ["tag1", "tag2"]


# ── get_issue_links ──


class TestGetIssueLinks:
    @pytest.mark.asyncio
    async def test_children_links(self, client: RtcClient):
        resp = _mock_resp(b"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rtc_cm="http://jazz.net/xmlns/prod/jazz/rtc/cm/1.0/">
  <rdf:Description>
    <rtc_cm:com.ibm.team.workitem.linktype.parentworkitem.children
        rdf:resource="https://rtc.test.com/ccm/oslc/workitems/201" />
  </rdf:Description>
</rdf:RDF>""")

        with patch.object(client, "_oslc_get", return_value=resp):
            links = await client.get_issue_links("100", link_type="children")

        assert len(links) == 1
        assert links[0]["key"] == "201"
        assert links[0]["type"] == "children"

    @pytest.mark.asyncio
    async def test_no_links(self, client: RtcClient):
        resp = _mock_resp(b"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description />
</rdf:RDF>""")

        with patch.object(client, "_oslc_get", return_value=resp):
            links = await client.get_issue_links("100")
        assert links == []


# ── get_remote_links ──


class TestGetRemoteLinks:
    @pytest.mark.asyncio
    async def test_implements_requirement(self, client: RtcClient):
        resp = _mock_resp(b"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:oslc_cm="http://open-services.net/ns/cm#">
  <rdf:Description>
    <oslc_cm:implementsRequirement
        rdf:resource="https://dng.test.com/rm/resources/REQ-042" />
  </rdf:Description>
</rdf:RDF>""")

        with patch.object(client, "_oslc_get", return_value=resp):
            links = await client.get_remote_links("100")

        assert len(links) == 1
        assert links[0]["object"]["url"] == "https://dng.test.com/rm/resources/REQ-042"


# ── search_issues ──


class TestSearchIssues:
    @pytest.mark.asyncio
    async def test_saved_query(self, client: RtcClient):
        mock_rtc_client = MagicMock()
        mock_query = MagicMock()

        wi1 = MagicMock()
        wi1.identifier = "501"
        wi1.title = "Bug A"
        wi1.state = "New"
        wi1.priority = "High"

        wi2 = MagicMock()
        wi2.identifier = "502"
        wi2.title = "Bug B"
        wi2.state = "InProgress"
        wi2.priority = "Medium"

        mock_query.runSavedQueryByID.return_value = [wi1, wi2]

        # 设置内部状态
        client._session = MagicMock()
        client._authenticated = True
        client._rtc_client = mock_rtc_client

        with patch("rtcclient.query.Query", return_value=mock_query):
            results = await client.search_issues("_TestQueryID")

        assert len(results) == 2
        assert results[0]["key"] == "501"
        assert results[0]["fields"]["summary"] == "Bug A"
        assert results[1]["key"] == "502"

    @pytest.mark.asyncio
    async def test_max_results(self, client: RtcClient):
        mock_query = MagicMock()

        workitems = []
        for i in range(10):
            wi = MagicMock()
            wi.identifier = str(i)
            wi.title = f"Bug {i}"
            wi.state = "New"
            wi.priority = "Low"
            workitems.append(wi)

        mock_query.runSavedQueryByID.return_value = workitems

        client._session = MagicMock()
        client._authenticated = True
        client._rtc_client = MagicMock()

        with patch("rtcclient.query.Query", return_value=mock_query):
            results = await client.search_issues("_Q", max_results=3)
        assert len(results) == 3


# ── add_comment ──


class TestAddComment:
    @pytest.mark.asyncio
    async def test_add_comment(self, client: RtcClient):
        get_resp = _mock_resp(b"""<?xml version="1.0"?>
<oslc_cm:Collection xmlns:oslc_cm="http://open-services.net/ns/cm#"
    oslc_cm:totalCount="5" />""")

        mock_session = MagicMock()
        mock_session.post.return_value = MagicMock(status_code=201)
        client._session = mock_session
        client._authenticated = True

        with patch.object(client, "_oslc_get", return_value=get_resp):
            result = await client.add_comment("100", "Test comment")

        assert result["body"] == "Test comment"
        assert result["id"] == "5"
        mock_session.post.assert_called_once()


# ── update_labels ──


class TestUpdateLabels:
    @pytest.mark.asyncio
    async def test_add_labels(self, client: RtcClient):
        get_resp = _mock_resp(b"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:dcterms="http://purl.org/dc/terms/">
  <rdf:Description>
    <dcterms:subject>existing_tag</dcterms:subject>
  </rdf:Description>
</rdf:RDF>""")

        with patch.object(client, "_oslc_get", return_value=get_resp), \
             patch.object(client, "_oslc_put") as mock_put:
            await client.update_labels("100", add_labels=["analyzed"])

        mock_put.assert_called_once()
        put_data = mock_put.call_args.kwargs.get("data", "")
        assert "analyzed" in put_data
        assert "existing_tag" in put_data

    @pytest.mark.asyncio
    async def test_remove_labels(self, client: RtcClient):
        get_resp = _mock_resp(b"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:dcterms="http://purl.org/dc/terms/">
  <rdf:Description>
    <dcterms:subject>tag_a, tag_b, tag_c</dcterms:subject>
  </rdf:Description>
</rdf:RDF>""")

        with patch.object(client, "_oslc_get", return_value=get_resp), \
             patch.object(client, "_oslc_put") as mock_put:
            await client.update_labels(
                "100", add_labels=["new_tag"], remove_labels=["tag_b"]
            )

        put_data = mock_put.call_args.kwargs.get("data", "")
        assert "new_tag" in put_data
        assert "tag_a" in put_data
        assert "tag_b" not in put_data


# ── create_issue ──


class TestCreateIssue:
    @pytest.mark.asyncio
    async def test_create_issue(self, client: RtcClient):
        post_resp = _mock_resp(b"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:dcterms="http://purl.org/dc/terms/">
  <rdf:Description rdf:about="https://rtc.test.com/ccm/oslc/workitems/999">
    <dcterms:identifier rdf:datatype="xsd:string">999</dcterms:identifier>
  </rdf:Description>
</rdf:RDF>""")

        with patch.object(client, "_oslc_post", return_value=post_resp):
            new_id = await client.create_issue(
                project_key="TestProject",
                issue_type="defect",
                summary="New Bug",
                description="Something broke",
            )

        assert new_id == "999"


# ── close ──


class TestClose:
    @pytest.mark.asyncio
    async def test_close_with_session(self, client: RtcClient):
        mock_session = MagicMock()
        client._session = mock_session
        client._authenticated = True

        await client.close()

        mock_session.close.assert_called_once()
        assert client._session is None
        assert client._authenticated is False

    @pytest.mark.asyncio
    async def test_close_without_init(self, client: RtcClient):
        """未初始化时 close 不应报错。"""
        await client.close()
        assert client._session is None


# ── _parse_attachments ──


_ATTACHMENT_XML_MULTI = b"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:dcterms="http://purl.org/dc/terms/"
         xmlns:rtc_cm="http://jazz.net/xmlns/prod/jazz/rtc/cm/1.0/">
  <rdf:Description rdf:nodeID="A0">
    <rdf:subject rdf:resource="https://rtc.test.com/ccm/oslc/workitems/100" />
    <rdf:predicate rdf:resource="http://jazz.net/xmlns/prod/jazz/rtc/cm/1.0/com.ibm.team.workitem.linktype.attachment.attachment" />
    <rdf:object rdf:resource="https://rtc.test.com/ccm/resource/itemOid/com.ibm.team.workitem.Attachment/_aaa" />
    <rdf:type rdf:resource="http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement" />
    <dcterms:title>2611566: performance_data.xlsx</dcterms:title>
  </rdf:Description>
  <rdf:Description rdf:about="https://rtc.test.com/ccm/oslc/workitems/100">
    <dcterms:title>Main WorkItem</dcterms:title>
    <dcterms:identifier>100</dcterms:identifier>
  </rdf:Description>
  <rdf:Description rdf:nodeID="A1">
    <rdf:subject rdf:resource="https://rtc.test.com/ccm/oslc/workitems/100" />
    <rdf:predicate rdf:resource="http://jazz.net/xmlns/prod/jazz/rtc/cm/1.0/com.ibm.team.workitem.linktype.attachment.attachment" />
    <rdf:object rdf:resource="https://rtc.test.com/ccm/resource/itemOid/com.ibm.team.workitem.Attachment/_bbb" />
    <rdf:type rdf:resource="http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement" />
    <dcterms:title>2611567: log_dump.zip</dcterms:title>
  </rdf:Description>
</rdf:RDF>"""


class TestParseAttachments:
    def test_parse_multiple_attachments(self):
        import xmltodict
        raw = xmltodict.parse(_ATTACHMENT_XML_MULTI)
        attachments = RtcClient._parse_attachments(raw)

        assert len(attachments) == 2

        assert attachments[0]["name"] == "performance_data.xlsx"
        assert attachments[0]["attachment_id"] == "2611566"
        assert "Attachment/_aaa" in attachments[0]["url"]

        assert attachments[1]["name"] == "log_dump.zip"
        assert attachments[1]["attachment_id"] == "2611567"
        assert "Attachment/_bbb" in attachments[1]["url"]

    def test_no_attachments(self):
        import xmltodict
        xml = b"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:dcterms="http://purl.org/dc/terms/">
  <rdf:Description rdf:about="https://rtc.test.com/ccm/oslc/workitems/200">
    <dcterms:title>No Attachments Bug</dcterms:title>
  </rdf:Description>
</rdf:RDF>"""
        raw = xmltodict.parse(xml)
        attachments = RtcClient._parse_attachments(raw)
        assert attachments == []

    def test_single_attachment(self):
        import xmltodict
        xml = b"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:dcterms="http://purl.org/dc/terms/">
  <rdf:Description rdf:nodeID="A0">
    <rdf:predicate rdf:resource="http://jazz.net/xmlns/prod/jazz/rtc/cm/1.0/com.ibm.team.workitem.linktype.attachment.attachment" />
    <rdf:object rdf:resource="https://rtc.test.com/ccm/attachment/_x" />
    <dcterms:title>12345: report.pdf</dcterms:title>
  </rdf:Description>
</rdf:RDF>"""
        raw = xmltodict.parse(xml)
        attachments = RtcClient._parse_attachments(raw)
        assert len(attachments) == 1
        assert attachments[0]["name"] == "report.pdf"
        assert attachments[0]["attachment_id"] == "12345"
        assert attachments[0]["url"] == "https://rtc.test.com/ccm/attachment/_x"

    def test_title_without_id_prefix(self):
        """dcterms:title 不含冒号时，整个标题作为文件名。"""
        import xmltodict
        xml = b"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:dcterms="http://purl.org/dc/terms/">
  <rdf:Description rdf:nodeID="A0">
    <rdf:predicate rdf:resource="http://jazz.net/xmlns/prod/jazz/rtc/cm/1.0/com.ibm.team.workitem.linktype.attachment.attachment" />
    <rdf:object rdf:resource="https://rtc.test.com/ccm/attachment/_y" />
    <dcterms:title>plain_filename.txt</dcterms:title>
  </rdf:Description>
</rdf:RDF>"""
        raw = xmltodict.parse(xml)
        attachments = RtcClient._parse_attachments(raw)
        assert len(attachments) == 1
        assert attachments[0]["name"] == "plain_filename.txt"
        assert attachments[0]["attachment_id"] == ""


# ── _sanitize_filename ──


class TestSanitizeFilename:
    def test_normal_filename(self):
        assert RtcClient._sanitize_filename("report.pdf") == "report.pdf"

    def test_unsafe_characters(self):
        result = RtcClient._sanitize_filename('file<>:"/\\|?*.txt')
        assert "<" not in result
        assert ">" not in result
        assert '"' not in result
        assert result.endswith(".txt")

    def test_empty_becomes_unnamed(self):
        assert RtcClient._sanitize_filename("") == "unnamed"

    def test_dots_only(self):
        assert RtcClient._sanitize_filename("...") == "unnamed"

    def test_long_filename_truncated(self):
        long_name = "a" * 250 + ".xlsx"
        result = RtcClient._sanitize_filename(long_name)
        assert len(result) <= 200


# ── get_attachments (async) ──


class TestGetAttachments:
    @pytest.mark.asyncio
    async def test_get_attachments_success(self, client: RtcClient):
        resp = _mock_resp(_ATTACHMENT_XML_MULTI)
        with patch.object(client, "_oslc_get", return_value=resp):
            attachments = await client.get_attachments("100")

        assert len(attachments) == 2
        assert attachments[0]["name"] == "performance_data.xlsx"
        assert attachments[1]["name"] == "log_dump.zip"

    @pytest.mark.asyncio
    async def test_get_attachments_empty(self, client: RtcClient):
        resp = _mock_resp(b"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about="https://rtc.test.com/ccm/oslc/workitems/999">
  </rdf:Description>
</rdf:RDF>""")
        with patch.object(client, "_oslc_get", return_value=resp):
            attachments = await client.get_attachments("999")
        assert attachments == []


# ── download_attachment ──


class TestDownloadAttachment:
    @pytest.mark.asyncio
    async def test_download_success(self, client: RtcClient, tmp_path):
        mock_session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.headers = {"Content-Length": "100"}
        mock_resp.iter_content.return_value = [b"file-content-data"]
        mock_resp.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_resp

        client._session = mock_session
        client._authenticated = True

        save_path = str(tmp_path / "test_file.xlsx")
        result = await client.download_attachment(
            "https://rtc.test.com/ccm/attachment/_aaa", save_path,
        )

        assert result == save_path
        assert os.path.exists(save_path)
        with open(save_path, "rb") as f:
            assert f.read() == b"file-content-data"

    @pytest.mark.asyncio
    async def test_download_creates_directory(self, client: RtcClient, tmp_path):
        mock_session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.headers = {"Content-Length": "5"}
        mock_resp.iter_content.return_value = [b"hello"]
        mock_resp.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_resp

        client._session = mock_session
        client._authenticated = True

        nested_path = str(tmp_path / "sub" / "dir" / "file.txt")
        result = await client.download_attachment(
            "https://rtc.test.com/ccm/attachment/_x", nested_path,
        )

        assert os.path.exists(nested_path)

    @pytest.mark.asyncio
    async def test_download_size_limit(self, client: RtcClient, tmp_path):
        """Content-Length 超出限制时应抛出 ValueError。"""
        mock_session = MagicMock()
        mock_resp = MagicMock()
        # 600 MB，超出默认 500 MB 限制
        mock_resp.headers = {"Content-Length": str(600 * 1024 * 1024)}
        mock_resp.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_resp

        client._session = mock_session
        client._authenticated = True

        save_path = str(tmp_path / "too_big.bin")
        with pytest.raises(ValueError, match="超出限制"):
            await client.download_attachment(
                "https://rtc.test.com/ccm/attachment/_big", save_path,
            )


# ── download_all_attachments ──


class TestDownloadAllAttachments:
    @pytest.mark.asyncio
    async def test_download_all(self, client: RtcClient, tmp_path):
        """批量下载多个附件。"""
        att_list = [
            {"name": "file1.xlsx", "url": "https://rtc/att/1", "attachment_id": "1"},
            {"name": "file2.zip", "url": "https://rtc/att/2", "attachment_id": "2"},
        ]

        with patch.object(client, "get_attachments", return_value=att_list), \
             patch.object(client, "download_attachment", side_effect=[
                 str(tmp_path / "file1.xlsx"),
                 str(tmp_path / "file2.zip"),
             ]):
            results = await client.download_all_attachments(
                "100", output_dir=str(tmp_path),
            )

        assert len(results) == 2
        assert all(r["success"] for r in results)
        assert results[0]["name"] == "file1.xlsx"
        assert results[1]["name"] == "file2.zip"

    @pytest.mark.asyncio
    async def test_skip_existing(self, client: RtcClient, tmp_path):
        """已存在的文件应跳过下载。"""
        existing_file = tmp_path / "exists.txt"
        existing_file.write_text("already here")

        att_list = [
            {"name": "exists.txt", "url": "https://rtc/att/1", "attachment_id": "1"},
        ]

        with patch.object(client, "get_attachments", return_value=att_list), \
             patch.object(client, "download_attachment") as mock_dl:
            results = await client.download_all_attachments(
                "100", output_dir=str(tmp_path),
            )

        # download_attachment 不应被调用
        mock_dl.assert_not_called()
        assert len(results) == 1
        assert results[0]["success"] is True

    @pytest.mark.asyncio
    async def test_empty_attachments(self, client: RtcClient, tmp_path):
        """无附件时返回空列表。"""
        with patch.object(client, "get_attachments", return_value=[]):
            results = await client.download_all_attachments(
                "100", output_dir=str(tmp_path),
            )
        assert results == []

    @pytest.mark.asyncio
    async def test_download_failure_recorded(self, client: RtcClient, tmp_path):
        """下载失败时记录错误但不中断。"""
        att_list = [
            {"name": "ok.txt", "url": "https://rtc/att/1", "attachment_id": "1"},
            {"name": "fail.txt", "url": "https://rtc/att/2", "attachment_id": "2"},
        ]

        with patch.object(client, "get_attachments", return_value=att_list), \
             patch.object(client, "download_attachment", side_effect=[
                 str(tmp_path / "ok.txt"),
                 Exception("Network error"),
             ]):
            results = await client.download_all_attachments(
                "100", output_dir=str(tmp_path),
            )

        assert len(results) == 2
        assert results[0]["success"] is True
        assert results[1]["success"] is False
        assert "Network error" in results[1]["error"]

    @pytest.mark.asyncio
    async def test_filename_sanitization(self, client: RtcClient, tmp_path):
        """包含非法字符的文件名应被清理。"""
        att_list = [
            {"name": 'file<>:bad".xlsx', "url": "https://rtc/att/1",
             "attachment_id": "1"},
        ]

        with patch.object(client, "get_attachments", return_value=att_list), \
             patch.object(client, "download_attachment",
                          return_value=str(tmp_path / "file___bad_.xlsx")) as mock_dl:
            results = await client.download_all_attachments(
                "100", output_dir=str(tmp_path),
            )

        # 验证传入 download_attachment 的 save_path 不含非法字符
        called_path = mock_dl.call_args[0][1]  # positional arg: save_path
        assert "<" not in called_path
        assert ">" not in called_path
        assert '"' not in called_path
