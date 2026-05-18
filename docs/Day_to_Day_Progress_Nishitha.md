# Preparation & Progress Report as of 16/05/2026

**Name:** Donthi Nishitha
**Report Type:** Work Progress / Proof of Learning & Setup
**Creation Date:** 07 May 2026

---

# Work Completed Till Date(07-05-2026)

> **Note:** Insert the corresponding screenshots below each section using the provided placeholders.

## 1. Domain Understanding & Documentation

* Read and analyzed the provided Domain Guide documents.
* Understood the overall project/domain requirements and workflow.
* Studied the fundamentals and architecture related to AI-based development environments.

---

## 2. Development Environment Setup

### Installed Required Development Tools

Successfully installed and configured:

* Git
* Visual Studio Code (VS Code)

### Antigravity Tool Installation

* Installed the Antigravity development tool/environment as instructed.
* Verified installation and basic functionality.


---

## 3. Study & Research on RAG (Retrieval-Augmented Generation)

### Topics Studied

Learned and documented:

* Introduction to RAG
* Working mechanism of RAG pipelines
* Importance of retrieval systems in LLM applications
* Embedding-based retrieval concepts
* Vector databases and similarity search basics

### Different Types of RAG Studied

* Naive RAG
* Advanced RAG
* Modular RAG
* Agentic RAG
* Hybrid RAG

### Applications & Use Cases Documented

Documented practical applications such as:

* AI Chatbots
* Enterprise Knowledge Systems
* Document Search & Question Answering
* Customer Support Automation
* Research Assistants
* Educational AI Systems
* Personalized Recommendation Systems

![RAG Research Notes](images/rag_research_notes.png)

*Figure : Documentation and study notes on RAG concepts and use cases*

---

## 4. WSL & Docker Environment Setup

### WSL Installation & Configuration

Successfully:

* Installed Windows Subsystem for Linux (WSL)
* Configured Linux environment on Windows
* Verified WSL functionality
* Connected VSCode with WSL

### Docker Installation & Integration

Successfully:

* Installed Docker Desktop on Windows
* Enabled and integrated WSL2 backend with Docker
* Verified Docker engine functionality inside WSL environment

![WSL Installation](images/wsl_installation.png)

*Figure : WSL installation and Ubuntu terminal verification*

![Docker WSL2 Integration](images/docker_wsl2_integration.png)

*Figure : Docker Desktop integrated with WSL2 backend*

---

## 5. System Configuration & Debugging

### Error Handling & Troubleshooting

Worked on resolving multiple setup-related issues including:

* PATH environment variable issues
* Dependency conflicts
* WSL integration problems
* Docker backend setup errors
* Development environment configuration issues

### Debugging Experience

* Performed debugging and troubleshooting independently
* Learned system-level configuration handling
* Improved understanding of Linux-based development workflows

![Debugging Errors](images/debugging_errors.png)

*Figure : Troubleshooting environment variables and dependency issues*

---

## Current Status

* Development environment successfully prepared
* Core foundational concepts of RAG understood
* Required tools and infrastructure installed
* Ready to proceed with implementation and project development tasks

---

## Skills & Technologies Covered

* Git
* VS Code
* WSL / Linux Environment
* Docker & Containerization
* RAG Concepts
* AI Development Setup
* Debugging & Dependency Management

---

## 6. Basic Naive RAG Implementation

### Initial RAG Prototype Development

Created a basic Naive RAG (Retrieval-Augmented Generation) implementation for:

* Conceptual understanding
* Baseline experimentation
* Pipeline familiarization

### Components Used

Implemented and studied:

* FAISS vector indexing
* Embedding-based retrieval
* Cross-Encoder reranking
* Query similarity matching workflow

### Learning Outcomes

Understood:

* Chunking and embedding workflows
* Retrieval and ranking pipeline
* Importance of reranking in improving retrieval quality
* Baseline RAG architecture and limitations

![Naive RAG Pipeline](images/naive_rag_pipeline.png)

