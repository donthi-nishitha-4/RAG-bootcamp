# 🚀 AI-PMS RAG BOOTCAMP: UBUNTU-CENTRIC EXECUTION STRATEGY

---

## 1. TEAM BEHAVIOR MODEL
*   **Ubuntu (Executor/Lead)**: The ONLY source of truth. If it doesn't run on Ubuntu, it's a failure. Shift from coding (Days 1-5) to full-time integration/debugging (Days 6-10).
*   **WSL/Windows (Builders)**: Feature factories. They push code frequently but never assume it works until the Ubuntu person gives the "Green Light."

---

## 2. DAY-WISE PLAN (MAY 4 - MAY 15)

### 🗓 DAY 1: INFRASTRUCTURE (MAY 4) — [UBUNTU SOLO]
*   **Person: Ubuntu**
    *   **Task**: Unified Docker Infrastructure Setup.
    *   **Output**: `docker-compose.yml`, `Dockerfile`, `.env.example`.
    *   **Verification (Ubuntu)**: Run `docker-compose up -d`. Verify `rag-db` is "Healthy" and `rag-app` is "Started."
    *   **Failure Signal**: `docker ps` shows container "Restarting" or "Exit (1)".
    *   **Fix Hint**: Check for port 5432/5433 conflicts. Check `POSTGRES_PASSWORD` in `.env`.

### 🗓 DAY 2: CORE SKELETON (MAY 5) — [UBUNTU SOLO]
*   **Person: Ubuntu**
    *   **Task**: Modular Source Reorganization.
    *   **Output**: `src/core/`, `src/evals/`, `scripts/` folders with `__init__.py`.
    *   **Verification (Ubuntu)**: Run `export PYTHONPATH=. && python3 src/core/pipeline.py`. Should see "Testing RAG pipeline..." without import errors.
    *   **Failure Signal**: `ModuleNotFoundError: No module named 'src'`.
    *   **Fix Hint**: Ensure `PYTHONPATH` includes the root. Check for missing `__init__.py`.

### 🗓 DAY 3: BREAKING & METADATA (MAY 6) — [UBUNTU + WSL]
*   **Person: WSL (Builder)**
    *   **Task**: Implement Metadata Filtering Logic.
    *   **Output**: `src/core/retriever.py` update with `tenant_id` and `entity_type` filters.
    *   **Verification (Ubuntu)**: Run a test query with a specific `tenant_id`. Check `rag_documents` table to ensure only that tenant's data is returned.
    *   **Failure Signal**: Query returns results from multiple tenants.
    *   **Fix Hint**: Check the `WHERE` clause in `retrieve_similar()`.
*   **Person: Ubuntu (Executor)**
    *   **Task**: Run "Breaking Experiments" Baseline.
    *   **Output**: `experiments/exp_01_baseline_failures.md`.
    *   **Verification (Ubuntu)**: Run `scripts/eval_baseline.py`. Verify it generates low scores for out-of-scope queries.
    *   **Failure Signal**: System hallucinates an answer for "Bitcoin price" instead of failing.
    *   **Fix Hint**: Check the system prompt in `src/core/pipeline.py`.

### 🗓 DAY 4: HYBRID SEARCH (MAY 7) — [UBUNTU + WSL]
*   **Person: WSL (Builder)**
    *   **Task**: Implement RRF (Reciprocal Rank Fusion).
    *   **Output**: `src/core/fusion.py` or update to `retriever.py`.
    *   **Verification (Ubuntu)**: Run a query with specific keywords. Compare results with pure vector search.
    *   **Failure Signal**: Hybrid scores are all 0 or identical to vector.
    *   **Fix Hint**: Check the BM25 `ts_rank` calculation in Postgres.
*   **Person: Ubuntu (Executor)**
    *   **Task**: Postgres Extension Validation.
    *   **Output**: Audit log update in `Documentation.md`.
    *   **Verification (Ubuntu)**: Run `psql -c "SELECT * FROM pg_extension;"`. Must see `vector` and `pg_trgm`.
    *   **Failure Signal**: `pg_trgm` or `vector` missing from output.
    *   **Fix Hint**: Check `scripts/reinit_db.py` execution logs.

### 🗓 DAY 5: RERANKING (MAY 8) — [UBUNTU + WSL]
*   **Person: WSL (Builder)**
    *   **Task**: Cross-Encoder Reranker Integration.
    *   **Output**: `src/core/pipeline.py` update with `CrossEncoder` call.
    *   **Verification (Ubuntu)**: Run query. Check logs to see `scores` before and after reranking.
    *   **Failure Signal**: Output order is identical to retrieval order despite reranking.
    *   **Fix Hint**: Ensure `ranked = sorted(zip(scores, docs), reverse=True)` is actually applied.

