# EnterpriseFlow AI — Enterprise Operations Copilot

An AI-powered enterprise operations copilot built with **Python, FastAPI, Pydantic, OpenRouter, ChromaDB, and Streamlit**. It enables users to upload enterprise documents, retrieve relevant information through semantic search, and receive AI-generated answers grounded in retrieved document context.

EnterpriseFlow AI demonstrates an end-to-end document intelligence workflow with a modular backend, remote embedding generation, vector search, source references, containerization, and automated testing.

## Key Features

### AI-Powered Question Answering
- OpenRouter integration using an OpenAI-compatible LLM interface.
- Configurable chat model through environment variables.
- Context-aware answer generation using retrieved document excerpts.
- Instructions designed to reduce unsupported answers when document context is available.
- Provider timeout and error handling.

### Retrieval-Augmented Generation (RAG)
- Upload PDF, TXT, and Markdown documents.
- Extract text from PDF pages while retaining page metadata.
- Split documents into overlapping text chunks.
- Generate embeddings through the OpenRouter embeddings API.
- Store and retrieve embeddings using ChromaDB.
- Semantic similarity search with configurable retrieval parameters in the RAG service.
- Return source filenames, page references, and text snippets with answers.
- Replace previously indexed chunks when the same filename is uploaded again.

**Current RAG configuration**
| Parameter | Value |
|---|---:|
| Chunk size | 1,000 characters |
| Chunk overlap | 150 characters |
| Retrieval top-k | 4 |
| Embedding batch size | 8 |
| Maximum upload size | 10 MB |
| Vector database | ChromaDB |
| Distance metric | Cosine |
| Embedding provider | OpenRouter |
| Default embedding model | `nvidia/nemotron-3.5-embed-1b:free` |

### Backend API
Built with FastAPI and Pydantic.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Application information |
| GET | `/health` | Health check |
| GET | `/documents/status` | Indexed document chunk status |
| POST | `/documents` | Upload and index a document |
| POST | `/ask` | Ask a question using retrieved context |

Interactive API documentation is available at `/docs`.

### Streamlit Frontend
- Knowledge Base interface for uploading documents.
- Document indexing and knowledge-base status.
- Conversational question-answering interface.
- Retrieved source references displayed alongside answers.
- Backend URL configurable through the sidebar.
- Backend connectivity check.

### Engineering and Development
- Modular Python application structure.
- Pydantic request and response schemas.
- Environment-based configuration using Pydantic Settings.
- Pinned Python dependencies.
- Automated API testing with pytest and HTTPX.
- Docker-based application packaging.
- GitHub Actions continuous integration.
- Application logging and provider error handling.

## Architecture

```text
                  User
                   |
                   v
          Streamlit Frontend
                   |
                   v
             FastAPI Backend
                   |
          +--------+---------+
          |                  |
          v                  v
    Document Upload       User Question
          |                  |
          v                  v
     PDF / TXT / MD      Query Embedding
          |                  |
          v                  v
     Text Extraction     ChromaDB Search
          |                  |
          v                  v
    Text Chunking       Relevant Chunks
          |                  |
          v                  |
   OpenRouter Embeddings     |
          |                  |
          v                  |
       ChromaDB <------------+
          |
          v
   Retrieved Context
          |
          v
    OpenRouter LLM
          |
          v
  Answer + Source References
          |
          v
     Streamlit UI
```

## Technology Stack

| Layer | Technologies |
|---|---|
| Language | Python 3.11 |
| Backend | FastAPI, Uvicorn |
| Validation | Pydantic, Pydantic Settings |
| LLM integration | OpenRouter, LangChain OpenAI integration |
| Embeddings | OpenRouter Embeddings API |
| RAG | LangChain Text Splitters |
| Vector database | ChromaDB |
| Document processing | PyPDF |
| Frontend | Streamlit |
| HTTP client | Requests, HTTPX |
| Testing | Pytest |
| Containerization | Docker |
| CI | GitHub Actions |
| Configuration | python-dotenv, environment variables |

## Project Structure

```text
EnterpriseFlow-AI/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── docs/
│   ├── architecture.md
│   ├── acceptance-testing.md
│   └── environment-parity.md
│
├── knowledge_base/
│
├── rag/
│   └── service.py
│
├── scripts/
│   └── run_acceptance.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
│
├── ai_service.py
├── config.py
├── frontend.py
├── ingest_knowledge_base.py
├── main.py
├── requirements.txt
├── schemas.py
├── test_api.py
│
├── README.md
└── README-acceptance-pack.md
```

## Getting Started

### Prerequisites
- Python 3.11.10
- Conda
- pip
- OpenRouter API key

### 1. Clone the repository

```cmd
git clone https://github.com/GouravGC/EnterpriseFlow-AI.git
cd EnterpriseFlow-AI
```

### 2. Create the Conda environment

```cmd
conda create -n techolution python=3.11.10 -y
conda activate techolution
```

### 3. Install dependencies

```cmd
python -m pip install -r requirements.txt
python -m pip check
```

### 4. Configure environment variables

Create a local `.env` file using `.env.example` as the template.

Configure the following values:

