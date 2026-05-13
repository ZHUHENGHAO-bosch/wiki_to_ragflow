"""
read_requirement.py — Node 2: 从 DNG 读取需求

输入 State 字段: test_cases[].linked_requirement_ids
输出 State 字段: requirements
依赖: DngClient
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from connectors.dng_client import DngClient
from models import RequirementInfo
from state import AnalysisState

logger = logging.getLogger(__name__)


def create_read_requirement_node(dng: DngClient):

    async def read_requirement(state: AnalysisState) -> dict[str, Any]:
        test_cases = state.get("test_cases", [])

        # 收集所有关联的需求 ID (去重)
        req_ids: list[str] = []
        seen: set[str] = set()
        for tc in test_cases:
            for rid in tc.linked_requirement_ids:
                if rid not in seen:
                    seen.add(rid)
                    req_ids.append(rid)

        if not req_ids:
            logger.info("[Node 2] 无关联需求 ID")
            return {"requirements": []}

        logger.info(f"[Node 2] 读取 {len(req_ids)} 个需求")

        tasks = [_read_single_req(dng, rid) for rid in req_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        requirements: list[RequirementInfo] = []
        errors: list[str] = []
        for rid, result in zip(req_ids, results):
            if isinstance(result, Exception):
                errors.append(f"读取需求 {rid} 失败: {result}")
                logger.warning(f"[Node 2] 读取 {rid} 失败: {result}")
            elif result:
                requirements.append(result)

        logger.info(f"[Node 2] 成功读取 {len(requirements)} 个需求")

        update: dict[str, Any] = {"requirements": requirements}
        if errors:
            update["errors"] = state.get("errors", []) + errors
        return update

    return read_requirement


async def _read_single_req(dng: DngClient, req_id: str) -> RequirementInfo | None:
    """读取并解析单个需求。"""
    req_data = await dng.get_requirement(req_id)
    trace_links = await dng.get_trace_links(req_id)

    return RequirementInfo(
        req_id=req_data.get("req_id", req_id),
        title=req_data.get("title", ""),
        description=req_data.get("description", ""),
        req_type=req_data.get("req_type", ""),
        asil_level=req_data.get("asil_level", ""),
        linked_module_names=trace_links.get("implemented_by", []),
        linked_test_case_ids=trace_links.get("validated_by", []),
        url=req_data.get("url", ""),
    )
