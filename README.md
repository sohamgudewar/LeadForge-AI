# LeadForge AI

[![CI](https://github.com/sohamgudewar/LeadForge-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/sohamgudewar/LeadForge-AI/actions/workflows/ci.yml)
[![Status: Evaluated prototype](https://img.shields.io/badge/status-evaluated_prototype-0F766E)](#known-limitations)

LeadForge AI is an evidence-grounded outreach generation system. It researches
a company, qualifies the lead, develops a personalization angle, drafts an
email, and sends the result through a bounded reviewer-and-revision workflow.

The project focuses on the engineering concerns behind an LLM application:
validated outputs, grounded citations, deterministic control flow, adversarial
input boundaries, repeatable evaluation, persistence, testing, and deployment.

## What it demonstrates

- A real LangGraph state machine with conditional approve/revise routing
- Pydantic-validated Gemini output rather than unrestricted text parsing
- Up to two reviewer-directed email revisions, preventing infinite loops
- Optional current web research with Tavily and source-level citations
- Citation allow-listing that removes model-invented source IDs
- PDF ingestion, chunking, embeddings, metadata filtering, and Chroma retrieval
- FastAPI endpoints, SQLAlchemy persistence, React UI, and lead history
- A ten-company evaluation dataset with objective quality metrics
- Secure PDF boundaries: signature, MIME type, extension, size, and safe names
- Deterministic unit/integration tests that do not consume model quota
- Docker, Railway, Vercel, and GitHub Actions configuration

## Workflow

```text
Company input
    |
    v
Knowledge retrieval -> Web-grounded research -> Enrichment -> Lead scoring
                                                            |
                                                            v
                                                    Personalization
                                                            |
                                                            v
                                                    Email generation
                                                            |
                                                            v
                                                        Reviewer
                                                       /        \
                                               approved          rejected
                                                  |                 |
                                                  v                 v
                                                finish       revise email
                                                                    |
                                                (maximum 2) <--------+
```

Every model-facing stage returns a validated schema. The reviewer produces an
explicit `approved` decision and concrete revision instructions, allowing
LangGraph to choose the next edge deterministically.

## Grounding and trust boundaries

When `TAVILY_API_KEY` is configured, the research stage retrieves up to five
current public sources. Search snippets are treated as untrusted evidence, not
instructions. The model cites fixed IDs (`S1`-`S5`), and the backend removes any
citation whose ID was not returned by the provider. The UI presents verified
evidence separately from inferred business challenges.

Uploaded PDFs are private company context. Files are restricted to PDF content,
10 MB, assigned server-generated names, split into chunks, embedded, and filtered
by normalized company metadata during retrieval.

Each chunk gets a deterministic ID (SHA-256 of company + text), so uploading the
same PDF again overwrites its chunks instead of duplicating them. Retrieval runs
three focused queries (products/services, customers/market, challenges/priorities)
for the company, merges and de-duplicates the hits, and passes up to five chunks
to the agents.

## Evaluation

The versioned dataset in `backend/evaluation/cases.json` covers ten companies.
The real-pipeline evaluator records:

- Schema validity
- Expected industry match
- Citation integrity
- Web-evidence coverage
- Email word-limit compliance
- Required company-name inclusion
- Reviewer approval and revision counts
- Per-case latency and failed runs
- Overall pass rate

Run three cases first to control API usage:

```powershell
cd backend
.\.venv\Scripts\python.exe -m evaluation.run --limit 3
```

Remove `--limit 3` for the complete dataset. Reports are written under
`backend/evaluation/results/` and ignored by Git. Evaluation uses real Gemini
and optional Tavily calls, so it may consume API quota.

## Technology

| Layer | Technology |
| --- | --- |
| Model | Google Gemini 2.5 Flash |
| Orchestration | LangGraph, LangChain |
| API | FastAPI, Pydantic |
| Retrieval | Chroma, PDF chunking and embeddings |
| Persistence | PostgreSQL/SQLite, SQLAlchemy |
| Web research | Tavily via HTTPX |
| Frontend | React 19, Vite, Tailwind CSS |
| Delivery | Docker, Railway, Vercel, GitHub Actions |

## Local development

### 1. Configure the backend

From the repository root:

```powershell
python -m venv backend\.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
Copy-Item .env.example .env
```

Set at least `GOOGLE_API_KEY` in `.env`:

```env
DATABASE_URL=sqlite:///./dev.db
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_optional_tavily_api_key
```

`TAVILY_API_KEY` is optional. Without it, generation still works but the run
will not contain current web evidence.

Start the API:

```powershell
cd backend
.\.venv\Scripts\python.exe run.py --dev
```

FastAPI documentation is available at `http://127.0.0.1:8000/docs`.

### 2. Start the frontend

In another terminal:

```powershell
cd frontend
npm ci
npm run dev
```

The UI is available at `http://127.0.0.1:5173`.

### 3. Run quality checks

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests -q

cd ..\frontend
npm run lint
npm run build
```

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Deployment health check |
| `POST` | `/run-agent` | Generate outreach from a company name |
| `POST` | `/run-agent-with-pdf` | Ingest a PDF and generate grounded outreach |
| `POST` | `/upload-pdf` | Add a PDF to the knowledge store |
| `GET` | `/leads` | List generated leads |
| `GET` | `/lead/{lead_id}` | Fetch a complete outreach package |

The three `POST` endpoints spend LLM, search and embedding quota, so they are
rate limited with an in-memory sliding window: `RUN_LIMIT_PER_CLIENT_HOUR`
(default 10) per client IP and `RUN_LIMIT_GLOBAL_HOUR` (default 100) in total.
The global cap bounds cost even if client IPs are rotated. Exceeding either
returns `429` with a `Retry-After` header. Blocking PDF parsing and pipeline
calls run in a worker thread so they don't stall the event loop.

Example request:

```bash
curl -X POST http://127.0.0.1:8000/run-agent \
  -H "Content-Type: application/json" \
  -d '{"company":"Stripe"}'
```

## Deployment

### Backend on Railway

The repository-level `railway.toml` selects `backend/Dockerfile`, checks
`/health`, and restarts failed containers. Configure these service variables:

- `DATABASE_URL`
- `GOOGLE_API_KEY`
- `TAVILY_API_KEY` (optional)
- `CORS_ORIGINS=https://leadforgeai0i0.vercel.app`
- `RUN_LIMIT_PER_CLIENT_HOUR`, `RUN_LIMIT_GLOBAL_HOUR` (optional rate limits)
- `RAILWAY_DOCKERFILE_PATH=backend/Dockerfile` if the dashboard does not pick up
  Config as Code

The image runs as a non-root user and listens on Railway's injected `PORT`.

Build the same image locally from the repository root:

```bash
docker build -f backend/Dockerfile -t leadforge-api .
docker run --rm -p 8000:8000 \
  -e DATABASE_URL=sqlite:////app/dev.db \
  -e GOOGLE_API_KEY=your_key \
  leadforge-api
```

### Frontend on Vercel

Use `frontend` as the Vercel root directory and configure:

```env
VITE_API_URL=https://your-railway-service.up.railway.app
```

Update the backend CORS allow-list in `backend/main.py` for the final frontend
domain before deployment.

## Repository structure

```text
backend/
  agents/       Structured model stages
  api/          FastAPI routes and upload boundary
  database/     SQLAlchemy engine, models, and CRUD
  evaluation/   Versioned cases, metrics, and report runner
  graph/        LangGraph state and workflow
  models/       API and structured-output schemas
  rag/          PDF ingestion and Chroma retrieval
  research/     Current web research provider
  tests/        Deterministic backend test suite
frontend/
  src/          React dashboard
.github/
  workflows/    CI quality gates
```

## Known limitations

- Company enrichment is model-generated rather than sourced from a licensed
  people/company data provider.
- Web evidence requires a Tavily key; a provider outage degrades to ungrounded
  hypotheses instead of failing the entire workflow.
- Long model runs execute synchronously inside the request. A production system
  should use background jobs and progress events.
- Authentication, tenant isolation, and database migrations are not yet
  implemented. Rate limiting is in-memory, so it is per instance; multiple
  instances would need a shared store such as Redis.
- Uploaded files and the local Chroma store require persistent storage when the
  backend is deployed on ephemeral infrastructure.

## Author

Soham Gudewar — [GitHub](https://github.com/sohamgudewar)

Copyright 2026 Soham Gudewar. Licensed under the Apache License 2.0.
