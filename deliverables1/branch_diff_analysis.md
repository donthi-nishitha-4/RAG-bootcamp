# Branch Diff Analysis: main vs balu

## 1. Architectural Refactoring
The project underwent a major structural change between the `main` and `balu` branches.

| Feature | `main` Branch | `balu` Branch | Improvement |
|---|---|---|---|
| **Structure** | Flat (single scripts like `rag_chroma.py`) | Modular (`src/` and `scripts/` separation) | Follows professional Python packaging standards; easier to test and scale. |
| **Vector Store** | ChromaDB (In-memory/Local) | PostgreSQL + pgvector (Dockerized) | Production-ready storage with metadata filtering and persistence. |
| **Code Reuse** | Logic repeated in multiple scripts | Core logic centralized in `src/` | Reduced technical debt; single source of truth for RAG and LLM calls. |

## 2. Critical Bug Fixes

### 2.1 Evaluation Pipeline (DEF-01)
- **main:** `context = answer`. Evaluated the model's output against itself, leading to false 1.0 faithfulness scores.
- **balu:** `context = rag_result['context']`. Correctly evaluates the generated answer against the actual retrieved text chunks. This fix is critical for identifying hallucinations.

### 2.2 LLM Fallback Chain (DEF-07)
- **main:** Limited fallback (typically just Groq + OpenRouter).
- **balu:** Robust 4-provider chain (Groq → OpenRouter → Cerebras → Google AI Studio). Includes automatic retries and failover logic in `src/llm.py`.

## 3. Infrastructure and Data

### 3.1 Dataset Usage (DEF-02)
- **main:** Used a small set of 4 placeholder sentences hardcoded in the script.
- **balu:** Processes real-world Indian Railways GCC PDF documents. Implemented an automated ingestion pipeline in `scripts/ingest_data.py`.

### 3.2 Metadata Support
- **main:** No metadata or filtering capability.
- **balu:** pgvector schema includes `tenant_id`, `entity_type`, and `contract_standard`. The retriever supports dynamic filtering on these fields.

## 4. Remaining Gaps in `balu`
- **Hybrid Search:** **RESOLVED.** Implemented Vector + Trigram hybrid search in `src/retriever.py`.
- **Graph Layer:** **RESOLVED.** Implemented Parent-Child chunk traversal logic for contextual expansion.
- **Comprehensive Benchmarking:** **RESOLVED.** 4+ experiments logged; UMAP comparison conducted on real domain data; 3 chunking strategies compared.

**Conclusion:** The `balu` branch (and its production refactor) is now ready to be merged back into `main` for the final bootcamp submission.
