# Experiment: exp_01_baseline_retrieval
- **Date:** 2026-04-25 08:58:07
- **Dataset:** GCC + Sample Docs
- **Search Type:** vector
- **Config:** {"top_k": 5, "final_k": 3}

## Query: What is the security deposit amount according to the contract?
- **Result:** PASSED
- **Reason:** Scores >= 0.7
- **Fix:** N/A
- **Faithfulness:** 1.0
- **Relevance:** 1.0

## Query: How is AI used in medicine?
- **Result:** FAILED
- **Reason:** Out-of-scope query; no medical AI content in GCC corpus
- **Root Cause:** Vector similarity still retrieved semantically adjacent contract clauses; LLM answer was faithful to context but could not answer the question, resulting in Relevance=0.0
- **Fix:** Implement out-of-scope detection or adversarial query guard before retrieval
- **Faithfulness:** 1.0
- **Relevance:** 0.0

## Query: What happens in case of a breach of contract?
- **Result:** PASSED
- **Reason:** Scores >= 0.7
- **Fix:** N/A
- **Faithfulness:** 1.0
- **Relevance:** 1.0

---

## Surprising Finding
Faithfulness remained 1.0 even for the out-of-scope query about AI in medicine. The LLM correctly refused to fabricate an answer using contract clauses, which proves the system prompt guardrail ("answer ONLY from context") is working. However, Relevance=0.0 confirms that high faithfulness does not imply high relevance — they measure orthogonal properties.

## Production Implication
A production system must filter out-of-scope queries **before** retrieval to avoid wasting compute cycles and confusing users with technically faithful but completely irrelevant responses. A lightweight intent classifier or keyword-based scope check should be added as a pre-retrieval gate.

