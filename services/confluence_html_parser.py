"""
services/confluence_html_parser.py -- Confluence export_view HTML → 结构化内容解析器

将 Confluence 的 export_view HTML 解析为结构化 JSON 内容块列表。
支持: 标题、段落、表格、代码块、面板、列表、图片。
"""
from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote

from bs4 import BeautifulSoup, NavigableString, Tag


def parse_confluence_html(html: str) -> list[dict[str, Any]]:
    """将 Confluence export_view HTML 解析为结构化内容块列表。

    Parameters
    ----------
    html : str
        Confluence ``body.export_view`` 的 HTML 内容。

    Returns
    -------
    list[dict]
        按文档顺序排列的内容块列表，每个块包含 ``type`` 字段和类型特定字段。
    """
    if not html or not html.strip():
        return []

    soup = BeautifulSoup(html, "html.parser")
    blocks: list[dict[str, Any]] = []

    for element in soup.children:
        if isinstance(element, NavigableString):
            text = element.strip()
            if text:
                blocks.append({"type": "paragraph", "text": text})
            continue

        if not isinstance(element, Tag):
            continue

        parsed = _parse_element(element)
        if parsed is not None:
            if isinstance(parsed, list):
                blocks.extend(parsed)
            else:
                blocks.append(parsed)

    return blocks


def _parse_element(el: Tag) -> dict[str, Any] | list[dict[str, Any]] | None:
    """解析单个顶层 HTML 元素为内容块。"""
    tag = el.name

    # 标题
    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        return _parse_heading(el)

    # 代码块（优先于面板，因为代码宏可能同时有 panel 类）
    if _is_code_block(el):
        return _parse_code_block(el)

    # 面板 / 信息宏（优先于通用 div 处理）
    if _is_panel(el):
        return _parse_panel(el)

    # 表格
    if tag == "table":
        return _parse_table(el)

    # 列表
    if tag in ("ul", "ol"):
        return _parse_list(el)

    # 段落
    if tag == "p":
        return _parse_paragraph(el)

    # 图片（独立 img 标签）
    if tag == "img":
        return _parse_image(el)

    # div / section 等容器: 递归提取子元素
    if tag in ("div", "section", "article", "main", "span"):
        return _parse_container(el)

    # 预格式化文本
    if tag == "pre":
        return _parse_code_block(el)

    # 其他块级元素: fallback 为 paragraph
    text = el.get_text(separator=" ", strip=True)
    if text:
        return {"type": "paragraph", "text": text}

    return None


# ── 各类型解析函数 ──


def _parse_heading(el: Tag) -> dict[str, Any]:
    level = int(el.name[1])
    text = el.get_text(separator=" ", strip=True)
    return {"type": "heading", "level": level, "text": text}


def _parse_paragraph(el: Tag) -> dict[str, Any] | None:
    # 检查是否只包含一个 img
    imgs = el.find_all("img")
    if len(imgs) == 1 and el.get_text(strip=True) == "":
        return _parse_image(imgs[0])

    text = el.get_text(separator=" ", strip=True)
    if not text:
        return None
    return {"type": "paragraph", "text": text}


def _parse_image(el: Tag) -> dict[str, Any] | None:
    src = el.get("src", "")
    if not src:
        return None
    alt = el.get("alt", "")
    return {"type": "image", "src": src, "alt": alt}


def _parse_table(el: Tag) -> dict[str, Any]:
    """解析表格，提取 headers 和 rows。处理 colspan。"""
    headers: list[str] = []
    rows: list[list[str]] = []

    # 查找 thead 中的表头
    thead = el.find("thead")
    if thead:
        header_row = thead.find("tr")
        if header_row:
            headers = _extract_row_cells(header_row)

    # 查找 tbody（如果存在）
    tbody = el.find("tbody")
    body_rows = tbody.find_all("tr") if tbody else el.find_all("tr")

    for tr in body_rows:
        # 跳过 thead 中的行
        if thead and tr.parent == thead:
            continue

        cells = _extract_row_cells(tr)

        # 如果还没有 headers，且第一行全是 th，则作为 header
        if not headers and not rows:
            ths = tr.find_all("th")
            if ths and not tr.find_all("td"):
                headers = cells
                continue

        rows.append(cells)

    return {"type": "table", "headers": headers, "rows": rows}


