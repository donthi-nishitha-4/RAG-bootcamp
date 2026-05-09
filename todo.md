RAG Bootcamp — Team TODOs & Ownership
====================================

Reference graph: [graphify-out/GRAPH_REPORT.md](graphify-out/GRAPH_REPORT.md)

Purpose
-------
This file captures per-person ownership, focused TODOs, checklists, and DO/DON'T guidance for the Phase 1 work described in the project review. Keep changes small, focused, and on personal branches. Use the existing pipeline in `src/` and reuse `graphify-out/` for context.

UDAY — Ownership
-----------------
- **Scope:** HyDE retrieval, multi-query retrieval, baseline comparison, short findings summary.
- **TODO:**
  - Implement HyDE retrieval flow (minimal, pipeline-integrated)
  - Implement multi-query retrieval
  - Compare HyDE + multi-query against current hybrid search baseline
  - Record Precision@5 observations on the 30+ query set
  - Push clean commits to a personal branch and open PR
  - Write short findings summary markdown
- **Checklist:** HyDE implemented • Multi-query implemented • Comparison completed • Metrics recorded • Findings added
- **DO:** Reuse existing pipeline, keep work minimal, commit small working changes.
- **DON'T:** Rebuild infra, change chunkers/evals, expand scope beyond retrieval experiments.

D NISHITHA — Ownership
----------------------
- **Scope:** Golden evaluation dataset, experiment logs, comparison summary tables, RAGAS experiment reporting.
- **TODO:**
  - Create 30+ query–answer–context triples including adversarial/out-of-scope queries
  - Categorize queries by entity type
  - Run evaluation experiments and update logs
  - Add "Surprising Finding" and "Production Implication" entries
  - Build consolidated comparison tables
- **Checklist:** 30+ queries • Expected answers • Context references • Adversarial queries • Logs updated • Tables completed
- **DO:** Keep outputs organized; store evaluation results in `Final_Deliverables/` or `experiments/` with structured logs.
- **DON'T:** Modify retrieval architecture frequently or change core pipeline logic unnecessarily.

BALU SIR — Ownership
--------------------
- **Scope:** Reranker comparison, NCR/DPR chunkers, breaking experiments, RAGAS integration.
- **TODO:**
  - Configure RAGAS evaluation pipeline and Groq integration
  - Implement reranking comparison (MiniLM vs bge-reranker)
  - Record latency and Precision@5 for rerankers (CPU measurements)
  - Build NCR and DPR chunkers (minimal, reproducible)
  - Complete remaining breaking experiments and document root cause analysis
- **Checklist:** RAGAS configured • Groq working • Two rerankers tested • Latency measured • Chunkers working
- **DO:** Keep experiments isolated, record failure analysis clearly, maintain reproducible setup.
- **DON'T:** Merge incomplete experiments or reuse same observations across branches.

Project-level Next Steps (short)
--------------------------------
1. Expand evaluation query set to 30+ queries covering all entity types.
2. Implement HyDE and multi-query retrieval; compare with hybrid baseline.
3. Build NCR/DPR chunkers and run additional chunking experiments.
4. Add cross-encoder reranking and record Precision@5 + CPU latency.
5. Set up RAGAS automated evaluation (Groq) and run experiments end-to-end.
6. Each member pushes to their own branch and documents independent observations.

Repository guidance
-------------------
- Store findings and experiment artifacts under `Final_Deliverables/`, `experiments/`, or `graphify-out/` as appropriate.
- Use `graphify-out/GRAPH_REPORT.md` for quick project context when writing experiments or summaries.
- Keep commits small and self-contained; include a short changelog entry in PR descriptions.

Communication
-------------
Add brief progress updates in `Final_Deliverables/task_update.md` and link the branch/PR. For reviews, include links to the RAGAS run logs and the updated `graphify-out/GRAPH_REPORT.md` snapshot.

Contact
-------
For coordination: Bhanu (review) and team leads as listed above.
