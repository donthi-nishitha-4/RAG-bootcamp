# Enterprise RAG Bootcamp

## DELIVERABLES DOCUMENT (Filled based on Cross-Branch Execution)

##### Diagrams | Metrics | Observations | Architecture Decisions AI-PMS for DMRC — 2-Week Intensive

|Team Lead|K. Bala Chowdappa (Balu Sir)|
|---|---|
|Team Members|Nishitha|
|Bootcamp Dates|May 2026|
|Document Version|v1.1 (Updated via Cross-Branch Consolidation)|
|Git Repository|aipms-rag-bootcamp|
|Data Classification|SYNTHETIC DATA ONLY — DMRC Mega Metro (AI-generated, valid for pipeline testing only)|

---

### D1. RAG Pipeline Architecture
**Architecture Decision Log**

|Decision Point|Options Evaluated|Decision & Rationale|Evidence|
|---|---|---|---|
|Primary Vector Store|pgvector, ChromaDB, FAISS|**pgvector** - Native PostgreSQL extension allows strict RLS and advanced metadata filtering (tenant_id).|Integration tested and working with full schema.|
|Sparse Search|pg_trgm, Elasticsearch|**pg_trgm** - Built into Postgres, zero extra infrastructure, successfully implemented hybrid search.|`exp_03_hybrid_search` results.|
|LLM Serving|vLLM, Ollama|**vLLM** - Fast API serving for Llama models.|Tested locally with Llama 3.1 8B.|
|Orchestration Framework|LangGraph, LlamaIndex, Custom|**Custom Pipeline** (Transitioning to LangGraph) - Needed for explicit control before agentic deployment.|`src/core/pipeline.py` modularization.|
|Fusion Strategy|RRF, CombSUM, CombMNZ|**RRF** - Reciprocal Rank Fusion provided best baseline combination of BM25 and Vector.|Retriever module implemented RRF successfully.|

---

### D2. Embedding Model Comparison

**D2.1 Quantitative Comparison**

|Metric|MiniLM L6-v2|bge-large en-v1.5|nomic embed|Winner|Notes|
|---|---|---|---|---|---|
|Embedding Dimension|384|1024|768|N/A|Affects index size|
|Embedding Latency (ms/doc)|7.03 ms|54.28 ms|43.74 ms|MiniLM|CPU Latency|
|Domain Term Separation|Poor|Excellent|Good|BGE-Large|Separates OHE, TBM well.|

**Recommended Model:** `BAAI/bge-large-en-v1.5` 
*Justification: Gives the best domain-term separation (metro-rail terms vs generic text) as proven by the UMAP visualizations, despite the higher latency cost.*

---

### D3. Chunking Strategy Comparison

|Strategy|Contract P@5|Best For|
|---|---|---|
|Fixed 512 tokens|Poor|Generic text|
|Semantic chunking|0.66 (Faithfulness 1.0)|Legal/Contract docs (GCC)|
|Document-structure|N/A|Hierarchical docs|
|NCR Regex Parser|Testing|NCR Forms|
|DPR Regex Parser|Testing|DPR Reports|

*Observation:* Semantic chunking was correctly identified as best for legal/contract documents compared to naive/simple splitters. Heading-based chunking fails when answers span multiple clauses.

---

### D4. Failure Experiment Results (Conducted by Balu Sir & Nishitha)

| Exp ID | Strategy | Success Rate | Avg Faithfulness | Key Finding |
|---|---|---|---|---|
| **exp_04** | Entity Confusion | 100% | 1.00 | LLM reasoning is a strong "last line of defense" against entity leakage, but metadata filtering is mandatory for production. |
| **exp_05** | Adversarial Guardrails | N/A | 1.00 | High negative pass rate shows LLM acts as a zero-shot filter, effectively refusing out-of-scope queries. |
| **exp_07** | Long Doc Summary Bias | N/A | N/A | Documented in `exp_07`. Top-5 retrieval covers only a tiny fraction of the document causing sampling bias. |
| **exp_08** | Wrong Contract Version | N/A | N/A | Documented in `exp_08`. |

---

### D5. Retrieval Strategy Head-to-Head Comparison

|Strategy|Precision@5|Latency (ms)|Notes|
|---|---|---|---|
|Naive Vector Only|0.26|-|Baseline vector search|
|+ Metadata Filter|0.26|-|Vector + Entity Type filtering|
|Hybrid (BM25+Vec+RRF)|0.26|-|Reciprocal Rank Fusion|
|Hybrid + ms-marco Rerank|0.26|2531 ms|ms-marco-MiniLM-L-12-v2|
|Hybrid + BGE Rerank|0.22|8207 ms|bge-reranker-v2-m3|
|HyDE|0.24|-|Hypothetical doc embeddings|
|Multi-Query|0.07|-|Union of paraphrase retrievals|
|Contextual Retrieval|0.39|-|Document context prepended to chunks|

*Observation:* Contextual retrieval showed the highest Precision@5 (0.39). Rerankers proved extremely slow on CPU (2.5s for MS-Marco, 8.2s for BGE). Production recommendation requires GPU for reranking to hit 5s NFR.

---

### D7. RAGAS Evaluation Results
*Evaluated on a diverse representative subset.*

| Strategy | Faithfulness | Answer Relevancy |
|---|---|---|
| **Vector Search** | 0.375 | 0.398 |
| **Hybrid Search** | [TBD Final Run] | [TBD Final Run] |

*(Note: These are synthetic baseline metrics. Final 30+ query run will populate full metrics).*

---

### D11. Architecture Decision Summary

|Decision|Recommendation|Trade-offs / Risks|
|---|---|---|
|Embedding Model|`bge-large-en-v1.5`|High quality, but larger memory footprint / latency.|
|Chunking: Contracts|Semantic Chunking|Computationally heavier than naive recursive splitting.|
|Retrieval Strategy|Hybrid (BM25 + Vector) + Contextual Retrieval|Contextual provides best precision, hybrid catches exact term matches.|
|Reranking Model|`ms-marco-MiniLM-L-12-v2` (if CPU bound)|BGE reranker is too slow on CPU (8s latency). MS-Marco is faster (2.5s).|
|Query Routing|Mandatory Pre-Retrieval Classifier|Need lightweight router to block adversarial queries before DB hit.|

**Open Questions:**
- Production load testing blocked by GPU provisioning.
- GraphRAG evaluation deferred to final phase.
