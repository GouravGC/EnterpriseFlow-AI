
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status

from ai_service import AIService, AIServiceError
from config import settings
from schemas import HealthResponse, AskRequest, AskResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ai_service = None

    if settings.openrouter_api_key and settings.openrouter_model:
        app.state.ai_service = AIService()

    yield

    if app.state.ai_service is not None:
        await app.state.ai_service.close()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Enterprise operations copilot API",
    lifespan=lifespan,
)


@app.get("/", tags=["General"])
def root():
    return {
        "message": "EnterpriseFlow AI API is running",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
def health():
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
    )


@app.post("/ask", response_model=AskResponse, tags=["AI"])
async def ask(request: AskRequest):
    ai_service = app.state.ai_service

    if ai_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not configured.",
        )

    try:
        answer = await ai_service.answer(request.question)
        return AskResponse(answer=answer)
    except AIServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
