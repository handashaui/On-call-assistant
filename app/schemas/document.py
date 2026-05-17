from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    id: str = Field(..., min_length=1)
    html: str = Field(..., min_length=1)


class DocumentResponse(BaseModel):
    id: str
    title: str


class Section(BaseModel):
    heading: str
    level: int
    content: str


class Document(BaseModel):
    id: str
    title: str
    h1: str | None = None
    metadata_text: str = ""
    h2_headings: list[str] = Field(default_factory=list)
    h3_headings: list[str] = Field(default_factory=list)
    sections: list[Section] = Field(default_factory=list)
    body: str = ""
    text: str
    html: str
    filename: str | None = None


class SearchResult(BaseModel):
    id: str
    title: str
    snippet: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, str]
    result_preview: str


class ChatResponse(BaseModel):
    answer: str
    tool_calls: list[ToolCall]
