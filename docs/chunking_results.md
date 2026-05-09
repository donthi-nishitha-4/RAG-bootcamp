# Chunking Strategy Comparison

| Strategy | Total Chunks | Avg Chunk Length (Chars) | Notes |
|---|---|---|---|
| **Semantic** | 1363 | 640 | Splits by Clause/Chapter headers. Best for contract alignment. |
| **Simple** | 1085 | 799 | Fixed-size overlapping chunks. Baseline strategy. |
| **Paragraph** | 272 | 2783 | Splits on double newlines. Leads to larger, more context-rich chunks. |

## P@5 Comparison (Baseline Retrieval)
*Evaluation run on 3 contract-related queries*

| Strategy | P@5 | R@5 | Faithfulness | Relevance |
|---|---|---|---|---|
| Semantic | 1.0 | 0.8 | 1.0 | 1.0 |
| Simple | 0.8 | 0.6 | 1.0 | 0.7 |
| Paragraph | 0.6 | 1.0 | 0.8 | 1.0 |

**Verdict:** Semantic chunking provides the best balance of retrieval precision and grounding for legal documents.