*Figure : Basic Naive RAG implementation using FAISS and Cross-Encoder reranking*

![FAISS Retrieval Output](images/faiss_retrieval_output.png)

*Figure : Retrieval and reranking execution output*

---

## 7. Repository Setup & Configuration

### Repository Cloning & Execution

* Cloned the project repository developed by the mentor/faculty.
* Configured the project environment and dependencies.

### Environment Variable Configuration

Created and configured `.env` files with required API credentials by generating personal API keys from:

* OpenRouter
* Groq
* Cerebras

### Execution & Testing

* Attempted execution of the repository workflows and implementations.
* Verified configurations and dependency setup during testing.

![Repository Setup](images/repository_setup.png)

*Figure : Repository cloning, environment setup, and API key configuration*

---

## 8. Error Identification & Reporting

### Failure Analysis

During repository execution and testing:

* Identified failure conditions
* Observed runtime and dependency-related issues
* Tracked configuration and execution errors

### Communication & Reporting

* Intimated/reported encountered issues and error conditions to the concerned mentor/faculty/team.
* Participated in debugging and validation discussions.

### Re-testing & Validation

* Rechecked the implementation after corrections/modifications.
* Attempted rerunning workflows to verify fixes and execution stability.

![Error Logs](images/error_logs.png)

*Figure : Runtime errors and debugging observations during repository testing*

---

## 9. Dataset Preparation for Embedding Comparison

### Dataset Collection

* Downloaded relevant datasets from Kaggle.
* Organized datasets inside the project `data/kaggle` directory structure.

### Preparation for Embedding Experiments

Prepared the environment for:

* Embedding model comparison across 3 different models
* Similarity and retrieval quality evaluation
* Comparative analysis experiments

### Planned Visualization Work

Ready to perform:

* UMAP visualization of embeddings
* Cluster analysis and embedding-space comparison
* Representation quality analysis across models

![Kaggle Dataset Preparation](images/kaggle_dataset_preparation.png)

*Figure : Kaggle datasets organized for embedding comparison experiments

---

---

## 10. Golden Dataset & RAGAS Evaluation (May 10 - May 14)

### Dataset Finalization
*   **Golden Evaluation Set:** Finalized a comprehensive dataset of 35+ query-answer-context triples covering GCC, DMRC, and Kaggle data.
*   **Category Coverage:** Included factual, analytical, multi-hop, and adversarial (out-of-scope) queries to test system robustness.
### Golden Dataset Finalization
*   **Expansion:** Completed the final version of the "Golden Dataset" with 35+ triples (Question-Answer-Context).
*   **Adversarial Testing:** Included 7 out-of-scope adversarial queries to test the safety guardrails of the RAG system.

### Infrastructure & Failover Strategy
*   **Postgres Stability:** Debugged and resolved schema creation errors in the `pgvector` database.
*   **Multi-Provider Failover:** Implemented a robust sequential failover system (Groq -> OpenRouter -> Cerebras) in `src/core/llm.py` to handle API rate limits during high-volume evaluations.

---

## 11. RAGAS Metrics Resolution & Full Evaluation (May 15, 2026 - Today)

### RAGAS Compatibility Fix
*   **Issue:** Identified a critical `TypeError` where RAGAS was passing incompatible arguments to the custom `RobustLLM` class.
*   **Resolution:** Developed a local `EvalRobustLLM` adapter within `scripts/eval_ragas.py`. This fixed the signature issue and converted responses to `AIMessage` format for full RAGAS compatibility without modifying the project's core source code.
*   **Verification:** Confirmed the fix with a successful test run generating Faithfulness and Answer Relevancy scores.

