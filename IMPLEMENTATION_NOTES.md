# EnterpriseFlow AI — Implementation Notes

## Added features

- Deterministic input guardrails for obvious prompt-injection patterns.
- Output validation for generated answer content and response size.
- Retrieved documents treated as untrusted reference data.
- Offline RAG evaluation metrics.
- Golden evaluation dataset for IT support workflows.
- Guardrail and evaluation regression tests.
- GitHub Actions CI for the complete pytest suite.

## Evaluation limitations

The offline evaluation metrics are deterministic regression signals.
They are not semantic faithfulness scores or LLM-as-a-judge results.

Pattern-based prompt-injection checks provide defense-in-depth,
not a complete security boundary.

## Infrastructure limitations

ChromaDB persistence is local to CHROMA_PATH.

Render instances require a persistent disk or external vector
database if the index must survive restarts and redeployments.

Redis remains optional and requires REDIS_URL to point to
a reachable Redis service.

## Validation

Run the following commands in the project Conda environment:

    python -m pip check
    python -m pytest -v

Do not commit .env, API keys, credentials, or local ChromaDB data.