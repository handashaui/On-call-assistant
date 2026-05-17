from dataclasses import dataclass

from app.schemas.document import Document, SearchResult
from app.services.chunker import DocumentChunk, chunk_documents
from app.services.document_profiles import profile_for
from app.services.embeddings import EmbeddingModel, cosine_similarity
from app.services.hybrid_search import aggregate_document_results, score_chunks
from app.services.html_parser import normalize_text


@dataclass
class SemanticIndex:
    documents_key: tuple[tuple[str, int], ...] = ()
    chunks: list[DocumentChunk] | None = None
    embeddings: list[list[float]] | None = None
    embedder: EmbeddingModel | None = None

    def build(self, documents: list[Document]) -> None:
        self.documents_key = _documents_key(documents)
        self.chunks = chunk_documents(documents)
        self.embedder = EmbeddingModel()
        self.embeddings = self.embedder.embed_documents(_embedding_text(chunk) for chunk in self.chunks)

    def ready_for(self, documents: list[Document]) -> bool:
        return (
            self.chunks is not None
            and self.embeddings is not None
            and self.embedder is not None
            and self.documents_key == _documents_key(documents)
        )

    def search_chunks(self, query: str) -> list[tuple[DocumentChunk, float]]:
        if self.chunks is None or self.embeddings is None or self.embedder is None:
            return []

        query_embedding = self.embedder.embed_query(query)
        hits = [
            (chunk, cosine_similarity(query_embedding, embedding))
            for chunk, embedding in zip(self.chunks, self.embeddings)
        ]
        return sorted(hits, key=lambda item: (-item[1], item[0].doc_id, item[0].id))


_index = SemanticIndex()


def build_index(documents: list[Document]) -> None:
    _index.build(documents)


def search(query: str, documents: list[Document], limit: int = 10) -> list[SearchResult]:
    query = normalize_text(query)
    if not query:
        return []

    if not _index.ready_for(documents):
        build_index(documents)

    semantic_hits = _index.search_chunks(query)
    chunk_scores = score_chunks(query, semantic_hits)
    return aggregate_document_results(query, chunk_scores, documents, limit=limit)


def index_backend() -> str:
    if _index.embedder is None:
        return "not-built"
    return _index.embedder.backend


def _documents_key(documents: list[Document]) -> tuple[tuple[str, int], ...]:
    return tuple((document.id, len(document.text)) for document in documents)


def _embedding_text(chunk: DocumentChunk) -> str:
    return normalize_text(f"{chunk.title} {chunk.heading} {chunk.text} {profile_for(chunk.doc_id)}")
