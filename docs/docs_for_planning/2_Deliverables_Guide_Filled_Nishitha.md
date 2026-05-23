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
|Graph Store|Apache AGE, Neo4j, PostgreSQL Native|**PostgreSQL Native (Recursive CTEs + pgvector)** - Native implementation resolves structural path backtrace queries under 20ms and completely eliminates separate Graph DB infrastructure overhead.|Tested and verified via systems taxonomy ingestion (`scripts/ingest_taxonomy.py`) and custom traversal module (`src/core/graph_rag.py`).|
|Sparse Search|pg_trgm, Elasticsearch|**pg_trgm** - Built into Postgres, zero extra infrastructure, successfully implemented hybrid search.|`exp_03_hybrid_search` results.|
|LLM Serving|vLLM, Ollama|**vLLM** - Fast API serving for Llama models.|Tested locally with Llama 3.1 8B.|
|Orchestration Framework|LangGraph, LlamaIndex, Custom|**LangGraph (StateGraph)** - Fully transitioned. Provides typed state schema, dynamic routing, and iterative self-correction loops.|Verified via Day 8 Agentic RAG execution tracing.|
|Fusion Strategy|RRF, CombSUM, CombMNZ|**RRF** - Reciprocal Rank Fusion provided best baseline combination of BM25 and Vector.|Retriever module implemented RRF successfully.|
|Service Integration|FastAPI, Flask, Express|**FastAPI** - Enterprise microservice wrapper for the LangGraph agent, providing async endpoints and CDM Layer 4 audit logging.|Verified via Day 10 Live Demo Evaluation.|

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
|NCR Regex Parser|Completed (`src/chunkers/ncr_dpr_chunker_BALU.py`)|NCR Forms|
|DPR Regex Parser|Completed (`src/chunkers/ncr_dpr_chunker_BALU.py`)|DPR Reports|
|Correspondence Parser|Completed (`scripts/correspondence_chunker_Nishitha.py`)|Transmittal Letters|

*Observation:* Semantic chunking was correctly identified as best for legal/contract documents compared to naive/simple splitters. Heading-based chunking fails when answers span multiple clauses.

---

### D4. Failure Experiment Results (Conducted by Balu Sir & Nishitha)

| Exp ID | Strategy | Success Rate | Avg Faithfulness | Key Finding |
|---|---|---|---|---|
| **exp_04** | Entity Confusion | 100% | 1.00 | LLM reasoning is a strong "last line of defense" against entity leakage, but metadata filtering is mandatory for production. |
| **exp_05** | Adversarial Guardrails | 100% | 1.00 | High negative pass rate shows LLM acts as a zero-shot filter, effectively refusing out-of-scope queries in milliseconds. |
| **exp_06** | Tenant Leakage | 100% | 1.00 | PostgreSQL Row-Level Security (RLS) policies completely isolate multi-tenant schemas with 0 leaks recorded. |
| **exp_07** | Long Doc Summary Bias | 70% | 0.85 | Top-K vector retrieval covers only a small fraction of long documents causing sampling bias. Map-Reduce chains are required. |
| **exp_08** | Wrong Contract Version | 95% | 0.90 | Querying across Red vs. Yellow Books causes model hallucination without strict schema and metadata indexing. |

---

### D5. Retrieval Strategy Head-to-Head Comparison

|Strategy|Precision@5|Latency (ms)|Notes|
|---|---|---|---|
|Naive Vector Only|0.26|15ms|Baseline vector search using BGE-Large|
|+ Metadata Filter|0.28|16ms|Vector + Entity Type filtering inside WHERE clause|
|Hybrid (BM25+Vec+RRF)|0.83|45ms|Reciprocal Rank Fusion on GIN index|
|Hybrid + ms-marco Rerank|0.96|2531 ms|CPU-benchmarked ms-marco-MiniLM-L-12-v2|
|Hybrid + BGE Rerank|0.98|8207 ms|CPU-benchmarked bge-reranker-v2-m3 (highly precise)|
|HyDE|0.74|110ms|Hypothetical document embeddings via Llama 3.1 instruct|
|Multi-Query|0.70|135ms|Union of three paraphrased query retrievals|
|Contextual Retrieval|0.92|120ms|Document context prepended to individual chunks|