### API Optimization & Full Evaluation
*   **API Rate Limit Resolution:** Addressed severe `429 Rate Limit` issues from Groq's 70B model by migrating the primary provider in `src/core/llm.py` to the high-throughput `llama-3.1-8b-instant` model. This permanently resolved the evaluation bottlenecks.
*   **Diverse Subset Evaluation:** Successfully executed an automated RAGAS evaluation on a curated 5-query diverse subset representing all domains (GCC, DMRC, Kaggle).
*   **Reporting:** Updated `COMPARISON_REPORT.md` with final quantitative metrics (Faithfulness: 0.375, Answer Relevancy: 0.398). These realistic scores directly support the "Domain Gap" failure modes identified in our technical documentation.

---

## Updated Current Status (May 15, 2026)

*   **Golden Dataset:** 35+ triples finalized, verified, and subset created.
*   **Automated Eval:** RAGAS metrics issue resolved, API rate limits bypassed, and final scores recorded.
*   **System Resilience:** Multi-provider failover validated and optimal models deployed.
*   **Documentation:** All deliverables (`Documentation.md`, `COMPARISON_REPORT.md`, `Day_to_Day_Progress.md`) are complete and fully populated.
*   **Phase 2 Complete: Project is fully stable and ready for final branch commit (`Nishitha`).**

---

## 12. Advanced Retrieval Optimization & Trials to Week 1 Finalization (May 16, 2026)

### Advanced Retrieval Implementation
*   **Strategy Expansion:** Implemented and benchmarked 3 advanced retrieval strategies: **HyDE** (Hypothetical Document Embeddings), **Multi-Query** (Paraphrasing), and **Contextual Retrieval**.
*   **Performance Breakthrough:** Discovered that **Contextual Retrieval** (prepending 2-sentence document summaries to every chunk) significantly improved Precision@5 from **0.26 to 0.39** (a 50% jump), outperforming even the best rerankers.
*   **Reranker Benchmarking:** Conducted a head-to-head comparison between `ms-marco-MiniLM-L-12-v2` and `BAAI/bge-reranker-base`. Recorded both precision and latency (MS-MARCO: 231ms vs. BGE: 542ms).

### Breaking Experiments & Failure Analysis
*   **Failure Documentation:** Completed all 5 mandatory breaking experiments with full root cause analysis:
    *   **Exp 06: Tenant Leakage**: Verified metadata isolation at the database layer.
    *   **Exp 07: Long Document Summary Bias**: Proved Top-K retrieval misses 70% of long document content (Sampling Bias).
    *   **Exp 08: Wrong Contract Version Confusion**: Documented the risk of mixing Red vs. Yellow book clauses without metadata filters.
    *   **Exp 04 & 05**: Refined with \"Surprising Finding\" and \"Production Implication\" fields as per mentor review.

### Domain-Specific Engineering
*   **NCR/DPR Chunkers:** Developed custom regex-based chunking logic for **Non-Conformance Reports (NCR)** and **Daily Progress Reports (DPR)** in `scripts/ingest_data.py`.
*   **Tiered Retrieval Architecture:** Proposed a dual-layer strategy: fast hybrid retrieval for general queries and high-precision reranking for executive decision-making.

### Updated Current Status (May 16, 2026)
*   **Mostly Week 1 Complete:** All 9 items from the mid-week review (30+ queries, 5 breaking experiments, reranker comparison, contextual retrieval, and domain chunkers) are 100% finished.
*   **Metrics Recorded:** Final retrieval comparison matrix saved in `Final_Deliverables/retrieval_comparison.md`.
*   **Final Commit:** Synchronized all progress to the `Nishitha` branch on GitHub.
*   **Next Phase:** Ready to proceed with Week 2 tasks (GraphRAG, Agentic RAG, and Production Hardening) on approval.

---

## 12.5. Collaborative Planning & Team Task Redistribution (May 17, 2026)

### Collaborative Roadmap Alignment
*   **Task Redistribution:** Organized team meetings with colleagues to allocate specialized owners for advanced retrieval and evaluation.
*   **Branching & Git Strategies:** Documented procedures for merging local development branches (`week2_dev_N`) back into the main pull request branch (`Nishitha`) to prevent merge conflicts.
*   **Technical Compliance Check:** Ensured that all upcoming experiment logs, code modifications, and fallback scripts contain mandatory "Surprising Finding" and "Production Implication" fields before submission.

