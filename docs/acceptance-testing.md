
# EnterpriseFlow AI — Cross-Environment Acceptance Testing

## Purpose

Run the same acceptance checks against local development, Render, and Google Cloud Platform.

The goal is consistent application behavior, not identical wording from the language model.

## Checks performed

1. API root responds successfully.
2. Health endpoint reports a healthy status.
3. The canonical SOP uploads successfully.
4. Document chunks are indexed.
5. An account-lockout question returns a grounded answer.
6. The response cites the canonical SOP filename.
7. An out-of-scope travel reimbursement question acknowledges missing information.

## Local test

Start FastAPI from the project root:

```bat
python -m uvicorn main:app --reload
```

Open another CMD window, activate the project Conda environment, navigate to the project root, and run:

```bat
python scripts/run_acceptance.py --base-url http://127.0.0.1:8000
```

## Render test

After deploying the API, run:

```bat
python scripts/run_acceptance.py --base-url https://YOUR-API-SERVICE.onrender.com
```

Replace the example hostname with the real API URL.

Render Free services may need time to wake up. The first request can be slow.

## GCP test

Use your actual Cloud Run URL:

```bat
python scripts/run_acceptance.py --base-url https://YOUR-CLOUD-RUN-URL
```

Replace the placeholder with the actual service URL. If authentication is enabled, configure the test client to authenticate before using this public-URL example.

## Important storage behavior

- The acceptance script uploads the same canonical SOP on every run.
- If ChromaDB retains previous uploads, repeated runs may create duplicate chunks unless document replacement or deduplication is implemented.
- Render Free local data may disappear after restarts, spin-down, or redeployment.
- Cloud Run's local filesystem must not be treated as durable storage.
- Re-run the acceptance script to upload the test SOP when the index is empty.

## Failure diagnosis

- Root or health failure: verify the URL and service status.
- Upload failure: inspect the server logs, supported file extensions, and upload-size limit.
- Zero indexed chunks: inspect ChromaDB initialization and document ingestion.
- Grounded-answer failure: inspect retrieval results, chunking, embeddings, and the system prompt.
- Missing source: inspect source metadata and the API response schema.
- Abstention failure: inspect retrieved context and the LLM instructions.

## Scope and limitations

Passing these checks demonstrates that the tested flow works at that moment. It does not certify authentication, tenant isolation, persistence, load capacity, or production security.
