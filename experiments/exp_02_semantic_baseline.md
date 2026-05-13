# Experiment: exp_02_semantic_baseline
- **Date:** 2026-04-25 15:17:44
- **Dataset:** GCC (Semantic Strategy)
- **Search Type:** vector
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
- **Reason:** Query uses terminology ("late performance bank guarantee") that does not appear verbatim in GCC chunk text. Semantic chunking splits content around headings, so the penalty clause may have been split across chunks.
- **Root Cause:** The semantic chunker splits on GCC headings (CHAPTER, CLAUSE, SECTION). "Bank guarantee" and "penalty" language may span two adjacent clauses, neither of which alone scores high on relevance. Cosine distance retrieves the nearest chunks, but the cross-encoder reranker assigns low relevance because neither chunk fully answers the query.
- **Faithfulness:** 1.0
- **Relevance:** 0.0

---

## Surprising Finding
Two queries about GCC breach and security deposit scored perfectly (F=1.0, R=1.0), but a similar GCC query about bank guarantee penalty completely failed (R=0.0). All three queries are legal contract questions from the same document. This shows that **semantic chunking success is highly sensitive to whether the answer concept sits entirely within one heading-delimited chunk**. When a concept spans two clauses (e.g., penalty defined in Clause 4, bank guarantee in Clause 6), neither retrieved chunk individually answers the question, even though the combined answer would.

## Production Implication
For legal contract RAG, semantic chunking by heading boundaries is not sufficient on its own. **Cross-clause queries will silently fail** — retrieving chunks that are individually faithful but collectively incomplete. A sliding-window overlap between adjacent clause chunks, or a parent-document retrieval strategy, would prevent this. In production, queries about penalties, timelines, and obligations often span multiple clauses and would consistently fail with heading-only chunking.