*Observation:* Contextual retrieval and Hybrid+Reranker showed the highest Precision@5 (0.92+). Rerankers proved slow on CPU (2.5s for MS-Marco, 8.2s for BGE). Production recommendation requires GPU serving for rerankers to hit the 5s NFR-04 latency budget.

---

### D7. RAGAS Evaluation Results
*Evaluated on a diverse representative subset.*

| Strategy | Faithfulness | Answer Relevancy |
|---|---|---|
| **Vector Search** | 0.366 | 0.366 |
| **Hybrid Search** | 0.833 | 0.766 |
| **Agentic RAG (StateGraph)** | **0.950** | **0.890** |

*(Note: These represent the overall average scores across the multi-source Golden Dataset. High performance on Indian Railways GCC and local DMRC schemas, with excellent safety enforcements on adversarial queries).*

---

### D8. Agentic RAG & Production Hardening (Week 2 Findings)

**D8.1 Agentic Workflow (LangGraph)**
- **Self-Correction:** Implemented iterative looping (up to 3 loops) via LLM evaluator to reformulate queries when retrieved context is insufficient.
- **Failover & Reliability:** Dynamic API failover (`Groq` ➔ `OpenRouter` ➔ `Cerebras` ➔ `Gemini`) ensures 100% router uptime.
- **Offline Resilience:** Failsafe hybrid offline scanner implemented to search raw text/JSON assets if the PostgreSQL container goes down.

**D8.2 Production Hardening & Security**
- **Idempotent Ingestion:** Implemented SHA-256 content hashing to skip duplicate document insertions automatically.
- **Tenant Isolation:** Enforced 100% data separation using PostgreSQL Row-Level Security (`SET LOCAL app.current_tenant_id`). Verified 0 data leaks.
- **Adversarial Fallback:** Pre-retrieval classifier instantly intercepts out-of-scope queries (e.g., "What is the capital of France?") with 100% success (0.01ms latency).
- **Audit Logging:** Integrated CDM Layer 4 `AuditEvent` schema for full traceability of queries, latencies, and chunks.

**D8.3 GraphRAG Performance**
- **Taxonomy Ingestion:** 100% of 383 taxonomy items and 195+ grid cell interfaces from the DMRC spreadsheet loaded into `taxonomy_nodes` and `taxonomy_edges`.
- **Query Latency:** Multi-table SQL JOINs and Recursive CTEs guarantee sub-20ms retrieval latencies for structural path backtraces.
- **Dual-Layer Hybrid:** Successfully complements vector search by returning graph dependencies when vector search yields 'insufficient context'.

---

### D11. Architecture Decision Summary

|Decision|Recommendation|Trade-offs / Risks|
|---|---|---|
|Embedding Model|`bge-large-en-v1.5`|High quality, but larger memory footprint / latency.|
|Chunking: Contracts|Semantic Chunking|Computationally heavier than naive recursive splitting.|
|Retrieval Strategy|Hybrid (BM25 + Vector) + Contextual Retrieval|Contextual provides best precision, hybrid catches exact term matches.|
|Reranking Model|`ms-marco-MiniLM-L-12-v2` (if CPU bound)|BGE reranker is too slow on CPU (8s latency). MS-Marco is faster (2.5s).|
|Query Routing|Mandatory Pre-Retrieval Classifier|Need lightweight router to block adversarial queries before DB hit.|
|Graph Store|PostgreSQL Native self-referential graph model|Low-latency, natively scales inside relational ecosystem; fully operational for Systems Taxonomy.|

**Open Questions:**
- Production load testing blocked by GPU provisioning.
- Dynamic auto-ingestion pipeline for unstructured stakeholder correspondence into the systems taxonomy graph.
