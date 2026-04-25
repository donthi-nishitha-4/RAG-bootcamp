# Experiment: exp_01_baseline_retrieval
- **Date:** 2026-04-25 08:58:07
- **Dataset:** GCC + Sample Docs
- **Config:** {"top_k": 5, "final_k": 3}

## Query: What is the security deposit amount according to the contract?
- **Result:** PASSED
- **Reason:** Scores >= 0.7
- **Fix:** N/A
- **Faithfulness:** 1.0
- **Relevance:** 1.0

## Query: How is AI used in medicine?
- **Result:** FAILED
- **Reason:** Low faithfulness or relevance scores
- **Fix:** Improve retrieval metadata filtering or chunking
- **Faithfulness:** 1.0
- **Relevance:** 0.0

## Query: What happens in case of a breach of contract?
- **Result:** PASSED
- **Reason:** Scores >= 0.7
- **Fix:** N/A
- **Faithfulness:** 1.0
- **Relevance:** 1.0

