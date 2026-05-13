"""
connectors/rtc_client.py — RTC (Rational Team Concert) 适配器

实现 BugTrackerClient Protocol，使用 requests.Session 直接访问 OSLC API。
所有同步调用通过 asyncio.to_thread() 包装为异步。

参考: refer/RTC_Api (组织内部验证可用版本)
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any

# 将内部修改版 rtcclient 包加入 Python 路径 (用于 search_issues 中的 Query)
_RTCCLIENT_PKGS = os.path.normpath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir,
                 "refer", "RTC_Api", "pkgs")
)
if os.path.isdir(_RTCCLIENT_PKGS) and _RTCCLIENT_PKGS not in sys.path:
    sys.path.insert(0, _RTCCLIENT_PKGS)

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests as _requests
import xmltodict
from requests.auth import HTTPBasicAuth

from config import RtcConfig

logger = logging.getLogger(__name__)


class RtcClient:
    """RTC 适配器，实现 BugTrackerClient Protocol。

    使用 requests.Session 管理认证和 Cookie，
    直接调用 OSLC REST API，不再依赖 rtcclient 的 HTTP 层。
    """

    OSLC_CR_RDF = "application/rdf+xml"
    OSLC_CR_JSON = "application/x-oslc-cm-change-request+json"

    def __init__(self, config: RtcConfig) -> None:
        self._config = config
        self._ccm_url = config.ccm_url.rstrip("/")
        self._auth = HTTPBasicAuth(config.username, config.password)
        self._field_mapping = config.field_mapping

        logger.info(
            "RtcClient 初始化: ccm_url=%r, username=%r",
            self._ccm_url, config.username,
        )
        if not self._ccm_url:
            logger.warning("ccm_url 为空，后续 API 调用将失败！")

        # 延迟初始化
        self._session: _requests.Session | None = None
        self._authenticated = False

    @property
    def source_type(self) -> str:
        return "rtc"

    # ── 认证 ──

    def _ensure_session(self) -> _requests.Session:
        """确保 session 已认证。使用 Form Challenge 流程。"""
        if self._session is not None and self._authenticated:
            return self._session

        session = _requests.Session()
        session.verify = self._config.verify_ssl

        # Step 1: GET /authenticated/identity 触发认证握手
        resp = session.get(
            f"{self._ccm_url}/authenticated/identity",
            auth=self._auth,
            allow_redirects=True,
        )

        # Step 2: 检测 Form Challenge
        auth_msg = resp.headers.get(
            "X-com-ibm-team-repository-web-auth-msg", ""
        )
        if auth_msg == "authrequired":
            logger.debug("RTC Form Challenge 检测到，提交凭据...")
            form_data = {
                "j_username": self._config.username,
                "j_password": self._config.password,
            }
            # 优先尝试 /j_security_check，失败则回退 /authenticated/j_security_check
            for path in ["/j_security_check", "/authenticated/j_security_check"]:
                try:
                    resp2 = session.post(
                        self._ccm_url + path,
                        data=form_data,
                        allow_redirects=True,
                    )
                    failed = resp2.headers.get(
                        "x-com-ibm-team-repository-web-auth-msg", ""
                    )
                    if failed == "authfailed":
                        raise RuntimeError("RTC 认证失败: 用户名或密码错误")
                    # 检查 session cookies 是否包含认证 token
                    cookies = dict(session.cookies)
                    if cookies.get("LtpaToken2") or cookies.get("JSESSIONID"):
                        break
                except _requests.HTTPError:
                    continue
            else:
                logger.warning("Form Challenge POST 完成但未获取到认证 Cookie")

        # Step 3: 检查认证结果
        cookies = dict(session.cookies)
        if cookies.get("LtpaToken2") or cookies.get("JSESSIONID"):
            logger.info("RTC 认证成功 (cookies: %s)", list(cookies.keys()))
        else:
            # 尝试 old_auth 方式
            if self._config.old_auth:
                logger.debug("尝试 old_auth 认证方式...")
                cookie_header = resp.headers.get("set-cookie", "")
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Cookie": cookie_header,
                }
                session.post(
                    f"{self._ccm_url}/authenticated/j_security_check",
                    data=form_data,
                    headers=headers,
                    allow_redirects=True,
                )
            logger.warning(
                "RTC 认证可能未完成，cookies: %s", list(cookies.keys())
            )

        self._session = session
        self._authenticated = True
        logger.info("RTC Session 初始化完成: %s", self._ccm_url)
        return session

    def _oslc_get(self, url: str, timeout: int = 180) -> _requests.Response:
        """OSLC GET 请求，带标准 Accept 头和重试。"""
        session = self._ensure_session()
        headers = {
            "Accept": self.OSLC_CR_RDF,
            "OSLC-Core-Version": "2.0",
            "Connection": "close",  # 避免代理 keep-alive 超时
        }
        last_err: Exception | None = None
        for attempt in range(3):
            try:
                resp = session.get(url, headers=headers, timeout=timeout)
                resp.raise_for_status()
                return resp
            except (_requests.ConnectionError, _requests.Timeout) as e:
                last_err = e
                wait = 3 * (attempt + 1)
                logger.warning(
                    "OSLC GET 失败 (attempt %d/3): %s, %ds 后重试...",
                    attempt + 1, e, wait,
                )
                import time
                time.sleep(wait)
        raise last_err  # type: ignore[misc]

    def _oslc_put(
        self, url: str, data: str, content_type: str | None = None,
        etag: str | None = None,
    ) -> _requests.Response:
        """OSLC PUT 请求。"""
        session = self._ensure_session()
        headers = {
            "Content-Type": content_type or self.OSLC_CR_RDF,
            "Accept": self.OSLC_CR_RDF,
            "OSLC-Core-Version": "2.0",
        }
        if etag:
            headers["If-Match"] = etag
        resp = session.put(url, data=data, headers=headers)
        resp.raise_for_status()
        return resp

    def _oslc_post(
        self, url: str, data: str, content_type: str | None = None,
    ) -> _requests.Response:
        """OSLC POST 请求。"""
        session = self._ensure_session()
        headers = {
            "Content-Type": content_type or self.OSLC_CR_RDF,
            "Accept": self.OSLC_CR_RDF,
            "OSLC-Core-Version": "2.0",
        }
        resp = session.post(url, data=data, headers=headers)
        resp.raise_for_status()
        return resp

    # ── BugTrackerClient Protocol 方法 ──

    async def get_issue(
        self, key: str, fields: str = "*all", include_raw: bool = False
    ) -> dict[str, Any]:
        """获取 RTC WorkItem，返回与 Jira 对齐的 dict 格式。

        Args:
            key: WorkItem ID
            fields: 字段选择 (未使用，保持接口兼容)
            include_raw: 是否在返回值中包含 _raw_oslc (原始 OSLC RDF 数据)
        """

        def _get() -> dict[str, Any]:
            url = f"{self._ccm_url}/oslc/workitems/{key}"
            resp = self._oslc_get(url)
            raw_data = xmltodict.parse(resp.content)
            wi_data = self._extract_description(raw_data)
            result = self._normalize_workitem(key, wi_data)
            if include_raw:
                result["_raw_oslc"] = raw_data
            return result

        return await asyncio.to_thread(_get)

    async def get_issue_links(
        self, key: str, link_type: str | None = None
    ) -> list[dict[str, Any]]:
        """获取 WorkItem 的关联链接 (parent/children/related)。"""

        def _get_links() -> list[dict[str, Any]]:
            url = f"{self._ccm_url}/oslc/workitems/{key}"
            resp = self._oslc_get(url)
            raw_data = xmltodict.parse(resp.content)
            wi_data = self._extract_description(raw_data)

            results: list[dict[str, Any]] = []
            link_tags = {
                "parent": "rtc_cm:com.ibm.team.workitem.linktype.parentworkitem.parent",
                "children": "rtc_cm:com.ibm.team.workitem.linktype.parentworkitem.children",
                "related": "rtc_cm:com.ibm.team.workitem.linktype.relatedworkitem.related",
                "blocks": "rtc_cm:com.ibm.team.workitem.linktype.blocksworkitem.blocks",
            }

            for lt_name, tag in link_tags.items():
                if link_type and lt_name != link_type:
                    continue
                value = wi_data.get(tag)
                if not value:
                    continue
                links = value if isinstance(value, list) else [value]
                for link in links:
                    resource = link if isinstance(link, str) else link.get("@rdf:resource", "")
                    if resource:
                        linked_id = resource.rstrip("/").split("/")[-1]
                        results.append({
                            "type": lt_name,
                            "direction": "outward",
                            "key": linked_id,
                            "summary": "",
                        })
            return results

        return await asyncio.to_thread(_get_links)

    async def get_remote_links(self, key: str) -> list[dict[str, Any]]:
        """获取 WorkItem 的外部链接 (如 DNG 链接)。"""

        def _get_remote() -> list[dict[str, Any]]:
            url = f"{self._ccm_url}/oslc/workitems/{key}"
            resp = self._oslc_get(url)
            raw_data = xmltodict.parse(resp.content)
            wi_data = self._extract_description(raw_data)

            results: list[dict[str, Any]] = []
            impl_tag = "oslc_cm:implementsRequirement"
            tracks_tag = "oslc_cm:tracksRequirement"

            for tag in [impl_tag, tracks_tag]:
                value = wi_data.get(tag)
                if not value:
                    continue
                links = value if isinstance(value, list) else [value]
                for link in links:
                    resource = link if isinstance(link, str) else link.get("@rdf:resource", "")
                    if resource:
                        results.append({
                            "object": {"url": resource, "title": ""},
                        })
            return results

        return await asyncio.to_thread(_get_remote)

    async def search_issues(
        self,
        query: str,
        fields: str = "summary,status,priority",
        max_results: int = 50,
    ) -> list[dict[str, Any]]:
        """搜索 WorkItem。query 为 Saved Query ID 或内联查询字符串。

        优先使用自有 session 直接调用 OSLC 查询 API（Saved Query 场景），
        如果直接查询失败则回退到 rtcclient Query 类。

        当 max_results <= 0 时返回全部结果。
        """

        def _search() -> list[dict[str, Any]]:
            self._ensure_session()

            is_saved_query = query.startswith("_") or len(query) < 60

            # 优先使用自有 session 直接查询 (避免代理/SSL 问题)
            if is_saved_query:
                try:
                    return self._search_saved_query_direct(query, max_results)
                except Exception as e:
                    logger.warning("OSLC 直接查询失败，回退到 rtcclient: %s", e)

            # 回退: rtcclient Query
            if not hasattr(self, "_rtc_client") or self._rtc_client is None:
                self._init_rtc_client()

            from rtcclient.query import Query
            query_obj = Query(self._rtc_client)

            if is_saved_query:
                workitems = query_obj.runSavedQueryByID(query) or []
            else:
                workitems = query_obj.queryWorkitems(
                    query,
                    projectarea_id=self._config.project_area_id or None,
                    projectarea_name=self._config.project_area_name or None,
                ) or []

            results: list[dict[str, Any]] = []
            items = workitems[:max_results] if max_results > 0 else workitems
            for wi in items:
                wi_id = str(getattr(wi, "identifier", ""))
                results.append({
                    "key": wi_id,
                    "fields": {
                        "summary": getattr(wi, "title", getattr(wi, "summary", "")),
                        "status": {"name": getattr(wi, "state", "")},
                        "priority": {"name": getattr(wi, "priority", "")},
                    },
                })
            return results

        return await asyncio.to_thread(_search)

    def _search_saved_query_direct(
        self, query_id: str, max_results: int = 50, page_size: int = 20,
    ) -> list[dict[str, Any]]:
        """使用自有 session 直接调用 OSLC Saved Query API，支持分页。

        URL 格式: /ccm/oslc/queries/{query_id}/rtc_cm:results
                   ?oslc_cm.pageSize={page_size}&_startIndex={start_index}
        """
        results: list[dict[str, Any]] = []
        start_index = 0

        while True:
            url = (
                f"{self._ccm_url}/oslc/queries/{query_id}/rtc_cm:results"
                f"?oslc_cm.pageSize={page_size}&_startIndex={start_index}"
            )
            logger.info("OSLC 查询: startIndex=%d, pageSize=%d", start_index, page_size)
            resp = self._oslc_get(url)
            raw = xmltodict.parse(resp.content)

            # 提取 ChangeRequest 条目
            collection = raw.get("oslc_cm:Collection") or raw.get("rdf:RDF", {})
            entries = collection.get("oslc_cm:ChangeRequest") or []
            if isinstance(entries, dict):
                entries = [entries]

            if not entries:
                break

            for entry in entries:
                # 从 @rdf:about URL 提取 WorkItem ID
                about = entry.get("@rdf:about", "")
                wi_id = about.rstrip("/").split("/")[-1] if about else ""

                # 也可能有 dcterms:identifier
                if not wi_id:
                    wi_id = self._extract_value(entry.get("dcterms:identifier", ""))

                summary = self._extract_value(entry.get("dcterms:title", ""))
                state = self._extract_value(entry.get("rtc_cm:state", ""))
                priority = self._extract_value(entry.get("oslc_cm:priority", ""))

                if state.startswith("http"):
                    state = state.rstrip("/").split("/")[-1]

                results.append({
                    "key": str(wi_id),
                    "fields": {
                        "summary": summary,
                        "status": {"name": state},
                        "priority": {"name": priority},
                    },
                })

            logger.info("  本页获取 %d 条，累计 %d 条", len(entries), len(results))

            # 检查是否达到上限
            if 0 < max_results <= len(results):
                results = results[:max_results]
                break

            # 检查是否还有下一页
            if len(entries) < page_size:
                break

            start_index += page_size

        return results

    def _init_rtc_client(self) -> None:
        """初始化 RTCClient (仅用于 Query)，复用已认证的 session cookies。"""
        try:
            from rtcclient.client import RTCClient
            self._rtc_client = RTCClient(
                url=self._ccm_url,
                username=self._config.username,
                password=self._config.password,
                ends_with_jazz=self._config.with_jazz,
                old_auth=self._config.old_auth,
            )
            # 用已认证 session 的 cookie 覆盖 RTCClient 的 headers
            if self._session:
                cookie_str = "; ".join(
                    f"{k}={v}" for k, v in self._session.cookies.items()
                )
                if cookie_str:
                    self._rtc_client.headers["Cookie"] = cookie_str
        except Exception as e:
            logger.warning("RTCClient 初始化失败 (Query 功能不可用): %s", e)
            self._rtc_client = None

    async def add_comment(self, key: str, body: str) -> dict[str, Any]:
        """向 WorkItem 添加评论。"""

        def _add() -> dict[str, Any]:
            # 先获取 comments 集合信息
            comments_url = f"{self._ccm_url}/oslc/workitems/{key}/rtc_cm:comments"
            resp = self._oslc_get(comments_url)
            raw = xmltodict.parse(resp.content)
            total = raw.get("oslc_cm:Collection", {}).get("@oslc_cm:totalCount", "0")
            comment_url = f"{comments_url}/{total}"

            comment_xml = f"""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:oslc="http://open-services.net/ns/core#">
  <rdf:Description rdf:about="{comment_url}">
    <rdf:type rdf:resource="http://open-services.net/ns/core#Comment"/>
    <dcterms:description rdf:parseType="Literal">{body}</dcterms:description>
  </rdf:Description>
