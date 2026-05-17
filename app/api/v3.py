from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.schemas.document import ChatRequest, ChatResponse
from app.services.agent import chat


router = APIRouter(prefix="/v3", tags=["v3"])
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


@router.post("/chat", response_model=ChatResponse)
def chat_with_agent(payload: ChatRequest) -> ChatResponse:
    answer, tool_calls = chat(payload.message)
    return ChatResponse(answer=answer, tool_calls=tool_calls)


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("v3.html", {"request": request})
