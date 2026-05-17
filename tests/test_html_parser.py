from pathlib import Path

from app.services.html_parser import parse_html_document
from app.services.keyword_search import search


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def test_parser_extracts_structured_sop_sections():
    html = (DATA_DIR / "sop-001.html").read_text(encoding="utf-8")
    document = parse_html_document("sop-001", html, filename="sop-001.html")

    assert document.title == "后端服务 On-Call SOP"
    assert document.h1 == "后端服务 On-Call SOP"
    assert "适用范围：后端服务团队全体值班人员" in document.metadata_text
    assert "三、常见故障处理" in document.h2_headings
    assert "场景二：单服务OOM崩溃" in document.h3_headings
    assert any(section.heading == "场景二：单服务OOM崩溃" for section in document.sections)
    assert "Java服务出现OutOfMemoryError" in document.body
    assert "场景二：单服务OOM崩溃" in document.text


def test_parser_removes_script_content_from_structured_text():
    html = (DATA_DIR / "sop-002.html").read_text(encoding="utf-8")
    document = parse_html_document("sop-002", html, filename="sop-002.html")

    assert "replicationLag" not in document.text
    assert "checkDatabaseHealth" not in document.body
    assert "主从延迟超过十秒" in document.body


def test_keyword_snippet_prefers_matching_section_and_highlights_query():
    html = (DATA_DIR / "sop-001.html").read_text(encoding="utf-8")
    document = parse_html_document("sop-001", html, filename="sop-001.html")

    result = search("OOM", [document])[0]

    assert "场景二：单服务<mark>OOM</mark>崩溃" in result.snippet
    assert "OutOfMemoryError" in result.snippet
