
# EnterpriseFlow AI — Enterprise Operations Copilot

An AI-powered enterprise operations assistant built with Python, FastAPI,
Pydantic, OpenRouter, and a production-oriented development workflow.

## Current Features

- REST API with FastAPI
- Request and response validation using Pydantic
- Health-check endpoint
- OpenRouter integration through an OpenAI-compatible client
- Configurable environment-based settings
- Timeout and provider-error handling
- Automated API tests using pytest and HTTPX
- Docker packaging
- GitHub Actions CI workflow

## Planned Features

- Document ingestion and parsing
- Retrieval-Augmented Generation (RAG)
- Answers grounded in uploaded enterprise documents
- Source citations and evidence tracking
- Structured operational action plans
- PostgreSQL persistence
- Redis caching and Celery background jobs
- LangSmith tracing and LLM evaluation
- Google Cloud Run deployment
- Cloud Logging and Secret Manager integration

## Architecture

The current application is a modular Python API.

- `main.py`: FastAPI routes and application lifecycle
- `config.py`: Application settings
- `schemas.py`: Pydantic request and response schemas
- `ai_service.py`: OpenRouter client and inference logic
- `test_api.py`: API tests

See `docs/architecture.md` for the development architecture.

## Requirements

- Python 3.11.10
- pip
- An OpenRouter API key and supported model ID for live AI inference

## Local Setup

Create and activate a Conda environment:

```bash
conda create -n techolution python=3.11.10 -y
conda activate techolution
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
python -m pip check
```

Create a local `.env` file using `.env.example` as a template.
Set `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` for live inference.

Run tests:

```bash
python -m pytest -v test_api.py
```

Start the development server:

```bash
python -m uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive API documentation.

## Docker

Build the image:

```bash
docker build -t enterpriseflow-ai .
```

Run the container:

```bash
docker run --rm -p 8080:8080 --env-file .env enterpriseflow-ai
```

Open `http://127.0.0.1:8080/docs`.

## Security

- Never commit `.env` or API credentials.
- Use GitHub Actions secrets and Google Cloud Secret Manager for deployment credentials.
- Grant cloud identities only the permissions they require.

## Project Status

Development in progress. Planned capabilities will be documented as they
are implemented and verified.
