# Repository Structure Guide

## Overview
This document describes the current reorganized structure of the AIPMS RAG Bootcamp repository.

## Source Code Organization

### `src/agents/`
LangGraph-based agent orchestration and routing logic.

- `langgraph_agent.py` - main agent loop with retrieval, evaluation, correction, and answer generation
- `query_router.py` - query intent classification and routing

### `src/api/`
FastAPI web service.

- `main.py` - API entry point with the `/query` endpoint

### `src/core/`
Core RAG and security components.

- `pipeline.py` - baseline RAG pipeline
- `llm.py` - multi-provider LLM integration
- `graph_rag.py` - GraphRAG implementation
- `entity_mapper.py` - entity extraction helpers
- `security.py` - security guardrails, OOS checks, citations, audit logging, and retrieval helpers
- `retriever.py` - retrieval and database access helpers

### `src/chunkers/`

- `ncr_dpr_chunker.py` - NCR/DPR correspondence parser

### `src/evals/`

- `metrics.py` - RAG evaluation metrics

### `src/utils/`

- `config.py` - configuration management

## Tests

### `tests/unit/`

- `test_routing.py` - query router tests
- `test_security.py` - security module tests

### `tests/integration/`

- `test_agent.py` - agent integration tests
- `test_api.py` - API endpoint tests

## File Path Mapping

| Old | New |
|-----|-----|
| `src/core/agent_Nishitha.py` | `src/agents/langgraph_agent.py` |
| `src/core/query_router_Nishitha.py` | `src/agents/query_router.py` |
| `src/core/hardening_Nishitha.py` | `src/core/security.py` |
| `src/api_Nishitha.py` | `src/api/main.py` |
| `scripts/correspondence_chunker_Nishitha.py` | `src/chunkers/ncr_dpr_chunker.py` |
| `scripts/setup_db_Nishitha.py` | `scripts/reinit_db.py` |
| `scripts/test_agent_Nishitha.py` | `tests/integration/test_agent.py` |
| `scripts/test_api_Nishitha.py` | `tests/integration/test_api.py` |
| `scripts/test_hardening_Nishitha.py` | `tests/unit/test_security.py` |
| `scripts/test_query_router_Nishitha.py` | `tests/unit/test_routing.py` |

## Import Examples

```python
from src.agents.langgraph_agent import run_agentic_query
from src.api.main import app
```

Generated: 2026-06-10
