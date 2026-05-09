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
v1.0 (Template) — Update as experiments are completed  

### Git Repository  
[TO FILL]

### Data Classification  
**SYNTHETIC DATA ONLY — DMRC Mega Metro**  
(AI-generated, valid for pipeline testing only)

---

# 📜 SR. DEV AUDIT LOG

| Date | Contributor | Section Updated | Reason / Rationale |
| :--- | :--- | :--- | :--- |
| [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |

---

---

# D1. RAG Pipeline Architecture

The complete end-to-end architecture of the AI-PMS RAG pipeline, from data ingestion through retrieval to answer generation.

**Figure D1.1: AI-PMS RAG Pipeline Architecture**

## D1.1 Architecture Decision Log

| Decision Point | Options Evaluated | Decision & Rationale | Evidence |
|---------------|------------------|---------------------|----------|
| Primary Vector Store | pgvector, ChromaDB, FAISS, Weaviate | [TO FILL] | [TO FILL] |
| Graph Store | Apache AGE, Neo4j, None | [TO FILL] | [TO FILL] |
| Sparse Search | pg_trgm, Elasticsearch, OpenSearch | [TO FILL] | [TO FILL] |
| LLM Serving | vLLM, Ollama, TGI | [TO FILL] | [TO FILL] |
| Orchestration Framework | LangGraph, LlamaIndex, Custom | [TO FILL] | [TO FILL] |
| Fusion Strategy | RRF, CombSUM, CombMNZ | [TO FILL] | [TO FILL] |

### 🔍 OBSERVATION: Overall Architecture Fitness
- **What we expected:** [TO FILL]  
- **What actually happened:** [TO FILL]  
- **Why it happened (root cause):** [TO FILL]  
- **Production implication for AI-PMS:** [TO FILL]  

---

# D2. Embedding Model Comparison

Side-by-side UMAP projections showing how each embedding model separates AI-PMS document types in vector space.

**Figure D2.1: UMAP Projections — Replace with actual experiment output**

## D2.1 Quantitative Comparison

| Metric | MiniLM L6-v2 | bge-large en-v1.5 | nomic embed | Winner | Margin | Notes |
|--------|--------------|-------------------|-------------|--------|--------|------|
| Embedding Dimension | 384 | 1024 | 768 | N/A | N/A | Affects index size |
| Index Size (1000 chunks) | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| Embedding Latency (p95) | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| Domain Term Separation | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| Contract Clause P@5 | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| NCR P@5 | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| DPR P@5 | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| Cross-Entity Confusion Rate | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |

## D2.2 Domain-Specific Observations

### 🔍 OBSERVATION: Metro-rail domain terms clustering (OHE, TBM, ballastless track)
- What we expected: [TO FILL]  
- What actually happened: [TO FILL]  
- Why it happened (root cause): [TO FILL]  
- Production implication for AI-PMS: [TO FILL]  

### 🔍 OBSERVATION: Cross-entity separation quality (do contracts separate from NCRs?)
- What we expected: [TO FILL]  
- What actually happened: [TO FILL]  
- Why it happened (root cause): [TO FILL]  
- Production implication for AI-PMS: [TO FILL]  

**Recommended Model:** [TO FILL — with justification based on above data]

---

# D3. Chunking Strategy Comparison

**Figure D3.1: Chunking Impact by Document Type — Replace with actual data**

## D3.1 Strategy-by-Document-Type Matrix

| Strategy | Contract P@5 | NCR P@5 | DPR P@5 | Corresp. P@5 | Best For |
|----------|-------------|---------|---------|--------------|----------|
| Fixed 512 tokens | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| Recursive character | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| Semantic chunking | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| Document-structure | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| Parent-child | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |

### 🔍 OBSERVATION: Which chunking strategy fails worst for FIDIC contracts, and why?
- What we expected: [TO FILL]  
- What actually happened: [TO FILL]  
- Why it happened (root cause): [TO FILL]  
- Production implication for AI-PMS: [TO FILL]  

### 🔍 OBSERVATION: Does parent-child retrieval consistently outperform flat chunking?
- What we expected: [TO FILL]  
- What actually happened: [TO FILL]  
- Why it happened (root cause): [TO FILL]  
- Production implication for AI-PMS: [TO FILL]  

---

# D4. Failure Experiment Results

Each experiment is designed to expose a specific RAG failure mode. Document failures more carefully than successes.

## FE-01: Cross-Entity Confusion
- Query Used: [TO FILL]  
- Retrieved Chunks (Top 5): [TO FILL]  
- Generated Answer: [TO FILL]  
- Expected Correct Answer: [TO FILL]  
- Failure Mode Observed: [TO FILL]  
- Root Cause: [TO FILL]  
- Fix Applied (if any): [TO FILL]  
- Result After Fix: [TO FILL]  

## FE-02: Wrong Contract Version
(Same structure...)

## FE-03: Long Document Summary Bias  
(Same structure...)

## FE-04: Adversarial Out-of-Scope  
(Same structure...)

## FE-05: Tenant Data Leakage  
(Same structure...)

---

# D5. Retrieval Strategy Head-to-Head Comparison

## D5.1 Hybrid Search Architecture  
**Figure D5.1: Hybrid Search with Reciprocal Rank Fusion**

## D5.2 Consolidated Metrics  
**Figure D5.2: Strategy Performance Comparison — Replace with actual data**

## D5.3 Detailed Metrics Table

| Strategy | P@5 | P@10 | MRR | NDCG @10 | Latency p95 | LLM Calls | Verdict |
|----------|-----|------|-----|----------|-------------|-----------|---------|
| Naive Vector Only | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | 1 | [TO FILL] |
| + Metadata Filter | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | 1 | [TO FILL] |
| Hybrid (BM25+Vec+RRF) | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | 1 | [TO FILL] |
| Hybrid + Rerank (ms-marco) | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | 1 | [TO FILL] |
| Hybrid + Rerank (bge-v2-m3) | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | 1 | [TO FILL] |
| HyDE | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | 2 | [TO FILL] |
| Multi-Query | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | 3–5 | [TO FILL] |
| Contextual Retrieval | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] | 0* | [TO FILL] |

