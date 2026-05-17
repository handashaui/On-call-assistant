import re
from pathlib import Path

from app.core.config import settings
from app.schemas.document import ToolCall
from app.services.html_parser import parse_html_document
from app.services.semantic_search import search as semantic_search
from app.storage.document_store import document_store


def read_file(fname: str) -> str:
    if Path(fname).name != fname or not fname.endswith(".html"):
        raise ValueError("readFile only accepts a data/ HTML filename")

    path = (settings.DATA_DIR / fname).resolve()
    data_dir = settings.DATA_DIR.resolve()
    if data_dir not in path.parents:
        raise ValueError("readFile path is outside data/")
    if not path.exists():
        raise FileNotFoundError(fname)
    return path.read_text(encoding="utf-8")


def _preferred_files(message: str) -> list[str]:
    rules: list[tuple[list[str], list[str]]] = [
        (["主从", "复制", "数据库", "慢查询", "连接池"], ["sop-002.html"]),
        (["oom", "outofmemory", "服务 oom", "服务oom"], ["sop-001.html"]),
        (["入侵", "黑客", "安全", "漏洞", "攻击", "数据泄露"], ["sop-005.html"]),
        (["推荐", "模型", "机器学习", "算法", "gpu", "质量下降"], ["sop-008.html"]),
        (["p0", "响应流程", "升级流程"], ["sop-001.html", "sop-004.html", "sop-005.html", "sop-010.html"]),
        (["cdn", "dns", "网络"], ["sop-010.html", "sop-003.html"]),
    ]
    lowered = message.lower()
    selected: list[str] = []
    for keywords, files in rules:
        if any(keyword.lower() in lowered for keyword in keywords):
            selected.extend(files)
    return list(dict.fromkeys(selected))


def _semantic_files(message: str, limit: int = 2) -> list[str]:
    results = semantic_search(message, document_store.all(), limit=limit)
    files: list[str] = []
    for result in results:
        document = document_store.get(result.id)
        if document and document.filename:
            files.append(document.filename)
    return files


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？])\s*", text)
    return [part.strip() for part in parts if part.strip()]


def _document_blocks(html: str) -> list[str]:
    parsed = parse_html_document("unknown", html)
    blocks = [f"{section.heading} {section.content}" for section in parsed.sections]
    if blocks:
        return blocks
    return _split_sentences(parsed.text)


def _query_terms(message: str) -> list[str]:
    known_terms = [
        "OOM",
        "OutOfMemoryError",
        "主从",
        "复制",
        "延迟",
        "数据库",
        "P0",
        "升级",
        "响应",
        "入侵",
        "安全",
        "攻击",
        "推荐",
        "质量下降",
        "模型",
        "CDN",
        "DNS",
    ]
    terms = [term for term in known_terms if term.lower() in message.lower()]
    terms.extend(re.findall(r"[A-Za-z0-9+#.-]{2,}", message))
    terms.extend(re.findall(r"[\u4e00-\u9fff]{2,}", message))
    return list(dict.fromkeys(terms))


def _answer_from_documents(message: str, docs: list[tuple[str, str]]) -> str:
    query_terms = _query_terms(message)
    focus_words = [
        "首先",
        "立即",
        "检查",
        "确认",
        "升级",
        "回滚",
        "隔离",
        "通知",
        "监控",
        "恢复",
        "处理",
    ]
    selected: list[str] = []
    wants_handling_steps = any(word in message for word in ["怎么处理", "怎么办", "如何处理", "排查", "处理"])
    for _, html in docs:
        blocks = _document_blocks(html)
        ranked = []
        for block in blocks:
            score = sum(4 for term in query_terms if term.lower() in block.lower())
            score += sum(1 for word in focus_words if word in block)
            if wants_handling_steps and ("常见故障处理" in block or "场景" in block):
                score += 10
            if score > 0:
                ranked.append((score, block))
        ranked.sort(key=lambda item: -item[0])
        selected.extend(block for _, block in ranked[:3])

    if not selected:
        selected = [parse_html_document(Path(fname).stem, html).text[:220] for fname, html in docs]

    unique_steps = list(dict.fromkeys(selected))[:8]
    source_names = "、".join(fname for fname, _ in docs)
    lines = [f"参考 {source_names}，建议按下面顺序处理："]
    for index, step in enumerate(unique_steps, start=1):
        lines.append(f"{index}. {step}")
    return "\n".join(lines)


def chat(message: str) -> tuple[str, list[ToolCall]]:
    files = _preferred_files(message)
    if not files:
        files = _semantic_files(message)
    files = files[:4]

    docs: list[tuple[str, str]] = []
    tool_calls: list[ToolCall] = []
    for fname in files:
        html = read_file(fname)
        docs.append((fname, html))
        preview = parse_html_document(Path(fname).stem, html, filename=fname).text[:180]
        tool_calls.append(
            ToolCall(
                name="readFile",
                arguments={"fname": fname},
                result_preview=preview,
            )
        )

    if not docs:
        return "暂时没有定位到相关 SOP。请补充故障现象、涉及系统或关键告警关键词。", tool_calls

    return _answer_from_documents(message, docs), tool_calls
