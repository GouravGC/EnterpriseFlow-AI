
FROM python:3.11.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV CHROMA_PATH=/app/data/chroma

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY config.py main.py schemas.py ai_service.py ./
COPY rag ./rag

RUN useradd --create-home appuser \
    && mkdir -p /app/data/chroma \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