```dotenv
ENVIRONMENT=development

OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openrouter/free

OPENROUTER_EMBEDDING_MODEL=nvidia/nemotron-3.5-embed-1b:free

CHROMA_PATH=./data/chroma

LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=enterpriseflow-ai
```

Never commit `.env` or expose API credentials.

### 5. Start the FastAPI backend

```cmd
python -m uvicorn main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Start the Streamlit frontend

Open another CMD window:

```cmd
conda activate techolution
cd "C:\path\to\EnterpriseFlow-AI"
python -m streamlit run frontend.py
```

Open the local Streamlit URL displayed in the terminal.

The frontend uses the configured backend URL. Set `API_BASE_URL` when running against a different backend.

## Document Ingestion

There are two supported ways to add documents.

**Option 1 — Through the frontend**

1. Open the Knowledge Base tab.
2. Select a PDF, TXT, or Markdown file.
3. Upload and index the document.
4. Check the number of indexed chunks.

**Option 2 — Through the ingestion script**

Place supported documents in `knowledge_base/`, then run:

```cmd
python ingest_knowledge_base.py
```

The ingestion script processes supported files and reports the indexed chunk counts.

## Running Tests

Run the automated API tests:

```cmd
python -m pytest -v test_api.py
```

Check installed dependency consistency:

```cmd
python -m pip check
```

## Acceptance Testing

The repository includes an acceptance-testing workflow for checking the document-question-answering process.

Run the backend first, then execute:

```cmd
python scripts/run_acceptance.py --base-url http://127.0.0.1:8000
```

The acceptance checks cover:
- API availability and health.
- Document upload.
- Document indexing.
- Evidence-grounded question answering.
- Source filename references.
- Responses to questions outside the available document context.

The same acceptance script can be used against a deployed API by supplying its base URL.

## Docker

Build the backend image:

```cmd
docker build -t enterpriseflow-ai .
```

Run it:

```cmd
docker run --rm -p 8080:8080 --env-file .env enterpriseflow-ai
```

Open:

```text
http://localhost:8080/docs
```

## Continuous Integration

GitHub Actions runs on pushes and pull requests targeting `main`.

The current CI workflow:
1. Checks out the repository.
2. Sets up Python 3.11.
3. Installs pinned dependencies.
4. Checks dependency consistency using `pip check`.
5. Runs the automated API tests.

## Deployment and Storage Considerations

The project has an existing Render deployment used for application validation.

The current ChromaDB implementation uses a local persistent directory configured through `CHROMA_PATH`. Local persistence does not automatically provide durable storage across ephemeral hosting environments, container replacement, or multiple application instances.

Before production deployment, configure:
- Durable vector storage.
- Persistent original document storage.
- Secure environment-variable and secret management.
- Authentication and authorization.
- User or tenant isolation where required.
- Monitoring, logging, backups, and recovery procedures.

**AWS deployment is a planned next step.** The existing application architecture will be retained while deployment and storage infrastructure are extended.

## Current Implementation Status

| Capability | Status |
|---|---|
| FastAPI backend | Implemented |
| Pydantic schemas and settings | Implemented |
| OpenRouter chat integration | Implemented |
| Document ingestion | Implemented |
| Remote embeddings | Implemented |
| ChromaDB vector search | Implemented |
| Source references | Implemented |
| Streamlit frontend | Implemented |
| Docker packaging | Implemented |
| GitHub Actions CI | Implemented |
| Acceptance testing | Repository support present |
| Render deployment | Existing deployment |
| Redis caching | Planned |
| PostgreSQL persistence | Planned |
| Celery background processing | Planned |
| LangSmith tracing and evaluation | Planned / requires verification |
| LLM evaluation and optimization | Planned |
| Guardrails | Planned |
| AWS deployment and CI/CD | Planned |

## Roadmap

- [ ] Add Redis-based caching.
- [ ] Introduce appropriate service boundaries for scalable backend components.
- [ ] Add persistent database-backed application metadata.
- [ ] Implement asynchronous background processing where justified.
- [ ] Add LLM evaluation datasets and measurable quality metrics.
- [ ] Improve tracing, monitoring, and observability.
- [ ] Add input and output guardrails.
- [ ] Improve deployment storage durability.
- [ ] Deploy to AWS with CI/CD.
- [ ] Expand automated integration and acceptance testing.

## Security Notes

- Keep API credentials in environment variables or a cloud secret manager.
- Never commit `.env` files.
- Validate uploaded file types and sizes.
- Avoid treating retrieved document content as trusted instructions.
- Add authentication and authorization before using private enterprise documents.
- Do not treat passing acceptance tests as a production security certification.

## Project Objective

EnterpriseFlow AI is being developed as a practical demonstration of backend engineering and applied Generative AI skills, with emphasis on:

- Python and object-oriented application design.
- FastAPI and Pydantic.
- Retrieval-Augmented Generation.
- Vector databases and semantic retrieval.
- Cloud-hosted LLM and embedding integration.
- Containerization and CI.
- Testing, reliability, and production-oriented engineering.

**Developer:** Gourav GC  
**GitHub:** https://github.com/GouravGC  
**Repository:** https://github.com/GouravGC/EnterpriseFlow-AI
