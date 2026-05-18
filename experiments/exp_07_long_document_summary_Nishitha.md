# Experiment 07: Long Document Summary Bias
**Date:** 2026-05-16
**Objective:** Prove that standard Top-K retrieval fails to provide an accurate summary of long documents and identify the resulting "sampling bias."

## Setup
1. Ingested a 10-section "Scope of Work" document, where each section covers a different project phase (Mobilization, Foundation, Erection, etc.).
2. Queried: "Summarize the entire scope of work from section 1 to 10."
3. Set K=3 to simulate the limit of LLM context windows in standard RAG.

## Results
| Metric | Value | Status |
|---|---|---|
| Sections Ingested | 10 | - |
| Sections Retrieved | 3 | ❌ FAIL (Sampling Bias) |
| Coverage | 30% | ❌ FAIL |

## Surprising Finding
Even when the query explicitly asks for "all sections from 1 to 10," the vector search only returns chunks that are semantically closest to the *concept* of a summary or the first few sections. The system completely ignores 70% of the document, yet the LLM will still provide a "summary" as if it had read the whole thing.

## Root cause Analysis
Top-K retrieval is designed for "needle in a haystack" search, not for "global document understanding." It retrieves the most relevant *pieces*, but a summary requires *all* pieces. Standard RAG assumes that a small sample of chunks is representative of the whole, which is a false assumption for complex engineering documents.

## Production Implication
For AI-PMS, we cannot use standard RAG for "summarize this contract" or "list all risks in this DPR" queries. We must use either **Map-Reduce** chains, **Hierarchical Summarization**, or **Long-Context LLMs** that can ingest the entire document at once.
