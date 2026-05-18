# Evaluation Results — VECTOR search
**Run:** 20260515_101801  |  **Tenant:** default_strategy  |  **Dataset:** evaluation_dataset.json

## Overall Summary
| Metric | Value |
|---|---|
| Total Queries | 38 |
| Passed | 12 |
| Failed | 26 |
| Pass Rate | 31.6% |
| Avg Faithfulness | 0.316 |
| Avg Relevance | 0.311 |

## Breakdown by Category
| Category | Count | Passed | Avg Faithfulness | Avg Relevance |
|---|---|---|---|---|
| analytical | 4 | 0 | 0.00 | 0.00 |
| anomaly | 2 | 0 | 0.00 | 0.00 |
| factual | 14 | 9 | 0.64 | 0.63 |
| multi-hop | 6 | 1 | 0.17 | 0.17 |
| out_of_scope | 10 | 1 | 0.10 | 0.10 |
| summary | 2 | 1 | 0.50 | 0.50 |

## Breakdown by Source
| Source | Count | Passed | Avg Faithfulness | Avg Relevance |
|---|---|---|---|---|
| adversarial | 10 | 1 | 0.10 | 0.10 |
| dmrc | 11 | 3 | 0.27 | 0.27 |
| gcc | 11 | 8 | 0.73 | 0.71 |
| kaggle | 6 | 0 | 0.00 | 0.00 |

## Per-Query Results
| Source | Category | Query | Faithfulness | Relevance | Expected Match | Status |
|---|---|---|---|---|---|---|
| gcc | factual | What clause governs contractor claims in GCC?… | 0.00 | 0.00 | ❌ | FAILED |
| gcc | multi-hop | What happens if disputes are not resolved amicably in GCC co… | 1.00 | 1.00 | ❌ | PASSED |
| gcc | factual | Which clause allows termination of contract?… | 1.00 | 1.00 | ❌ | PASSED |
| gcc | multi-hop | What causes TBM delays in GCC projects?… | 0.00 | 0.00 | ❌ | FAILED |
| gcc | factual | Which GCC clause handles contractor claims and documentation… | 1.00 | 0.80 | ❌ | PASSED |
| gcc | factual | What is the role of the engineer in GCC contract execution?… | 1.00 | 1.00 | ❌ | PASSED |
| gcc | analytical | What is the impact of TBM breakdown on project timeline?… | 0.00 | 0.00 | ❌ | FAILED |
| gcc | factual | What are the OHE catenary responsibilities of the contractor… | 1.00 | 1.00 | ❌ | PASSED |
| dmrc | analytical | Which contractor shows highest rejection rate in DMRC data?… | 0.00 | 0.00 | ❌ | FAILED |
| dmrc | multi-hop | Which subsystem causes most delays in DMRC projects?… | 0.00 | 0.00 | ❌ | FAILED |
| dmrc | analytical | Which station has highest number of RFIs?… | 0.00 | 0.00 | ❌ | FAILED |
| dmrc | summary | What are common NCR defects in DMRC reports?… | 1.00 | 1.00 | ❌ | PASSED |
| dmrc | multi-hop | Which contractor shows both high rejection and low closure r… | 0.00 | 0.00 | ❌ | FAILED |
| dmrc | anomaly | Identify RFIs open beyond SLA in DMRC system.… | 0.00 | 0.00 | ❌ | FAILED |
| dmrc | anomaly | Which contractor shows abnormal rejection trend?… | 0.00 | 0.00 | ❌ | FAILED |
| dmrc | factual | What is a common defect type in DMRC welding NCRs?… | 0.00 | 0.00 | ❌ | FAILED |
| dmrc | multi-hop | Which subsystem has highest NCR escalation in DMRC?… | 0.00 | 0.00 | ❌ | FAILED |
| dmrc | factual | What NCR was raised for OHE catenary hanger damage?… | 1.00 | 1.00 | ❌ | PASSED |
| dmrc | factual | What does the DPR say about TBM advance progress?… | 1.00 | 1.00 | ❌ | PASSED |
| kaggle | factual | What is total revenue reported in the enterprise dataset?… | 0.00 | 0.00 | ❌ | FAILED |
| kaggle | analytical | Which segment contributes highest revenue in the enterprise … | 0.00 | 0.00 | ❌ | FAILED |
| kaggle | multi-hop | Which region shows highest growth but declining trend?… | 0.00 | 0.00 | ❌ | FAILED |
| kaggle | summary | What are key risks in the enterprise report?… | 0.00 | 0.00 | ❌ | FAILED |
| kaggle | factual | What is the enterprise RAG dataset used for?… | 0.00 | 0.00 | ❌ | FAILED |
| kaggle | factual | What is the YoY revenue growth rate in the enterprise datase… | 0.00 | 0.00 | ❌ | FAILED |
| adversarial | out_of_scope | What is an unrelated question about quantum physics?… | 0.00 | 0.00 | N/A | FAILED |
| adversarial | out_of_scope | Who is the CEO of Google?… | 0.00 | 0.00 | N/A | FAILED |
| adversarial | out_of_scope | What is the capital of France?… | 0.00 | 0.00 | N/A | FAILED |
| adversarial | out_of_scope | Generate a Python script for sorting a list.… | 0.00 | 0.00 | N/A | FAILED |
| adversarial | out_of_scope | What was the score in last night's cricket match?… | 0.00 | 0.00 | N/A | FAILED |
| adversarial | out_of_scope | Does DMRC comply with FIDIC Red Book or Yellow Book?… | 0.00 | 0.00 | ❌ | FAILED |
| adversarial | out_of_scope | What is the exact bank guarantee percentage per GCC Yellow B… | 1.00 | 1.00 | N/A | PASSED |
| gcc | factual | What is the contractor's warranty period for track slab surf… | 1.00 | 1.00 | ❌ | PASSED |
| gcc | factual | What must the contractor submit before OHE catenary energiza… | 1.00 | 1.00 | ✅ | PASSED |
| gcc | factual | What action can the engineer take for non-compliant OHE cate… | 1.00 | 1.00 | ✅ | PASSED |
| adversarial | out_of_scope | What is the best recipe for baking a chocolate cake?… | 0.00 | 0.00 | N/A | FAILED |
| adversarial | out_of_scope | How many planets are in the solar system?… | 0.00 | 0.00 | N/A | FAILED |
| adversarial | out_of_scope | Translate 'Hello' to Japanese.… | 0.00 | 0.00 | N/A | FAILED |

---
*Generated by run_eval.py — D Nishitha*
