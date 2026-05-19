# 📝 EXAMPLE: ANTIGRAVITY'S EXPERIMENT SUBMISSION (Day 3)

---

## FILLED TEMPLATE - READY TO SEND TO CLAUDE

```
# BALU'S EXPERIMENT REPORT
Date: 2026-05-03
Experimenter: Balu Sir
Experiment ID: EXP-001

## HYPOTHESIS
"Hybrid search (BM25 + Vector + RRF) outperforms pure vector search on contract clause retrieval"

## STRATEGY / CONFIG
- Retrieval Method: Hybrid (pg_trgm + pgvector + RRF)
- Vector Model: bge-large-en-v1.5
- Sparse Search: pg_trgm with GIN index
- Top-K: 5 documents
- Fusion: Reciprocal Rank Fusion (k=60)
- Reranking: None
- LLM: Llama 3.1 (Groq API)
- Dataset: 500 synthetic DMRC contracts (1000 chunks)

## DATASET USED
- Size: 1000 chunks from 500 contracts
- Type: GCC clauses, FIDIC Red/Yellow Books, NCRs
- Location: data/synthetic_dmrc_v1/contracts/
- Sampling: Stratified by contract type

## RESULTS - RETRIEVAL METRICS

| Metric | Value | Proof File | Notes |
|--------|-------|-----------|-------|
| P@5    | 0.89  | experiments/exp_001_hybrid_vs_vector.json:L45 | Top-5 precision excellent |
| P@10   | 0.92  | experiments/exp_001_hybrid_vs_vector.json:L46 | Strong recall at top-10 |
| MRR    | 0.85  | experiments/exp_001_hybrid_vs_vector.json:L47 | Good ranking quality |
| NDCG@10| 0.87  | experiments/exp_001_hybrid_vs_vector.json:L48 | DCG normalized well |

## RESULTS - ANSWER QUALITY METRICS

| Metric | Value | Proof File | Function |
|--------|-------|-----------|----------|
| Faithfulness | 0.92 | experiments/ragas_eval_exp_001.py:L120 | ragas.evaluate() |
| Answer Relevancy | 0.78 | experiments/ragas_eval_exp_001.py:L125 | Ambiguous queries drag score |
| Context Precision | 0.85 | experiments/ragas_eval_exp_001.py:L130 | Good chunk selection |
| Context Recall | 0.88 | experiments/ragas_eval_exp_001.py:L135 | Hybrid captures all relevant docs |

## RESULTS - LATENCY (on synthetic data, 1000 queries)

| Component | p50 (ms) | p95 (ms) | p99 (ms) | Query Count | Notes |
|-----------|----------|----------|----------|------------|-------|
| Metadata Filtering | 15 | 22 | 35 | 1000 | PG query plan fast |
| Vector Search (pgvector) | 120 | 245 | 310 | 1000 | GiST index on 1000 chunks |
| BM25 Search (pg_trgm) | 45 | 88 | 112 | 1000 | GIN index super fast |
| RRF Fusion | 12 | 18 | 25 | 1000 | Array math in Python |
| LLM Generation | 1800 | 3200 | 4100 | 1000 | Groq API latency |
| Citation + Audit Log | 150 | 210 | 280 | 1000 | JSON serialization |
| TOTAL END-TO-END | 2142 | 3783 | 4862 | 1000 | **PASS** (< 5000ms NFR) |

## WHAT ACTUALLY HAPPENED
Pure vector search (P@5=0.75) lost hard to hybrid (P@5=0.89) because:
- Contract identifiers like "GCC Clause 16.2" need exact keyword matches (BM25 strength)
- Semantic meaning alone wasn't enough for legal precision
- RRF fusion amplified the best of both methods

## ROOT CAUSE ANALYSIS
Semantic embeddings (bge-large) prioritize conceptual meaning over exact token matching.
Legal documents *require* both:
- **Semantic**: Understanding "warranty period" vs "maintenance window"
- **Lexical**: Finding exact clause numbers, section references

This is why **hybrid is mandatory for contracts**.

## CODE PROOF REFERENCES

```python
# Retrieval implementation
File: src/retriever.py
Function: retrieve_hybrid()
Lines: 45-78
Description: Combined BM25 + pgvector + RRF

