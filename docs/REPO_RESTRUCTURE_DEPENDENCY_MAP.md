# Repository Restructure Dependency Map

This document maps how the current runtime files depend on each other and what path updates matter if files are moved.

## Current Backend Shape

```text
FastAPI request
  -> src/api/main.py
  -> src/core/security.py
  -> src/agents/langgraph_agent.py
  -> src/agents/query_router.py
  -> src/core/retriever.py
  -> src/core/llm.py
  -> PostgreSQL / pgvector / local fallback
```

Primary API endpoint:

| Method | Path | Handler | Request model | Response model |
| --- | --- | --- | --- | --- |
| `POST` | `/query` | `src/api/main.py::execute_query` | `QueryRequest` | `QueryResponse` |

Recommended local API command from repo root:

```bash
uvicorn src.api.main:app --reload
```

## Core Files And Their Links

| File | Role | Depends on | Used by |
| --- | --- | --- | --- |
| `src/api/main.py` | FastAPI app and `/query` endpoint | `src.agents.langgraph_agent`, `src.core.security`, `fastapi`, `pydantic` | `uvicorn`, `tests/integration/test_api.py`, frontend clients |
| `src/agents/langgraph_agent.py` | Agent loop: route, retrieve, evaluate, self-correct, answer | `src.core.llm`, `src.agents.query_router`, `src.core.retriever` | `src/api/main.py`, `tests/integration/test_agent.py`, `tests/unit/test_security.py` |
| `src/agents/query_router.py` | Query classification and routing | `src.core.llm` | `src/agents/langgraph_agent.py`, `tests/unit/test_routing.py` |
| `src/core/retriever.py` | Database connection and hybrid retrieval | `.env` via `dotenv`, `psycopg2`, PostgreSQL tables | `src/core/pipeline.py`, `src/agents/langgraph_agent.py`, ingestion and eval scripts |
| `src/core/security.py` | RLS, sanitization, citations, audit log, OOS guardrails | `src.core.retriever.get_connection`, `experiments/results/...` | `src/api/main.py`, `tests/unit/test_security.py` |
| `src/core/llm.py` | Multi-provider LLM fallback and wrapper | API keys from `.env` | router, agent, pipeline, eval scripts |
| `src/core/pipeline.py` | Baseline RAG pipeline | `src.core.retriever`, `src.core.llm` | eval scripts, experiments |
| `src/core/graph_rag.py` | Taxonomy graph schema and graph retrieval queries | `src.core.retriever.get_connection` | `scripts/ingest_taxonomy.py`, `scripts/demo_graph_rag.py` |
| `src/evals/metrics.py` | Retrieval and generation scoring helpers | `src.core.llm.query_llm` | evaluation scripts |
| `src/chunkers/ncr_dpr_chunker.py` | NCR/DPR chunking utilities | standard library only | ingestion scripts |

## Entrypoint Scripts

| Script | What it runs | Depends on | Writes to |
| --- | --- | --- | --- |
| `scripts/ingest_data.py` | Loads PDFs/JSON into pgvector | `src.core.retriever`, `src.core.llm` | PostgreSQL `rag_documents` |
| `scripts/demo_graph_rag.py` | Runs graph retrieval demo | `src.core.graph_rag`, `src.core.retriever`, `src.core.llm` | `experiments/results/graph_rag_test_Nishitha.md` |
| `scripts/eval_baseline.py` | Baseline evaluation runner | `src.core.pipeline`, `src.evals.metrics` | `experiments/results/` |
| `tests/integration/test_api.py` | FastAPI integration test | `src.api.main.app` | test output only |
| `tests/integration/test_agent.py` | Agent integration test | `src.agents.langgraph_agent` | test output only |
| `tests/unit/test_security.py` | Security and hardening tests | `src.core.security`, `src.agents.langgraph_agent` | test output only |
| `tests/unit/test_routing.py` | Routing tests | `src.agents.query_router` | test output only |

## What To Update If Files Move

1. `uvicorn src.api.main:app`
2. Any `from src...` imports in tests and scripts
3. Data and results paths inside scripts
4. Frontend base URL configuration

## Historical Notes

Old `_Nishitha` filenames still appear in archived reports and migration notes, but they should not be treated as the live runtime path for the current code.
