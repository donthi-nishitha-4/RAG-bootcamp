# Experiment 08: Wrong Contract Version Confusion
**Date:** 2026-05-16
**Objective:** Document how the system handles multiple versions of the same legal clause (e.g., FIDIC Red vs. Yellow Book) and prove that metadata filtering is required for legal accuracy.

## Setup
1. Ingested Clause 20.1 from FIDIC Red Book (28 days time-bar).
2. Ingested Clause 20.1 from FIDIC Yellow Book (42 days time-bar).
3. Queried: "What is the time-bar period for claims under the Yellow Book?"

## Results
| Mode | Top Result | Status |
|---|---|---|
| No Metadata Filter | Mix of Red/Yellow clauses | ❌ FAIL (Risk of legal error) |
| With Metadata Filter | Correct Yellow Book clause | ✅ PASS |

## Surprising Finding
Semantic similarity alone is not enough to distinguish between contract versions because the wording of the clauses is nearly identical (95% overlap), differing only in the specific numerical value (28 vs 42 days). The vector space puts them extremely close together.

## Root cause Analysis
Because the clauses share high semantic overlap, a naive vector search will retrieve both. If the Red Book chunk happens to have a slightly higher cosine similarity (perhaps due to random noise in the embedding), the LLM will incorrectly cite the Red Book value as the answer for a Yellow Book query.

## Production Implication
For AI-PMS, we must enforce a mandatory `contract_standard` metadata filter whenever a user asks a contract-related question. We cannot rely on the LLM to "figure out" which book it is reading if multiple books are in the same vector space.
