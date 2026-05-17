# AI-PMS RAG Bootcamp — Production Refactor

This repository has been fully refactored into a modular, production-ready RAG system, addressing all deficiencies identified in the **Day 0 Peer Review** and successfully completing the **Week 1 Bootcamp Deliverables** (Week 2 deliverables are currently in progress).

## 🚀 System Status: ADVANCED EXPERIMENTATION (Nishitha Branch)
- **Architecture**: Modular `src/core/` and `scripts/` structure.
- **Vector Store**: PostgreSQL + `pgvector` with `pg_trgm` for hybrid search.
- **Dataset**: Real-world **Indian Railways GCC**, Synthetic **DMRC Mega Metro** datasets.
- **Team**: **Nishitha** (WSL/Ubuntu) & **K. Bala Chowdappa Sir** (Windows)
- **Setup Guide**: [Detailed Pipeline Setup Guide](docs/guides/pipeline_setup.md)

---

## ✅ Bootcamp Milestones Achieved

| Milestone | Status | Description |
| :--- | :--- | :--- |
| **Working Pipeline** | ✅ Done | Modular `src/core/pipeline.py` returning `{context, answer, chunk_ids, sources}`. |
| **Evaluation Bug Fixed**| ✅ Done | Tautological evaluation resolved. Context and answer are strictly separated. |
| **UMAP Comparison** | ✅ Done | Benchmarked `all-MiniLM`, `bge-large`, `nomic-embed`. `bge-large` selected for best domain separation. |
| **Metadata Filtering** | ✅ Done | Enforced `tenant_id`, `entity_type`, and `contract_standard` filtering. Tested via Tenant Leakage experiment. |
| **Hybrid Search** | ✅ Done | Integrated BM25 via PostgreSQL `pg_trgm` + Vector search + Reciprocal Rank Fusion (RRF). |
| **Breaking Experiments**| ✅ Done | **5 documented failure modes**: Entity Confusion, Adversarial Guardrails, Tenant Leakage, Long Doc Summary, Wrong Contract. |
| **RAGAS Evaluation** | ✅ Done | Integrated **Ragas** metrics via `eval_ragas.py`. |
| **Project Planning** | ✅ Done | Fully mapped deliverables and updated 2-week checklist for strict 2-person execution. |

---

## 🛠 Project Structure
```text
aipms-rag-bootcamp/
├── src/
│   └── core/
│       ├── pipeline.py    # Single source of truth (RAG Logic)
│       ├── retriever.py   # pgvector, pg_trgm & metadata filtering
│       └── llm.py         # Resilient fallback chain
├── scripts/
│   ├── run_experiments.py # Automated batch testing & logging
│   └── ...
├── data/                  # Raw PDFs and processed JSON chunks
├── experiments/           # 8 structured markdown logs with root cause analysis
│   └── results/           # Raw JSON/MD results of evaluations
├── docs/                  # Comparison reports and images
│   ├── docs_for_planning/ # Updated 2-week plans and execution guides
│   ├── guides/            # Setup and installation guides
│   └── images/            # Visualizations (UMAP, etc.)
└── tests/                 # Unit and integration tests
```

---

## 📊 Core Metrics & Results
*Latest evaluations across varied datasets:*

- **Faithfulness**: ~1.00 on Baseline / Semantic evaluations (LLM rejects out-of-scope).
- **Domain Term Separation**: `BAAI/bge-large-en-v1.5` identified as the winner for Metro-rail terms.
- **Reranker Latency**: Identified significant CPU bottleneck with `bge-reranker-v2-m3` (~8s) vs `ms-marco` (~2.5s).
- **Adversarial Resilience**: 100% negative pass rate for out-of-scope queries (LLM filter).

---

## 🚀 Getting Started

### 1. Database Setup
```bash
docker-compose up -d
```
*Note: The database is exposed on port `5433` by default to avoid conflicts with local PostgreSQL instances. You can change this in the `.env` file.*

### 2. Configure Environment
Rename `.env.example` to `.env` and fill in your API keys.

### 3. Run Experiments
```bash
python scripts/run_experiments.py
```

### 4. Advanced Evaluation (RAGAS)
```bash
python eval_ragas.py
```

## 🧠 Graphify Knowledge Graph
Use Graphify to generate an architecture-aware knowledge graph for this repository.

### Install
```bash
python -m pip install graphifyy
```

### Build the graph
```bash
graphify .
```

### Recommended assistant integration
- `AGENTS.md` and `.github/copilot-instructions.md` are included for AI assistant guidance.
- Commit `graphify-out/GRAPH_REPORT.md` and `graphify-out/graph.json` for team-wide graph navigation.

---

## 🛡 Security & Resilience
- **Secrets**: Managed via `.env`. Never committed to Git.
- **Failover**: Sequential provider chain with timeouts and retries.
- **Isolation**: Multi-tenant support via `tenant_id` metadata filtering (Tested via `exp_06_tenant_leakage`).
