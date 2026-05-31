"""
================================================================================
Author: Nishitha
Role: Advanced RAG Ingestion Engineering
Created: 2026-05-18
Description: Test runner for the LLM-based Query Router.
             Runs query classification, measures latency, and generates a
             premium verification report (Day 7 Proof).
================================================================================
"""
import os
import sys
import time

# Add project root to path so we can import src core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.query_router_Nishitha import route_query

def run_query_router_evaluation():
    test_suite = [
        # Contract Clauses Domain
        {
            "query": "What does Chapter 14 say about OHE contractor delay liability?",
            "expected": "contract_clause"
        },
        {
            "query": "Is the contractor responsible for warranties on concrete slab surfacing?",
            "expected": "contract_clause"
        },
        # NCR Domain
        {
            "query": "Corrective action status for OHE catenary hanger damage NCR-0051",
            "expected": "ncr"
        },
        {
            "query": "Active water seepage in station cavern ceiling platform edge NCR-0056",
            "expected": "ncr"
        },
        # DPR Domain
        {
            "query": "Daily TBM advance rate during Metro Line 3 night shift",
            "expected": "dpr"
        },
        {
            "query": "Curing logs and moisture control duration for concrete pouring",
            "expected": "dpr"
        },
        # Correspondence Domain
        {
            "query": "Who sent the transmittal regarding grout joint alignment NCR-0054?",
            "expected": "correspondence"
        },
        {
            "query": "Email communication from Yamuna to Ganga about curing temperature",
            "expected": "correspondence"
        }
    ]
    
    print("=== DMRC METRO RAG: LLM QUERY ROUTER EVALUATION ===")
    results = []
    correct_count = 0
    
    for idx, item in enumerate(test_suite):
        query = item["query"]
        expected = item["expected"]
        
        print(f"\n[TEST {idx+1}/{len(test_suite)}] Evaluating Query: \"{query}\"")
        start_time = time.time()
        
        # Route query using LLM and fallback framework
        routed = route_query(query)
        
        latency = (time.time() - start_time) * 1000  # in ms
        is_correct = routed == expected
        if is_correct:
            correct_count += 1
            
        print(f"-> Expected: {expected.upper()} | Routed: {routed.upper()} | Latency: {latency:.2f}ms | Correct: {is_correct}")
        
        results.append({
            "query": query,
            "expected": expected,
            "routed": routed,
            "latency": latency,
            "status": "✅ PASS" if is_correct else "❌ FAIL"
        })
        
    accuracy = (correct_count / len(test_suite)) * 100
    avg_latency = sum(r["latency"] for r in results) / len(results)
    
    print(f"\n=== EVALUATION COMPLETE | Accuracy: {accuracy:.1f}% | Avg Latency: {avg_latency:.2f}ms ===")
    
    # Save Report
    report_path = "experiments/results/query_router_test_Nishitha.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    report_content = [
        "# 🚦 DMRC Metro Project: LLM Query Router Test Report",
        "**Author:** Nishitha  ",
        "**Role:** Advanced RAG Ingestion Engineering  ",
        "**Bootcamp Phase:** Day 7 — GraphRAG & Query Router (Week 2)  ",
        f"**Classification Accuracy:** `{accuracy:.1f}%`  ",
        f"**Average Classification Latency:** `{avg_latency:.2f}ms`  ",
        "",
        "## 📊 Evaluation Summary Table",
        "| ID | Query Text | Expected Domain | Routed Domain | Latency (ms) | Status |",
        "|:--- |:--- |:--- |:--- |:--- |:---:|",
    ]
    
    for idx, r in enumerate(results):
        report_content.append(
            f"| {idx+1} | {r['query']} | `{r['expected']}` | `{r['routed']}` | {r['latency']:.1f}ms | {r['status']} |"
        )
        
    report_content.extend([
        "",
        "## 🛡️ Technical Implementation Summary",
        "1. **Sequential API Failover Framework**: Integrated into `RobustLLM` which dynamically fails over (`Groq` ➔ `OpenRouter` ➔ `Cerebras` ➔ `Gemini`) to guarantee 100% router uptime.",
        "2. **Zero-Punctuation Regex Filter**: Uses robust string sanitization to clean LLM outputs and match exact domain keys.",
        "3. **Local Keyword Heuristic Fallback**: Instantly recovers query routing using fast keyword matching in case the internet or API keys are unavailable, securing zero-latency fallback performance.",
        "",
        "---",
        "Report generated successfully on WSL2 terminal."
    ])
    
    with open(report_path, "w", encoding="utf-8") as rf:
        rf.write("\n".join(report_content))
        
    print(f"\n[SUCCESS] Generated premium test report: {report_path}")

if __name__ == "__main__":
    run_query_router_evaluation()
