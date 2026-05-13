"""
connectors/dng_client.py — DNG (DOORS Next Generation) OSLC API 封装

使用 OSLC (Open Services for Lifecycle Collaboration) 协议与 DNG 通信。
"""
from __future__ import annotations

import logging
import re
from typing import Any
from xml.etree import ElementTree as ET

import httpx

from config import DngConfig

logger = logging.getLogger(__name__)

# OSLC / RDF 命名空间
NS = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "dcterms": "http://purl.org/dc/terms/",
    "oslc": "http://open-services.net/ns/core#",
    "oslc_rm": "http://open-services.net/ns/rm#",
    "rm": "http://www.ibm.com/xmlns/rdm/rdf/",
}


class DngClient:
    """DNG OSLC API 客户端。"""

    def __init__(self, config: DngConfig) -> None:
        self._config = config
        self._base = config.base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            verify=config.verify_ssl,
            timeout=30.0,
        )
        self._auth_cookies: dict[str, str] = {}

    async def authenticate(self) -> None:
        """
        Jazz Form-based 认证。

        POST /j_security_check 获取 session cookie。
        """
        auth_url = f"{self._base}/j_security_check"
        resp = await self._client.post(
            auth_url,
            data={
                "j_username": self._config.username,
                "j_password": self._config.password,
            },
            follow_redirects=True,
        )
        resp.raise_for_status()
        self._auth_cookies = dict(resp.cookies)
        logger.info("DNG 认证成功")

    async def get_requirement(self, req_id: str) -> dict[str, Any]:
        """
        通过 OSLC 获取单个需求的属性。

        返回 dict 包含: req_id, title, description, req_type, asil_level, url
        """
        url = self._resolve_requirement_url(req_id)
        resp = await self._client.get(
            url,
            headers={"Accept": "application/rdf+xml", "OSLC-Core-Version": "2.0"},
            cookies=self._auth_cookies,
        )
        resp.raise_for_status()
        return self._parse_requirement_xml(req_id, resp.text, url)

    async def get_trace_links(self, req_id: str) -> dict[str, list[str]]:
        """
        获取需求的追溯链接。

        返回:
        {
            "implemented_by": ["module_a", "module_b"],
            "validated_by": ["TC-001", "TC-002"]
        }
        """
        url = self._resolve_requirement_url(req_id)
        links_url = f"{url}/links"
        resp = await self._client.get(
            links_url,
            headers={"Accept": "application/rdf+xml", "OSLC-Core-Version": "2.0"},
            cookies=self._auth_cookies,
        )

        if resp.status_code == 404:
            resp = await self._client.get(
                url,
                headers={
                    "Accept": "application/rdf+xml",
                    "OSLC-Core-Version": "2.0",
                },
                cookies=self._auth_cookies,
            )
            resp.raise_for_status()

        return self._parse_trace_links(resp.text)

    async def search_requirements(self, keyword: str) -> list[dict[str, Any]]:
        """
        通过 OSLC Query 搜索需求。

        使用 oslc.where=dcterms:title 模糊匹配。
        """
        query_url = (
            f"{self._base}/rm/views"
            f"?projectURL={self._config.project_area}"
            f"&oslc.query=true"
            f'&oslc.where=dcterms:title="{keyword}"'
            f"&oslc.select=dcterms:title,dcterms:description"
        )
        resp = await self._client.get(
            query_url,
            headers={"Accept": "application/rdf+xml", "OSLC-Core-Version": "2.0"},
            cookies=self._auth_cookies,
        )
        resp.raise_for_status()
        return self._parse_search_results(resp.text)

    # ── 内部方法 ──

    def _resolve_requirement_url(self, req_id: str) -> str:
        """将需求 ID 转为 OSLC URL。"""
        if req_id.startswith("http"):
            return req_id
        return f"{self._base}/rm/resources/{req_id}"

    def _parse_requirement_xml(
        self, req_id: str, xml_text: str, url: str
    ) -> dict[str, Any]:
        """解析 OSLC RDF/XML 获取需求属性。"""
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            logger.warning(f"无法解析需求 {req_id} 的 XML 响应")
            return {
                "req_id": req_id,
                "title": "",
                "description": xml_text[:500],
                "req_type": "",
                "asil_level": "",
                "url": url,
            }

        desc = root.find(".//rdf:Description", NS) or root
        title = self._get_text(desc, "dcterms:title")
        description = self._get_text(desc, "dcterms:description")
        req_type = self._get_text(desc, "rm:type") or self._get_text(
            desc, "oslc_rm:instanceShape"
        )

        # ASIL level 可能在自定义属性中
        asil = ""
        for elem in desc:
            tag_local = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if "asil" in tag_local.lower() or "safety" in tag_local.lower():
                asil = elem.text or elem.get(f"{{{NS['rdf']}}}resource", "")
                break

        return {
            "req_id": req_id,
            "title": title,
            "description": description,
            "req_type": req_type,
            "asil_level": asil,
            "url": url,
        }

    def _parse_trace_links(self, xml_text: str) -> dict[str, list[str]]:
        """解析追溯链接 XML。"""
        result: dict[str, list[str]] = {"implemented_by": [], "validated_by": []}
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            logger.warning("无法解析追溯链接 XML")
            return result

        impl_type = self._config.implemented_by_link_type
        valid_type = self._config.validated_by_link_type

        for elem in root.iter():
            tag_local = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            resource = elem.get(f"{{{NS['rdf']}}}resource", "")

            if impl_type in tag_local.lower() or impl_type in resource.lower():
                target = resource or (elem.text or "").strip()
                if target:
                    name = self._extract_module_name(target)
                    result["implemented_by"].append(name)

            if valid_type in tag_local.lower() or valid_type in resource.lower():
                target = resource or (elem.text or "").strip()
                if target:
                    result["validated_by"].append(target.split("/")[-1])

        return result

    def _parse_search_results(self, xml_text: str) -> list[dict[str, Any]]:
        """解析 OSLC 搜索结果。"""
        results: list[dict[str, Any]] = []
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return results

        for desc in root.findall(".//rdf:Description", NS):
            about = desc.get(f"{{{NS['rdf']}}}about", "")
            if not about:
                continue
            title = self._get_text(desc, "dcterms:title")
            req_id = about.split("/")[-1]
            results.append(
                {
                    "req_id": req_id,
                    "title": title,
                    "description": self._get_text(desc, "dcterms:description"),
                    "url": about,
                }
            )
        return results

    @staticmethod
    def _extract_module_name(url_or_path: str) -> str:
        """从 URL 或路径中提取模块名。"""
        # URL: .../resources/module_name -> module_name
        name = url_or_path.rstrip("/").split("/")[-1]
        # 去掉可能的 fragment
        name = name.split("#")[0]
        return name

    @staticmethod
    def _get_text(elem: ET.Element, tag: str) -> str:
        """安全获取子元素文本。"""
        ns_prefix, local = tag.split(":")
        full_tag = f"{{{NS[ns_prefix]}}}{local}"
        child = elem.find(full_tag)
        if child is not None:
            return (child.text or "").strip()
        return ""

    async def close(self) -> None:
        """关闭 HTTP 客户端。"""
        await self._client.aclose()
