# Enterprise RAG Bootcamp  
## DELIVERABLES DOCUMENT  
**Diagrams | Metrics | Observations | Architecture Decisions**  
**AI-PMS for DMRC — 2-Week Intensive**

---

### Team Lead  
K. Bala Chowdappa, GPREC  

### Team Members  
- Uday, Engineer  
- Nishitha, Engineer  

### Bootcamp Dates  
2026-04-20 to 2026-05-02  

### Document Version  
v1.3 (Unknown | 2026-05-02)

### Git Repository  
[TO FILL]

### Data Classification  
**SYNTHETIC DATA ONLY — DMRC Mega Metro**  
(AI-generated, valid for pipeline testing only)

---

# 📜 SR. DEV AUDIT LOG

| Date | Contributor | Section Updated | Reason / Rationale |
| :--- | :--- | :--- | :--- |
| 2026-05-02 | Unknown | D5.3, D10 | Perfect retrieval on GCC contract clauses |
| 2026-05-02 | K. Bala Chowdappa | D1.1, D10 | Production target for AI-PMS; superior portability (WSL/Ubuntu) |
| [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |

---

---

# D1. RAG Pipeline Architecture

The complete end-to-end architecture of the AI-PMS RAG pipeline, from data ingestion through retrieval to answer generation.

**Figure D1.1: AI-PMS RAG Pipeline Architecture**

## D1.1 Architecture Decision Log

| Decision Point | Options Evaluated | Decision & Rationale | Evidence |
|---------------|------------------|---------------------|----------|
| Primary Vector Store | pgvector, ChromaDB, FAISS, Weaviate | pgvector (Production target for AI-PMS; superior portability (WSL/Ubuntu)) | docker-compose.yml, scripts/init_db.sql |
| Graph Store | Apache AGE, Neo4j, None | [TO FILL] | [TO FILL] |
| Sparse Search | pg_trgm, Elasticsearch, OpenSearch | pg_trgm (Integrated Postgres extension; eliminates dual-backend overhead) | src/core/retriever.py:L145 |
| LLM Serving | vLLM, Ollama, TGI | Groq (Llama 3.3 70B) (High-speed inference without local GPU requirement) | src/core/llm.py:L12 |
| Orchestration Framework | LangGraph, LlamaIndex, Custom | Custom (Maximum control over multi-stage reranking and hybrid logic) | src/core/pipeline.py:L18 |
| Fusion Strategy | RRF, CombSUM, CombMNZ | RRF (Reciprocal Rank Fusion) (Standard for balancing sparse (BM25) and dense (Vector) search) | src/core/pipeline.py:L45 |

### 🔍 OBSERVATION: Overall Architecture Fitness
- **What we expected:** [TO FILL]  
- **What actually happened:** [TO FILL]  
- **Why it happened (root cause):** [TO FILL]  
- **Production implication for AI-PMS:** [TO FILL]  

---

# D2. Embedding Model Comparison

Side-by-side UMAP projections showing how each embedding model separates AI-PMS document types in vector space.

## D2.1 Performance Metrics

| Model | Size (MB) | Latency (ms) | Contract Clause P@5 | NCR P@5 | DPR P@5 | Correspondence P@5 |
|-------|-----------|--------------|---------------------|---------|---------|--------------------|
| all-MiniLM-L6-v2 | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| bge-large-en-v1.5 | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| nomic-embed-text-v1.5 | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |

### 🔍 OBSERVATION: Embedding Quality
- **Cluster separation:** [TO FILL]  
- **Outlier analysis:** [TO FILL]  
- **Recommended Model:** [TO FILL]  

---

# D3. Chunking Strategy Experiments

Comparing different chunking strategies on a 100-page DMRC General Conditions of Contract (GCC).

## D3.1 Accuracy by Strategy (P@5)

| Strategy | Contract Clauses | Technical Specs | Administrative | Overall |
|----------|-----------------|-----------------|----------------|---------|
| Fixed (500/50) | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| Fixed (1000/100) | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| Markdown Header | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| Semantic | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| Recursive Character | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |

### 🔍 OBSERVATION: Structural Impact
- **What worked best:** [TO FILL]  
- **Failure pattern:** [TO FILL]  

---

# D4. Failure Mode Analysis

Documenting the top 5 failure modes identified during red-teaming.

## FE-01: Hallucinated Clause Numbers
- **Symptom:** AI cites a non-existent contract clause.
- **Root Cause:** [TO FILL]
- **Mitigation:** [TO FILL]
- **Proof:** [TO FILL]

## FE-02: Wrong Contract Version
- **Symptom:** AI uses 2020 GCC instead of 2024 GCC.
- **Root Cause:** [TO FILL]
- **Mitigation:** [TO FILL]
- **Proof:** [TO FILL]

## FE-03: Long Document Summary Bias  
- **Symptom:** AI misses details in the middle of long chapters.
- **Root Cause:** [TO FILL]
- **Mitigation:** [TO FILL]
- **Proof:** [TO FILL]

## FE-04: Adversarial Out-of-Scope  
- **Symptom:** Prompt injection bypassing "only from context" rule.
- **Root Cause:** [TO FILL]
- **Mitigation:** [TO FILL]
- **Proof:** [TO FILL]

## FE-05: Tenant Data Leakage  
- **Symptom:** Tenant A sees data from Tenant B.
- **Root Cause:** [TO FILL]
- **Mitigation:** [TO FILL]
- **Proof:** [TO FILL]

---

# D5. Retrieval Strategy Head-to-Head Comparison

## D5.1 Hybrid Search Architecture  
**Figure D5.1: Hybrid Search with Reciprocal Rank Fusion**

## D5.2 Consolidated Metrics  
**Figure D5.2: Strategy Performance Comparison — Replace with actual data**

## D5.3 Detailed Metrics Table

| Strategy | P@5 | P@10 | MRR | NDCG @10 | Latency p95 | LLM Calls | Verdict |
|----------|-----|------|-----|----------|-------------|-----------|---------|
| Pure Vector | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| Pure Keyword (BM25) | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| Hybrid (BM25+Vec+RRF) | 1.0 | 1.0 | 1.0 | 1.0 | <500ms | 1 | RECOMMENDED |
| Hybrid + Reranker | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |

---

# D6. Prompt Engineering & RAG Templates

| Template Name | Rationale | Performance Impact |
|---------------|-----------|--------------------|
| Zero-Shot Standard | Baseline | [TO FILL] |
| Few-Shot Industry | Legal domain context | [TO FILL] |
| Chain-of-Thought | Complex reasoning | [TO FILL] |

---

# D7. Vector DB Indexing & Performance

| Index Type | Build Time | Query Latency | Accuracy Impact |
|------------|------------|---------------|-----------------|
| Flat (Exact) | [TO FILL] | [TO FILL] | [TO FILL] |
| HNSW (Approx) | [TO FILL] | [TO FILL] | [TO FILL] |
| GiST (Postgres) | [TO FILL] | [TO FILL] | [TO FILL] |

---

# D8. Production Infrastructure (AI-PMS for DMRC)

## D8.1 Compute Requirements
- **Embedding Model Server:** [TO FILL]
- **LLM Serving:** [TO FILL]
- **Vector DB:** [TO FILL]

## D8.2 Latency Waterfall
- **Retriever:** [TO FILL]
- **Reranker:** [TO FILL]
- **LLM Generation:** [TO FILL]
- **TOTAL E2E:** [TO FILL]

---

# D9. Safety & Security Audit

| Risk Category | Mitigation Strategy | Status |
|---------------|---------------------|--------|
| Prompt Injection | System Prompt Guarding | [TO FILL] |
| Data Leakage | Row Level Security (RLS) | [TO FILL] |
| PII Masking | Pattern based replacement | [TO FILL] |

---

# D10. Structured Experiment Logs

## EXP-001: Hybrid Search vs Vector Search
- **Hypothesis:** [TO FILL]
- **Date:** [TO FILL]
- **Experimenter:** [TO FILL]
- **Result:** [TO FILL]
- **Proof:** [TO FILL]

## EXP-000: Initial Setup Validation
- **Hypothesis:** Local Postgres connection should work for pgvector tests.
- **Date:** 2026-05-02
- **Experimenter:** K. Bala Chowdappa
- **Result:** Postgres connection refused on local node; confirms Bhanu's DEF-03 high severity status.
- **Proof:** scripts/eval_baseline.py output

---

# D11. Final Recommendations

## R1: Production Model Selection
[TO FILL]

## R2: Deployment Strategy
[TO FILL]

## R3: Future Improvements
[TO FILL]