def _extract_row_cells(tr: Tag) -> list[str]:
    """提取一行中所有单元格的内容，保留内嵌图片为 inline ![alt](src)。"""
    cells: list[str] = []
    for cell in tr.find_all(["td", "th"]):
        text = _render_cell_inline(cell)
        colspan = 1
        cs_attr = cell.get("colspan")
        if cs_attr:
            try:
                colspan = int(cs_attr)
            except (ValueError, TypeError):
                pass
        cells.append(text)
        # colspan > 1: 填充空字符串
        for _ in range(colspan - 1):
            cells.append("")
    return cells


def _render_cell_inline(cell: Tag) -> str:
    """渲染单元格为 inline 字符串：文本 + ![alt](src) 表示图片。

    遍历 descendants 仅收集 NavigableString 文本与 <img> 标签，
    避免容器标签自身被重复计入。src 保持原始（未编码），
    后续由 downloader 替换为本地路径，再由 blocks_to_markdown 做 URL 编码。
    """
    parts: list[str] = []
    for descendant in cell.descendants:
        if isinstance(descendant, NavigableString):
            t = str(descendant).strip()
            if t:
                parts.append(t)
        elif isinstance(descendant, Tag) and descendant.name == "img":
            src = (descendant.get("src") or "").strip()
            alt = (descendant.get("alt") or "").strip()
            if src:
                parts.append(f"![{alt}]({src})")
    return " ".join(parts).strip()


def _is_code_block(el: Tag) -> bool:
    """判断元素是否为代码块。"""
    if el.name == "pre":
        return True
    # Confluence 代码宏渲染后的结构
    cls = " ".join(el.get("class", []))
    if "code-block" in cls or "codeContent" in cls:
        return True
    if "syntaxhighlighter" in cls:
        return True
    # 包含 class="code" 的 div
    if el.name == "div" and "code" in el.get("class", []):
        code_el = el.find("pre") or el.find("code")
        if code_el:
            return True
    return False


def _parse_code_block(el: Tag) -> dict[str, Any]:
    """解析代码块，提取语言和内容。"""
    language = ""
    content = ""

    cls = " ".join(el.get("class", []))

    # 从 class 中提取语言 (如 "brush: python" 或 "language-python")
    lang_match = re.search(r"brush:\s*(\w+)", cls)
    if lang_match:
        language = lang_match.group(1)
    else:
        lang_match = re.search(r"language-(\w+)", cls)
        if lang_match:
            language = lang_match.group(1)

    # 从 data-syntaxhighlighter-params 中提取语言
    if not language:
        params = el.get("data-syntaxhighlighter-params", "")
        lang_match = re.search(r"brush:\s*(\w+)", params)
        if lang_match:
            language = lang_match.group(1)

    # 提取内容
    pre = el.find("pre") if el.name != "pre" else el
    code = el.find("code")

    if code:
        # 检查 code 元素的 class 获取语言
        if not language:
            code_cls = " ".join(code.get("class", []))
            lang_match = re.search(r"language-(\w+)", code_cls)
            if lang_match:
                language = lang_match.group(1)
        content = code.get_text()
    elif pre:
        content = pre.get_text()
    else:
        content = el.get_text()

    return {"type": "code_block", "language": language, "content": content}


def _is_panel(el: Tag) -> bool:
    """判断元素是否为 Confluence 面板/信息宏。"""
    cls = " ".join(el.get("class", []))
    panel_classes = [
        "confluence-information-macro",
        "panel",
        "aui-message",
    ]
    return any(pc in cls for pc in panel_classes)


