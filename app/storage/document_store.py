from pathlib import Path

from app.core.config import settings
from app.schemas.document import Document
from app.services.html_parser import parse_html_document


class DocumentStore:
    def __init__(self) -> None:
        self._documents: dict[str, Document] = {}

    def add(self, document: Document) -> Document:
        self._documents[document.id] = document
        return document

    def get(self, doc_id: str) -> Document | None:
        return self._documents.get(doc_id)

    def get_by_filename(self, filename: str) -> Document | None:
        for document in self._documents.values():
            if document.filename == filename:
                return document
        return None

    def all(self) -> list[Document]:
        return [self._documents[key] for key in sorted(self._documents)]

    def clear(self) -> None:
        self._documents.clear()

    def __len__(self) -> int:
        return len(self._documents)


document_store = DocumentStore()


def document_id_from_path(path: Path) -> str:
    return path.stem


def load_documents_from_directory(data_dir: Path = settings.DATA_DIR) -> int:
    if not data_dir.exists():
        return 0

    loaded = 0
    for path in sorted(data_dir.glob("*.html")):
        html = path.read_text(encoding="utf-8")
        document = parse_html_document(document_id_from_path(path), html, filename=path.name)
        document_store.add(document)
        loaded += 1
    return loaded
