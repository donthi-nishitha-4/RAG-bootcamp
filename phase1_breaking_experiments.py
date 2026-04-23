#!/usr/bin/env python3
"""
Phase 1 Breaking Experiments
Purpose: Systematically break the RAG pipeline to understand failure modes
"""

import sys
import os
sys.path.insert(0, '/home/ecs/aipms-rag-bootcamp')

from rag_pgvector import load_documents, ask_rag, init_pgvector, DB_CONFIG
import psycopg2

# ---- EXPERIMENT 1: Query-Document Mismatch ----
def experiment_query_document_mismatch():
    """
    EXPERIMENT 1: Query-Document Mismatch
    
    Query: "What is the time-bar period for delay claims under FIDIC Yellow Book?"
    Expected failure: If chunks are from FIDIC Red Book, system will hallucinate
    using Red Book clauses as if they were Yellow Book clauses.
    """
    print("\n" + "="*70)
    print("EXPERIMENT 1: Query-Document Mismatch")
    print("="*70)
    print("\n[SETUP] Loading FIDIC Red Book clauses (wrong contract type)")
    
    # Load Red Book clauses (wrong type for Yellow Book query)
    red_book_clauses = [
        "Under FIDIC Red Book Clause 20.1, the Contractor shall give notice of any claim within 28 days.",
        "Red Book: The Engineer's decision on any claim shall be given within 42 days.",
        "Red Book: If the Contractor fails to give notice, he shall not be entitled to additional time.",
        "Red Book: Claims for extension of time must be supported by detailed particulars.",
    ]
    
    load_documents(red_book_clauses, entity_type="contract_clause", tenant_id="default")
    
    print("\n[QUERY] What is the time-bar period for delay claims under FIDIC Yellow Book?")
    print("[EXPECTED] System should NOT know this is Red Book data - may hallucinate")
    
    result = ask_rag("What is the time-bar period for delay claims under FIDIC Yellow Book?")
    
    print("\n[RESULT]")
    print(f"  Retrieved chunks: {result['retrieved_chunks']}")
    print(f"  Answer: {result['answer']}")
    
    print("\n[OBSERVATION]")
    print("  ❌ Did the system distinguish between Red Book vs Yellow Book?")
    print("  ❌ Did it cite the source contract type?")
    print("  ❌ Did it say 'I don't know' or hallucinate?")
    
    # Clean up
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("DELETE FROM rag_documents WHERE entity_type = 'contract_clause'")
    conn.commit()
    cur.close()
    conn.close()
    
    return {
        "experiment": "Query-Document Mismatch",
        "issue": "System cannot distinguish contract types",
        "lesson": "Metadata filtering by contract_standard (Red/Yellow/Silver) is REQUIRED"
    }

# ---- EXPERIMENT 2: Cross-Entity Confusion ----
def experiment_cross_entity_confusion():
    """
    EXPERIMENT 2: Cross-Entity Confusion
    
    Load NCR descriptions AND contract clauses into same vector space.
    Query: "What corrective action should be taken for concrete honeycombing?"
    Expected failure: Retriever mixes NCR corrective actions with contract clauses.
    """
    print("\n" + "="*70)
    print("EXPERIMENT 2: Cross-Entity Confusion")
    print("="*70)
    
    # Clear previous data
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("DELETE FROM rag_documents")
    conn.commit()
    cur.close()
    conn.close()
    
    print("\n[SETUP] Loading mixed entities: NCRs + Contract Clauses")
    
    # Load contract clauses
    contract_clauses = [
        "Under the contract, defects liability period is 12 months after taking over.",
        "The contractor shall remedy defects at his own cost within the defects notification period.",
        "Contract clause 11.1: The contractor warrants that works shall be fit for purpose.",
    ]
    load_documents(contract_clauses, entity_type="contract_clause", tenant_id="default")
    
    # Load NCR descriptions
    ncr_descriptions = [
        "NCR-001: Concrete honeycombing detected in Column C4. Root cause: improper vibration.",
        "NCR-002: Corrective action - rework concrete surface, apply epoxy coating.",
        "NCR-003: Root cause analysis shows aggregate grading issue in mix design.",
    ]
    load_documents(ncr_descriptions, entity_type="ncr", tenant_id="default")
    
    print("\n[QUERY] What corrective action should be taken for concrete honeycombing?")
    print("[EXPECTED] Should retrieve NCR, NOT contract clauses")
    
    result = ask_rag("What corrective action should be taken for concrete honeycombing?")
    
    print("\n[RESULT]")
    print(f"  Retrieved chunks: {result['retrieved_chunks']}")
    print(f"  Answer: {result['answer']}")
    print(f"  Sources: {result['sources']}")
    
    print("\n[OBSERVATION]")
    # Check if we got mixed results
    has_ncr = any('NCR' in str(s) for s in result['sources'])
    has_contract = any('contract' in str(s).lower() for s in result['sources'])
    
    if has_ncr and has_contract:
        print("  ❌ CROSS-ENTITY CONFUSION: Got BOTH NCR and contract clauses!")
    elif has_ncr and not has_contract:
        print("  ✅ Correct: Retrieved only NCR")
    elif has_contract and not has_ncr:
        print("  ❌ WRONG: Retrieved contract clause instead of NCR")
    
    print("\n[LESSON]")
    print("  → Metadata filtering by entity_type is REQUIRED")
    print("  → Without filtering, system mixes operational (NCR) with legal (contract)")
    
    return {
        "experiment": "Cross-Entity Confusion",
        "issue": "No entity_type filtering causes mixed results",
        "lesson": "Add entity_type filter to every retrieval query"
    }

