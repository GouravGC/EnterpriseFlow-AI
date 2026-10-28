
import hashlib
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from redis.asyncio import Redis

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
CACHE_VERSION_KEY = "enterpriseflow:knowledge_base_version"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ai_service = None
    app.state.rag_service = RAGService()
    app.state.redis = None

    if settings.openrouter_api_key and settings.openrouter_model:
        try:
            app.state.ai_service = AIService()
            logger.info("OpenRouter AI service initialized.")
        except Exception:
            logger.exception("Failed to initialize AI service.")

    # Redis is optional. The API continues without it.
    if settings.cache_enabled and settings.redis_url:
        redis_client = None

        try:
            redis_client = Redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )

            await redis_client.ping()
            app.state.redis = redis_client
            logger.info("Redis cache connected.")

        except Exception:
            logger.warning(
                "Redis unavailable. Running without caching.",
                exc_info=True,
            )

            if redis_client:
                try:
                    await redis_client.aclose()
                except Exception:
                    logger.warning("Redis cleanup failed.")

    logger.info("EnterpriseFlow AI startup complete.")

    yield

    if app.state.redis:
        try:
            await app.state.redis.aclose()
            logger.info("Redis connection closed.")
        except Exception:
            logger.warning("Redis shutdown failed.")

    logger.info("EnterpriseFlow AI shutting down.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Enterprise operations copilot with document retrieval, "
        "OpenRouter embeddings, and LLM inference."
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
            "embedding_provider": "OpenRouter",
            "embedding_model": settings.openrouter_embedding_model,
            "vector_database": "ChromaDB",
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
async def upload_document(file: UploadFile = File(...)):
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

        # Version-based invalidation: old answer keys become unreachable.
        redis_client = getattr(app.state, "redis", None)

        if redis_client:
            try:
                await redis_client.incr(CACHE_VERSION_KEY)
                logger.info("Knowledge-base cache version updated.")
            except Exception:
                logger.warning(
                    "Cache version update failed.",
                    exc_info=True,
                )

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
        # Retrieve relevant document chunks.
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

        redis_client = getattr(app.state, "redis", None)

        # Include knowledge-base version in the cache key.
        knowledge_version = "0"

        if redis_client:
            try:
                knowledge_version = (
                    await redis_client.get(CACHE_VERSION_KEY) or "0"
                )
            except Exception:
                logger.warning("Redis version lookup failed.")

        normalized_question = request.question.strip().casefold()

        cache_material = (
            f"{knowledge_version}\0"
            f"{normalized_question}\0"
            f"{context}"
        )

        cache_key = (
            "enterpriseflow:answer:"
            + hashlib.sha256(
                cache_material.encode("utf-8")
            ).hexdigest()
        )

        # Try cache before calling the LLM.
        if redis_client:
            try:
                cached = await redis_client.get(cache_key)

                if cached:
                    logger.info("Answer cache hit.")

                    return AskResponse.model_validate_json(cached)

            except Exception:
                logger.warning(
                    "Redis read failed. Bypassing cache.",
                    exc_info=True,
                )

        # Generate answer through OpenRouter.
        answer = await ai_service.answer(
            question=request.question,
            context=context,
        )

        result = AskResponse(
            answer=answer,
            status="success",
            sources=sources,
        )

        # Cache successful responses.
        if redis_client:
            try:
                await redis_client.setex(
                    cache_key,
                    settings.cache_ttl_seconds,
                    result.model_dump_json(),
                )

                logger.info("Answer cached successfully.")

            except Exception:
                logger.warning(
                    "Redis write failed. Returning uncached answer.",
                    exc_info=True,
                )

        return result

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
                "Check API logs."
            ),
        ) from exc
