# 🤝 AI-PMS RAG Bootcamp: Phase 1 Collaboration Plan

## 📌 Context
Based on the recent review from Bhanu Sir, the team must demonstrate **independent experiments and unique observations** on our respective branches. While we share the core infrastructure in `src/core/`, our experiment logs and specific strategy focus must be distinct.

---

## 🎭 Team Roles & Branch Ownership

### 1. **Balu Sir** (Branch: `balu`)
*   **Role**: Retrieval & Metrics Lead
*   **Key Responsibilities**:
    *   **Strategies**: Multi-Query Retrieval & Hybrid Baseline.
    *   **Automation**: Implementation of the RAGAS automated evaluation pipeline.
    *   **Ownership**: The `eval_retrievals.py` engine and the consolidated performance table.
*   **Independent Log**: `experiments/exp_multi_query.md` (Focus: Handling vague/short queries).

### 2. **Balu Sir** (Branch: `balu`)
*   **Role**: Search Architect & Optimization Lead
*   **Key Responsibilities**:
    *   **Strategies**: HyDE (Hypothetical Document Embeddings) & Reranking Benchmarks.
    *   **Benchmarking**: Comparison of `ms-marco` vs `bge-reranker` (Speed vs. Precision).
    *   **Ownership**: Architectural decisions regarding search latency vs. accuracy trade-offs.
*   **Independent Log**: `experiments/exp_hyde_reranker.md` (Focus: Semantic separation and latency costs).

### 3. **Nishitha** (Branch: `Nishitha`)
*   **Role**: Domain Engineering & Reliability Lead
*   **Key Responsibilities**:
    *   **Strategies**: Contextual Retrieval (Document Context Prepending).
    *   **Reliability**: 5/5 Breaking Experiments (Tenant Leakage, Summary Bias, etc.).
    *   **Ownership**: Custom NCR/DPR Chunkers and CDM metadata integration.
*   **Independent Log**: `experiments/exp_contextual_retrieval.md` (Focus: Global document context).

---

## 🛠️ Step-by-Step for Success

1.  **Keep the Code Shared**: Every branch should have the full `src/core/` and `scripts/` folder to remain modular. 
2.  **Differentiate the Logs**: Each person must write their own "Surprising Finding" and "Production Implication." 
    *   *Balu Sir* focuses on query diversity.
    *   *Balu Sir* focuses on system architecture/latency.
    *   *Nishitha* focuses on failure modes and domain precision.
3.  **Independent Commits**: Each lead should commit their own experiment markdown file to their branch. This ensures Bhanu Sir sees unique activity in the Git history.

## 🎯 Final Submission Goal
By splitting the work this way, we show that we are a **coordinated team** with **individual expertise**, ensuring we meet all 9 requirements for the Phase 1 Exit Criteria.
