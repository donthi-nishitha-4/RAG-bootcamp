# 🤖 DMRC Metro Project: LangGraph Agentic RAG Test Report
**Author:** Nishitha  
**Role:** Advanced RAG Ingestion Engineering  
**Bootcamp Phase:** Day 8 — Agentic RAG with LangGraph (Week 2)  
**Status:** Verification Successful  

## 📊 Execution Tracing Summary
Below is the complete execution trace of the LangGraph `StateGraph` agent, demonstrating node transitions, iterative self-correction, and citation accuracy:

### 📦 Query 1: What active water seepage issue was detected in Station B cavern ceiling and what is the corrective action?
- **Routed Domain Index**: `NCR`
- **Iterative Loops Completed**: `1 loop(s)`
- **Response Latency**: `15233.97ms`
- **Node Traversal Path**:  
  `query_analyzer (route ➔ NCR) ➔ retriever (iter 1) ➔ evaluator ➔ self_correct ➔ answer_generator (generate)`

#### ✍️ Final Agent Response:
Based on the provided context chunks, the active water seepage issue detected in Station B cavern ceiling is related to water ingress in the concrete segment joints of the station cavern ceiling. This issue is directly impacting the installation of cable trays and fire alarm wiring.

According to the NCR dataset [NCR DATASET] ID: DMRC-0056, an NCR was issued for water seepage in the station cavern ceiling.

Regarding the corrective action, although the specific details are not mentioned in the provided context chunks, it can be inferred that the corrective action would involve addressing the water seepage issue to prevent further impact on the installation of cable trays and fire alarm wiring.

However, to obtain the specific corrective action, it would be necessary to refer to additional context chunks or documentation that may have been shared outside of the provided information.

References:
- [CORRESPONDENCE LET] File: let_004_station_cavern_seepage_Nishitha.txt - Chunk 3
- [NCR DATASET] ID: DMRC-0056

---

### 📦 Query 2: Who sent the notice regarding OHE catenary hanger damage NCR-0051 and what is the exact deadline to resolve it?
- **Routed Domain Index**: `NCR`
- **Iterative Loops Completed**: `2 loop(s)`
- **Response Latency**: `24712.06ms`
- **Node Traversal Path**:  
  `query_analyzer (route ➔ NCR) ➔ retriever (iter 1) ➔ evaluator ➔ self_correct ➔ retriever (iter 2) ➔ evaluator ➔ self_correct ➔ answer_generator (generate)`

#### ✍️ Final Agent Response:
Based on the provided context chunks, the notice regarding OHE catenary hanger damage NCR-0051 was sent by Ganga, Chief Project Engineer, Metro Project Authority, to Yamuna, Senior Infrastructure Lead, Energy Kernel, on May 10, 2026, as per File: let_001_ohe_catenary_ncr_Nishitha.txt - Chunk 1 [1].

The exact deadline to resolve the issue is within 48 hours, as stated in File: let_001_ohe_catenary_ncr_Nishitha.txt - Chunk 3 [2]. This is to prevent dynamic load testing delays and ensure safety, as the damaged OHE catenary hanger assembly represents a major safety hazard [2].

Reference:
[1] File: let_001_ohe_catenary_ncr_Nishitha.txt - Chunk 1
[2] File: let_001_ohe_catenary_ncr_Nishitha.txt - Chunk 3

---

### 📦 Query 3: What concrete moist curing measures did Yamuna from Energy Kernel implement for the track slab near the tunnel portal?
- **Routed Domain Index**: `DPR`
- **Iterative Loops Completed**: `1 loop(s)`
- **Response Latency**: `14155.59ms`
- **Node Traversal Path**:  
  `query_analyzer (route ➔ DPR) ➔ retriever (iter 1) ➔ evaluator ➔ self_correct ➔ answer_generator (generate)`

#### ✍️ Final Agent Response:
Based on the provided context chunks, Yamuna from Energy Kernel implemented the following concrete moist curing measures for the track slab near the tunnel portal:

1. **Hourly monitoring of the track slab concrete temperature**: This measure ensures that the temperature of the concrete is closely monitored to prevent any potential issues that may arise due to temperature fluctuations [let_002_ballastless_track_curing_Nishitha.txt, Chunk 4].
2. **Saturated moist curing blanket for 14 continuous days**: The moist curing blanket will remain saturated for 14 days as specified in the technical specification manual, which is a crucial measure to ensure proper curing of the concrete [let_002_ballastless_track_curing_Nishitha.txt, Chunk 4].

These measures were implemented in response to the joint site inspection on 2026-05-11 regarding the grout separation in the ballastless track slab near the tunnel portal (NCR-0052) [let_002_ballastless_track_curing_Nishitha.txt, Chunk 3].

Source: [let_002_ballastless_track_curing_Nishitha.txt, Chunks 3 and 4]

---

## 🛠️ StateGraph Architecture Details
1. **Typed State Schema**: Orchestrated using a standard `AgentState(TypedDict)` containing `query`, `retrieved_chunks`, `retrieval_history`, `confidence`, and `iteration_count`.
2. **Dynamic Query Analyzer**: Integrates the Day 7 classifier to route intent to separated vector indices instantly, eliminating cross-entity confusion.
3. **Self-Correction & Query Reformulation Node**: Evaluates retrieved chunks for completeness. If an LLM judges them as insufficient, the agent reformulates search parameters and loops back up to 3 times to retrieve better context.
4. **Failsafe Hybrid Offline Search**: Includes an automatic filesystem scanner fallback to search raw transmittals and synthetic JSON assets when the PostgreSQL database container is offline, ensuring 100% test reliability.

Report generated successfully on WSL2 terminal.