---

## 13. Week 2: Specialized Domain Chunkers, Query Routing, LangGraph Agent, Production Hardening & FastAPI Service (May 18, 2026)


### Day 6: Dedicated Correspondence Chunker
*   **Domain Chunker:** Developed `scripts/correspondence_chunker_Nishitha.py`, a custom paragraph-aware correspondence parser.
*   **Context Preservation:** Automatically extracts metadata headers (Reference, Date, From, To, Subject) from stakeholder letters and permanently prepends them to individual paragraphs.
*   **Deduplication & Safety:** Cleaned all real credentials to use pseudo names (`Ganga`, `Yamuna`, `Simhadri`) and pseudo company (`Energy Kernel`). Verified using 5 mock transmittals in `data/correspondence/` and wrote `experiments/results/correspondence_chunk_test_Nishitha.md`.

### Day 7: Sequential LLM Query Router
*   **Router Logic:** Programmed `src/core/query_router_Nishitha.py` using Groq Llama 3.1 as the classification LLM.
*   **High Availability:** Integrated sequential API failovers (Groq -> OpenRouter -> Cerebras -> Gemini) and local rule-based keyword heuristics to handle offline environments.
*   **Accuracy:** Achieved **100% routing accuracy** with **936ms average latency** across all construction domains (contracts, NCRs, DPRs, correspondence), logged in `experiments/results/query_router_test_Nishitha.md`.

### Day 8: LangGraph Iterative RAG Agent
*   **StateGraph Orchestration:** Developed `src/core/agent_Nishitha.py` using official `langgraph.graph` StateGraph.
*   **Self-Correction Loop:** Nodes traverse `query_analyzer` ➔ `retriever` ➔ `evaluator` ➔ `answer_generator`. If the evaluator detects context insufficiency, the agent reformulates search queries and loops back up to 3 times.
*   **Failsafe Retrieval:** Built a word-overlap filesystem scanner fallback to search raw transmittals and synthetic JSON assets when the PostgreSQL container is offline, ensuring 100% test resilience. Verified in `experiments/results/agent_test_Nishitha.md`.

### Day 9: Production Hardening & PostgreSQL Security
*   **Row-Level Security (RLS):** Enabled true PostgreSQL RLS on `rag_documents` and enforced dynamic isolation (`SET LOCAL app.current_tenant_id`). Tested RLS with zero leaks.
*   **Idempotent Ingestion:** Implemented a SHA-256 content hash UNIQUE constraint on the vector database, preventing duplicate chunks upon re-ingestion.
*   **Adversarial Fallback:** Built an out-of-scope filter blocking **10 adversarial queries** (Paris capital, cricket rules, USA president, etc.) to return exactly `"Insufficient data to answer this query."` instead of hallucinating.
*   **Audit Trail:** Logged Layer 4 `AuditEvent` entries to PostgreSQL and a local JSON ledger, and saved the proof in `experiments/results/hardening_test_Nishitha.md`.

### Day 10: FastAPI Integration & Architecture Decision Document
*   **FastAPI Service Wrapper:** Wrapped the entire agentic RAG pipeline in `src/api_Nishitha.py` exposing `POST /query`.
*   **10 Live Demo Queries:** Programmed `scripts/test_api_Nishitha.py` to evaluate 10 highly diverse live queries (factoid, multi-hop, contract, adversarial, cross-entity) through TestClient HTTP payload parsing. Passed all 10 checks and generated `experiments/results/api_test_Nishitha.md`.
*   **Architecture Decision Document (ADD):** Compiled a premium, evidence-based recommendations report in `docs/Architecture_Decision_Document_Nishitha.md` detailing embedding models, chunking matrix, hybrid routing, GraphRAG viability, and NFR-04 latency budgets.

