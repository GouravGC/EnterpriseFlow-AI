
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


class SourceReference(BaseModel):
    filename: str
    page: int | None = None
    snippet: str


class AskResponse(BaseModel):
    answer: str
    status: str = "success"
    sources: list[SourceReference] = Field(default_factory=list)


class DocumentUploadResponse(BaseModel):
    filename: str
    chunks_indexed: int
    total_chunks: int
    status: str = "success"
