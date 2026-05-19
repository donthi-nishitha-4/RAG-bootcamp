# 🚦 DMRC Metro Project: LLM Query Router Test Report
**Author:** Nishitha  
**Role:** Advanced RAG Ingestion Engineering  
**Bootcamp Phase:** Day 7 — GraphRAG & Query Router (Week 2)  
**Classification Accuracy:** `100.0%`  
**Average Classification Latency:** `936.05ms`  

## 📊 Evaluation Summary Table
| ID | Query Text | Expected Domain | Routed Domain | Latency (ms) | Status |
|:--- |:--- |:--- |:--- |:--- |:---:|
| 1 | What does Chapter 14 say about OHE contractor delay liability? | `contract_clause` | `contract_clause` | 1428.5ms | ✅ PASS |
| 2 | Is the contractor responsible for warranties on concrete slab surfacing? | `contract_clause` | `contract_clause` | 703.8ms | ✅ PASS |
| 3 | Corrective action status for OHE catenary hanger damage NCR-0051 | `ncr` | `ncr` | 716.6ms | ✅ PASS |
| 4 | Active water seepage in station cavern ceiling platform edge NCR-0056 | `ncr` | `ncr` | 1875.6ms | ✅ PASS |
| 5 | Daily TBM advance rate during Metro Line 3 night shift | `dpr` | `dpr` | 586.9ms | ✅ PASS |
| 6 | Curing logs and moisture control duration for concrete pouring | `dpr` | `dpr` | 415.3ms | ✅ PASS |
| 7 | Who sent the transmittal regarding grout joint alignment NCR-0054? | `correspondence` | `correspondence` | 943.2ms | ✅ PASS |
| 8 | Email communication from Yamuna to Ganga about curing temperature | `correspondence` | `correspondence` | 818.5ms | ✅ PASS |

## 🛡️ Technical Implementation Summary
1. **Sequential API Failover Framework**: Integrated into `RobustLLM` which dynamically fails over (`Groq` ➔ `OpenRouter` ➔ `Cerebras` ➔ `Gemini`) to guarantee 100% router uptime.
2. **Zero-Punctuation Regex Filter**: Uses robust string sanitization to clean LLM outputs and match exact domain keys.
3. **Local Keyword Heuristic Fallback**: Instantly recovers query routing using fast keyword matching in case the internet or API keys are unavailable, securing zero-latency fallback performance.

---
Report generated successfully on WSL2 terminal.