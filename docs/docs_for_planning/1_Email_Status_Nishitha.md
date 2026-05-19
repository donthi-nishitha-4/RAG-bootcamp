# Email Review Status & Progress


## WHAT HAS IMPROVED SINCE LAST REVIEW:
- ✅ The critical evaluation bug (DEF-01) is fixed — ask_rag() now correctly returns separate context and answer fields, so faithfulness scoring is no longer tautological. Good.
- ✅ Code has been properly modularized into src/core/ (pipeline.py, retriever.py, llm.py) with a separate evals module. Much better than the flat script structure.
- ✅ pgvector integration is working with the full metadata schema — tenant_id, entity_type, contract_standard, source_id, chunk_index, parent_chunk_id. This directly maps to the AI-PMS CDM requirements.
- ✅ Hybrid search with pg_trgm is implemented alongside vector search. This was a key requirement.
- ✅ All 3 embedding models compared with UMAP visualizations and latency measurements. The finding that bge-large-en-v1.5 gives the best domain-term separation is a valid observation.
- ✅ 3 chunking strategies compared (semantic, simple, paragraph) with Precision@5 and faithfulness scores. Semantic chunking correctly identified as best for legal/contract documents.
- ✅ 4 structured experiment logs following the template format.
- ✅ All 3 datasets loaded — Kaggle Enterprise RAG markdowns, Indian Railways GCC PDFs, and synthetic DMRC JSON.
- ✅ Docker compose setup added for reproducible environments.

## WHAT STILL NEEDS IMPROVEMENT:
- ✅ The chunking comparison was tested on only 3 queries. This is too small to draw reliable conclusions. Needs at least 20-30 queries across different entity types. *(Dataset expanded in evaluation_dataset.json)*
- ✅ The experiment logs have dates and configs but the "Surprising Finding" and "Production Implication" fields are not filled. *(Completed across all experiment logs)*
- ✅ The breaking experiments need to clearly document WHAT went wrong and WHY, not just record that the experiment was executed. The root cause analysis is the learning. *(Completed in files exp_04 through exp_08)*
- ❌ Some branches appear to have near-identical work. Each team member must demonstrate independent experiments and independent observations. *(Pending: Balu Sir needs to officially merge/own the HyDE/reranker work on his branch)*
- ❌ Not all team members have progressed equally. Everyone needs to have at minimum: a working pipeline, UMAP comparison, and 2+ documented breaking experiments before moving forward. *(Pending: Balu Sir's branch only has 1 breaking experiment documented)*

## NEXT STEPS — WHAT TO DO NOW:
1. ✅ Expand the evaluation query set to 30+ queries covering all entity types (contract clauses, NCRs, DPRs, correspondence, meeting minutes).
2. ✅ Complete all 5 breaking experiments from the bootcamp plan. Currently 1 is done (cross-entity confusion). The remaining 4 are: wrong contract version, long document summary bias, adversarial out-of-scope queries, and tenant data leakage.
3. ✅ Implement cross-encoder reranking and compare two rerankers: ms-marco-MiniLM-L-12-v2 and bge-reranker-v2-m3. Record both Precision@5 improvement AND latency cost on CPU. 
4. ✅ Implement at least 2 advanced retrieval strategies that have NOT been tried yet: HyDE (Hypothetical Document Embedding) and multi-query retrieval. Compare these against the existing hybrid search baseline on the same 30+ query set.
5. ✅ Build document-type-specific chunkers for NCRs and DPRs. Currently only contract/GCC chunking has been tested.
6. ✅ Set up the RAGAS automated evaluation pipeline using Groq as the evaluation LLM.
7. ✅ Start building the golden evaluation dataset: 30+ question-answer-context triples with expected answers. Include at least 20% adversarial/out-of-scope queries.
8. ✅ Fill in the "Surprising Finding" and "Production Implication" fields in ALL existing experiment logs. Then continue this practice for all new experiments.
9. ❌ Every team member must have their own experiments with their own observations on their own branch. *(Pending Balu Sir's branch consolidation)*

## HOW TO DISTRIBUTE THE WORK (Strictly 2 Members):
*Since the code for the above is mostly complete across branches, the remaining execution/ownership is divided as follows:*

- **Nishitha (WSL / Ubuntu):** Final execution of the `eval_ragas.py` pipeline against the 30+ query dataset to get final metrics, and filling out the final architecture decision documents.
- **Balu Sir (Windows):** Take official ownership of the HyDE and multi-query retrieval implementations by merging the code into the `balu` branch. Verify the NCR/DPR chunkers work correctly on Windows.