---

# D6. Agentic RAG & Multi-Hop Retrieval

## D6.1 LangGraph Architecture  
**Figure D6.1: Agentic RAG with LangGraph StateGraph**

## D6.2 Query Router  
**Figure D6.2: Query Router — Strategy Selection Logic**

## D6.3 Multi-Hop Query Trace Log  
(Keep same table format as original)

## D6.4 Router Accuracy  
(Keep table)

---

# D7. RAGAS Evaluation Results

**Figure D7.1: RAGAS Metrics — Baseline vs. Final**

## D7.1 Overall Metrics  
(Keep table)

## D7.2 Metrics by Query Category  
(Keep table)

⚠️ **REMINDER:**  
These metrics are on **SYNTHETIC data**.  
Re-evaluate on real STAMP data post-DMRC engagement.

---

# D8. Latency Analysis & NFR-04 Compliance

**Figure D8.1: Latency Budget Breakdown**

## D8.1 Component-Level Latency  
(Keep table)

---

# D9. Tenant Isolation & Security Validation

## D9.1 Cross-Tenant Leakage Test Results  
(Keep table)

## D9.2 Fallback Behavior Validation  
(Keep table)

---

# D10. Structured Experiment Log

Minimum 15 experiment entries required.

## Experiment EXP-001  
- Date: [TO FILL]  
- Experimenter: [TO FILL]  
- Hypothesis: [TO FILL]  
- Strategy / Config: [TO FILL]  
- Dataset Used: [TO FILL]  

**Retrieval Metrics**  
P@5: [ ]  P@10: [ ]  MRR: [ ]  NDCG@10: [ ]  

**Answer Metrics**  
Faithfulness: [ ]  Relevancy: [ ]  Completeness: [ ]  

**Latency**  
p50: [ ] ms  p95: [ ] ms  p99: [ ] ms  

- Result (vs. baseline): [TO FILL]  
- Surprising Finding: [TO FILL]  
- Production Implication: [TO FILL]  

(Repeat template up to EXP-015+)

---

# D11. Architecture Decision Summary

| Decision | Recommendation | Evidence (Exp IDs) | Trade-offs / Risks |
|----------|---------------|-------------------|-------------------|
| Embedding Model | [TO FILL] | [TO FILL] | [TO FILL] |
| Chunking: Contracts | [TO FILL] | [TO FILL] | [TO FILL] |
| Chunking: NCRs | [TO FILL] | [TO FILL] | [TO FILL] |
| Chunking: DPRs | [TO FILL] | [TO FILL] | [TO FILL] |
| Retrieval Strategy | [TO FILL] | [TO FILL] | [TO FILL] |
| Reranking Model | [TO FILL] | [TO FILL] | [TO FILL] |
| Fusion Method | [TO FILL] | [TO FILL] | [TO FILL] |
| GraphRAG Scope | [TO FILL] | [TO FILL] | [TO FILL] |
| Query Routing | [TO FILL] | [TO FILL] | [TO FILL] |
| LLM for Generation | [TO FILL] | [TO FILL] | [TO FILL] |

---

## D11.1 Open Questions & Deferred Items

| Open Question | Blocked By | When Resolvable |
|--------------|-----------|----------------|
| Real data evaluation accuracy | DMRC engagement / STAMP data | Post-pilot kickoff |
| Domain embedding fine-tuning | Sufficient real corpus | Phase 2 (Tier 1 maturity) |
| Production load testing | Hardware provisioning + L40S GPUs | Post-GPU procurement |
| [TO FILL] | [TO FILL] | [TO FILL] |

---

**End of Deliverables Document**  
All `[TO FILL]` fields must be completed by end of Day 10.