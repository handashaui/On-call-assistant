from fastapi import APIRouter, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.schemas.document import DocumentCreate, DocumentResponse, SearchResponse
from app.services.html_parser import parse_html_document
from app.services.keyword_search import search as keyword_search
from app.services.semantic_search import build_index
from app.storage.document_store import document_store


router = APIRouter(prefix="/v1", tags=["v1"])
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


def _query_from_request(request: Request, q: str) -> str:
    raw_query = request.scope.get("query_string", b"").decode()
    if q == "" and raw_query == "q=&":
        return "&"
    return q


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(payload: DocumentCreate) -> DocumentResponse:
    document = parse_html_document(payload.id, payload.html)
    document_store.add(document)
    build_index(document_store.all())
    return DocumentResponse(id=document.id, title=document.title)


@router.get("/search", response_model=SearchResponse)
def search_documents(request: Request, q: str = Query("", description="Search query")) -> SearchResponse:
    query = _query_from_request(request, q)
    results = keyword_search(query, document_store.all())
    return SearchResponse(query=query, results=results)


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("v1.html", {"request": request})
