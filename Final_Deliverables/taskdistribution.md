# 🚀 AI-PMS RAG BOOTCAMP: TASK DISTRIBUTION & EXECUTION STRATEGY

---

## 1. TEAM BEHAVIOR MODEL: "BUILD FAST, INTEGRATE FASTER"
This project operates on a **Continuous Integration (CI)** model where Ubuntu is the final arbiter of truth.

*   **BUILDERS (WSL / Windows)**:
    *   **Motto**: "If it works on my machine, push it."
    *   **Task**: Aggressive feature development. Do not wait for perfection.
    *   **Git**: Push to feature branches at least 3 times a day.
*   **EXECUTOR (Ubuntu - Lead)**:
    *   **Motto**: "If it doesn't run on Ubuntu, it doesn't exist."
    *   **Task**: Pull, Run, Debug, Document. 
    *   **Shift**: Developer (Days 1-5) → Full-time Integrator (Days 6-10).

---

## 2. DAY-WISE EXECUTION PLAN (AVAILABILITY ALIGNED)

### 🗓 WEEK 1: FOUNDATIONS & FAILURE
| Day | Available Team | Focus | Primary Goal |
| :--- | :--- | :--- | :--- |
| **Day 1–2** | Ubuntu (Only) | Infrastructure & Skeleton | Golden Skeleton & Repo Setup |
| **Day 3** | Ubuntu + WSL | Failure Experiments | Document 5+ failure modes |
| **Day 4** | Ubuntu + WSL | Hybrid Search | BM25 + Vector + RRF |
| **Day 5** | Ubuntu + WSL | Reranking & Benchmarks | Cross-Encoder integration |

### 🗓 WEEK 2: DOMAIN & AGENTS
| Day | Available Team | Focus | Primary Goal |
| :--- | :--- | :--- | :--- |
| **Day 6** | Ubuntu + WSL + Windows | Domain Parsers | 4 custom doc chunkers |
| **Day 7** | Ubuntu + WSL + Windows | GraphRAG & Routing | Systems Taxonomy Graph |
| **Day 8** | Ubuntu + WSL + Windows | Agentic RAG | LangGraph iterative retrieval |
| **Day 9** | Ubuntu + WSL + Windows | RAGAS & Hardening | 80+ query eval & RLS |
| **Day 10** | Ubuntu + WSL + Windows | Demo & Final Docs | FastAPI Demo & Decision Doc |

---

## 3. TASK ALLOCATION PER DAY

### PHASE 1: SKELETON (Days 1–2) — [UBUNTU ONLY]
*   **Task 1.1**: Unified Docker System (Postgres, vLLM, App).
*   **Task 1.2**: Modular Source Structure (`src/core`, `src/evals`).
*   **Task 1.3**: Baseline Ingestion script for GCC PDFs.
*   **Task 1.4**: First README.md and Setup Guides (WSL/Ubuntu).

### PHASE 2: HYBRID & BREAKING (Days 3–5) — [UBUNTU + WSL]
*   **WSL Builder**: 
    *   Implement Hybrid Search (BM25 logic).
    *   Implement Cross-Encoder Reranking.
*   **Ubuntu Executor**: 
    *   Run "Breaking Experiments" (Entity confusion, Out-of-scope).
    *   Log Baseline Metrics to MLflow.
    *   Debug WSL code merges.

### PHASE 3: DOMAIN & AGENTS (Days 6–10) — [ALL 3 MEMBERS]
*   **Windows Builder**: 
    *   Domain Parsers (NCR, DPR, Correspondence).
    *   FastAPI Service Wrapper.
*   **WSL Builder**: 
    *   GraphRAG (Apache AGE) & Taxonomy Graph.
    *   Agentic RAG (LangGraph implementation).
*   **Ubuntu Executor (Full-time)**: 
    *   Integrate all parsers into Ingestion Pipeline.
    *   Run 80-query RAGAS suite.
    *   Maintain "The System Runs" status.
    *   Final Documentation & Audit Logging.

---

## 4. PARALLEL WORK STRATEGY
*   **Feature Branching**: Every task gets a branch `feature/[name]/[task]`.
*   **No Blocking**: If the Windows dev is stuck on a parser, they push what they have; the Executor fixes the imports/logic on Ubuntu.
*   **Mocking**: Builders use Mock LLMs if API limits are hit; Executor always uses real Groq/Llama 3.1.

---

## 5. EXECUTION LOOP DESIGN
1.  **Builder** → `git push origin feature/xyz`
2.  **Executor** → `git checkout feature/xyz` + `docker-compose up --build`
3.  **Result PASS** → Executor merges to `main` + updates `Documentation.md`.
4.  **Result FAIL** → Executor fixes locally + pushes fix + notifies Builder.

---

## 6. DOCKER SYSTEM DESIGN
*   **One Compose to Rule Them All**: `docker-compose.yml` in root.
*   **Profiles**: `cpu` profile for dev, `gpu` profile for HPC reranking.
*   **Persistent Volumes**: `postgres_data` and `model_cache` to avoid re-downloads.

---

## 7. CROSS-PLATFORM SETUP GUIDE
*   **Ubuntu (Truth)**: Direct Docker execution. Source of truth for paths.
*   **WSL**: Docker Desktop + Ubuntu 22.04 Backend. Shared `/mnt/c` for data.
*   **Windows**: Docker Desktop. Use `.env` to point `DB_HOST` to `localhost`.

---

## 8. INTEGRATION & DEBUG WORKFLOW
*   **Immediate Fix Policy**: If a merge breaks the Ubuntu build, the Executor has 30 minutes to fix it before reverting the commit.
*   **Log Verbosity**: All modules must use `logging` with timestamps for trace-ability across platforms.

---

## 9. DOCUMENTATION SYSTEM DESIGN
*   **Master Deliverable**: `Final_Deliverables/Documentation.md` (Auto-updated via YAML).
*   **Setup Guides**: Individual files in `docs/setup/` for Windows/WSL/Ubuntu.
*   **Experiment Logs**: One Markdown file per experiment in `experiments/`.

---

## 10. TROUBLESHOOTING STRATEGY
*   **Port Conflicts**: Standardize on 5433 (DB) and 8080 (App).
*   **Line Endings**: Enforce `LF` (Unix) via `.gitattributes` to prevent Windows `CRLF` breaking Docker scripts.
*   **Memory Errors**: Aggressive `gc.collect()` in ingestion scripts.

---

## 11. FINAL SYSTEM CHECKLIST
- [ ] End-to-end RAG runs on Ubuntu.
- [ ] Hybrid search beats Vector baseline.
- [ ] 4+ Domain parsers integrated.
- [ ] Agentic RAG handles multi-hop queries.
- [ ] 100% Audit trail in `Documentation.md`.
- [ ] Works on Windows Docker Desktop.
