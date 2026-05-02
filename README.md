# AI-PMS RAG Bootcamp — Production Refactor

This repository has been fully refactored into a modular, production-ready RAG system, addressing all deficiencies identified in the **Day 0 Peer Review**.

## 🚀 System Status: PRODUCTION-READY
- **Architecture**: Modular `src/` and `scripts/` structure.
- **Vector Store**: PostgreSQL + `pgvector` (Migrated from ChromaDB).
- **Dataset**: Real-world **Indian Railways GCC** (Contract Clauses).
- **Environment**: Linux-native (Compatible with Ubuntu, WSL2, and Windows via Docker).
- **Setup Guide**: [Detailed Multi-Platform Setup Guide](docs/guides/multi_platform_setup.md)

---

## ✅ Peer Review Fixes (DEF-01 to DEF-10)

| ID | Deficiency | Fix Description |
| :--- | :--- | :--- |
| **DEF-01** | Evaluation Bug | Refactored `ask_rag()` to return `{context, answer, chunk_ids}` separately. Evaluation now correctly compares answer vs retrieved context. |
| **DEF-02** | Placeholder Data | Ingested **1,311 chunks** from real Indian Railways GCC PDF documents. |
| **DEF-03** | Windows Environment | Migrated to **Linux environment** with a dedicated `pgvector` Docker container. |
| **DEF-04** | Embedding Comparison| Conducted benchmark across `all-MiniLM-L6-v2`, `bge-large`, and `nomic-embed` using real GCC data. |
| **DEF-05** | No Chunking | Implemented **Hierarchical Chunking** (Headings -> Paragraphs -> Sentences) with 100-char overlap. |
| **DEF-06** | ChromaDB usage | Fully migrated to **pgvector** for production-standard vector operations. |
| **DEF-07** | Incomplete Fallback | Expanded fallback chain: **Groq -> OpenRouter -> Cerebras -> Google (Gemini)**. |
| **DEF-08** | No Exp Logs | Created `experiments/` folder with automated logging via `run_experiments.py`. |
| **DEF-09** | .gitignore issues | Updated `.gitignore` to protect `data/`, models, and environment secrets. |
| **DEF-10** | Documentation | README updated with real execution metrics and architectural evidence. |
| **RAGAS** | Eval Framework | Integrated **Ragas** via `eval_ragas.py`. |
| **Legacy** | Review Support | Restored neater root wrappers (`eval_baseline.py`, etc.) for reviewer navigation. |

---

## 🛠 Project Structure
```text
aipms-rag-bootcamp/
├── src/
│   ├── rag_pipeline.py    # Single source of truth (RAG Logic)
│   ├── retriever.py       # pgvector & metadata filtering
│   ├── llm.py             # Resilient fallback chain (4 providers)
│   └── evaluator.py       # Faithfulness, Relevance, P@K, R@K
├── scripts/
│   ├── ingest_data.py     # Hierarchical chunking & DB loading
│   ├── run_experiments.py # Automated batch testing & logging
│   └── compare_embeddings.py # Embedding model benchmarking
├── data/                  # Raw PDFs and processed JSON chunks
├── experiments/           # Structured markdown logs for every run
├── docs/                  # Comparison reports and images
│   ├── guides/            # Setup and installation guides
│   ├── reports/           # Completion and status reports
│   └── images/            # Visualizations (UMAP, etc.)
└── tests/                 # Unit and integration tests
```

---

## 📊 Core Metrics (Baseline: exp_01)
*Latest run on GCC Dataset:*

- **Faithfulness**: 0.92 (Avg)
- **Relevance**: 0.88 (Avg)
- **Retrieval Latency**: <50ms (pgvector indexed)
- **Fallback Success**: 100% (Sequential provider failover)

---

## 🚀 Getting Started

### 1. Database Setup
```bash
docker-compose up -d
```
*Note: The database is exposed on port `5433` by default to avoid conflicts with local PostgreSQL instances. You can change this in the `.env` file.*

### 2. Configure Environment
Rename `.env.example` to `.env` and fill in your API keys. The database settings are pre-configured for a smooth experience across **Ubuntu, WSL, and Windows**.

### 3. Ingestion
```bash
python scripts/ingest_data.py
```

### 3. Run Experiments
```bash
python scripts/run_experiments.py
```

### 4. Advanced Evaluation (RAGAS)
```bash
python eval_ragas.py
```

### 5. Baseline Evaluation (Legacy)
```bash
python eval_baseline.py
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

### Ignore local Graphify artifacts
`graphify-out/cache/`, `graphify-out/manifest.json`, and `graphify-out/cost.json` are excluded from git.

---

## 🛡 Security & Resilience
- **Secrets**: Managed via `.env`. Never committed to Git.
- **Failover**: Sequential provider chain with timeouts and retries.
- **Isolation**: Multi-tenant support via `tenant_id` metadata filtering.
