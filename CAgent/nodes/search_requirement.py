"""
search_requirement.py — Node 2b: 需求列表为空时的降级搜索

触发条件: state["requirements"] 为空
输入 State 字段: bug_info.components
输出 State 字段: requirements, errors (追加)
依赖: DngClient
"""
from __future__ import annotations

import logging
from typing import Any

from connectors.dng_client import DngClient
from models import RequirementInfo
from state import AnalysisState

logger = logging.getLogger(__name__)


def create_search_requirement_node(dng: DngClient):

    async def search_requirement(state: AnalysisState) -> dict[str, Any]:
        bug_info = state.get("bug_info")
        if not bug_info:
            return {
                "requirements": [],
                "errors": state.get("errors", [])
                + ["降级搜索需求: bug_info 为空"],
            }

        logger.info("[Node 2b] 降级搜索需求")

        # 用 components 作为搜索关键词
        keywords = bug_info.components
        if not keywords:
            # fallback: 从 summary 提取
            keywords = [
                w for w in bug_info.summary.split() if len(w) > 3
            ][:3]

        requirements: list[RequirementInfo] = []
        errors: list[str] = []

        for keyword in keywords:
            try:
                results = await dng.search_requirements(keyword)
                for item in results:
                    req_id = item.get("req_id", "")
                    if not req_id:
                        continue

                    # 获取追溯链接
                    try:
                        trace_links = await dng.get_trace_links(req_id)
                    except Exception:
                        trace_links = {"implemented_by": [], "validated_by": []}

                    req = RequirementInfo(
                        req_id=req_id,
                        title=item.get("title", ""),
                        description=item.get("description", ""),
                        linked_module_names=trace_links.get("implemented_by", []),
                        linked_test_case_ids=trace_links.get("validated_by", []),
                        url=item.get("url", ""),
                    )
                    # 去重
                    if not any(r.req_id == req.req_id for r in requirements):
                        requirements.append(req)

            except Exception as e:
                errors.append(f"搜索需求 (keyword={keyword}) 失败: {e}")
                logger.warning(f"[Node 2b] 搜索失败: {e}")

        msg = f"通过关键词搜索找到 {len(requirements)} 个需求"
        logger.info(f"[Node 2b] {msg}")

        return {
            "requirements": requirements,
            "errors": state.get("errors", []) + errors + [msg],
        }

    return search_requirement
