import re
from dataclasses import dataclass

from app.schemas.document import Document, SearchResult
from app.services.chunker import DocumentChunk
from app.services.document_profiles import profile_for
from app.services.html_parser import normalize_text
from app.services.snippets import highlighted_snippet, highlight_terms


SEMANTIC_WEIGHT = 0.7
KEYWORD_WEIGHT = 0.3


@dataclass(frozen=True)
class ChunkScore:
    chunk: DocumentChunk
    semantic_score: float
    keyword_score: float
    final_score: float


def score_chunks(query: str, semantic_hits: list[tuple[DocumentChunk, float]]) -> list[ChunkScore]:
    scored: list[ChunkScore] = []
    for chunk, semantic_score in semantic_hits:
        semantic = max(0.0, min(semantic_score, 1.0))
        keyword = keyword_score(query, f"{chunk.title} {chunk.heading} {chunk.text} {profile_for(chunk.doc_id)}")
        final = SEMANTIC_WEIGHT * semantic + KEYWORD_WEIGHT * keyword
        scored.append(
            ChunkScore(
                chunk=chunk,
                semantic_score=semantic,
                keyword_score=keyword,
                final_score=final,
            )
        )
    return sorted(scored, key=lambda item: (-item.final_score, item.chunk.doc_id, item.chunk.id))


def aggregate_document_results(
    query: str,
    chunk_scores: list[ChunkScore],
    documents: list[Document],
    limit: int = 10,
) -> list[SearchResult]:
    documents_by_id = {document.id: document for document in documents}
    best_by_doc: dict[str, ChunkScore] = {}

    for chunk_score in chunk_scores:
        doc_id = chunk_score.chunk.doc_id
        current = best_by_doc.get(doc_id)
        if current is None or chunk_score.final_score > current.final_score:
            best_by_doc[doc_id] = chunk_score

    results: list[SearchResult] = []
    for doc_id, chunk_score in best_by_doc.items():
        document = documents_by_id.get(doc_id)
        if document is None:
            continue
        results.append(
            SearchResult(
                id=document.id,
                title=document.title,
                snippet=make_snippet(chunk_score.chunk, query),
                score=round(chunk_score.final_score, 4),
            )
        )

    return sorted(results, key=lambda item: (-item.score, item.id))[:limit]


def keyword_score(query: str, text: str) -> float:
    query = normalize_text(query)
    if not query:
        return 0.0

    text_lower = text.lower()
    query_lower = query.lower()
    exact_phrase = 1.0 if query_lower in text_lower else 0.0

    raw_terms = _keyword_terms(query)
    matched_terms = sum(1 for term in raw_terms if term.lower() in text_lower)
    term_score = matched_terms / max(len(raw_terms), 1)

    acronym_terms = re.findall(r"[A-Za-z0-9+#.-]{2,}", query)
    acronym_score = 0.0
    if acronym_terms:
        acronym_matches = sum(1 for term in acronym_terms if term.lower() in text_lower)
        acronym_score = acronym_matches / len(acronym_terms)

    return min(1.0, 0.45 * exact_phrase + 0.4 * term_score + 0.15 * acronym_score)


def make_snippet(chunk: DocumentChunk, query: str) -> str:
    content = highlighted_snippet(chunk.text, query, radius=90)
    if not chunk.heading:
        return content
    return f"{highlight_terms(chunk.heading, query)}：{content}"


def _keyword_terms(query: str) -> list[str]:
    ascii_terms = re.findall(r"[A-Za-z0-9+#.-]+", query)
    chinese_terms = re.findall(r"[\u4e00-\u9fff]{2,}", query)
    chinese_bigrams = [
        term[index : index + 2]
        for term in chinese_terms
        for index in range(max(len(term) - 1, 0))
    ]
    return list(dict.fromkeys(ascii_terms + chinese_terms + chinese_bigrams))