# ---- EXPERIMENT 3: Long-Document Problem ----
def experiment_long_document():
    """
    EXPERIMENT 3: The Long-Document Problem
    
    Load a simulated long document (many chunks).
    Query: "Summarize the contractor's obligations"
    Expected failure: Top-K (3) returns only 3 chunks from many - not a summary.
    """
    print("\n" + "="*70)
    print("EXPERIMENT 3: Long-Document Problem")
    print("="*70)
    
    # Clear previous
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("DELETE FROM rag_documents")
    conn.commit()
    cur.close()
    conn.close()
    
    print("\n[SETUP] Simulating a long contract (20+ chunks)")
    
    # Simulate a long contract with many clauses
    long_contract = [
        f"Contract Clause {i}: The contractor shall {action}" 
        for i, action in enumerate([
            "provide all materials and labor", "execute works as specified",
            "comply with applicable laws", "maintain insurance coverage",
            "provide progress reports monthly", "attend site meetings",
            "coordinate with other contractors", "follow safety regulations",
            "protect existing structures", "manage site access",
            "provide temporary facilities", "dispose of waste materials",
            "rectify defects promptly", "maintain quality records",
            "allow inspection of works", "provide as-built drawings",
            "train operator personnel", "supply spare parts",
            "warrant workmanship", "complete final cleanup"
        ], 1)
    ]
    
    load_documents(long_contract, entity_type="contract_clause", tenant_id="default")
    
    print("\n[QUERY] Summarize the contractor's obligations")
    print("[EXPECTED] Top-K=3 returns only 3/20 clauses - biased sample, not summary!")
    
    result = ask_rag("Summarize the contractor's obligations")
    
    print("\n[RESULT]")
    print(f"  Retrieved chunks: {len(result['retrieved_chunks'])} out of 20")
    print(f"  Chunks: {result['retrieved_chunks']}")
    print(f"  Answer: {result['answer'][:200]}...")
    
    print("\n[OBSERVATION]")
    print(f"  ❌ Only {len(result['retrieved_chunks'])}/20 chunks retrieved")
    print("  ❌ This is sampling bias, not summarization")
    print("  ❌ LLM has recency bias - favors chunks at end of context")
    
    print("\n[LESSON]")
    print("  → Different query intents need different retrieval strategies")
    print("  → Factoid queries: Top-K works")
    print("  → Summarization queries: Need document-level strategies (map-reduce)")
    
    return {
        "experiment": "Long-Document Problem",
        "issue": "Top-K insufficient for summarization",
        "lesson": "Query intent detection + adaptive retrieval strategy"
    }

# ---- MAIN ----
def main():
    print("\n" + "="*70)
    print("PHASE 1 BREAKING EXPERIMENTS")
    print("Purpose: Understand RAG failure modes for production hardening")
    print("="*70)
    
    # Initialize fresh
    init_pgvector()
    
    results = []
    
    # Run experiments
    results.append(experiment_query_document_mismatch())
    results.append(experiment_cross_entity_confusion())
    results.append(experiment_long_document())
    
    # Summary
    print("\n" + "="*70)
    print("EXPERIMENT SUMMARY")
    print("="*70)
    
    for r in results:
        print(f"\n🔴 {r['experiment']}")
        print(f"   Issue: {r['issue']}")
        print(f"   Lesson: {r['lesson']}")
    
    print("\n" + "="*70)
    print("PRODUCTION REQUIREMENTS IDENTIFIED")
    print("="*70)
    print("""
    1. METADATA FILTERING (Required)
       - tenant_id: Multi-tenant isolation
       - entity_type: Prevent cross-entity confusion
       - contract_standard: Distinguish Red/Yellow/Silver Book
    
    2. QUERY ROUTING (Required)
       - Detect query intent (factoid vs summarization)
       - Route to appropriate retrieval strategy
    
    3. FALLBACK BEHAVIOR (Required)
       - When confidence is low: say "I don't know"
       - Never hallucinate when data is insufficient
    """)
    
    print("="*70)
    print("✅ Breaking Experiments Complete!")
    print("="*70)

if __name__ == "__main__":
    main()