</rdf:RDF>"""
            post_url = f"{comments_url}/oslc:comment"
            session = self._ensure_session()
            headers = {
                "Content-Type": self.OSLC_CR_RDF,
                "Accept": self.OSLC_CR_RDF,
                "OSLC-Core-Version": "2.0",
                "If-Match": resp.headers.get("etag", "*"),
            }
            session.post(post_url, data=comment_xml, headers=headers)
            return {"id": total, "body": body}

        return await asyncio.to_thread(_add)

    async def get_comments(self, key: str) -> list[dict[str, Any]]:
        """获取 WorkItem 的所有评论 (Discussion)。

        一次请求即返回全部评论（RDF 格式）。

        Returns:
            [{"id": "0", "creator": "user_id", "created": "2024-...", "body": "..."},
             ...]
        """

        def _get() -> list[dict[str, Any]]:
            comments_url = f"{self._ccm_url}/oslc/workitems/{key}/rtc_cm:comments"
            resp = self._oslc_get(comments_url)
            raw = xmltodict.parse(resp.content)

            rdf = raw.get("rdf:RDF", raw)
            desc_nodes = rdf.get("rdf:Description", [])
            if isinstance(desc_nodes, dict):
                desc_nodes = [desc_nodes]

            # 筛选 oslc:Comment 类型的节点（排除 oslc:Discussion 节点）
            comment_nodes = []
            for node in desc_nodes:
                rdf_type = node.get("rdf:type", {})
                type_url = rdf_type.get("@rdf:resource", "") if isinstance(rdf_type, dict) else ""
                if type_url.endswith("#Comment"):
                    comment_nodes.append(node)

            if not comment_nodes:
                return []

            comments: list[dict[str, Any]] = []
            for node in comment_nodes:
                # 提取评论 ID（从 URL 中）
                about = node.get("@rdf:about", "")
                comment_id = about.rsplit("/", 1)[-1] if about else ""

                # 提取 body
                body_raw = node.get("dcterms:description", {})
                if isinstance(body_raw, dict):
                    body = body_raw.get("#text", "")
                    # 有些评论有 synthetic 字段（系统自动生成的消息）
                    if not body:
                        body = body_raw.get("synthetic", "")
                else:
                    body = str(body_raw)

                # 提取 creator
                creator_raw = node.get("dcterms:creator", {})
                creator_url = creator_raw.get("@rdf:resource", "") if isinstance(creator_raw, dict) else str(creator_raw)
                creator = creator_url.rsplit("/", 1)[-1] if creator_url else ""

                # 提取 created
                created_raw = node.get("dcterms:created", {})
                created = created_raw.get("#text", "") if isinstance(created_raw, dict) else str(created_raw)

                comments.append({
                    "id": comment_id,
                    "creator": creator,
                    "created": created,
                    "body": body,
                })

            # 按 created 时间排序（从早到晚）
            comments.sort(key=lambda c: c.get("created", ""))
            return comments

        return await asyncio.to_thread(_get)

    async def update_labels(
        self,
        key: str,
        add_labels: list[str],
        remove_labels: list[str] | None = None,
    ) -> None:
        """更新 WorkItem 的 tags (dc:subject)。"""

        def _update() -> None:
            url = f"{self._ccm_url}/oslc/workitems/{key}"
            props_url = url + "?oslc_cm.properties=dcterms:subject"

            resp = self._oslc_get(props_url)
            raw = xmltodict.parse(resp.content)
            desc = self._extract_description(raw)
            # 兼容 dcterms:subject 和 dc:subject
            current_tags_str = self._extract_value(
                desc.get("dcterms:subject") or desc.get("dc:subject")
            )
            current_tags = [
                t.strip() for t in current_tags_str.split(",") if t.strip()
            ]

            tag_set = set(current_tags)
            tag_set.update(add_labels)
            if remove_labels:
                tag_set -= set(remove_labels)
            new_tags_str = ", ".join(sorted(tag_set))

            put_body = f"""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dcterms="http://purl.org/dc/terms/">
  <rdf:Description rdf:about="{url}">
    <dcterms:subject>{new_tags_str}</dcterms:subject>
  </rdf:Description>
