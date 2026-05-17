from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api import v1, v2, v3
from app.core.config import settings
from app.services.semantic_search import build_index
from app.storage.document_store import document_store
from app.storage.document_store import load_documents_from_directory


def initialize_data_and_indexes() -> None:
    load_documents_from_directory()
    build_index(document_store.all())


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_data_and_indexes()
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
app.include_router(v1.router)
app.include_router(v2.router)
app.include_router(v3.router)

initialize_data_and_indexes()


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/v1")
