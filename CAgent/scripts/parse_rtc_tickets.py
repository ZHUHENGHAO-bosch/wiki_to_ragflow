"""
scripts/parse_rtc_tickets.py — 将 RTC OSLC RDF/XML (JSON) 解析为结构化可读格式

将 rtc_ticket_pages/ticket_*.json 文件解析为按 "基本信息 / 状态信息 / 人员信息 / 时间信息 /
测试信息 / 缺陷详情 / 版本信息 / RPN指标 / 关联" 等分组的结构化输出。

用法:
    python scripts/parse_rtc_tickets.py [--input-dir rtc_ticket_pages] [--output tickets_structured.json]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_CAGENT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir))


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _extract_text(val: Any) -> str:
    """从 OSLC RDF 值中提取文本。"""
    if val is None:
        return ""
    if isinstance(val, str):
        return val
    if isinstance(val, dict):
        # resource 引用
        if "@rdf:resource" in val:
            return val["@rdf:resource"]
        # 文本值
        return val.get("#text", "")
    if isinstance(val, list):
        # 多值 (e.g. subscribers)
        parts = []
        for item in val:
            parts.append(_extract_text(item))
        return ", ".join(p for p in parts if p)
    return str(val)


def _user_from_url(url: str) -> str:
    """从 /jts/users/xxx 提取用户 ID。"""
    if not url:
        return ""
    m = re.search(r'/jts/users/([^/]+)$', url)
    if m:
        return m.group(1)
    return url


def _id_from_url(url: str) -> str:
    """从资源 URL 中提取尾部 ID。"""
    if not url:
        return ""
    # .../types/_xxx/defect → defect
    # .../states/.../com.xxx.s9 → com.xxx.s9
    # .../resolutions/.../com.xxx.r2 → com.xxx.r2
    # .../itemOid/.../_xxx → _xxx
    return url.rstrip("/").rsplit("/", 1)[-1]


def _type_from_url(url: str) -> str:
    """从 type URL 提取类型名。例如 .../defect → defect。"""
    return _id_from_url(url)


def _parse_wiki_user(wiki: str) -> str:
    """解析 owner info wiki 中的中文名。
    格式: {{url|中文名,English Name}}
    """
    if not wiki:
        return ""
    m = re.search(r'\|([^}]+)\}', wiki)
    if m:
        return m.group(1)
    return wiki


def _calc_duration_days(start_iso: str, end_iso: str) -> str:
    """计算两个 ISO 日期之间的天数。"""
    if not start_iso or not end_iso:
        return ""
    try:
        t1 = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
        t2 = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
        delta = t2 - t1
        days = delta.days
        if days < 0:
            return ""
        return f"{days} 天"
    except Exception:
        return ""


def _format_datetime(iso_str: str) -> str:
    """将 ISO 日期时间格式化为可读格式。"""
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return iso_str


def _is_empty(val: str) -> bool:
    """判断值是否为空/无意义。"""
    if not val:
        return True
    val = val.strip()
    if not val:
        return True
    # rdf datatype 残留
    if val.startswith("{'@rdf:"):
        return True
    if val in ("unassigned", "Unassigned"):
        return False  # 保留 unassigned 作为有意义值
    return False


# ---------------------------------------------------------------------------
# 状态映射
# ---------------------------------------------------------------------------

STATE_MAP = {
    "s1": "New",
    "s2": "Assigned",
    "s3": "Reopened",
    "s4": "Deferred",
    "s5": "Pending",
    "s6": "Working",
    "s7": "Fixed",
    "s8": "Verified",
    "s9": "Closed",
    "s10": "Rejected",
    "s11": "Duplicate",
}

RESOLUTION_MAP = {
    "r1": "Fixed",
    "r2": "Verified",
    "r3": "Rejected",
    "r4": "Duplicate",
    "r5": "Deferred",
    "r6": "Works As Designed",
    "r7": "Cannot Reproduce",
}

PRIORITY_MAP = {
    "l01": "Unassigned",
    "l11": "High",
    "l07": "Medium",
    "l13": "Low",
    "l14": "None",
}

SEVERITY_MAP = {
    "l1": "Unassigned",
    "l2": "Blocker",
    "l3": "Major",
    "l4": "Normal",
    "l5": "Minor",
    "l6": "Trivial",
}


def _map_state(state_url: str) -> str:
    """将 state URL 映射为可读名称。"""
    state_id = _id_from_url(state_url)
    # 尝试从 state_id 中提取 sN
    m = re.search(r'\.state\.(\w+)$', state_id)
    if m:
        code = m.group(1)
        return STATE_MAP.get(code, code)
    return state_id


def _map_resolution(res_url: str) -> str:
    """将 resolution URL 映射为可读名称。"""
    res_id = _id_from_url(res_url)
    m = re.search(r'\.resolution\.(\w+)$', res_id)
    if m:
        code = m.group(1)
        return RESOLUTION_MAP.get(code, code)
    return res_id


def _map_priority(priority_url: str) -> str:
    """将 priority URL 映射为可读名称。"""
    p_id = _id_from_url(priority_url)
    m = re.search(r'\.literal\.(\w+)$', p_id)
    if m:
        code = m.group(1)
        return PRIORITY_MAP.get(code, code)
    return p_id


def _map_severity(severity_url: str) -> str:
    """将 severity URL 映射为可读名称。"""
    s_id = _id_from_url(severity_url)
    m = re.search(r'\.literal\.(\w+)$', s_id)
    if m:
        code = m.group(1)
        return SEVERITY_MAP.get(code, code)
    return s_id


# ---------------------------------------------------------------------------
# 主解析
# ---------------------------------------------------------------------------

def parse_ticket(raw: dict) -> dict:
    """将一条 OSLC RDF/XML JSON 解析为结构化 ticket。"""
    rdf = raw.get("rdf:RDF", raw)
    desc_raw = rdf.get("rdf:Description", {})

    # rdf:Description 可能是 dict（单节点）或 list（多节点，含 Statement 节点）
    # 主 ticket 数据是包含 dcterms:identifier 的那个节点
    links_nodes = []
    if isinstance(desc_raw, list):
        desc = {}
        for node in desc_raw:
            if not isinstance(node, dict):
                continue
            if "dcterms:identifier" in node:
                desc = node
            elif node.get("rdf:type", {}).get("@rdf:resource", "").endswith("Statement"):
                links_nodes.append(node)
        if not desc:
            # fallback: 取含有 @rdf:about 且指向 /workitems/ 的节点
            for node in desc_raw:
                about = node.get("@rdf:about", "")
                if "/workitems/" in about and "dcterms:created" in node:
                    desc = node
                    break
            if not desc and desc_raw:
                desc = desc_raw[0]
    else:
        desc = desc_raw

    def _get(key: str) -> str:
        return _extract_text(desc.get(key))

    def _get_user(key: str) -> str:
        return _user_from_url(_get(key))

    def _get_users(key: str) -> str:
        """处理多值用户字段。"""
        val = desc.get(key)
        if val is None:
            return ""
        if isinstance(val, list):
            users = [_user_from_url(_extract_text(v)) for v in val]
            return ", ".join(u for u in users if u)
        return _user_from_url(_extract_text(val))

    # 提取各字段
    wi_id = _get("dcterms:identifier")
    title = _get("dcterms:title")
    short_title = _get("oslc:shortTitle")
    description = _get("dcterms:description")
    tags = _get("dcterms:subject")
    wi_type_url = _get("rtc_cm:type")
    wi_type = _type_from_url(wi_type_url)
    dcterms_type = _get("dcterms:type")  # e.g. "Bug"

    # 状态
    state_url = _get("rtc_cm:state")
    state_name = _map_state(state_url)
    status = _get("oslc_cm:status")
    resolution_url = _get("rtc_cm:resolution")
    resolution = _map_resolution(resolution_url) if resolution_url else ""
    in_progress = _get("oslc_cm:inprogress")
    closed = _get("oslc_cm:closed")
    fixed = _get("oslc_cm:fixed")
    approved = _get("oslc_cm:approved")
    verified = _get("oslc_cm:verified")
    reviewed = _get("oslc_cm:reviewed")

    # Priority / Severity
    priority_url = _get("oslc_cmx:priority")
    priority = _map_priority(priority_url) if priority_url else ""
    severity_url = _get("oslc_cmx:severity")
    severity = _map_severity(severity_url) if severity_url else ""

    # 人员
    creator = _get_user("dcterms:creator")
    owner = _get_user("dcterms:contributor")
    modified_by = _get_user("rtc_cm:modifiedBy")
    resolved_by = _get_user("rtc_cm:resolvedBy")
    subscribers = _get_users("rtc_cm:subscribers")
    product_owner = _get_user("rtc_ext:com.patac.workitem.attribute.bugproductowner")
    feature_owner = _get_user("rtc_ext:com.patac.workitem.attribute.bugfeatureowner")
    owner_group = _get("rtc_ext:com.patac.workitem.attribute.bugownergroup")
    reviewed_resolver = _get_user("rtc_ext:com.patac.workitem.attribute.34reviewedresolver")
    resolver_34 = _get_user("rtc_ext:com.patac.workitem.attribute.34Resolver")
    resolver_group_34 = _get_user("rtc_ext:com.patac.workitem.attribute.34ResolverGroup")
    created_by_602 = _get_user("rtc_ext:com.patac.team.workitem.attribute.602CreatedBy")
    owner_info_wiki = _get("rtc_ext:com.patac.team.workitem.attribute.defectownerinfowiki")
    owner_info = _parse_wiki_user(owner_info_wiki)

    # 时间
    created = _get("dcterms:created")
    modified = _get("dcterms:modified")
    due = _get("rtc_cm:due")
    close_date = _get("oslc_cm:closeDate")

    # Bug Fixing Duration
    bug_duration = _calc_duration_days(created, close_date)

    # 测试信息
    test_env = _get("rtc_ext:com.patac.team.workitem.attribute.defecttestenvironment")
    confirm_env = _get("rtc_ext:com.patac.team.workitem.attribute.defectconfirmenvironment")
    found_in_region = _get("rtc_ext:com.patac.team.workitem.attribute.defectfoundinregion")
    recur_freq = _get("rtc_ext:com.patac.team.workitem.attribute.defectrecurfrequency")
    init_setting = _get("rtc_ext:com.patac.team.workitem.attribute.defectinitsetting")
    operation_schedule = _get("rtc_ext:com.patac.team.workitem.attribute.defectoperationschedule")
    actual_result = _get("rtc_ext:com.patac.team.workitem.attribute.defectactualresult")
    expect_result = _get("rtc_ext:com.patac.team.workitem.attribute.defectexpectresult")
    recovery = _get("rtc_ext:com.patac.team.workitem.attribute.defectrecovery")
    hardware_variant = _get("rtc_ext:com.patac.team.workitem.attribute.defecthardwarevariant")

    # 缺陷详情
    discover_phase = _get("rtc_ext:com.patac.workitem.attribute.discoverphase") or \
                     _get("rtc_ext:com.patac.workitem.attribute.defectdiscoverphase")
    introduce_phase = _get("rtc_ext:com.patac.workitem.attribute.defectintroducephase") or \
                      _get("rtc_ext:com.patac.workitem.attribute.introducephase")
    root_cause_cate = _get("rtc_ext:com.patac.workitem.attribute.bugrootcausecate")
    root_cause_sub = _get("rtc_ext:com.patac.workitem.attribute.bugrootcausesubcate")
    issue_cate = _get("rtc_ext:com.patac.workitem.attribute.bugissuecate")
    root_cause_detail = _get("rtc_ext:com.patac.team.workitem.attribute.defectsolutionandresolve")
    solution = _get("rtc_ext:com.patac.team.workitem.attribute.defectresolve")
    rejected_cause = _get("rtc_ext:com.patac.team.workitem.attribute.defectrejectedcause")
    pend_cause = _get("rtc_ext:com.patac.team.workitem.attribute.defectpendcause")
    defer_cause = _get("rtc_ext:com.patac.team.workitem.attribute.defectdefercause")
    trigger_cr = _get("rtc_ext:com.patac.workitem.attribute.defecttriggercr")
    is_transfer = _get("rtc_ext:com.patac.team.workitem.attribute.defectistransfer")
    hot_q = _get("rtc_ext:com.patac.team.workitem.attribute.defecthotq")
    uer_exp_issue = _get("rtc_ext:com.patac.team.workitem.attribute.uerexperienceissue")
    overdue_cause_cat = _get("rtc_ext:com.patac.workitem.attribute.bugoverduecausecategory")
    overdue_cause_desc = _get("rtc_ext:com.patac.workitem.attribute.bugoverduecausedescription")
    next_action = _get("rtc_ext:com.patac.workitem.attribute.bugnextaction")

    # 版本信息
    find_version = _get("rtc_ext:com.patac.team.workitem.attribute.defectfindversion")
    find_version_id = _id_from_url(find_version) if find_version and find_version.startswith("http") else find_version
    confirm_version = _get("rtc_ext:com.patac.team.workitem.attribute.defectconfirmversion")
    confirm_version_id = _id_from_url(confirm_version) if confirm_version and confirm_version.startswith("http") else confirm_version
    fixed_version = _get("rtc_ext:com.patac.workitem.attribute.defectfixedversion")
    fixed_version_id = _id_from_url(fixed_version) if fixed_version and fixed_version.startswith("http") else fixed_version
    found_in_vescom = _get("rtc_ext:com.patac.team.workitem.attribute.defectfoundinvescom")
    resolved_in_vescom = _get("rtc_ext:com.patac.team.workitem.attribute.defectresolvedinvescom")
    found_in_ea = _get("rtc_ext:com.patac.team.workitem.attribute.defectfoundinelectricalarchitecture")
    found_in_ea_list = _get("rtc_ext:com.patac.team.workitem.attribute.defectfoundinelectricalarchitecturelist")

    # 指标
    reopen_times = _get("rtc_ext:com.patac.team.workitem.attribute.defectreopentimes")
    confirm_times = _get("rtc_ext:com.patac.team.workitem.attribute.defectconfirmtimes")
    rpn = _get("rtc_ext:com.patac.workitem.attribute.defectrpn")
    rpn_severity = _get("rtc_ext:com.patac.workitem.attribute.defectrpnsevertiy")
    rpn_occurrence = _get("rtc_ext:com.patac.workitem.attribute.defectrpnoccurrence")
    rpn_detection = _get("rtc_ext:com.patac.workitem.attribute.defectrpndetection")
    rpl = _get("rtc_ext:com.patac.workitem.attribute.defectrpl")
    state_string_list = _get("rtc_ext:com.patac.team.workitem.attribute.defectstatestringlist")

    # 项目
    platform_vehicle = _get("rtc_ext:com.patac.team.workitem.attribute.platformvehiclemodel")
    project = _get("rtc_ext:com.patac.team.workitem.attribute.project")
    subsystem = _get("rtc_ext:com.patac.team.workitem.attribute.subsystem")
    assigned_to_system = _get("rtc_ext:com.patac.team.workitem.attribute.assignedtosystem")
    originator = _get("rtc_ext:com.patac.team.workitem.attribute.workitemoriginator")

    # 其他
    filed_against = _get("rtc_cm:filedAgainst")
    filed_against_id = _id_from_url(filed_against) if filed_against and filed_against.startswith("http") else filed_against
    planned_for = _get("rtc_cm:plannedFor")
    planned_for_id = _id_from_url(planned_for) if planned_for and planned_for.startswith("http") else planned_for
    team_area = _get("rtc_cm:teamArea")
    team_area_id = _id_from_url(team_area) if team_area and team_area.startswith("http") else team_area
    defect_wiki = _get("rtc_ext:com.patac.workitem.attribute.defectwiki")
    pm_comment = _get("rtc_ext:com.patac.team.workitem.attribute.defectpmcomment")
    qa_comment = _get("rtc_ext:com.patac.team.workitem.attribute.defectqacomment")
    sync_to = _get("rtc_ext:com.patac.team.workitem.attribute.syncto")
    approval_resolution = _get("rtc_ext:com.patac.team.workitem.attribute.defectapprovalresolution")
    archived = _get("rtc_ext:archived")

    # ---------------------------------------------------------------------------
    # 构建结构化输出
    # ---------------------------------------------------------------------------
    def _section(items: list[tuple[str, str]]) -> dict:
        """过滤空值后构建 section dict。"""
        return {k: v for k, v in items if not _is_empty(v)}

    ticket = {
        "基本信息": _section([
            ("ID", wi_id),
            ("Short Title", short_title or f"Bug {wi_id}"),
            ("标题 (Title)", title),
            ("类型 (Type)", f"{dcterms_type}/{wi_type}" if dcterms_type else wi_type),
            ("描述 (Description)", description),
            ("标签 (Tags)", tags),
            ("优先级 (Priority)", priority),
            ("严重程度 (Severity)", severity),
            ("平台/车型 (Platform/Vehicle)", platform_vehicle),
            ("项目 (Project)", project),
            ("子系统 (Subsystem)", subsystem),
            ("分配系统 (Assigned To System)", assigned_to_system),
            ("来源 (Originator)", originator),
            ("Filed Against", filed_against_id),
            ("Planned For", planned_for_id),
            ("Team Area", team_area_id),
            ("已归档 (Archived)", archived),
        ]),
        "状态信息": _section([
            ("状态 (State)", state_name),
            ("Status", status),
            ("Resolution", resolution),
            ("In Progress", in_progress),
            ("Fixed", fixed),
            ("Verified", verified),
            ("Approved", approved),
            ("Reviewed", reviewed),
            ("Closed", closed),
            ("状态历史 (State History)", state_string_list),
            ("Defect Wiki", defect_wiki),
            ("Hot Q", hot_q),
        ]),
        "人员信息": _section([
            ("创建者 (Creator)", creator),
            ("负责人 (Owner)", owner),
            ("Owner Info", owner_info),
            ("Owner Group", owner_group),
            ("最后修改者 (Modified By)", modified_by),
            ("解决者 (Resolved By)", resolved_by),
            ("3+4 Resolver", resolver_34),
            ("3+4 Resolver Group", resolver_group_34),
            ("Reviewed Resolver", reviewed_resolver),
            ("Product Owner", product_owner),
            ("Feature Owner", feature_owner),
            ("602 Created By", created_by_602),
            ("订阅者 (Subscribers)", subscribers),
        ]),
        "时间信息": _section([
            ("创建时间 (Created)", _format_datetime(created)),
            ("最后修改 (Modified)", _format_datetime(modified)),
            ("到期日 (Due)", _format_datetime(due)),
            ("关闭时间 (Close Date)", _format_datetime(close_date)),
            ("Bug修复时长 (Bug Fixing Duration)", bug_duration),
            ("Reopen Times", reopen_times),
            ("Confirm Times", confirm_times),
        ]),
        "测试信息": _section([
            ("测试环境 (Test Environment)", test_env),
            ("确认环境 (Confirm Environment)", confirm_env),
            ("发现地区 (Found In Region)", found_in_region),
            ("复现频率 (Recurrence Frequency)", recur_freq),
            ("硬件变体 (Hardware Variant)", hardware_variant),
            ("初始设置 (Initial Setting)", init_setting),
            ("操作步骤 (Operation Schedule)", operation_schedule),
            ("实际结果 (Actual Result)", actual_result),
            ("期望结果 (Expected Result)", expect_result),
            ("恢复方法 (Recovery)", recovery),
        ]),
        "缺陷详情": _section([
            ("发现阶段 (Discover Phase)", discover_phase),
            ("引入阶段 (Introduce Phase)", introduce_phase),
            ("根因分类 (Root Cause Category)", root_cause_cate),
            ("根因子类 (Root Cause Sub-Category)", root_cause_sub),
            ("问题分类 (Issue Category)", issue_cate),
            ("根本原因 (Root Cause Detail)", root_cause_detail),
            ("解决方案 (Solution)", solution),
            ("拒绝原因 (Rejected Cause)", rejected_cause),
            ("挂起原因 (Pend Cause)", pend_cause),
            ("延迟原因 (Defer Cause)", defer_cause),
            ("触发CR (Trigger CR)", trigger_cr),
            ("是否转移 (Is Transfer)", is_transfer),
            ("用户体验问题 (UER Experience Issue)", uer_exp_issue),
            ("逾期原因分类 (Overdue Cause Category)", overdue_cause_cat),
            ("逾期原因描述 (Overdue Cause Description)", overdue_cause_desc),
            ("下一步 (Next Action)", next_action),
            ("审批Resolution (Approval Resolution)", approval_resolution),
            ("PM Comment", pm_comment),
            ("QA Comment", qa_comment),
            ("Sync To", sync_to),
        ]),
        "版本信息": _section([
            ("发现版本 (Find Version)", find_version_id),
            ("确认版本 (Confirm Version)", confirm_version_id),
            ("修复版本 (Fixed Version)", fixed_version_id),
            ("发现VESCOM版本 (Found In VESCOM)", found_in_vescom),
            ("修复VESCOM版本 (Resolved In VESCOM)", resolved_in_vescom),
            ("电气架构 (Electrical Architecture)", found_in_ea),
            ("电气架构列表 (EA List)", found_in_ea_list),
        ]),
        "RPN指标": _section([
            ("RPN", rpn),
            ("RPN Severity", rpn_severity),
            ("RPN Occurrence", rpn_occurrence),
            ("RPN Detection", rpn_detection),
            ("RPL", rpl),
        ]),
    }

    # 提取关联链接和附件
    if links_nodes:
        links = []
        attachments = []
        for ln in links_nodes:
            pred = _extract_text(ln.get("rdf:predicate", {}))
            obj = _extract_text(ln.get("rdf:object", {}))
            link_title = _extract_text(ln.get("dcterms:title", {}))
            link_type = pred.rsplit("/", 1)[-1] if pred else ""

            # 附件节点: predicate 包含 attachment
            if "attachment" in link_type.lower():
                att_name = link_title
                att_id = ""
                if ": " in link_title or "：" in link_title:
                    # 格式: "2241：filename.doc" 或 "12345: filename.xlsx"
                    sep = "：" if "：" in link_title else ": "
                    parts = link_title.split(sep, 1)
                    att_id = parts[0].strip()
                    att_name = parts[1].strip()
                attachments.append({
                    "文件名 (Filename)": att_name,
                    "附件ID (Attachment ID)": att_id,
                    "下载链接 (URL)": obj,
                })
            else:
                obj_id = re.search(r'/(\d+)$', obj)
                obj_id = obj_id.group(1) if obj_id else _id_from_url(obj)
                links.append({
                    "类型 (Type)": link_type,
                    "关联ID (Target)": obj_id,
                    "标题 (Title)": link_title,
                })
        if attachments:
            ticket["附件 (Attachments)"] = attachments
        if links:
            ticket["关联链接"] = links

    # 移除空 section
    ticket = {k: v for k, v in ticket.items() if v}

    return ticket


def parse_all_tickets(input_dir: str, merge_discussions: bool = True) -> list[dict]:
    """解析目录下所有 ticket_*.json 文件。

    如果同目录下存在 discussions.json，会自动合并评论。
    """
    # 加载 discussions (如果存在)
    discussions: dict[str, dict] = {}
    disc_path = os.path.join(input_dir, "discussions.json")
    if merge_discussions and os.path.exists(disc_path):
        try:
            with open(disc_path, "r", encoding="utf-8") as f:
                discussions = json.load(f)
            print(f"  已加载 discussions.json ({len(discussions)} 个 ticket 的评论)")
        except Exception as e:
            print(f"  加载 discussions.json 失败: {e}")

    results = []
    json_files = sorted(Path(input_dir).glob("ticket_*.json"))
    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                raw = json.load(f)
            ticket = parse_ticket(raw)

            # 合并评论
            wi_id = ticket.get("基本信息", {}).get("ID", "")
            disc = discussions.get(wi_id, {})
            if disc.get("comments"):
                ticket["讨论 (Discussion)"] = [
                    {
                        "评论者": c.get("creator", ""),
                        "时间": c.get("created", ""),
                        "内容": c.get("body", ""),
                    }
                    for c in disc["comments"]
                ]

            results.append(ticket)
            n_comments = len(ticket.get("讨论 (Discussion)", []))
            print(f"  [OK] {jf.name} -> ID={wi_id}, {n_comments} 条评论")
        except Exception as e:
            print(f"  [FAIL] {jf.name}: {e}")
    return results


def main():
    parser = argparse.ArgumentParser(description="解析 RTC OSLC JSON 为结构化格式")
    parser.add_argument(
        "--input-dir",
        default=os.path.join(_CAGENT_ROOT, "rtc_ticket_pages"),
        help="存放 ticket_*.json 的目录",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="输出文件路径 (默认: input-dir/tickets_structured.json)",
    )
    parser.add_argument(
        "--no-discussions", action="store_true",
        help="不合并评论",
    )
    args = parser.parse_args()

    out_path = args.output or os.path.join(args.input_dir, "tickets_structured.json")

    print(f"输入目录: {args.input_dir}")
    print(f"输出文件: {out_path}")
    print()

    results = parse_all_tickets(args.input_dir, merge_discussions=not args.no_discussions)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n完成! 共解析 {len(results)} 个 ticket → {out_path}")


if __name__ == "__main__":
    main()
