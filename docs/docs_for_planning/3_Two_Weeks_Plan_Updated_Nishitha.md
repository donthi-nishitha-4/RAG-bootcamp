# Enterprise RAG Bootcamp
## 2-Week Intensive Implementation Plan (2-Person Execution)

### 1. Week 1: Foundations → Naive RAG → Break It (Days 1–5)

**Day 1: Environment Setup + Embedding Fundamentals**
- ✅ Install PostgreSQL + pgvector + pg_trgm + Apache AGE
- ✅ Install vLLM, load Llama 3.1 8B Instruct
- ✅ Install ChromaDB for rapid prototyping
- ✅ Embed with all-MiniLM, bge-large, nomic-embed
- ✅ 3-model UMAP comparison notebook

**Day 2: Chunking Experiments + Naive RAG Pipeline**
- ✅ Test fixed-size, recursive, and semantic chunkers
- ✅ Build Naive RAG End-to-End (Top-K retrieval K=5)
- ✅ Baseline metrics on queries

**Day 3: Break the Naive Pipeline + Metadata Filtering**
- ✅ Cross-Entity Confusion Experiment
- ✅ Wrong Contract Version Experiment
- ✅ Long Document Summary Experiment
- ✅ Adversarial Out-of-Scope Experiment
- ✅ Tenant Leakage Experiment
- ✅ Implement Metadata Filtering (tenant_id, entity_type, etc.)

**Day 4: Hybrid Search + Reranking**
- ✅ Hybrid Search (BM25 + Vector + RRF)
- ✅ Cross-Encoder Reranking (ms-marco-MiniLM-L-12-v2)
- ✅ BAAI/bge-reranker-v2-m3 test

**Day 5: Advanced Retrieval Strategies**
- ✅ HyDE (Hypothetical Document Embedding)
- ✅ Multi-Query Retrieval
- ❌ Contextual Retrieval (Pending)

---

### 2. Week 2: Domain RAG → Agentic RAG → Evaluation (Days 6–10)

**Day 6: Domain-Specific Chunkers for AI-PMS**
- ✅ FIDIC Contract hierarchical parser
- ✅ NCR form-field extraction
- ✅ DPR section-based parser
- ❌ Correspondence parser (Pending)

**Day 7: GraphRAG + Query Routing**
- ❌ GraphRAG on Metro Rail Systems Taxonomy (Apache AGE)
- ❌ LLM-based Query Router

**Day 8: Agentic RAG with LangGraph**
- ❌ Build iterative agentic pipeline with LangGraph
- ❌ Multi-Hop Query Demonstrations

**Day 9: Evaluation + Hardening**
- ❌ Expand query set to 80+ queries (Currently at 30+)
- ✅ Set up RAGAS evaluation
- ❌ Run RAGAS across full 80+ set
- ✅ Tenant isolation testing
- ❌ Fallback behavior implementation
- ❌ Citation chain tracking
- ❌ Latency compliance & Audit logging

**Day 10: Integration Demo + Architecture Decision Document**
- ❌ FastAPI service wrapping pipeline
- ❌ Architecture Decision Document (D11)

---

## 3. Team Assignment Matrix (Strictly 2 People)

| Person | Environment | Assigned Week 1 & Early Week 2 Tasks (Mostly ✅) | Assigned Week 2 Final Deliverables (Mostly ❌) |
|---|---|---|---|
| **Nishitha** | WSL / Ubuntu | Naive pipeline, RAGAS integration, Breaking Experiments, Manual evaluation (30+ queries) | Agentic RAG with LangGraph, FastAPI wrapper, Final Architecture Docs |
| **K. Bala Chowdappa (Balu Sir)** | Windows | Hybrid Search, Chunking strategies, UMAP comparisons, Reranking, HyDE & Multi-Query | GraphRAG, Query Router, Correspondence Chunker, Windows Pipeline verification |

### 3.1 Daily Rhythm
- **9:00 AM** — 15-min standup: What I built yesterday, what I am building today, what is blocking me
- **1:00 PM** — Midday sync: Quick experiment results sharing.
- **5:00 PM** — Git commit deadline: All code and experiment logs committed.
