# ADR-0001: Baseline RAG stack

- Status: Accepted
- Date: 2026-11-24
- Tag: v0.1-baseline

## Context

Need a working end-to-end baseline (PDF → answer with citations) before measuring anything.
Constraints: zero cost, runs on a laptop, no Docker yet, free-tier LLM.

## Decisions

| Component       | Choice                                                                                     | Why                                          | Trade-off                                                                                           |
| --------------- | ------------------------------------------------------------------------------------------ | -------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Package manager | uv + `uv.lock`                                                                             | Reproducible env across laptop / CI / server | Team must have uv installed                                                                         |
| PDF parsing     | pypdf                                                                                      | Simple, pure Python                          | Loses table structure; glues some words (`LiquidFund`)                                              |
| Chunking        | Fixed 1000 chars, 150 overlap                                                              | Simplest baseline                            | Ignores clause/section boundaries; values are guesses, to be tuned with eval                        |
| Embeddings      | fastembed `BAAI/bge-small-en-v1.5` (runs as Qdrant's ONNX build, cached in `data/models/`) | Free, local, fast on CPU                     | Small model: similarity scores tightly packed (0.745–0.777 on eval case #1)                         |
| Vector DB       | Qdrant, embedded local mode                                                                | No server/Docker needed                      | Single process only: can't ingest while API is running                                              |
| Retrieval       | Dense only, top-k = 5                                                                      | Baseline                                     | Only 1/5 chunks relevant on eval case #1 → reranker candidate                                       |
| LLM access      | LiteLLM                                                                                    | Swap provider with one `.env` line           | Its model map can be wrong (said temperature unsupported; API accepts it) → `allowed_openai_params` |
| LLM             | `gemini-3.5-flash-lite` (free tier: 15 RPM / 500 RPD)                                      | Highest free daily limit among tested models | Free-tier inputs may be used by Google → never send client data                                     |
| Determinism     | `temperature=0`                                                                            | Comparable eval runs                         | Not yet verified that the model honours it                                                          |
| Resilience      | `num_retries=3`                                                                            | Gemini returned 503 "high demand" once       | Retries count against rate limits; slower worst-case latency                                        |
| Ingestion       | Full rebuild every run                                                                     | No duplicate chunks, simple                  | Slow at scale → incremental later                                                                   |

## Consequences / revisit when

- Week 2 eval shows weak table questions → try a table-aware parser
- Hybrid search (BM25) added → fix glued words first
- Eval shows irrelevant chunks in top-5 → add reranker
