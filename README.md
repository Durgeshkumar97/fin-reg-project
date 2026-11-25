# Fin-Reg Copilot

RAG system that answers questions about SEBI mutual fund regulations with citations (file + page).
Built for Independent Financial Advisors (IFAs). Answers are informational only, not investment advice.

## Status
**v0.1-baseline**: PDF ingestion → dense retrieval → LLM answer with citations, served via FastAPI.
Next: evaluation set (Week 2), then retrieval improvements measured against it.

## Stack
pypdf · fastembed (bge-small-en-v1.5) · Qdrant (local) · LiteLLM → Gemini · FastAPI · uv
Design decisions and trade-offs: [docs/adr/0001-baseline-stack.md](docs/adr/0001-baseline-stack.md)

## Setup
```bash
git clone git@github.com:Durgeshkumar97/fin-reg-project.git
cd fin-reg-project
uv sync
cp .env.example .env        # add GEMINI_API_KEY and LLM_MODEL
```
Put SEBI circular PDFs in `data/raw/` (not committed).

## Run
```bash
uv run python -m fin_reg_copilot.ingest              # build the vector index
uv run uvicorn fin_reg_copilot.api:app --reload      # start the API
```
Open http://localhost:8000/docs, or:
```bash
curl -s -X POST localhost:8000/ask -H "Content-Type: application/json" \
  -d '{"question":"Can mutual funds invest in InvITs in debt schemes?"}'
```
Stop the API before re-running ingest (local Qdrant allows one process at a time).

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/retrieve` | Retrieved chunks only (no LLM call) |
| POST | `/ask` | Answer with citations + sources |