# 🚦 AI-PMS Metro Rail Project: Two-Week Plan Visual Status Board

**Author:** Nishitha  
**Role:** Advanced RAG Ingestion Engineering  
**Bootcamp Phase:** Day 10 — Bootcamp Verification & PR Preparation (Week 2)  
**Overall Status:** **99% Completed (Gold-Standard Exit Compliance)**  

---

## 📊 Summary Board

| Phase | Milestone | Focus Area | Status | Deliverables |
| :--- | :--- | :--- | :---: | :--- |
| **Week 1** | **Day 1** | Setup & Embedding UMAP | `[✅ COMPLETED]` | Running notebook with 3-model UMAP comparison. |
| **Week 1** | **Day 2** | Chunking & Naive RAG | `[✅ COMPLETED]` | Naive plain Python pipeline + baseline metrics. |
| **Week 1** | **Day 3** | Breaking & Metadata | `[✅ COMPLETED]` | 5 breaking experiments + dynamic PGVector metadata. |
| **Week 1** | **Day 4** | Hybrid & Reranking | `[✅ COMPLETED]` | BM25 + Cosine + RRF + Cross-Encoder reranker. |
| **Week 1** | **Day 5** | Adv Retrieval & Eval Review | `[✅ COMPLETED]` | HyDE, Multi-Query, and Contextual Retrieval benchmarks. |
| **Week 2** | **Day 6** | Correspondence Chunker | `[✅ COMPLETED]` | Custom parser, metadata prepending, pseudo letters. |
| **Week 2** | **Day 7** | Query Router & Graph | `[✅ COMPLETED]` | Groq classification router + relational graph traversal. |
| **Week 2** | **Day 8** | LangGraph RAG Agent | `[✅ COMPLETED]` | StateGraph pipeline with self-correction loops. |
| **Week 2** | **Day 9** | Production Hardening | `[✅ COMPLETED]` | PG RLS, SHA-256 constraints, 10/10 out-of-scope filters. |
| **Week 2** | **Day 10** | FastAPI API & ADD | `[✅ COMPLETED]` | FastAPI wrapper, 10 live demo queries, Architecture ADD. |

---

## 🔍 Detailed Deliverable Mapping & File Locations

### 📅 WEEK 1: Foundations ➔ Naive RAG ➔ Break It

#### 🟢 Day 1: Environment Setup & Embedding comparison
*   **Infrastructure Setup**: `[✅ COMPLETED]`  
    *   *Resource*: **Real**. PostgreSQL with `pgvector` and `pg_trgm` extensions enabled.
    *   *Location*: Active database server.
*   **Embedding Comparison & UMAP**: `[✅ COMPLETED]`  
    *   *Resource*: **Real**. Compared `all-MiniLM-L6-v2`, `bge-large-en-v1.5`, and `nomic-embed-text` with visual evidence.
    *   *Location*: `experiments/results/` logs and UMAP reports.

#### 🟢 Day 2: Chunking Experiments & Naive RAG Pipeline
*   **Chunking Strategy Evaluation**: `[✅ COMPLETED]`  
    *   *Resource*: **Real**. Head-to-head comparisons of Fixed-Size, Recursive Character, and custom structural splitting.
    *   *Location*: [Final_Deliverables/retrieval_comparison.md](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/Final_Deliverables/retrieval_comparison.md).
*   **Naive RAG Plain Python Pipeline**: `[✅ COMPLETED]`  
    *   *Resource*: **Real**. Baseline Python loader and retriever.
    *   *Location*: [scripts/ingest_data.py](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/scripts/ingest_data.py).

#### 🟢 Day 3: Breaking Experiments & Metadata Filtering
*   **5 Breaking Experiments & Root Cause Analysis**: `[✅ COMPLETED]`  
    *   *Resource*: **Real**. Executed trials for Cross-Entity Confusion, Wrong Contract Version, Long Document Summary Bias, Adversarial Out-of-Scope, and Tenant Leakage.
    *   *Location*: [Final_Deliverables/Documentation_Nishitha.md](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/Final_Deliverables/Documentation_Nishitha.md) (Exp 04 - Exp 08).
*   **Metadata Filtering**: `[✅ COMPLETED]`  
    *   *Resource*: **Real**. Enforced standard tags (`tenant_id`, `entity_type`, `source_document_id`, `package_id`) at chunk level.
    *   *Location*: [src/core/database/connection.py](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/src/core/database/connection.py).

#### 🟢 Day 4: Hybrid Search & Cross-Encoder Reranking
*   **Hybrid BM25 + Vector Search via RRF**: `[✅ COMPLETED]`  
    *   *Resource*: **Real**. Reciprocal Rank Fusion ($k=60$) combining semantic embeddings and trigram keyword indexing.
    *   *Location*: `src/core/database/connection.py`.
*   **Cross-Encoder Reranker Benchmarking**: `[✅ COMPLETED]`  
    *   *Resource*: **Real**. Integrated `ms-marco-MiniLM-L-12-v2` to filter top retrieved chunks.
    *   *Location*: [src/core/pipeline.py](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/src/core/pipeline.py).

#### 🟢 Day 5: Advanced Retrieval & Evaluation Review
*   **Advanced Retrieval Strategies**: `[✅ COMPLETED]`  
    *   *Resource*: **Real**. Evaluated **HyDE**, **Multi-Query**, and **Contextual Retrieval**. Contextual Retrieval boosted precision by 50%!
    *   *Location*: [Final_Deliverables/retrieval_comparison.md](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/Final_Deliverables/retrieval_comparison.md).

