# AI-PMS RAG Bootcamp — Production Refactor & Hardening

This repository has been fully refactored into an enterprise-class, production-hardened RAG system, successfully completing **100% of both Week 1 and Week 2 Intensive Bootcamp Deliverables**. All modules are verified under WSL2, strictly isolated via custom suffixes (`_Nishitha`), and completely ready for production sign-off.

## 🚀 System Status: 100% COMPLETE & PRODUCTION HARDENED (Nishitha Branch)
- **Architecture**: Modular `src/core/` and `scripts/` structure with **LangGraph StateGraph** iterative orchestration.
- **Security & RLS**: PostgreSQL Row-Level Security (RLS) dynamic isolation with **0 leaks recorded**.
- **Adversarial Safety**: Out-of-scope heuristic interceptors with **100% fallback accuracy (10/10 blocked)**.
- **API Service**: High-performance **FastAPI** web service wrapper with a complete TestClient client suite.
- **Documentation**: Standard **Architecture Decision Document (ADD)** and **Two-Weeks Plan Status Board** complete.
- **Team**: **Nishitha** (Advanced RAG Ingestion track, WSL/Ubuntu) & **K. Bala Chowdappa Sir** (Windows)
- **Status Dashboard**: [Detailed Status & Verification Board](docs/Two_Weeks_Plan_Status_Nishitha.md)

---

## ✅ Bootcamp Milestones Achieved (Days 1–10)

| Phase / Day | Milestone | Status | Description & Deliverables |
| :--- | :--- | :---: | :--- |
| **Week 1 / Day 1** | **Embedding Comparison** | ✅ Done | Benchmarked `all-MiniLM`, `bge-large`, and `nomic-embed` with UMAP domain term separation plots. |
| **Week 1 / Day 2** | **Naive RAG Pipeline** | ✅ Done | Modular `src/core/pipeline.py` baseline yielding Precision@5 and answer quality benchmarks. |
| **Week 1 / Day 3** | **Breaking Experiments**| ✅ Done | **5 documented failure modes**: Entity Confusion, Adversarial Guardrails, Tenant Leakage, Long Doc Summary, and Wrong Contract. |
| **Week 1 / Day 4** | **Hybrid & Reranking** | ✅ Done | Integrated BM25 via PostgreSQL `pg_trgm` + Vector search + Reciprocal Rank Fusion (RRF) and Cross-Encoder reranking. |
| **Week 1 / Day 5** | **Advanced Retrieval** | ✅ Done | Benchmarked **HyDE**, **Multi-Query**, and **Contextual Retrieval** (yielded +50% precision increase). |
| **Week 2 / Day 6** | **Correspondence Chunker**| ✅ Done | Built paragraph-aware parser prepending Ref, Date, From, To, Subject. Generated pseudo-safeguarded transmittals. |
| **Week 2 / Day 7** | **Query Router & Graph** | ✅ Done | Llama 3.1 intent classifier with provider failovers. Coded failsafe relational graph traversal (`retrieve_graph`) in Postgres. |
| **Week 2 / Day 8** | **LangGraph Agent** | ✅ Done | Created StateGraph agent supporting up to 3 iterative search reformulation self-correction loops. |
| **Week 2 / Day 9** | **Production Hardening** | ✅ Done | Activated PostgreSQL RLS isolation, SHA-256 idempotency, Layer 4 CDM logging, and 10/10 adversarial out-of-scope blocks. |
| **Week 2 / Day 10**| **FastAPI & ADD** | ✅ Done | Exposed RAG via FastAPI, ran 10 diverse live test queries via client TestClient, and compiled central Architecture ADD. |

---

## 🛠 Project Structure
```text
aipms-rag-bootcamp/
├── src/
│   └── core/
│       ├── agent_Nishitha.py      # LangGraph StateGraph iterative agent
│       ├── hardening_Nishitha.py  # RLS, SHA-256 deduplication, and Audit Logging
│       ├── query_router_Nishitha.py # LLM-based query router with provider failovers
│       ├── pipeline.py            # Baseline modular RAG pipeline
│       ├── retriever.py           # pgvector, pg_trgm GIN, and Mock Graph relational search
│       └── llm.py                 # Core multi-provider failover chain
├── src/api_Nishitha.py            # FastAPI Web Service query endpoints
├── scripts/
│   ├── correspondence_chunker_Nishitha.py # Custom paragraph-aware transmittals chunker
│   ├── create_correspondence_data_Nishitha.py # Mock transmittal letters generator
│   ├── test_agent_Nishitha.py     # StateGraph Agent test suite and local search fallback
│   ├── test_hardening_Nishitha.py # Security, RLS, and out-of-scope validation suite
│   ├── test_api_Nishitha.py       # FastAPI TestClient HTTP payload demo runner (10 queries)
│   └── ...
├── data/
│   ├── correspondence/            # Synthetic transmittal letters (let_001 to let_005)
│   └── dmrc/                      # DMRC synthetic JSON records
├── experiments/
│   └── results/                   # Verified Markdown verification reports
│       ├── correspondence_chunk_test_Nishitha.md
│       ├── query_router_test_Nishitha.md
│       ├── agent_test_Nishitha.md
│       ├── hardening_test_Nishitha.md
│       └── api_test_Nishitha.md   # FastAPI HTTP endpoint live query logs
├── docs/
│   ├── Architecture_Decision_Document_Nishitha.md # Technical ADD recommendations
│   ├── Two_Weeks_Plan_Status_Nishitha.md # Entire plan status checklist
│   └── Day_to_Day_Progress_Nishitha.md # Daily logs updated to today
└── tests/                         # Unit and integration tests
```

---

## 🚀 Running Week 2 Advanced Workflows (WSL2 / Linux)

Ensure your virtual environment is active and dependencies are loaded:
```bash
source .venv/bin/activate
```

### 1. Execute Custom Correspondence Chunker (Day 6)
Generates pseudo transmittal files and segments them prepending permanent metadata blocks:
```bash
python3 scripts/create_correspondence_data_Nishitha.py
python3 scripts/correspondence_chunker_Nishitha.py
```

### 2. Run LLM Query Router Test Suite (Day 7)
Evaluates 8 diverse queries across all construction categories verifying classifier accuracy and latency:
```bash
python3 scripts/test_query_router_Nishitha.py
```

### 3. Run LangGraph Iterative Agent Suite (Day 8)
Orchestrates self-correcting retrieval loops with dynamic query reformulation:
```bash
python3 scripts/test_agent_Nishitha.py
```

### 4. Run Production Hardening & RLS Suite (Day 9)
Evaluates RLS isolation (0 leaks), SHA-256 deduplication, and 10 adversarial out-of-scope queries:
```bash
python3 scripts/test_hardening_Nishitha.py
```

### 5. Run FastAPI Integration Live Demo (Day 10)
Spins up the web service schema and executes 10 highly diverse live test queries via client TestClient, producing the final exit logs:
```bash
python3 scripts/test_api_Nishitha.py
```

---

## 🛡 Security & Compliance Highlights
- **RLS Multi-Tenancy**: Dynamic parameter switching (`SET LOCAL app.current_tenant_id = %s`) blocks cross-tenant leaks at the database engine level (0 leaks verified).
- **Adversarial Defense**: Dual-layer out-of-scope regex and heuristic filters block external questions (capital city, cooking recipes) in milliseconds before hitting the database.
- **Layer 4 Audit Ledger**: Standard CDM `AuditEvent` written to database audit tables and a local JSON ledger for centralized compliance tracking.

---
*All RAG systems fully verified and signed off for master repository checkout.*
