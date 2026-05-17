from dataclasses import dataclass

from app.schemas.document import Document
from app.services.html_parser import normalize_text


CHUNK_SIZE = 400
CHUNK_OVERLAP = 80


@dataclass(frozen=True)
class DocumentChunk:
    id: str
    doc_id: str
    title: str
    text: str
    heading: str = ""


def chunk_documents(
    documents: list[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for document in documents:
        chunks.extend(chunk_document(document, chunk_size=chunk_size, chunk_overlap=chunk_overlap))
    return chunks


def chunk_document(
    document: Document,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[DocumentChunk]:
    blocks = [(section.heading, section.content) for section in document.sections]
    if not blocks:
        blocks = [("", document.body or document.text)]

    chunks: list[DocumentChunk] = []
    current_parts: list[str] = []
    current_heading = ""

    def flush() -> None:
        nonlocal current_parts, current_heading
        text = normalize_text(" ".join(current_parts))
        if not text:
            current_parts = []
            return
        chunks.extend(
            _split_text_chunk(
                document=document,
                text=text,
                heading=current_heading,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                start_index=len(chunks),
            )
        )
        current_parts = []

    for heading, text in blocks:
        candidate = normalize_text(" ".join([*current_parts, text]))
        if current_parts and len(candidate) > chunk_size:
            flush()
        current_heading = heading or current_heading
        current_parts.append(text)

    flush()
    return chunks


def _split_text_chunk(
    document: Document,
    text: str,
    heading: str,
    chunk_size: int,
    chunk_overlap: int,
    start_index: int,
) -> list[DocumentChunk]:
    if len(text) <= chunk_size:
        return [
            DocumentChunk(
                id=f"{document.id}:{start_index}",
                doc_id=document.id,
                title=document.title,
                text=text,
                heading=heading,
            )
        ]

    chunks: list[DocumentChunk] = []
    step = max(chunk_size - chunk_overlap, 1)
    cursor = 0
    index = start_index
    while cursor < len(text):
        chunk_text = normalize_text(text[cursor : cursor + chunk_size])
        if chunk_text:
            chunks.append(
                DocumentChunk(
                    id=f"{document.id}:{index}",
                    doc_id=document.id,
                    title=document.title,
                    text=chunk_text,
                    heading=heading,
                )
            )
            index += 1
        cursor += step
    return chunks
