# Bootcamp Status & Final Execution Plan

## PART 1: MENTOR'S EMAIL REQUIREMENTS

### 1.1 Email Progress Checklist
Here is exactly what was requested in the mentor's email, mapped against the current code in your branches:

**Phase 0 & Early Phase 1 (Completed Before Email)**
- ✅ Fix critical evaluation bug (DEF-01 - `ask_rag()`)
- ✅ Modularize code into `src/core/` (pipeline, retriever, llm)
- ✅ `pgvector` integration working with full metadata schema
- ✅ Hybrid search with `pg_trgm` implemented
- ✅ 3 embedding models compared with UMAP visualizations
- ✅ 3 chunking strategies compared (semantic, simple, paragraph)
- ✅ Docker compose setup added
- ✅ Datasets loaded (Kaggle RAG, Indian Railways, synthetic DMRC)

**Next Steps Requested in Email (Found Implemented in Branches!)**
- ✅ Expand evaluation query set to 30+ queries
- ✅ Complete all 5 breaking experiments
- ✅ Implement cross-encoder reranking comparison
- ✅ Implement HyDE and multi-query retrieval
- ✅ NCR and DPR chunkers
- ✅ RAGAS automated pipeline
- ✅ Golden evaluation dataset (30+ triples)
- ✅ Fill in "Surprising Finding" in logs

**What is Pending from Email (❌)**
- ❌ **Independent Branch Ownership:** The mentor checks git commits. Balu Sir needs to officially own the `dev-uday` work on his `balu` branch.
- ❌ **Final Execution & Reports:** Run the final RAGAS metrics against the 30+ dataset to fill out the `D11 Architecture Decision Summary` in the Deliverables Guide.

### 1.2 Work Division for Email Items (Strictly 2 People)
*If your goal is just to finish the email requirements, here is the division:*

**👩‍💻 Nishitha (Environment: WSL / Ubuntu)**
- **Final RAGAS Execution:** Run `eval_ragas.py` against the 30+ dataset to generate metrics.
- **Architecture Documentation (D11):** Fill out the final `Architecture Decision Summary` in the `Deliverables_guide`.

**👨‍💻 K. Bala Chowdappa / Balu Sir (Environment: Windows)**
- **Take Official Code Ownership:** Merge `dev-uday` code into the `balu` branch.
- **Consolidate Comparison Report:** Finalize the `COMPARISON_REPORT.md` combining insights from all breaking experiments.

---

## PART 2: THE FULL 2-WEEK PLAN REQUIREMENTS

### 2.1 2-Week Plan Progress Checklist
Looking strictly at the **Full 2-Week Plan (Days 7-10)**, the following advanced features were never mentioned in the email and are **NOT DONE (❌)**:

- ❌ **GraphRAG (Apache AGE):** Loading Metro Rail Systems Taxonomy into `Apache AGE`.
- ❌ **Query Router:** Building an LLM query router to classify queries (Vector vs. Graph).
- ❌ **Agentic RAG with LangGraph:** Implementing an iterative multi-hop retrieval state graph.
- ❌ **80+ Evaluation Queries:** Expanding the 30+ dataset to 80+ queries.
- ❌ **Integration Demo (FastAPI):** Wrapping the pipeline in a `FastAPI` service with audit logs.
- ❌ **Production Hardening:** Testing fallback behaviors (preventing hallucination).
- ❌ **Contextual Retrieval:** Implementing Contextual Retrieval (situating chunks).
- ❌ **Correspondence Chunker:** Building the parser for correspondence documents.

### 2.2 Work Division for 2-Week Plan Items (Strictly 2 People)
*If your goal is to hit 100% completion of the entire 2-Week Plan, add these tasks:*

**👩‍💻 Nishitha (Environment: WSL / Ubuntu)**
- **Agentic RAG (LangGraph):** Build the iterative, multi-hop retrieval StateGraph.
- **Integration Demo & GraphRAG:** Install `Apache AGE` on WSL for GraphRAG and wrap the final pipeline into a `FastAPI` service.

**👨‍💻 K. Bala Chowdappa / Balu Sir (Environment: Windows)**
- **Query Router & Data Expansion:** Build the LLM Query Router and expand the golden dataset from 30+ to 80+ queries.
- **Remaining Chunkers & Contextual Retrieval:** Finish the Correspondence chunker and test contextual retrieval.
- **Windows Pipeline Verification:** Run the chunkers and cross-encoder reranking scripts on Windows to verify CPU latency.
