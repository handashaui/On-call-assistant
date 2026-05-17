from app.schemas.document import Document, SearchResult
from app.services.html_parser import normalize_text
from app.services.snippets import highlighted_snippet, highlight_terms


def _count_term(text: str, query: str) -> int:
    if not query:
        return 0
    return text.lower().count(query.lower())


def _joined(values: list[str]) -> str:
    return " ".join(values)


def _make_snippet(document: Document, query: str) -> str:
    for section in document.sections:
        heading_hits = _count_term(section.heading, query)
        content_hits = _count_term(section.content, query)
        if heading_hits or content_hits:
            heading = highlight_terms(section.heading, query)
            content = (
                highlight_terms(section.content[:160].strip(), query)
                if heading_hits
                else highlighted_snippet(section.content, query)
            )
            return f"{heading}：{content}" if content else heading

    if _count_term(document.body, query):
        return highlighted_snippet(document.body, query)

    return highlighted_snippet(document.text, query)


def search(query: str, documents: list[Document], limit: int = 10) -> list[SearchResult]:
    query = normalize_text(query)
    if not query:
        return []

    results: list[SearchResult] = []
    for document in documents:
        title_hits = _count_term(document.title, query)
        h1_hits = _count_term(document.h1 or "", query)
        h2_hits = _count_term(_joined(document.h2_headings), query)
        h3_hits = _count_term(_joined(document.h3_headings), query)
        body_hits = _count_term(document.body, query)
        metadata_hits = _count_term(document.metadata_text, query)
        score = (
            title_hits * 5.0
            + h1_hits * 5.0
            + h3_hits * 4.0
            + h2_hits * 3.0
            + body_hits * 1.0
            + metadata_hits * 0.5
        )
        if score <= 0:
            continue

        results.append(
            SearchResult(
                id=document.id,
                title=document.title,
                snippet=_make_snippet(document, query),
                score=score,
            )
        )

    return sorted(results, key=lambda item: (-item.score, item.id))[:limit]
