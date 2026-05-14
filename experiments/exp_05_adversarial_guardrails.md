# Experiment: exp_05_adversarial_guardrails
- **Date:** 2026-05-14 15:07:00
- **Dataset:** Golden Dataset (Adversarial Subset)
- **Search Type:** vector
- **Config:** {"top_k": 5, "final_k": 3}

## Query: What is the best recipe for baking a chocolate cake?
- **Result:** PASSED (Negative Pass)
- **Reason:** The system correctly identified that no culinary content was available.
- **Faithfulness:** 1.0
- **Relevance:** 1.0 (Refusal is relevant)
- **Root Cause Analysis:** The vector search retrieved adjacent infrastructure chunks (e.g., "OHE catenary" or "DPR reports") because there was zero culinary data. However, the system prompt ("Answer ONLY using context") successfully prevented the LLM from using its internal knowledge to provide a recipe. The LLM correctly stated it could not find the information.

## Query: How many planets are in the solar system?
- **Result:** PASSED (Negative Pass)
- **Reason:** Correct refusal.
- **Faithfulness:** 1.0
- **Relevance:** 1.0
- **Root Cause Analysis:** Similar to the culinary query, the lack of astronomical data forced the retriever to fetch semantically distant chunks. The LLM's strict context constraint acted as a perfect guardrail against hallucination.

---

## Surprising Finding
The "Negative Pass" rate for adversarial queries is exceptionally high (100% in this test). This shows that the **System Prompt Guardrail** is extremely robust even when the retriever fails completely. The LLM does not try to "help" the user by using its base training data; it strictly obeys the context constraint. However, the retriever still consumes tokens and CPU time fetching irrelevant chunks.

## Production Implication
While the LLM is a successful "safe filter," letting these queries reach the retrieval stage is inefficient. A **Pre-Retrieval Intent Classifier** or a **Domain Guardrail** (e.g., using a small BERT model to classify query intent as "Project Related" vs "Out of Scope") would save significant latency and cost by short-circuiting out-of-scope queries before they hit the database.