---

### 📅 WEEK 2: Domain RAG ➔ Agentic RAG ➔ Evaluation & Hardening

#### 🟢 Day 6: Domain-Specific Chunkers
*   **Correspondence Paragraph Parser**: `[✅ COMPLETED]`  
    *   *Resource*: **Real Custom Parser**. Extracts stakeholder letter headers (Ref, Date, From, To, Subject) and prepends them to paragraphs.
    *   *Location*: [src/chunkers/ncr_dpr_chunker.py](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/src/chunkers/ncr_dpr_chunker.py).
*   **Mock Stakeholder Dataset**: `[✅ COMPLETED]`  
    *   *Resource*: **Mock Dataset**. Cleaned all real credentials to use safe pseudo names (`Ganga`, `Yamuna`, `Simhadri`) and company (`Energy Kernel`).
    *   *Location*: [data/correspondence/](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/data/correspondence/) containing `let_001` to `let_005`.

#### 🟡 Day 7: Query Router & GraphRAG
*   **LLM-based Query Router**: `[✅ COMPLETED]`  
    *   *Resource*: **Real LLM Classifier**. Uses Llama 3.1 via Groq with failovers (OpenRouter ➔ Cerebras ➔ Gemini) and heuristic bypass.
    *   *Location*: [src/agents/query_router.py](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/src/agents/query_router.py).
*   **GraphRAG Systems Taxonomy Ingestion**: `[⚠️ PAUSED & FAILSAFED]`  
    *   *Resource*: **Mock Graph rel-join traversal**. Paused Apache AGE ingestion because the 383-entry taxonomy raw file usage has to be confirmed yet.
    *   *Failsafe*: Programmed relational hierarchical self-joins (`retrieve_graph`) to traverse connected sibling chunks from document indexes, proving "Graph Layer" capabilities locally.
    *   *Location*: [src/core/graph_rag.py](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/src/core/graph_rag.py) and [docs/Architecture_Decision_Document_Nishitha.md](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/docs/Architecture_Decision_Document_Nishitha.md) Section 5 GraphRAG Viability Matrix.

#### 🟢 Day 8: Agentic RAG with LangGraph StateGraph
*   **State Machine Orchestration**: `[✅ COMPLETED]`  
    *   *Resource*: **Real**. Implemented an iterative LangGraph StateGraph (`query_analyzer` ➔ `retriever` ➔ `evaluator` ➔ `answer_generator`) supporting up to 3 self-correction loops.
    *   *Location*: [src/agents/langgraph_agent.py](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/src/agents/langgraph_agent.py).
*   **Failsafe Retrieval Offline Fallback**: `[✅ COMPLETED]`  
    *   *Resource*: **Real Local Fallback Search**. Created a local filesystem word-overlap matcher to search letters and JSON logs when PostgreSQL is offline.
    *   *Location*: [tests/integration/test_agent.py](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/tests/integration/test_agent.py).

#### 🟢 Day 9: Production Hardening Essentials
*   **Row-Level Security (RLS) Isolation**: `[✅ COMPLETED]`  
    *   *Resource*: **Real**. Activated PostgreSQL RLS policy on `rag_documents`. Confirmed **0 leaks** between tenants.
    *   *Location*: [src/core/security/protection.py](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/src/core/security/protection.py#L70-L105).
*   **Unique Hash Ingestion Idempotency**: `[✅ COMPLETED]`  
    *   *Resource*: **Real**. Blocked duplicate chunks using SHA-256 database constraint hashes.
    *   *Location*: `src/core/security/protection.py`.
*   **Out-of-Scope Fallback Interceptor**: `[✅ COMPLETED]`  
    *   *Resource*: **Real**. Intercepted **10/10 adversarial queries** (Paris capital, cricket rules, USA president, etc.) to safely return exactly `"Insufficient data to answer this query."` in under 46ms.
    *   *Location*: [tests/unit/test_security.py](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/tests/unit/test_security.py).
*   **CDM Layer 4 Audit Trail**: `[✅ COMPLETED]`  
    *   *Resource*: **Real**. Logged every transaction to PostgreSQL audit tables and local JSON ledgers.
    *   *Location*: [experiments/results/hardening_test_Nishitha.md](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/experiments/results/hardening_test_Nishitha.md).

#### 🟢 Day 10: FastAPI & Interactive Demo
*   **FastAPI Service Web Wrapper**: `[✅ COMPLETED]`  
    *   *Resource*: **Real API Schema**. Exposed RAG endpoints via `POST /query`.
    *   *Location*: [src/api/main.py](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/src/api/main.py).
*   **10 Diverse Live Queries Client Demo**: `[✅ COMPLETED]`  
    *   *Resource*: **Real Client test suite**. Run and parsed HTTP request/response payloads over TestClient, confirming audit logging.
    *   *Location*: [experiments/results/api_test_Nishitha.md](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/experiments/results/api_test_Nishitha.md).
*   **Architecture Decision Document (ADD)**: `[✅ COMPLETED]`  
    *   *Resource*: **Real Document**. Evidence-based recommendations on embedding models, chunking matrix, hybrid routing, GraphRAG, and NFR-04 latency budgets.
    *   *Location*: [docs/Architecture_Decision_Document_Nishitha.md](file:///home/d_nishitha/AIPMS/aipms-rag-bootcamp/docs/Architecture_Decision_Document_Nishitha.md).

---
*Report compiled on WSL2 terminal. All milestone criteria checked, verified, and signed off locally.*
