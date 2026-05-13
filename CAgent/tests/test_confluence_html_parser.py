"""tests/test_confluence_html_parser.py — confluence_html_parser 单元测试"""
from __future__ import annotations

from services.confluence_html_parser import parse_confluence_html


class TestParseHeading:
    def test_h1(self):
        blocks = parse_confluence_html("<h1>标题一</h1>")
        assert len(blocks) == 1
        assert blocks[0] == {"type": "heading", "level": 1, "text": "标题一"}

    def test_h3(self):
        blocks = parse_confluence_html("<h3>三级标题</h3>")
        assert blocks[0]["level"] == 3


class TestParseParagraph:
    def test_simple(self):
        blocks = parse_confluence_html("<p>这是一段文字</p>")
        assert blocks == [{"type": "paragraph", "text": "这是一段文字"}]

    def test_empty_paragraph(self):
        blocks = parse_confluence_html("<p></p>")
        assert blocks == []

    def test_paragraph_with_inline(self):
        blocks = parse_confluence_html("<p>Hello <strong>world</strong></p>")
        assert blocks[0]["text"] == "Hello world"


class TestParseTable:
    def test_simple_table(self):
        html = """
        <table>
          <thead><tr><th>列1</th><th>列2</th></tr></thead>
          <tbody>
            <tr><td>A</td><td>B</td></tr>
            <tr><td>C</td><td>D</td></tr>
          </tbody>
        </table>
        """
        blocks = parse_confluence_html(html)
        assert len(blocks) == 1
        t = blocks[0]
        assert t["type"] == "table"
        assert t["headers"] == ["列1", "列2"]
        assert t["rows"] == [["A", "B"], ["C", "D"]]

    def test_table_th_first_row(self):
        """没有 thead，但第一行全是 th 的情况。"""
        html = """
        <table>
          <tr><th>Name</th><th>Age</th></tr>
          <tr><td>Alice</td><td>30</td></tr>
        </table>
        """
        blocks = parse_confluence_html(html)
        t = blocks[0]
        assert t["headers"] == ["Name", "Age"]
        assert t["rows"] == [["Alice", "30"]]

    def test_colspan(self):
        html = """
        <table>
          <tr><th>A</th><th>B</th><th>C</th></tr>
          <tr><td colspan="2">AB</td><td>C</td></tr>
        </table>
        """
        blocks = parse_confluence_html(html)
        t = blocks[0]
        assert t["rows"] == [["AB", "", "C"]]


class TestParseCodeBlock:
    def test_pre_tag(self):
        html = '<pre>print("hello")</pre>'
        blocks = parse_confluence_html(html)
        assert len(blocks) == 1
        assert blocks[0]["type"] == "code_block"
        assert blocks[0]["content"] == 'print("hello")'

    def test_code_with_language(self):
        html = '<pre class="language-python"><code>x = 1</code></pre>'
        blocks = parse_confluence_html(html)
        b = blocks[0]
        assert b["type"] == "code_block"
        assert b["language"] == "python"
        assert b["content"] == "x = 1"

    def test_syntaxhighlighter(self):
        html = """
        <div class="code panel syntaxhighlighter" data-syntaxhighlighter-params="brush: java;">
          <pre>int x = 0;</pre>
        </div>
        """
        blocks = parse_confluence_html(html)
        # 应找到一个 code_block
        code_blocks = [b for b in blocks if b["type"] == "code_block"]
        assert len(code_blocks) == 1
        assert code_blocks[0]["language"] == "java"
        assert "int x = 0;" in code_blocks[0]["content"]


class TestParsePanel:
    def test_info_panel(self):
        html = """
        <div class="confluence-information-macro confluence-information-macro-information">
          <div class="confluence-information-macro-body">
            <p>这是一条信息</p>
          </div>
        </div>
        """
        blocks = parse_confluence_html(html)
        assert len(blocks) == 1
        p = blocks[0]
        assert p["type"] == "panel"
        assert p["panel_type"] == "info"
        assert "这是一条信息" in p["content"]

    def test_warning_panel(self):
        html = """
        <div class="confluence-information-macro confluence-information-macro-warning">
          <div class="confluence-information-macro-body"><p>注意!</p></div>
        </div>
        """
        blocks = parse_confluence_html(html)
        assert blocks[0]["panel_type"] == "warning"

    def test_note_panel(self):
        html = """
        <div class="confluence-information-macro confluence-information-macro-note">
          <div class="confluence-information-macro-body"><p>备注</p></div>
        </div>
        """
        blocks = parse_confluence_html(html)
        assert blocks[0]["panel_type"] == "note"

    def test_tip_panel(self):
        html = """
        <div class="confluence-information-macro confluence-information-macro-tip">
          <div class="confluence-information-macro-body"><p>提示</p></div>
        </div>
        """
        blocks = parse_confluence_html(html)
        assert blocks[0]["panel_type"] == "tip"


class TestParseList:
    def test_unordered(self):
        html = "<ul><li>项1</li><li>项2</li></ul>"
        blocks = parse_confluence_html(html)
        assert len(blocks) == 1
        assert blocks[0] == {
            "type": "list",
            "ordered": False,
            "items": ["项1", "项2"],
        }

    def test_ordered(self):
        html = "<ol><li>步骤1</li><li>步骤2</li></ol>"
        blocks = parse_confluence_html(html)
        assert blocks[0]["ordered"] is True
        assert blocks[0]["items"] == ["步骤1", "步骤2"]


class TestParseImage:
    def test_img_in_paragraph(self):
        html = '<p><img src="/download/attachments/123/pic.png" alt="截图"></p>'
        blocks = parse_confluence_html(html)
        assert len(blocks) == 1
        assert blocks[0]["type"] == "image"
        assert blocks[0]["src"] == "/download/attachments/123/pic.png"
        assert blocks[0]["alt"] == "截图"

    def test_standalone_img(self):
        html = '<img src="/img.png" alt="test">'
        blocks = parse_confluence_html(html)
        assert blocks[0]["type"] == "image"


class TestMixedContent:
    def test_multiple_blocks(self):
        html = """
        <h1>标题</h1>
        <p>段落内容</p>
        <table><tr><th>A</th></tr><tr><td>1</td></tr></table>
        <ul><li>条目</li></ul>
        """
        blocks = parse_confluence_html(html)
        types = [b["type"] for b in blocks]
        assert "heading" in types
        assert "paragraph" in types
        assert "table" in types
        assert "list" in types

    def test_empty_html(self):
        assert parse_confluence_html("") == []
        assert parse_confluence_html("   ") == []

    def test_plain_text(self):
        blocks = parse_confluence_html("Hello world")
        assert len(blocks) == 1
        assert blocks[0] == {"type": "paragraph", "text": "Hello world"}
