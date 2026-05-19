# 🚀 AI-PMS RAG Bootcamp: Week 2 Execution Plan

This plan outlines the remaining tasks required to reach 100% completion of the bootcamp. It is optimized for a distributed team where **Nishitha** handles infrastructure (WSL/Ubuntu) and **Balu Sir** & **Balu Sir** handle logic, data, and architecture (Windows).

---

## 🛠️ Phase 2: Domain RAG & Agentic RAG

| Day | Module | Task Description | Status |
|:--- |:--- |:--- |:---:|
| **Day 6** | **Domain Chunkers** | Build a dedicated **Correspondence Chunker**; Re-ingest all data using hierarchical parsers for FIDIC, NCR, and DPR. | ⏳ |
| **Day 7** | **GraphRAG** | Load **Metro Rail Systems Taxonomy** (383 entries) into Apache AGE; Implement LLM-based **Query Router**. | ⏳ |
| **Day 8** | **Agentic RAG** | Build a **LangGraph Iterative Agent** for multi-hop retrieval and self-correction. | ⏳ |
| **Day 9** | **Hardening** | Expand Golden Dataset to **80+ queries**; Implement **PostgreSQL RLS** and **Citation Chains**. | ⏳ |
| **Day 10** | **Deployment** | Build **FastAPI service** (`src/api.py`); Finalize **Architecture Decision Document**. | ⏳ |

---

## 🤝 Team Workload Distribution (WSL vs. Windows)

To overcome hardware constraints, we split the work into **Logic/Data** (Windows) and **Execution** (WSL).

### 🔓 Windows-Friendly Tasks (Independent of WSL)
*Can be completed by **Balu Sir** and **Balu Sir** using VS Code & Browser.*

| Task | Lead | Description |
|:--- |:--- |:--- |
| **Golden Dataset Expansion** | **Balu Sir** | Generate 40+ new Query-Answer triples in JSON format. |
| **Query Router Design** | **Balu Sir** | Prompt engineering for the "Traffic Cop" classifier. |
| **Agent Workflow Design** | **Balu Sir** | Designing the LangGraph State Machine logic and pseudocode. |
| **Evaluation Analysis** | **Balu Sir** | Review RAGAS scores and document failure modes. |
| **Arch. Decision Doc** | **Balu Sir** | Final 5-page technical recommendation for Kernex/DMRC. |

### 🔐 WSL-Dependent Tasks (Execution)
*Handled by **Nishitha** on the WSL/Ubuntu environment.*

*   **GraphRAG Ingestion**: Loading taxonomy into the live database.
*   **Pipeline Execution**: Running chunking and ingestion scripts.
*   **Automated Eval**: Running RAGAS scores against the local database.
*   **FastAPI Build**: Implementing the live API server.

---

## 📋 The Collaborative Workflow

1.  **Input**: **Balu Sir** creates/updates the 40+ query JSON on Windows and pushes to GitHub.
2.  **Run**: **Nishitha** pulls the JSON, executes the evaluation on WSL, and pushes results back.
3.  **Refine**: **Balu Sir** reviews the results and writes the **Decision Document** and **Agent Logic**.

---

## 🏁 Final Bootcamp Exit Criteria
By following this plan, we will demonstrate:
*   **4 Domain-Specific Chunkers** (better than generic ones).
*   **Knowledge Graph** answering dependency questions vector search can't.
*   **Iterative Agent** that thinks through multi-step legal questions.
*   **Hardened Database** with zero leakage between tenants (RLS).