# RAGAS evaluation
File: experiments/ragas_eval_exp_001.py
Function: evaluate_retrieval()
Lines: 100-150
Description: Metrics calculation on 100-query test set

# Latency profiling
File: scripts/benchmark_latency.py
Function: profile_components()
Lines: 200-280
Description: Component-level latency measurement with p50/p95/p99
```

## SURPRISING FINDINGS
- Answer Relevancy (0.78) lower than expected because many queries were ambiguous ("What about delays?")
- BM25 alone (p95=112ms) is surprisingly fast — we could optimize by dropping vector search for pure keyword queries
- LLM generation (p95=3200ms) is the bottleneck, not retrieval (p95=245ms)

## PRODUCTION IMPLICATION
**Recommendation**: Deploy hybrid search for all contract/legal queries. For simple factoids, BM25-only could save 300ms retrieval time. LLM optimization is the next lever (consider streaming, quantization, or smaller model).

---

## AUTO-UPDATE INSTRUCTIONS FOR CLAUDE:

[Copy-paste this YAML block into Claude's master prompt below]

```yaml
updates:
  # D2.1 - Embedding comparison table
  - section: "D2.1"
    field: "Contract Clause P@5 — bge-large-en-v1.5"
    value: "0.91"
    contributor: "Balu Sir"
    date: "2026-05-03"
    reasoning: "Semantic depth on legal terminology"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L45, src/retriever.py:L45"
  
  - section: "D2.1"
    field: "NCR P@5 — bge-large-en-v1.5"
    value: "0.85"
    contributor: "Balu Sir"
    date: "2026-05-03"
    reasoning: "Contextual awareness on change requests"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L46"
  
  - section: "D2.1"
    field: "DPR P@5 — bge-large-en-v1.5"
    value: "0.82"
    contributor: "Balu Sir"
    date: "2026-05-03"
    reasoning: "Robustness on defect reports"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L47"
  
  # D5.3 - Retrieval strategy comparison
  - section: "D5.3"
    field: "Hybrid (BM25+Vec+RRF) — P@5"
    value: "0.89"
    contributor: "Balu Sir"
    date: "2026-05-03"
    reasoning: "Excellent precision on contract clauses"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L50, src/retriever.py:L65"
  
  - section: "D5.3"
    field: "Hybrid (BM25+Vec+RRF) — P@10"
    value: "0.92"
    contributor: "Balu Sir"
    date: "2026-05-03"
    reasoning: "Strong recall at top-10"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L51"
  
  - section: "D5.3"
    field: "Hybrid (BM25+Vec+RRF) — MRR"
    value: "0.85"
    contributor: "Balu Sir"
    date: "2026-05-03"
    reasoning: "Good ranking quality"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L52"
  
  - section: "D5.3"
    field: "Hybrid (BM25+Vec+RRF) — NDCG @10"
    value: "0.87"
    contributor: "Balu Sir"
    date: "2026-05-03"
    reasoning: "DCG normalized well"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L53"
  
  - section: "D5.3"
    field: "Hybrid (BM25+Vec+RRF) — Latency p95"
    value: "345ms"
    contributor: "Balu Sir"
    date: "2026-05-03"
    reasoning: "Vector p95 245ms + BM25 p95 88ms + RRF p95 18ms (concurrent)"
    proof: "experiments/latency_benchmark_exp_001.json:L67, scripts/benchmark_latency.py:L210"
  
  - section: "D5.3"
    field: "Hybrid (BM25+Vec+RRF) — Verdict"
    value: "RECOMMENDED for legal/contract queries"
    contributor: "Balu Sir"
    date: "2026-05-03"
    reasoning: "Best precision-recall balance for DMRC use case"
    proof: "experiments/exp_001_hybrid_vs_vector.json"
  
  # D7.1 - RAGAS metrics
  - section: "D7.1"
    field: "Faithfulness — Day 2 Baseline"
    value: "1.0"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "High consistency on synthetic data"
    proof: "experiments/ragas_eval_exp_001.py:L120, results/ragas_baseline.json"
  
  - section: "D7.1"
    field: "Answer Relevancy — Day 2 Baseline"
    value: "0.67"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Needs improvement on ambiguous queries"
    proof: "experiments/ragas_eval_exp_001.py:L125, results/ragas_baseline.json"
  
  - section: "D7.1"
    field: "Context Precision — Day 2 Baseline"
    value: "0.72"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Hybrid search improved recall, but precision needs reranking"
    proof: "experiments/ragas_eval_exp_001.py:L130, results/ragas_baseline.json"
  
  - section: "D7.1"
    field: "Context Recall — Day 2 Baseline"
    value: "0.88"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Hybrid retrieval (Vector + Trigram) is highly robust"
    proof: "experiments/ragas_eval_exp_001.py:L135, results/ragas_baseline.json"
  
  # D8.1 - Latency analysis
  - section: "D8.1"
    field: "p50 (ms) — Metadata Filtering"
    value: "15"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "PG query plan optimized"
    proof: "experiments/latency_benchmark_exp_001.json:L15, scripts/benchmark_latency.py:L220"
  
  - section: "D8.1"
    field: "p95 (ms) — Metadata Filtering"
    value: "22"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Consistent performance under load"
    proof: "experiments/latency_benchmark_exp_001.json:L20"
  
  - section: "D8.1"
    field: "p99 (ms) — Metadata Filtering"
    value: "35"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Tail latency acceptable"
    proof: "experiments/latency_benchmark_exp_001.json:L25"
  
  - section: "D8.1"
    field: "p50 (ms) — Vector Search (pgvector)"
    value: "120"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "GiST index on 1000 chunks"
    proof: "experiments/latency_benchmark_exp_001.json:L40, scripts/benchmark_latency.py:L235"
  
  - section: "D8.1"
    field: "p95 (ms) — Vector Search (pgvector)"
    value: "245"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Index hit rate good, variance from PG load"
    proof: "experiments/latency_benchmark_exp_001.json:L45"
  
  - section: "D8.1"
    field: "p99 (ms) — Vector Search (pgvector)"
    value: "310"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Tail latency within budget"
    proof: "experiments/latency_benchmark_exp_001.json:L50"
  
  - section: "D8.1"
    field: "p50 (ms) — BM25 Search (pg_trgm)"
    value: "45"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "GIN index super fast"
    proof: "experiments/latency_benchmark_exp_001.json:L60, scripts/benchmark_latency.py:L245"
  
  - section: "D8.1"
    field: "p95 (ms) — BM25 Search (pg_trgm)"
    value: "88"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Keyword search consistently quick"
    proof: "experiments/latency_benchmark_exp_001.json:L65"
  
  - section: "D8.1"
    field: "p99 (ms) — BM25 Search (pg_trgm)"
    value: "112"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Excellent tail latency"
    proof: "experiments/latency_benchmark_exp_001.json:L70"
  
  - section: "D8.1"
    field: "p50 (ms) — RRF Fusion"
    value: "12"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Array math in Python is fast"
    proof: "experiments/latency_benchmark_exp_001.json:L80, scripts/benchmark_latency.py:L255"
  
  - section: "D8.1"
    field: "p95 (ms) — RRF Fusion"
    value: "18"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Negligible overhead"
    proof: "experiments/latency_benchmark_exp_001.json:L85"
  
  - section: "D8.1"
    field: "p99 (ms) — RRF Fusion"
    value: "25"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Consistent, minimal variance"
    proof: "experiments/latency_benchmark_exp_001.json:L90"
  
  - section: "D8.1"
    field: "p50 (ms) — LLM Generation (Llama 3.1)"
    value: "1800"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Groq API latency"
    proof: "experiments/latency_benchmark_exp_001.json:L100, scripts/benchmark_latency.py:L265"
  
  - section: "D8.1"
    field: "p95 (ms) — LLM Generation (Llama 3.1)"
    value: "3200"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Groq API variable latency"
    proof: "experiments/latency_benchmark_exp_001.json:L105"
  
  - section: "D8.1"
    field: "p99 (ms) — LLM Generation (Llama 3.1)"
    value: "4100"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Tail latency within 5s budget"
    proof: "experiments/latency_benchmark_exp_001.json:L110"
  
  - section: "D8.1"
    field: "p50 (ms) — Citation + Audit Log"
    value: "150"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "JSON serialization overhead"
    proof: "experiments/latency_benchmark_exp_001.json:L120, scripts/benchmark_latency.py:L275"
  
  - section: "D8.1"
    field: "p95 (ms) — Citation + Audit Log"
    value: "210"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Disk IO occasional spike"
    proof: "experiments/latency_benchmark_exp_001.json:L125"
  
  - section: "D8.1"
    field: "p99 (ms) — Citation + Audit Log"
    value: "280"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Still well under budget"
    proof: "experiments/latency_benchmark_exp_001.json:L130"
  
  - section: "D8.1"
    field: "p50 (ms) — TOTAL END-TO-END"
    value: "2142"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Combined latencies (concurrent where possible)"
    proof: "experiments/latency_benchmark_exp_001.json:L140, scripts/benchmark_latency.py:L285"
  
  - section: "D8.1"
    field: "p95 (ms) — TOTAL END-TO-END"
    value: "3783"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "PASS: Below 5000ms NFR"
    proof: "experiments/latency_benchmark_exp_001.json:L145"
  
  - section: "D8.1"
    field: "p99 (ms) — TOTAL END-TO-END"
    value: "4862"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Tail latency compliant"
    proof: "experiments/latency_benchmark_exp_001.json:L150"
  
  - section: "D8.1"
    field: "Status — TOTAL END-TO-END"
    value: "PASS"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Meets NFR-04 requirement"
    proof: "experiments/latency_benchmark_exp_001.json"
  
  # D10 - Experiment log
  - section: "D10"
    field: "Experiment EXP-001 — Date"
    value: "2026-05-03"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Completion date"
    proof: "experiments/exp_001_hybrid_vs_vector.json"
  
  - section: "D10"
    field: "Experiment EXP-001 — Experimenter"
    value: "Antigravity"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Person who ran the experiment"
    proof: "experiments/exp_001_hybrid_vs_vector.json"
  
  - section: "D10"
    field: "Experiment EXP-001 — Hypothesis"
    value: "Hybrid search (BM25 + Vector + RRF) outperforms pure vector search on contract clause retrieval"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Core experimental hypothesis"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L1"
  
  - section: "D10"
    field: "Experiment EXP-001 — Strategy / Config"
    value: "Hybrid (pg_trgm + pgvector + RRF); bge-large-en-v1.5 embeddings; 1000 contract chunks"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Exact configuration used"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L5, src/retriever.py:L45"
  
  - section: "D10"
    field: "Experiment EXP-001 — Dataset Used"
    value: "1000 chunks from 500 synthetic DMRC contracts (GCC + FIDIC Red/Yellow Books)"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Dataset composition and source"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L10, data/synthetic_dmrc_v1/README.md"
  
  - section: "D10"
    field: "Experiment EXP-001 — Retrieval Metrics"
    value: "P@5: 0.89  P@10: 0.92  MRR: 0.85  NDCG@10: 0.87"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "All retrieval metrics from evaluation"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L45-48"
  
  - section: "D10"
    field: "Experiment EXP-001 — Answer Metrics"
    value: "Faithfulness: 1.0  Relevancy: 0.78  Completeness: 0.92"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "RAGAS evaluation metrics"
    proof: "experiments/ragas_eval_exp_001.py:L120-135, results/ragas_exp_001.json"
  
  - section: "D10"
    field: "Experiment EXP-001 — Latency"
    value: "p50: 2142ms  p95: 3783ms  p99: 4862ms"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "End-to-end latency percentiles"
    proof: "experiments/latency_benchmark_exp_001.json:L140-150"
  
  - section: "D10"
    field: "Experiment EXP-001 — Result (vs. baseline)"
    value: "+14% P@5 vs. vector-only (0.75), +7% vs. BM25-only (0.82), PASS NFR-04 latency"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Key improvement metrics"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L200"
  
  - section: "D10"
    field: "Experiment EXP-001 — Surprising Finding"
    value: "BM25 alone (p95=112ms) is surprisingly fast; could optimize for keyword-only queries"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Unexpected observation"
    proof: "experiments/latency_benchmark_exp_001.json:L65"
  
  - section: "D10"
    field: "Experiment EXP-001 — Production Implication"
    value: "Deploy hybrid for contracts/legal. LLM generation (p95=3200ms) is bottleneck, not retrieval. Consider streaming or quantization for next phase."
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Actionable recommendation for production"
    proof: "experiments/latency_benchmark_exp_001.json:L100, scripts/benchmark_latency.py:L265"
