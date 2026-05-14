# Consolidated RAG Comparison Report — AI-PMS Bootcamp

## Overview
This report summarizes the results of various retrieval strategies tested on the **Golden Dataset** (38 queries). The evaluation focus was on resolving key challenges in infrastructure project documentation: domain-specific terminology, cross-clause dependencies, and entity confusion.

## Experiment Matrix

| Exp ID | Strategy | Dataset | Success Rate | Avg Faithfulness | Avg Answer Relevancy | Key Finding |
|---|---|---|---|---|---|---|
| **exp_01** | Vector Baseline | Mixed | 66% | 1.00 | 0.65 | LLM system prompt successfully filters out-of-scope queries. |
| **exp_02** | Semantic Vector | GCC | 66% | 1.00 | 0.66 | Heading-based chunking fails when answers span multiple clauses. |
| **exp_03** | Hybrid Search | GCC | 66% | 1.00 | 0.66 | Trigram search fixes technical term misses but cannot fix small chunk issues. |
| **exp_04** | Entity Confusion | DMRC/GCC | 100% | 1.00 | 1.00 | LLM reasoning is a strong "last line of defense" against entity leakage. |

## RAGAS Automated Evaluation (Global Summary)
*Evaluated on the full 29-query non-adversarial subset.*

| Strategy | Faithfulness | Answer Relevancy | Context Precision | Context Recall |
|---|---|---|---|---|
| **Vector Search** | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| **Hybrid Search** | [PENDING] | [PENDING] | [PENDING] | [PENDING] |

---

## Surprising Findings (Aggregated)
1. **The "Faithful Failure" Paradox**: In `exp_01`, the system achieved 1.0 faithfulness on out-of-scope queries by correctly refusing to answer. This proves the system is safe, but it highlights that faithfulness alone is not a sufficient metric for "helpfulness."
2. **Hybrid Search's False Promise**: `exp_03` showed that while Hybrid search (Trigram + Vector) correctly located the "Performance Bank Guarantee" clause where Vector failed, the final answer was still wrong because the relevant penalty value was in the *next* chunk. Retrieval precision does not guarantee extraction success if chunking is too aggressive.
3. **LLM as a Zero-Shot Filter**: `exp_04` demonstrated that a high-reasoning model (Llama 3.3 70B) can effectively prevent entity confusion (answering DMRC questions with GCC data) even when the retriever is "lazy" and fetches the wrong entity.

## Production Implications
1. **Metadata Filtering is Mandatory**: Relying on the LLM to filter entity confusion is slow and expensive. Production systems **must** use hard metadata filters (e.g., `WHERE tenant_id = 'DMRC'`) to guarantee data isolation.
2. **Context Enrichment**: To solve the "cut-off" issue observed in `exp_03`, the retriever should implement **Parent Document Retrieval** or neighbor-chunk inclusion (k=1 window).
3. **Adversarial Guardrails**: The high "Negative Pass" rate on adversarial queries suggests we should implement a lightweight pre-retrieval classifier to handle out-of-scope queries before they reach the vector database.
