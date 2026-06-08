[INFO] Embed & Rerank Models loaded successfully.
=== DMRC METRO RAG: PRODUCTION HARDENING EVALUATION ===

--- [TEST 1/6] Initializing PostgreSQL Security Policies ---
[TEST 1 STATUS] DB Security Hardened: True

--- [TEST 2/6] Evaluating RLS Tenant Isolation ---
[METRO TENANT] Retracted: 5 chunks.
[DFCC TENANT] Retracted: 5 chunks.
[INFO] Row-Level Security (RLS) isolation successfully verified. 0 leaks recorded!

--- [TEST 3/6] Testing Idempotent Ingestion Deduplication ---
[INGEST 1] Loading sample chunk for the first time...
[INGEST 2] Loading duplicate sample chunk for the second time...
[IDEMPOTENCY RESULTS] Load 1: 0 inserted | Load 2: 0 inserted.
[TEST 3 STATUS] Idempotent Ingestion Pass: True (Deduplicator blocked duplicate chunk successfully)

--- [TEST 4/6] Evaluating Fallback Behavior on 10 Out-of-Scope Queries ---
  [Q 1] "What is the capital city of France?" ➔ Result: "Insufficient data to answer this query." (6669.34ms)
  [Q 2] "Who won the FIFA Football World Cup in 2022?" ➔ Result: "Insufficient data to answer this query." (10.39ms)
  [Q 3] "Give me a recipe for baking chocolate chip cookies." ➔ Result: "Insufficient data to answer this query." (14.47ms)
  [Q 4] "What is the weather today in New York?" ➔ Result: "Insufficient data to answer this query." (10.53ms)
  [Q 5] "Who is the Prime Minister of Canada?" ➔ Result: "Insufficient data to answer this query." (6.44ms)
  [Q 6] "Explain the basic rules of cricket." ➔ Result: "Insufficient data to answer this query." (12.02ms)
  [Q 7] "What is the best movie to watch this weekend?" ➔ Result: "Insufficient data to answer this query." (11.33ms)
  [Q 8] "Can you tell me a funny joke?" ➔ Result: "Insufficient data to answer this query." (9.36ms)
  [Q 9] "Who is the current President of the United States?" ➔ Result: "Insufficient data to answer this query." (5.71ms)
  [Q 10] "What is the capital of Japan?" ➔ Result: "Insufficient data to answer this query." (9.01ms)
[TEST 4 STATUS] Out-of-Scope Fallback Pass: True

--- [TEST 5/6] Measuring Latency (NFR-04) & Citation Chains ---
[INFO] Successfully used provider: groq
[ROUTER] LLM Classified query as: ncr
[INFO] Successfully used provider: groq
[INFO] Successfully used provider: groq
[INFO] Successfully used provider: groq
[INFO] Successfully used provider: groq

[HARDENED ANSWER OUTPUT]
There is no information about an active water seepage issue in Station B cavern ceiling. The context only mentions that an NCR (Non-Conformance Report) was issued for water seepage in the station cavern ceiling, but it does not specify which station.

### 🔗 Hardened Citation Chain (Traceable back to CDM):
- **Chunk ID**: `json_DMRC-0056` | **Tenant**: `DEFAULT` | **Domain**: `GENERAL`
- **Chunk ID**: `json_DMRC-0067` | **Tenant**: `DEFAULT` | **Domain**: `GENERAL`
- **Chunk ID**: `json_DMRC-0061` | **Tenant**: `DEFAULT` | **Domain**: `GENERAL`
--------------------------------------------------
[LATENCY BREAKDOWN]
- Routing Latency: 0.00ms
- Retrieval & Citation Latency: 3985.49ms
- Generation Latency: 0.00ms
- End-to-End Latency: 3985.49ms
[TEST 5 STATUS] NFR-04 Latency Compliance (<5s): 3.99s Pass

--- [TEST 6/6] Generating CDM Layer 4 AuditEvent Logs ---
[TEST 6 STATUS] Layer 4 Audit Log Written Successfully!

[SUCCESS] Generated premium Hardening Verification Report: experiments/results/hardening_test_Nishitha.md