def _parse_panel(el: Tag) -> dict[str, Any]:
    """解析 Confluence 面板（info/warning/note/tip）。"""
    cls = " ".join(el.get("class", []))

    # 判断面板类型
    panel_type = "info"
    if "confluence-information-macro-note" in cls or "aui-message-error" in cls:
        panel_type = "note"
    elif "confluence-information-macro-warning" in cls or "aui-message-warning" in cls:
        panel_type = "warning"
    elif "confluence-information-macro-tip" in cls or "aui-message-success" in cls:
        panel_type = "tip"
    elif "confluence-information-macro-information" in cls or "aui-message-info" in cls:
        panel_type = "info"

    # 提取标题
    title = ""
    title_el = el.find(
        class_=re.compile(r"(title|panel-header|macro-default-parameter)")
    )
    if title_el:
        title = title_el.get_text(strip=True)

    # 提取内容
    body_el = el.find(
        class_=re.compile(r"(confluence-information-macro-body|panelContent|panel-body)")
    )
    if body_el:
        content = body_el.get_text(separator=" ", strip=True)
    else:
        content = el.get_text(separator=" ", strip=True)

    return {
        "type": "panel",
        "panel_type": panel_type,
        "title": title,
        "content": content,
    }


def _parse_list(el: Tag) -> dict[str, Any]:
    """解析有序/无序列表。"""
    ordered = el.name == "ol"
    items = _extract_list_items(el)
    return {"type": "list", "ordered": ordered, "items": items}


def _extract_list_items(el: Tag) -> list[str | dict]:
    """递归提取列表项文本。"""
    items: list[str | dict] = []
    for li in el.find_all("li", recursive=False):
        # 检查是否有嵌套列表
        nested = li.find(["ul", "ol"])
        if nested:
            # 获取 li 的直接文本（不含嵌套列表）
            text_parts = []
            for child in li.children:
                if isinstance(child, NavigableString):
                    t = child.strip()
                    if t:
                        text_parts.append(t)
                elif isinstance(child, Tag) and child.name not in ("ul", "ol"):
                    t = child.get_text(separator=" ", strip=True)
                    if t:
                        text_parts.append(t)
            text = " ".join(text_parts)
            items.append(text if text else li.get_text(separator=" ", strip=True))
        else:
            text = li.get_text(separator=" ", strip=True)
            if text:
                items.append(text)
    return items


def _parse_container(el: Tag) -> list[dict[str, Any]] | None:
    """递归解析容器元素（div/section 等）的子元素。"""
    blocks: list[dict[str, Any]] = []
    for child in el.children:
        if isinstance(child, NavigableString):
            text = child.strip()
            if text:
                blocks.append({"type": "paragraph", "text": text})
            continue
        if not isinstance(child, Tag):
            continue
        parsed = _parse_element(child)
        if parsed is not None:
            if isinstance(parsed, list):
                blocks.extend(parsed)
            else:
                blocks.append(parsed)

    return blocks if blocks else None


# ── Markdown 渲染 ──


_PANEL_LABEL = {
    "info": "INFO",
    "note": "NOTE",
    "warning": "WARNING",
    "tip": "TIP",
}

_INLINE_IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def _encode_inline_image_urls(text: str) -> str:
    """对文本中所有 ``![alt](url)`` 内嵌图片做 URL 编码。

    用于表格单元格等场景：单元格内容是字符串，里面可能含原始（未编码）
    的 ``![alt](raw_path)``。CommonMark 要求 image URL 不能含裸空格。
    """
    def repl(m: re.Match) -> str:
        alt = m.group(1)
        src = m.group(2)
        encoded = quote(src, safe="/:?&=#%~+")
        return f"![{alt}]({encoded})"

    return _INLINE_IMG_RE.sub(repl, text)


