
# EnterpriseFlow AI — Acceptance Test Pack

## Purpose

This pack introduces repeatable black-box acceptance testing for the existing EnterpriseFlow AI project without replacing the current API, RAG service, frontend, Dockerfile, or dependency pins.

## Files

- `scripts/run_acceptance.py`: acceptance runner for local, Render, and GCP.
- `knowledge_base/it_support_sop.md`: canonical fictional SOP.
- `docs/acceptance-testing.md`: execution instructions and failure diagnosis.
- `docs/environment-parity.md`: configuration, storage, and deployment requirements.

## Installation

Copy the supplied files into the existing EnterpriseFlow AI project root. Merge the folders; do not create a nested project directory.

Expected layout:

```text
EnterpriseFlow AI/
├── scripts/
│   └── run_acceptance.py
├── knowledge_base/
│   └── it_support_sop.md
└── docs/
    ├── acceptance-testing.md
    └── environment-parity.md
```

## Run locally

Start the API in one CMD window:

```bat
python -m uvicorn main:app --reload
```

Run the acceptance script from another CMD window:

```bat
python scripts/run_acceptance.py --base-url http://127.0.0.1:8000
```

## Run against deployed services

Use the actual API base URL:

```bat
python scripts/run_acceptance.py --base-url https://YOUR-API-URL
```

## What this pack does not change

It does not replace `main.py`, `rag/service.py`, `config.py`, `schemas.py`, `ai_service.py`, `frontend.py`, `Dockerfile`, `.env`, or `requirements.txt`.

The acceptance tests will help identify which behaviors need fixing before changing those core files.
