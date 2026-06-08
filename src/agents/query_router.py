"""
================================================================================
Author: Nishitha
Role: Advanced RAG Ingestion Engineering
Created: 2026-05-18
Description: Custom LLM Query Router for Day 7 (Week 2).
             Classifies user queries into construction RAG domains:
             (contract_clause | ncr | dpr | correspondence) using robust prompts 
             with sequential LLM failovers and keyword heuristics.
================================================================================
"""
import os
import sys
import re

# Add project root to path so we can import src core modules

from src.core.llm import query_llm

VALID_DOMAINS = {"contract_clause", "ncr", "dpr", "correspondence"}

def classify_query_by_heuristics(query_text):
    """
    Fast, offline rule-based classification fallback if the LLM is completely offline
    or returns an invalid classification.
    """
    q = query_text.lower()
    
    # Correspondence keywords
    if any(k in q for k in ["letter", "email", "ref:", "from:", "to:", "subject:", "dear", "sincerely", "regards", "stakeholder", "ganga", "yamuna", "simhadri", "energy kernel"]):
        return "correspondence"
        
    # NCR keywords
    if any(k in q for k in ["ncr", "non-conformance", "violation", "defect", "damage", "seepage", "crack", "barrier", "unauthorized", "grout separation"]):
        return "ncr"
        
    # DPR keywords
    if any(k in q for k in ["dpr", "daily progress", "progress report", "curing", "concrete", "shift", "casting", "advance", "tbm advance"]):
        return "dpr"
        
    # Contract keywords
    if any(k in q for k in ["clause", "contract", "fidic", "warranty", "liability", "payment", "subcontractor", "specification", "employer", "contractor"]):
        return "contract_clause"
        
    # Default fallback
    return "contract_clause"

def route_query(query_text):
    """
    Classifies a user construction query into a specific domain using Robust LLM failovers.
    If ambiguous or multi-domain, returns 'ambiguous'.
    """
    system_prompt = (
        "You are an advanced classification router for a Metro Rail construction RAG system.\n"
        "Your task is to classify the user's search query into exactly one of the following domains:\n"
        "1. contract_clause\n"
        "2. ncr\n"
        "3. dpr\n"
        "4. correspondence\n\n"
        "Rules:\n"
        "- Assess if the query clearly belongs to one domain.\n"
        "- If it is vague, overly broad, or spans multiple domains (e.g. 'tell me everything', 'abbreviated question?'), return 'ambiguous'.\n"
        "- Reply with ONLY the category name: contract_clause, ncr, dpr, correspondence, or ambiguous.\n"
        "- Do not explain your choice."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Query to classify: \"{query_text}\""}
    ]
    
    try:
        llm_response = query_llm(messages, temperature=0.0)
        
        if llm_response and not llm_response.startswith("[ERROR]"):
            clean_res = llm_response.strip().lower()
            clean_res = re.sub(r'[^a-z_]', '', clean_res)
            
            if "ambiguous" in clean_res:
                print("[ROUTER] Query detected as AMBIGUOUS.")
                return "ambiguous"
                
            for d in VALID_DOMAINS:
                if d in clean_res:
                    print(f"[ROUTER] LLM Classified query as: {d}")
                    return d
                    
        print(f"[ROUTER WARNING] LLM returned invalid domain '{llm_response}'. Using fallback heuristics.")
    except Exception as e:
        print(f"[ROUTER WARNING] LLM classification error: {e}. Using fallback heuristics.")
        
    fallback_domain = classify_query_by_heuristics(query_text)
    print(f"[ROUTER] Heuristic Fallback Classified query as: {fallback_domain}")
    return fallback_domain

if __name__ == "__main__":
    # Standard CLI test loop
    test_queries = [
        "What is the warranty period for track slab concrete surfacing?",
        "NCR-0051 OHE catenary hanger damage report and corrective actions",
        "How many meters did the tunnel boring machine advance during the night shift?",
        "Who sent the letter regarding the active water seepage at Station B?",
        "What is the required transition zone slope gradient in depot yard?"
    ]
    
    print("=== DMRC METRO RAG QUERY ROUTER CLI TEST ===")
    for q in test_queries:
        print(f"\nQuery: \"{q}\"")
        routed = route_query(q)
        print(f"Routed Domain: => {routed.upper()}")