def blocks_to_markdown(
    blocks: list[dict[str, Any]],
    page_title: str = "",
    page_url: str = "",
    last_modified: str = "",
) -> str:
    """将 :func:`parse_confluence_html` 产出的内容块渲染为 Markdown 文本。

    Parameters
    ----------
    blocks : list[dict]
        结构化内容块列表（由 ``parse_confluence_html`` 产出）。
    page_title : str
        页面标题，作为 H1 写在文档开头。
    page_url : str
        Confluence 页面原始 URL，作为元信息写在标题下方。
    last_modified : str
        页面最后修改时间，作为元信息写在标题下方。

    Returns
    -------
    str
        Markdown 文本，UTF-8 编码安全，行尾 ``\\n``。
    """
    lines: list[str] = []

    if page_title:
        lines.append(f"# {page_title}")
        lines.append("")
        meta_parts: list[str] = []
        if page_url:
            meta_parts.append(f"Source: {page_url}")
        if last_modified:
            meta_parts.append(f"Last modified: {last_modified}")
        if meta_parts:
            for m in meta_parts:
                lines.append(f"> {m}")
            lines.append("")
        lines.append("---")
        lines.append("")

    for block in blocks:
        btype = block.get("type", "")

        if btype == "heading":
            level = max(1, min(6, int(block.get("level", 1))))
            # 正文 heading 整体下降一级，避免和 page_title 的 H1 冲突
            level = min(6, level + 1) if page_title else level
            lines.append("#" * level + " " + (block.get("text") or "").strip())
            lines.append("")

        elif btype == "paragraph":
            text = (block.get("text") or "").strip()
            if text:
                lines.append(text)
                lines.append("")

        elif btype == "image":
            alt = (block.get("alt") or "").strip()
            src = block.get("local_path") or block.get("src") or ""
            if src:
                # CommonMark 不允许 image URL 中出现空格，必须 URL 编码。
                # safe 保留 URL 中的语法字符，避免对已编码的远程 URL 双重编码。
                encoded = quote(src, safe="/:?&=#%~+")
                lines.append(f"![{alt}]({encoded})")
                lines.append("")

        elif btype == "table":
            headers = [
                _encode_inline_image_urls(str(h)).replace("|", "\\|")
                for h in block.get("headers") or []
            ]
            rows = block.get("rows") or []
            if headers:
                lines.append("| " + " | ".join(headers) + " |")
                lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
            elif rows:
                width = max(len(r) for r in rows)
                lines.append("| " + " | ".join([" "] * width) + " |")
                lines.append("| " + " | ".join(["---"] * width) + " |")
            for row in rows:
                cells = [
                    _encode_inline_image_urls(str(c))
                    .replace("|", "\\|").replace("\n", " ").strip()
                    for c in row
                ]
                lines.append("| " + " | ".join(cells) + " |")
            lines.append("")

        elif btype == "code_block":
            language = (block.get("language") or "").strip()
            content = (block.get("content") or "").rstrip()
            lines.append(f"```{language}")
            lines.append(content)
            lines.append("```")
            lines.append("")

        elif btype == "panel":
            ptype = block.get("panel_type", "info")
            label = _PANEL_LABEL.get(ptype, ptype.upper() or "INFO")
            title = (block.get("title") or "").strip()
            content = (block.get("content") or "").strip()
            if title:
                lines.append(f"> **{label}: {title}**")
            else:
                lines.append(f"> **{label}**")
            if content:
                for ln in content.splitlines():
                    lines.append(f"> {ln}")
            lines.append("")

        elif btype == "list":
            ordered = bool(block.get("ordered"))
            for idx, item in enumerate(block.get("items") or [], start=1):
                text = item.get("text", "") if isinstance(item, dict) else str(item)
                marker = f"{idx}." if ordered else "-"
                lines.append(f"{marker} {text}")
            lines.append("")

        else:
            # 未知类型，尽量保留文本内容，避免静默丢失
            text = (block.get("text") or block.get("content") or "").strip()
            if text:
                lines.append(text)
                lines.append("")

    md = "\n".join(lines).rstrip() + "\n"
    return md
