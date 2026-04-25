# Experiment: exp_03_hybrid_search
- **Date:** 2026-04-25 15:17:49
- **Dataset:** GCC (Semantic Strategy)
- **Search Type:** hybrid
- **Config:** {"top_k": 5, "final_k": 3}

## Query: What is the security deposit amount according to the contract?
- **Result:** PASSED
- **Reason:** Scores >= 0.7
- **Faithfulness:** 1.0
- **Relevance:** 1.0

## Query: Explain the procedure for breach of contract.
- **Result:** PASSED
- **Reason:** Scores >= 0.7
- **Faithfulness:** 1.0
- **Relevance:** 1.0

## Query: What is the penalty for late performance bank guarantee?
- **Result:** FAILED
- **Reason:** Low faithfulness or relevance scores
- **Faithfulness:** 1.0
- **Relevance:** 0.0

