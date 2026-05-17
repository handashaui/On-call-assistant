from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.schemas.document import SearchResponse
from app.services.semantic_search import search as semantic_search
from app.storage.document_store import document_store


router = APIRouter(prefix="/v2", tags=["v2"])
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


@router.get("/search", response_model=SearchResponse)
def search_documents(q: str = Query("", description="Semantic search query")) -> SearchResponse:
    results = semantic_search(q, document_store.all())
    return SearchResponse(query=q, results=results)


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("v2.html", {"request": request})
