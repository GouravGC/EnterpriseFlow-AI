
# EnterpriseFlow AI — Environment Parity Plan

## Principle

Maintain one application codebase and one API contract. Configure environment-specific differences through environment variables and storage adapters rather than separate implementations.

## Behavior that must remain consistent

- Python version and pinned dependencies.
- OpenRouter model identifier and generation settings.
- Embedding model and distance metric.
- Chunk size, overlap, metadata, and retrieval count.
- API response schemas and error behavior.
- Source citation structure.
- Canonical acceptance document and questions.

## Environment comparison

| Concern | Local Windows | Render validation | GCP deployment |
|---|---|---|---|
| Configuration | Local `.env`, excluded from Git | Dashboard environment variables and secrets | Cloud Run environment variables and secrets |
| API process | Uvicorn | Container or platform start command | Cloud Run container |
| Vector data | Local ChromaDB directory | Temporary index or external vector database | Persistent vector service or suitable durable deployment |
| Original documents | Local files | Re-upload for temporary demos if data is lost | Cloud Storage or another durable object store |
| Validation | Acceptance script | Same script and canonical SOP | Same script and canonical SOP |

## Storage and model behavior

A storage backend can differ between environments, but it must preserve the RAG retrieval contract.

Each retrieved result should contain:

- `text`: retrieved text chunk.
- `source`: original filename.
- `page`: optional page number.
- Internal relevance metadata where applicable.

The API should not need to know which storage backend is in use.

## Before production use on GCP

- Configure durable document storage.
- Configure a persistent vector store or another supported durable retrieval design.
- Add authentication and authorization before handling private documents.
- Add tenant/user isolation if multiple users or organizations can upload documents.
- Store API keys in a secret manager rather than source control.
- Run the acceptance tests against the deployed service.
- Configure logging, resource limits, backups, and recovery procedures.

## Limitations

Passing acceptance tests validates a limited user flow only. It is not a security review or production-readiness certification.
