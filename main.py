
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile

from ai_service import AIService, AIServiceError
from config import settings
from rag.service import RAGService
from schemas import (
    AskRequest,
    AskResponse,
    DocumentUploadResponse,
    HealthResponse,
    SourceReference,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_UPLOAD_SIZE = 10 * 1024 * 1024


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ai_service = None
    app.state.rag_service = RAGService()

    if settings.openrouter_api_key and settings.openrouter_model:
        try:
            app.state.ai_service = AIService()
            logger.info("OpenRouter AI service initialized.")
        except Exception:
            logger.exception("Failed to initialize AI service.")

    logger.info("EnterpriseFlow AI startup complete.")

    yield

    logger.info("EnterpriseFlow AI shutting down.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Enterprise operations copilot with document retrieval, "
        "Hugging Face hosted embeddings, and OpenRouter inference."
    ),
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
    )


@app.get("/documents/status")
async def document_status():
    try:
        count = app.state.rag_service.chunk_count()
        return {
            "status": "ready",
            "indexed_chunks": count,
            "embedding_provider": "Hugging Face Inference API",
            "embedding_model": settings.hf_embedding_model,
        }
    except Exception as exc:
        logger.exception("Failed to retrieve document index status.")
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve document index status.",
        ) from exc


@app.post(
    "/documents",
    response_model=DocumentUploadResponse,
)
async def upload_document(
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 10 MB upload limit.",
        )

    try:
        chunks_indexed = app.state.rag_service.add_document(
            filename=file.filename,
            content=content,
        )

        total_chunks = app.state.rag_service.chunk_count()

        logger.info(
            "Indexed file '%s': %s new chunks.",
            file.filename,
            chunks_indexed,
        )

        return DocumentUploadResponse(
            filename=file.filename,
            chunks_indexed=chunks_indexed,
            total_chunks=total_chunks,
            status="indexed",
        )

    except ValueError as exc:
        logger.warning(
            "Document validation failed for '%s': %s",
            file.filename,
            exc,
        )
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Document indexing failed for file: %s",
            file.filename,
        )
        raise HTTPException(
            status_code=500,
            detail=(
                "Document indexing failed. "
                "Check the API terminal logs."
            ),
        ) from exc

    finally:
        await file.close()


@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    ai_service = app.state.ai_service

    if ai_service is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "AI service is not configured. Set OPENROUTER_API_KEY "
                "and OPENROUTER_MODEL in your environment."
            ),
        )

    try:
        retrieved = app.state.rag_service.retrieve(
            question=request.question,
            top_k=4,
        )

        context_parts = []
        sources = []

        for item in retrieved:
            source = item.get("source", "Unknown document")
            page = item.get("page")
            snippet = item.get("text", "")

            page_label = (
                f", page {page}"
                if page is not None
                else ""
            )

            context_parts.append(
                f"[Source: {source}{page_label}]\n{snippet}"
            )

            sources.append(
                SourceReference(
                    filename=source,
                    page=page,
                    snippet=snippet[:300],
                )
            )

        context = "\n\n".join(context_parts)

        answer = await ai_service.answer(
            question=request.question,
            context=context,
        )

        return AskResponse(
            answer=answer,
            status="success",
            sources=sources,
        )

    except AIServiceError as exc:
        logger.exception("OpenRouter answer generation failed.")
        raise HTTPException(
            status_code=502,
            detail="The AI provider could not generate an answer.",
        ) from exc

    except Exception as exc:
        logger.exception("Question-answering request failed.")
        raise HTTPException(
            status_code=500,
            detail=(
                "Question answering failed. "
                "Check the API terminal logs."
            ),
        ) from exc
