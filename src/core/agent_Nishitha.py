"""
================================================================================
Author: Nishitha
Role: Advanced RAG Ingestion Engineering
Created: 2026-05-18
Description: Custom LangGraph Iterative Agent for Day 8 (Week 2).
             Implements StateGraph with nodes for routing, retrieval,
             self-correction evaluation, and cited generation.
             Includes a bulletproof hybrid local fallback for offline robustness.
================================================================================
"""
import os
import sys
import json
import re
import gc
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from sentence_transformers import SentenceTransformer

# Add project root to path so we can import src core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.llm import query_llm
from src.core.query_router_Nishitha import route_query
from src.core.retriever import retrieve_similar

# 1. Define Agentic State
class AgentState(TypedDict):
    query: str
    current_search_query: str
    retrieved_chunks: List[str]
    retrieval_history: List[Dict[str, Any]]
    confidence: str  # "high" | "low"
    iteration_count: int
    routed_domain: str
    answer: str

# 2. Local Offline Fallback Retriever (Failsafe with Multi-Hop Cross-Domain capability)
def retrieve_local_fallback(query_text: str, domain: str, k: int = 3) -> List[str]:
    """
    Scans local files across both the primary routed domain AND the correspondence domain 
    to enable true multi-hop cross-referencing.
    """
    candidate_chunks = []
    
    # Load DMRC Synthetic JSON dataset (Contracts, NCR, DPR)
    json_path = "data/dmrc/dmrc_Synthetic_Dataset_Nishitha.json"
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    cat = item.get("category", "").lower()
                    text = item.get("text", "")
                    
                    # Map categories to RAG domains
                    mapped_domain = None
                    if "contract" in cat: mapped_domain = "contract_clause"
                    elif "ncr" in cat: mapped_domain = "ncr"
                    elif "dpr" in cat: mapped_domain = "dpr"
                    
                    # Multi-hop: include chunks from the target domain, and keep other domains as candidates
                    if text:
                        prefix = f"[{mapped_domain.upper()} DATASET] ID: {item.get('id')} - "
                        candidate_chunks.append((mapped_domain, f"{prefix}{text}"))
        except Exception as e:
            print(f"[FALLBACK WARNING] Failed to read JSON dataset: {e}")

    # Load local correspondence transmittal letters (always included as candidates for multi-hop cross-referencing)
    corr_dir = "data/correspondence"
    if os.path.exists(corr_dir):
        try:
            for file_name in os.listdir(corr_dir):
                if file_name.endswith(".txt"):
                    with open(os.path.join(corr_dir, file_name), 'r', encoding='utf-8') as f:
                        text = f.read().strip()
                        # Segment into paragraphs
                        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                        for i, p in enumerate(paragraphs):
                            candidate_chunks.append(("correspondence", f"[CORRESPONDENCE LET] File: {file_name} - Chunk {i+1}:\n{p}"))
        except Exception as e:
            print(f"[FALLBACK WARNING] Failed to read correspondence: {e}")

    if not candidate_chunks:
        return ["[SYSTEM ERROR] No local document chunks available to retrieve."]

    # Rank candidates by relevance to the query
    query_words = set(re.findall(r'\w+', query_text.lower()))
    ranked_chunks = []
    
    for ch_domain, chunk_text in candidate_chunks:
        chunk_words = set(re.findall(r'\w+', chunk_text.lower()))
        overlap = len(query_words.intersection(chunk_words))
        
        # Multi-Hop Boost: give a high weight to matches that contain key search words
        # and boost candidate chunks that belong to the primary routed domain or correspondence
        boost = 0
        if ch_domain == domain:
            boost += 3
        if ch_domain == "correspondence" and any(w in query_text.lower() for w in ["letter", "notice", "sent", "email", "yamuna", "ganga", "simhadri"]):
            boost += 5
            
        score = overlap + boost
        ranked_chunks.append((score, chunk_text))
        
    # Sort descending by custom multi-hop score
    ranked_chunks.sort(key=lambda x: x[0], reverse=True)
    return [c[1] for c in ranked_chunks[:k]]

# 3. Define StateGraph Node Functions

def query_analyzer_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 1: Analyzes the query, runs LLM routing, and initializes state values.
    """
    query = state["query"]
    print(f"\n--- [NODE: query_analyzer] Analyzing Query: \"{query}\" ---")
    
    # Day 7 Query Router
    domain = route_query(query)
    
    return {
        "routed_domain": domain,
        "current_search_query": query,
        "retrieval_history": [{"action": "initial_routing", "domain": domain}],
        "iteration_count": 0,
        "retrieved_chunks": []
    }

def retriever_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 2: Retrieves context chunks from the selected domain (using DB or failsafe fallback).
    """
    domain = state["routed_domain"]
    search_query = state["current_search_query"]
    iter_count = state["iteration_count"]
    
    print(f"--- [NODE: retriever] (Iteration {iter_count+1}) Retrieving chunks for \"{search_query}\" in domain \"{domain}\" ---")
    
    chunks = []
    # 1. Attempt vector search via database
    try:
        embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        q_emb = embed_model.encode(search_query).tolist()
        db_results = retrieve_similar(
            query_embedding=q_emb,
            tenant_id="default",
            entity_type=domain,
            k=3
        )
        if db_results and not any("Connection refused" in str(r) for r in db_results):
            chunks = [r[0] for r in db_results]  # extract text from result tuples
            print("[INFO] Successfully retrieved chunks from active pgvector database.")
    except Exception as e:
        print(f"[INFO] Database search unavailable: {e}. Switching to Hybrid Offline Fallback.")
        
    # 2. Offline Fallback (Failsafe)
    if not chunks:
        chunks = retrieve_local_fallback(search_query, domain, k=3)
        print(f"[INFO] Hybrid local fallback successfully retrieved {len(chunks)} chunks.")
        
    history_entry = {
        "iteration": iter_count + 1,
        "search_query": search_query,
        "chunks_retrieved_count": len(chunks)
    }
    
    new_history = list(state["retrieval_history"])
    new_history.append(history_entry)
    
    return {
        "retrieved_chunks": chunks,
        "retrieval_history": new_history
    }