```

---
```

## HOW TO SEND THIS TO CLAUDE

1. Copy the **AUTO-UPDATE INSTRUCTIONS** YAML block above
2. Go to Claude chat
3. Paste the **MASTER CLAUDE AUTO-UPDATE PROMPT** (from main document)
4. Replace `[PASTE THE ENTIRE CURRENT DELIVERABLES.md DOCUMENT HERE]` with actual document
5. Paste your YAML updates
6. Send!

Claude will return updated document with all 36 fields filled from this one experiment.

---

## FOR BALU (After you review all experiments)

```
# BALU'S ARCHITECTURE DECISION REPORT
Date: 2026-05-08
Contributor: K. Bala Chowdappa (GPREC)

## DECISION: Primary Retrieval Strategy

**Options Evaluated:**
- Vector-only (pgvector)
- Hybrid (BM25 + Vector + RRF)
- HyDE with reranking
- Multi-query expansion

**Decision & Rationale:**
**Hybrid (BM25 + Vector + RRF)** — Wins on precision (P@5 0.89), latency compliance (p95 345ms), and production fitness for legal domain.

**Evidence (Experiments):**
- EXP-001: Hybrid P@5=0.89 vs Vector-only P@5=0.75 (+14%)
- EXP-003: Legal queries need keyword + semantic (proof: contract ID matching)
- EXP-005: Latency p95=345ms < 5s budget

**Trade-offs & Risks:**
- Complexity: Requires two search backends (increases deployment/maintenance)
- Cost: Both vector + sparse indexes consume disk/memory
- Fallback: If one fails, other can still work

**Production Implication for AI-PMS:**
Mandatory for contract/legal queries. Simple factoid queries could use BM25-only (faster), but hybrid is safe default.

---

## AUTO-UPDATE FOR CLAUDE:

```yaml
updates:
  - section: "D11"
    field: "Retrieval Strategy — Recommendation"
    value: "Hybrid (BM25 + Vector + RRF)"
    contributor: "K. Bala Chowdappa"
    date: "2026-05-08"
    reasoning: "Best precision-latency trade-off for DMRC"
    proof: "EXP-001:P@5=0.89, EXP-005:latency p95=345ms, src/retriever.py:L45"
  
  - section: "D11"
    field: "Retrieval Strategy — Evidence (Exp IDs)"
    value: "EXP-001, EXP-003, EXP-005"
    contributor: "K. Bala Chowdappa"
    date: "2026-05-08"
    reasoning: "All support hybrid architecture"
    proof: "experiments/"
  
  - section: "D11"
    field: "Retrieval Strategy — Trade-offs / Risks"
    value: "Increased deployment complexity; dual index maintenance required; fallback: either backend can work independently"
    contributor: "K. Bala Chowdappa"
    date: "2026-05-08"
    reasoning: "Risk mitigation documented"
    proof: "Design review notes"
```
```

---

**READY TO GO!**  
Antigravity can submit this exact format for each of 15 experiments.  
Balu can submit architecture decisions after reviewing all experiments.  
Support can submit security/failure test results.

All updates go through Claude → Auto-merged into DELIVERABLES → Git commit → Done ✅
