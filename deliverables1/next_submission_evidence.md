# Next Submission Evidence (FINAL)

## 1. Fixed Evaluation Pipeline
- **Status:** **READY**
- **Evidence:** `src/rag_pipeline.py` (Lines 110-117) and `src/evaluator.py`.
- **Proof:** Evaluated in 4 experiments; scores correctly reflect grounded vs hallucinated answers.

## 2. UMAP Comparison Notebook
- **Status:** **READY**
- **Evidence:** `docs/embedding_comparison.md` and `docs/images/umap_comparison.png`.
- **Proof:** Plot shows clear clustering differences between baseline (MiniLM) and high-perf (BGE/Nomic) models.

## 3. Chunking Comparison (P@5)
- **Status:** **READY**
- **Evidence:** `docs/chunking_results.md`.
- **Proof:** Table compares 3 strategies with P@5, R@5, and length metrics.

## 4. Breaking Experiments (≥3)
- **Status:** **READY**
- **Evidence:** `experiments/` folder.
- **Proof:** 
  - `exp_02_semantic_baseline.md`
  - `exp_03_hybrid_search.md`
  - `exp_04_breaking_entity_confusion.md`

## 5. pgvector running
- **Status:** **READY**
- **Evidence:** Port 5433 open; `vector` and `pg_trgm` extensions enabled.
- **Proof:**
  ```sql
   extname | extversion 
  ---------+------------
   vector  | 0.8.2
   pg_trgm | 1.6
  ```

---

## Final Submission Package Instructions
1. Zip the `/home/ecs/aipms-rag-bootcamp` folder (excluding `data/raw` if too large).
2. Ensure `.env.example` contains placeholders.
3. Include the `deliverables1/` folder as the core audit trail.