def evaluator_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 3: Evaluates retrieved context for sufficiency (Self-Correction Logic).
    """
    query = state["query"]
    chunks = state["retrieved_chunks"]
    iter_count = state["iteration_count"]
    domain = state["routed_domain"]
    
    print(f"--- [NODE: evaluator] Checking context sufficiency (Iteration {iter_count+1}) ---")
    
    context_str = "\n\n".join(chunks)
    
    prompt = [
        {
            "role": "system",
            "content": (
                "You are an expert quality auditor. Review the retrieved context chunks against the user's query.\n"
                "Determine if the chunks contain sufficient facts and details to answer the query accurately.\n"
                "Reply with exactly one word: 'sufficient' (if it can be answered fully) or 'insufficient' (if critical details are missing).\n"
                "Do not write anything else. No explanation, no punctuation."
            )
        },
        {
            "role": "user",
            "content": f"User Query: \"{query}\"\n\nRetrieved Chunks:\n{context_str}"
        }
    ]
    
    eval_res = query_llm(prompt, temperature=0.0).strip().lower()
    
    # Clean response
    eval_res = re.sub(r'[^a-z]', '', eval_res)
    
    print(f"[EVALUATOR] LLM evaluated chunk sufficiency as: {eval_res.upper()}")
    
    if "sufficient" in eval_res and "insufficient" not in eval_res:
        return {
            "confidence": "high",
            "iteration_count": iter_count + 1
        }
    else:
        # Insufficient - self-correct and reformulate the query
        reformulate_prompt = [
            {
                "role": "system",
                "content": (
                    "You are a search expert. The previous search failed to retrieve sufficient information.\n"
                    "Based on the original query, write a reformulated search query that is broader or uses synonyms to find better chunks.\n"
                    "Do not include quotes, greetings, or explanations. Return ONLY the search query text."
                )
            },
            {
                "role": "user",
                "content": f"Original Query: \"{query}\"\n\nDomain: {domain}"
            }
        ]
        new_search_query = query_llm(reformulate_prompt, temperature=0.3).strip()
        print(f"[SELF-CORRECTION] Reformulated search query: \"{new_search_query}\"")
        
        return {
            "confidence": "low",
            "current_search_query": new_search_query,
            "iteration_count": iter_count + 1
        }

def answer_generator_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 4: Generates the final cited answer using the compiled context.
    """
    query = state["query"]
    chunks = state["retrieved_chunks"]
    routed_domain = state["routed_domain"]
    
    print(f"--- [NODE: answer_generator] Synthesizing final cited answer (Domain: {routed_domain}) ---")
    
    context_str = "\n\n".join(chunks)
    
    prompt = [
        {
            "role": "system",
            "content": (
                "You are a professional Metro Rail RAG Assistant. Synthesize a detailed, professional answer to the user's query.\n"
                "You MUST base your answer strictly on the provided context chunks.\n"
                "You MUST include specific source citations (e.g. [NCR-0051], [Paragraph 2], [File: let_001_ohe_catenary_ncr_Nishitha.txt]) for all facts stated."
            )
        },
        {
            "role": "user",
            "content": f"User Query: \"{query}\"\n\nContext Chunks:\n{context_str}"
        }
    ]
    
    final_answer = query_llm(prompt, temperature=0.1)
    return {"answer": final_answer}

# 4. Define Router Edge Function
def route_after_evaluation(state: AgentState) -> str:
    """
    Determines whether to loop back to retrieve or move to answer generation.
    """
    confidence = state["confidence"]
    iter_count = state["iteration_count"]
    
    if confidence == "high" or iter_count >= 3:
        print(f"[ROUTER EDGE] Routing to answer_generator (Confidence: {confidence.upper()}, Iterations: {iter_count})")
        return "generate"
    else:
        print(f"[ROUTER EDGE] Routing back to retriever for self-correction (Confidence: LOW, Iterations: {iter_count}/3)")
        return "loop"

# 5. Build and Compile StateGraph
def build_agent():
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("query_analyzer", query_analyzer_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("answer_generator", answer_generator_node)
    
    # Set Entry Point
    workflow.set_entry_point("query_analyzer")
    
    # Add Edges
    workflow.add_edge("query_analyzer", "retriever")
    workflow.add_edge("retriever", "evaluator")
    
    # Add Conditional Edges
    workflow.add_conditional_edges(
        "evaluator",
        route_after_evaluation,
        {
            "generate": "answer_generator",
            "loop": "retriever"
        }
    )
    
    workflow.add_edge("answer_generator", END)
    
    return workflow.compile()

# Compile the final agentic runner
agent_app = build_agent()

def run_agentic_query(query_text: str) -> Dict[str, Any]:
    """
    Runs a query through the LangGraph StateGraph pipeline.
    """
    initial_state = {
        "query": query_text,
        "current_search_query": query_text,
        "retrieved_chunks": [],
        "retrieval_history": [],
        "confidence": "low",
        "iteration_count": 0,
        "routed_domain": "",
        "answer": ""
    }
    return agent_app.invoke(initial_state)
