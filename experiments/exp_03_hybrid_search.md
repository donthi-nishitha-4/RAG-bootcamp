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
- **Reason:** Hybrid search retrieved the correct clause via keyword match on "bank guarantee", but the LLM still struggled to extract the specific "penalty" value because the chunk was cut off.
- **Root Cause:** While Trigram (keyword) search improved retrieval by finding the specific clause for "bank guarantee" (which vector search missed in exp_02), the **chunk size was too small**. The retrieved context contained the clause header but the penalty calculation details were in the subsequent paragraph, which was not retrieved.
- **Faithfulness:** 1.0
- **Relevance:** 0.0

---

## Surprising Finding
Hybrid search successfully "fixed" the retrieval failure from exp_02 by using keyword matching for specific domain terms like "Bank Guarantee." However, the experiment **still failed** because retrieval is only half the battle. If the chunking strategy is too aggressive (too small), the keyword match finds the right *place* but the context lacks the actual *answer*.

## Production Implication
Hybrid search is a "must-have" for infrastructure projects where specific technical terms (e.g., "Performance Bank Guarantee", "TBM", "OHE") are used. However, **Hybrid search cannot compensate for poor chunking.** In production, we must implement "Parent Document Retrieval" or "Context Enrichment"—where we retrieve a small keyword-matched chunk but feed the LLM the surrounding 2-3 chunks to ensure the answer isn't cut off.
