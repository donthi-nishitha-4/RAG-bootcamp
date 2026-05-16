# Experiment 04: Breaking Entity Confusion
**Date:** 2026-05-16
**Objective:** To test if the RAG system leaks information across different entities (e.g., DMRC vs. GCC) when using vector search alone.

## Setup
1. **Dataset:** Only GCC documents were ingested (DMRC data excluded).
2. **Query:** "Does the DMRC agreement specify a different bank guarantee period?"
3. **Config:** Top-K=5, Final-K=3 (Vector search only).

## Results
- **Result:** PASSED (Negative Pass)
- **Faithfulness:** 1.0
- **Relevance:** 1.0

## Analysis
Even though the retriever found **GCC** bank guarantee clauses (because they were the only ones available in the DB), the **LLM** acted as a successful filter. It correctly identified that the context was about "GCC" and refused to answer for "DMRC."

## Surprising Finding
The system is highly resistant to "Cross-Entity Confusion" as long as the LLM is powerful (Llama 3.3 70B). Even when the retriever "failed" by fetching GCC chunks for a DMRC question, the LLM acted as a successful filter.

## Production Implication
This confirms that **LLM Reasoning is our last line of defense against data leakage.** However, relying on the LLM to filter wrong entities is expensive and slow. In production, we must implement **Metadata Filtering** (e.g., `WHERE entity_type = 'DMRC'`) at the database level. This would prevent the retriever from even fetching the GCC chunks, saving tokens and improving speed while providing a hard guarantee against entity confusion.



# Experiment: exp_04_breaking_entity_confusion
- **Date:** 2026-04-25 15:17:55
- **Dataset:** GCC Only (DMRC data excluded)
- **Search Type:** vector
- **Config:** {"top_k": 5, "final_k": 3}

## Query: Does the DMRC agreement specify a different bank guarantee period?
- **Result:** PASSED (Negative Pass)
- **Reason:** The system correctly identified that no DMRC data was available.
- **Faithfulness:** 1.0
- **Relevance:** 1.0
- **Root Cause Analysis:** Since the database at the time of this experiment only contained GCC documents, the vector search retrieved GCC bank guarantee clauses. However, the LLM prompt instructions ("Answer ONLY using the provided context. If the answer is not there, say you do not know") successfully prevented "Entity Hallucination." The LLM compared the query (DMRC) to the context (GCC) and correctly stated it could not find a DMRC-specific period.

---

## Surprising Finding
The system is highly resistant to "Cross-Entity Confusion" as long as the LLM is powerful (Llama 3.3 70B). Even when the retriever "failed" by fetching GCC chunks for a DMRC question, the LLM acted as a successful filter. It correctly identified that while it had "Bank Guarantee" info, it did not have "DMRC" info.

## Production Implication
This confirms that **LLM Reasoning is our last line of defense against data leakage.** However, relying on the LLM to filter wrong entities is expensive and slow. In production, we must implement **Metadata Filtering** (e.g., `WHERE entity_type = 'DMRC'`) at the database level. This would prevent the retriever from even fetching the GCC chunks, saving tokens and improving speed while providing a hard guarantee against entity confusion.
