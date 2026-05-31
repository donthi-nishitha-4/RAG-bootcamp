# AREAS TO NOTE:

• RAGAS overall metrics (faithfulness 0.34, answer relevancy 0.34) are below the 0.85 target. However, the per-category breakdown shows Contract/Legal at 0.82 faithfulness which is close to the target. The low overall score is dragged down by adversarial refusals (scored 0 by RAGAS) and multi-hop queries (0.17). The team correctly identified this as the Faithful Failure Paradox and the multi-hop gap. For production, the evaluation methodology will need adjustment to not penalize correct refusals.

• Router accuracy at 100% across 80 queries is strong but should be tested with more ambiguous edge cases in future iterations — real production queries will not always be cleanly classifiable.

• Cross-encoder reranking shows "0.00ms / Bypassed" in the end-to-end latency table. The rerankers were benchmarked separately (ms-marco at 231ms, bge at 542ms) but not integrated into the final pipeline. For production, reranking should be in the hot path, not bypassed. And even check for these too I have reviewed the code, experiment results, and the retrieved answers in detail. The architecture and engineering work is strong — the LangGraph agent, GraphRAG with PostgreSQL CTEs, RLS tenant isolation, idempotent ingestion, query router with failover, and the FastAPI wrapper are all well-built. The code is clean, modular, and well-documented. Good work on all of that.


However, when I checked the actual evaluation data and retrieved answers, I found a few issues that need to be fixed before we can treat this as a reliable baseline.

1. All 38 queries in the evaluation JSON show retrieved_chunks as empty ([]). This means either the retrieval is silently failing and the LLM is answering from its own knowledge, or the logging is not capturing the chunks. Either way, we cannot verify whether answers are grounded in context or are hallucinations. This needs investigation — check whether the eval script is actually passing retrieved chunks to the JSON output.

2. The citation chain shows the same Chunk IDs (84 and 105) for completely different queries — an NCR query, a TBM operations query, and a contract liability query all cite the same two chunks. Real citations should be different for different queries. Check whether the citation generator is pulling from actual retrieval results or using a static/cached value.

3. The hardening report marks NFR-04 latency as PASSED but the actual measured latency is 13,725ms (13.7 seconds). That is not a pass — it is 3x over the 5-second budget. I understand the cloud API is the bottleneck, but the report should say FAILED (cloud API) rather than PASSED. Accuracy in reporting matters more than having green checkmarks.

4. Query 1 (NCR-0051 corrective action) — the answer says "I couldn't find information" but then generates a generic corrective action framework from LLM knowledge. This contradicts the system prompt which says "answer using ONLY the provided context." The system should have stopped at "I cannot answer" instead of generating ungrounded advice. This is exactly the kind of hallucination-disguised-as-helpfulness that the HITL system is designed to prevent.

5. The OOS keyword filter will produce false positives on legitimate domain queries. For example, "What is the weather impact on tunnel boring operations?" contains the word "weather" and would be blocked, even though it is a valid construction query. Consider using embedding similarity against a domain centroid instead of a keyword list.

These are fixable issues. The underlying architecture does not need to change — it is the data pipeline, logging, and reporting accuracy that need attention.

Also, regarding your idea about restructuring the repository into a cleaner production-style folder architecture — yes, please go ahead and share your proposal. The current naming convention served its purpose for the bootcamp, but it needs to be refactored for integration into the AI-PMS codebase.

Overall you have done strong work and these corrections will make it production-worthy./home/d_nishitha/AIPMS/RAG-bootcamp/src/Review_spec_30.md