---

### 🗓 DAY 6: DOMAIN PARSERS (MAY 11) — [ALL 3 MEMBERS]
*   **Person: Windows (Builder)**
    *   **Task**: FIDIC Contract Hierarchical Chunker.
    *   **Output**: `src/utils/parsers/fidic_parser.py`.
    *   **Verification (Ubuntu)**: Run `python3 scripts/ingest_data.py --file gcc.pdf`. Verify chunks preserve clause numbers (e.g., 20.1).
    *   **Failure Signal**: Chunks are split mid-sentence or lose legal numbering.
    *   **Fix Hint**: Check the regex pattern for `CLAUSE` and `SECTION`.
*   **Person: Ubuntu (Executor)**
    *   **Task**: INGESTION COORDINATION.
    *   **Output**: Fully populated `rag_documents` table with GCC data.
    *   **Verification (Ubuntu)**: `SELECT count(*) FROM rag_documents;` should show > 500 chunks.

### 🗓 DAY 7: GRAPHRAG (MAY 12) — [ALL 3 MEMBERS]
*   **Person: WSL (Builder)**
    *   **Task**: Systems Taxonomy Graph Ingestion.
    *   **Output**: Apache AGE nodes/edges for Metro Taxonomy.
    *   **Verification (Ubuntu)**: Run `scripts/test_graph.py`. Verify it can find interfaces between "Signalling" and "Civil".
    *   **Failure Signal**: `Graph retrieval failed: relation 'age_entities' does not exist`.
    *   **Fix Hint**: Check if `cypher()` calls have the correct graph name.
*   **Person: Ubuntu (Executor)**
    *   **Task**: INTEGRATION & DEBUG.
    *   **Output**: Updated version `v1.5` in `Documentation.md`.

### 🗓 DAY 8: AGENTIC RAG (MAY 13) — [ALL 3 MEMBERS]
*   **Person: WSL (Builder)**
    *   **Task**: LangGraph Iterative Retriever.
    *   **Output**: `src/core/agent.py` using `StateGraph`.
    *   **Verification (Ubuntu)**: Run a multi-hop query. Verify logs show the agent calling `retriever` more than once.
    *   **Failure Signal**: Agent terminates after 1 loop even if confidence is low.
    *   **Fix Hint**: Check the `conditional_edges` in LangGraph setup.

---

## 3. WORKLOAD PROGRESSION
*   **May 4–5 (Phase 0)**: 10% Workload. Focus on "Unbreakable Baseline."
*   **May 6–8 (Phase 1)**: 40% Workload. Parallel development of search logic.
*   **May 9–End (Phase 2)**: 100% Workload. Full parallel execution of Domain/Agentic features.

## 4. UBUNTU ROLE TRANSITION
*   **Until May 8**: Ubuntu lead is a coder. He builds the pipeline.
*   **From May 9**: Ubuntu lead is a "Watchman." He stops writing new features and spends 100% of his time pulling code from Builders, running it on Ubuntu, and fixing integration bugs.

## 5. EXECUTION LOOP
1.  **Builder** pushes code.
2.  **Ubuntu** pulls code.
3.  **Ubuntu** runs Verification Command.
4.  **If FAIL**: Ubuntu fixes code + logs the fix.
5.  **If PASS**: Ubuntu updates `Documentation.md` and bumps version.

## 6. DOCKER DESIGN
*   **Reference Environment**: Ubuntu 22.04 LTS.
*   **Architecture**:
    *   `db`: pgvector/pgvector:pg16.
    *   `app`: Python 3.10 + PyTorch (CPU).
    *   `vllm`: (Optional) External or separate container for LLM serving.

## 7. CROSS-PLATFORM CONSTRAINTS
*   **Windows/WSL**: Never use `C:\` paths in code. Always use relative paths from repo root.
*   **Line Endings**: Git `autocrlf` must be `input` to prevent Windows breaking shell scripts.

## 8. DOCUMENTATION WORKFLOW
*   **Owner**: Ubuntu Executor ONLY.
*   **Master File**: `Final_Deliverables/Documentation.md`.
*   **Audit Trail**: Every verification PASS results in a YAML entry to the audit log.

## 9. FINAL SYSTEM CHECKLIST (MAY 15)
- [ ] End-to-end RAG runs on Ubuntu with 1 command.
- [ ] 4+ Domain parsers successfully ingested real GCC data.
- [ ] Hybrid search (BM25 + Vector) beats pure vector baseline by 20%+.
- [ ] LangGraph agent handles "Time-Bar" multi-hop queries.
- [ ] All 15+ experiment logs committed and verified.
