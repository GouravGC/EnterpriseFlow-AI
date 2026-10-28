
# EnterpriseFlow AI Architecture

## Current Request Flow

1. A client sends an HTTP request.
2. FastAPI validates the request with Pydantic.
3. The route calls the AI service when configured.
4. The AI service sends a request to OpenRouter.
5. The API returns a validated response or an appropriate HTTP error.

## Current Components

| Component | Responsibility |
|---|---|
| FastAPI | REST API and HTTP handling |
| Pydantic | Input validation and response schemas |
| OpenAI SDK | OpenRouter-compatible API client |
| pytest / HTTPX | Automated API testing |
| Docker | Reproducible application packaging |
| GitHub Actions | Continuous integration |

## Planned Request Flow

1. User uploads an enterprise document.
2. The application extracts and chunks its text.
3. Chunks are indexed for retrieval.
4. A question retrieves relevant evidence.
5. The LLM generates an evidence-grounded response.
6. The API returns the answer with source references.
7. Tracing and evaluation capture quality and latency.

## Planned Deployment

GitHub repository -> GitHub Actions -> Docker image -> Artifact Registry
-> Cloud Run.

Production secrets and cloud permissions will be configured separately.
PostgreSQL, Redis, and background workers will be added when their features
are implemented.

## Design Principles

- Keep provider credentials out of source code.
- Validate requests at the API boundary.
- Use deterministic tests for normal CI runs.
- Handle provider failures and timeouts explicitly.
- Add infrastructure only when it supports a concrete requirement.