</rdf:RDF>"""
            self._oslc_put(
                props_url, data=put_body,
                etag=resp.headers.get("etag", "*"),
            )

        await asyncio.to_thread(_update)

    async def create_issue(
        self,
        project_key: str,
        issue_type: str,
        summary: str,
        description: str = "",
        **extra_fields: Any,
    ) -> str:
        """创建新 WorkItem，返回 ID。"""

        def _create() -> str:
            pa_id = self._config.project_area_id
            wi_type = issue_type or self._config.bug_work_item_type

            creation_url = (
                f"{self._ccm_url}/oslc/contexts/{pa_id}/workitems/{wi_type}"
            )

            desc_escaped = (
                description.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            summary_escaped = (
                summary.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            body = f"""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:rtc_cm="http://jazz.net/xmlns/prod/jazz/rtc/cm/1.0/">
  <rdf:Description>
    <dcterms:title>{summary_escaped}</dcterms:title>
    <dcterms:description>{desc_escaped}</dcterms:description>
  </rdf:Description>
</rdf:RDF>"""

            resp = self._oslc_post(creation_url, data=body)
            raw = xmltodict.parse(resp.content)
            desc = self._extract_description(raw)
            new_id = self._extract_value(
                desc.get("dcterms:identifier") or desc.get("dc:identifier")
            )
            logger.info("RTC WorkItem 创建成功: %s", new_id)
            return str(new_id)

        return await asyncio.to_thread(_create)

    async def create_link(
        self, link_type: str, inward_key: str, outward_key: str
    ) -> None:
        """创建两个 WorkItem 之间的链接。"""

        def _link() -> None:
            link_tag_map = {
                "parent": "rtc_cm:com.ibm.team.workitem.linktype.parentworkitem.parent",
                "children": "rtc_cm:com.ibm.team.workitem.linktype.parentworkitem.children",
                "related": "rtc_cm:com.ibm.team.workitem.linktype.relatedworkitem.related",
                "relates to": "rtc_cm:com.ibm.team.workitem.linktype.relatedworkitem.related",
                "blocks": "rtc_cm:com.ibm.team.workitem.linktype.blocksworkitem.blocks",
            }

            tag = link_tag_map.get(
                link_type,
                "rtc_cm:com.ibm.team.workitem.linktype.relatedworkitem.related",
            )
            outward_url = (
                f"{self._ccm_url}/resource/itemName/"
                f"com.ibm.team.workitem.WorkItem/{outward_key}"
            )
            payload = {tag: [{"rdf:resource": outward_url}]}

            url = (
                f"{self._ccm_url}/oslc/workitems/{inward_key}"
                f"?oslc_cm.properties="
                f"{tag.split(':')[1]}"
            )
            self._oslc_put(
                url,
                data=json.dumps(payload),
                content_type=self.OSLC_CR_JSON,
            )

        await asyncio.to_thread(_link)

    # ── 附件操作 ──

    async def get_attachments(self, key: str) -> list[dict[str, Any]]:
        """获取 WorkItem 的附件列表。

        从 OSLC RDF/XML 中解析附件 Statement 节点 (rdf:nodeID)，提取:
        - name:          文件名 (dcterms:title 冒号后部分)
        - url:           下载 URL (rdf:object/@rdf:resource)
        - attachment_id: 附件序号 (dcterms:title 冒号前数字)
        """

        def _get() -> list[dict[str, Any]]:
            url = f"{self._ccm_url}/oslc/workitems/{key}"
            resp = self._oslc_get(url)
            raw_data = xmltodict.parse(resp.content)
            return self._parse_attachments(raw_data)

        return await asyncio.to_thread(_get)

    async def download_attachment(self, url: str, save_path: str) -> str:
        """下载单个附件到指定路径，返回保存的文件路径。

        使用已认证的 session 流式下载二进制内容。
        """

        def _download() -> str:
            session = self._ensure_session()
            max_bytes = self._config.max_attachment_size_mb * 1024 * 1024

            # 流式下载 (RTC 附件需要 Accept: */* 而非 application/octet-stream)
            resp = session.get(
                url,
                headers={"Accept": "*/*"},
                stream=True,
            )
            resp.raise_for_status()

            # 检查 Content-Length
            content_length = int(resp.headers.get("Content-Length", 0))
            if content_length > max_bytes > 0:
                raise ValueError(
                    f"附件大小 {content_length / 1024 / 1024:.1f} MB "
                    f"超出限制 {self._config.max_attachment_size_mb} MB"
                )

            # 确保目录存在
            out = Path(save_path)
            out.parent.mkdir(parents=True, exist_ok=True)

            # 写入文件 (分块)
            written = 0
            with open(out, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        written += len(chunk)
                        if max_bytes > 0 and written > max_bytes:
                            raise ValueError(
                                f"附件下载超出大小限制 "
                                f"{self._config.max_attachment_size_mb} MB"
                            )
                        f.write(chunk)

            logger.info(
                "附件下载完成: %s (%d bytes)", out.name, written,
            )
            return str(out)

        return await asyncio.to_thread(_download)

    async def download_all_attachments(
        self, key: str, output_dir: str | None = None,
    ) -> list[dict[str, Any]]:
        """下载 WorkItem 的所有附件。

        Args:
            key:        WorkItem ID
            output_dir: 下载目录 (默认 {attachments_output_dir}/{key}/)

        Returns:
            [{name, path, success, error?}, ...]
        """
        attachments = await self.get_attachments(key)
        if not attachments:
            logger.info("WorkItem %s 没有附件", key)
            return []

        base_dir = Path(
            output_dir or os.path.join(
                self._config.attachments_output_dir, str(key),
            )
        )

        results: list[dict[str, Any]] = []
        for att in attachments:
            name = att["name"]
            safe_name = self._sanitize_filename(name)
            save_path = str(base_dir / safe_name)

            # 跳过已存在的文件
            if os.path.exists(save_path):
                logger.debug("跳过已存在文件: %s", safe_name)
                results.append(
                    {"name": name, "path": save_path, "success": True}
                )
                continue

            try:
                path = await self.download_attachment(att["url"], save_path)
                results.append({"name": name, "path": path, "success": True})
            except Exception as e:
                logger.error("下载附件 '%s' 失败: %s", name, e)
                results.append(
                    {"name": name, "path": save_path, "success": False,
                     "error": str(e)}
                )

        ok = sum(1 for r in results if r["success"])
        logger.info(
            "WorkItem %s 附件下载完成: %d/%d 成功",
            key, ok, len(results),
        )
        return results

    async def close(self) -> None:
        """关闭 session。"""
        if self._session is not None:
            try:
                self._session.close()
            except Exception:
                pass
            self._session = None
            self._authenticated = False
            logger.info("RTC Session 已关闭")

    # ── 内部方法 ──

    @staticmethod
    def _extract_description(raw_data: dict[str, Any]) -> dict[str, Any]:
        """从 xmltodict 解析结果中提取 rdf:Description 层级的数据。

        处理多种 XML 结构:
        1. <rdf:Description>...</rdf:Description> (root 即 Description)
        2. <rdf:RDF><rdf:Description>...</rdf:Description></rdf:RDF> (嵌套)
        3. 多个 rdf:Description 节点 — 找 @rdf:about 含 /workitems/ 的主条目
        """
        root_key = list(raw_data.keys())[0]
        wi_data = raw_data.get(root_key) or {}
        # 如果 root 是 rdf:RDF，提取其中的 rdf:Description
        if "rdf:Description" in wi_data:
            desc = wi_data["rdf:Description"]
            if isinstance(desc, list):
                # 多个 Description 节点 — 找到主 WorkItem 的那个
                # 优先匹配 @rdf:about 包含 /workitems/ 的节点
                for d in desc:
                    if isinstance(d, dict):
                        about = d.get("@rdf:about", "")
                        if "/workitems/" in about or "/oslc/workitems/" in about:
                            return d
                # 回退: 找含 dcterms:identifier 或 dc:identifier 的节点
                for d in desc:
                    if isinstance(d, dict):
                        if d.get("dcterms:identifier") or d.get("dc:identifier"):
                            return d
                # 最终回退: 返回最后一个
                return desc[-1] if desc else {}
            return desc or {}
        return wi_data

    @staticmethod
    def _extract_value(value: Any) -> str:
        """从 OSLC 字段值中提取纯文本。

        处理多种格式:
        - 字符串: 直接返回
        - OrderedDict/dict: 优先 #text，其次 @rdf:resource
        - None: 返回空串
        """
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            text = value.get("#text")
            if text is not None:
                return str(text)
            resource = value.get("@rdf:resource", "")
            return str(resource) if resource else ""
        return str(value)

    def _normalize_workitem(
        self, key: str, raw: dict[str, Any]
    ) -> dict[str, Any]:
        """将 OSLC WorkItem 原始数据映射为与 Jira issue 对齐的 dict。"""
        fields: dict[str, Any] = {}

        for internal_name, oslc_field in self._field_mapping.items():
            value = raw.get(oslc_field)
            fields[internal_name] = self._extract_value(value)

        identifier = fields.get("identifier") or key
        summary = fields.get("summary", "")
        description = fields.get("description", "")
        state = fields.get("state", "")
        priority = fields.get("priority", "")
        created = fields.get("created", "") or fields.get("modified", "")
        tags_str = fields.get("tags", "")
        labels = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []

        # state 可能是完整 URL，提取末尾可读名称
        if state.startswith("http"):
            state = state.rstrip("/").split("/")[-1]

        return {
            "key": str(identifier),
            "fields": {
                "summary": summary,
                "description": description,
                "status": {"name": state},
                "priority": {"name": priority},
                "labels": labels,
                "components": [],
                "environment": "",
                "created": created,
                "reporter": {},
                "issuelinks": [],
            },
            "rtc_raw": fields,
        }

    # ── 附件解析 ──

    _ATTACHMENT_PREDICATE = (
        "http://jazz.net/xmlns/prod/jazz/rtc/cm/1.0/"
        "com.ibm.team.workitem.linktype.attachment.attachment"
    )

    @classmethod
    def _parse_attachments(cls, raw_data: dict[str, Any]) -> list[dict[str, Any]]:
        """从 OSLC RDF/XML 解析结果中提取附件列表。

        附件在 RDF 中以 rdf:Statement 节点表示 (rdf:nodeID="A0"...):
        - rdf:predicate -> ...attachment.attachment
        - rdf:object/@rdf:resource -> 附件下载 URL
        - dcterms:title -> "2611566: filename.xlsx"
        """
        root_key = list(raw_data.keys())[0]
        wi_data = raw_data.get(root_key) or {}

        descriptions = wi_data.get("rdf:Description")
        if not descriptions:
            return []
        if not isinstance(descriptions, list):
            descriptions = [descriptions]

        attachments: list[dict[str, Any]] = []
        for desc in descriptions:
            if not isinstance(desc, dict):
                continue

            # 检查是否为附件 Statement 节点
            predicate = desc.get("rdf:predicate")
            if not predicate:
                continue
            pred_url = (
                predicate.get("@rdf:resource", "")
                if isinstance(predicate, dict) else str(predicate)
            )
            if pred_url != cls._ATTACHMENT_PREDICATE:
                continue

            # 提取下载 URL
            rdf_obj = desc.get("rdf:object")
            if not rdf_obj:
                continue
            att_url = (
                rdf_obj.get("@rdf:resource", "")
                if isinstance(rdf_obj, dict) else str(rdf_obj)
            )
            if not att_url:
                continue

            # 提取文件名和 ID: "2611566: filename.xlsx"
            raw_title = cls._extract_value(desc.get("dcterms:title"))
            attachment_id = ""
            name = raw_title
            if ": " in raw_title:
                parts = raw_title.split(": ", 1)
                attachment_id = parts[0].strip()
                name = parts[1].strip()

            attachments.append({
                "name": name,
                "url": att_url,
                "attachment_id": attachment_id,
            })

        return attachments

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """清理文件名中的非法字符。"""
        safe = re.sub(r'[<>:"/\\|?*]', "_", name)
        safe = safe.strip(". ")
        return safe[:200] if safe else "unnamed"
