# ================== IMPORTS ==================
import os
import sys
import json
import re
from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, END
from sentence_transformers import SentenceTransformer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.llm import query_llm
from src.core.query_router_Nishitha import route_query
from src.core.retriever import retrieve_similar
from src.core.entity_mapper import resolve_entity_types
from src.core.hardening_Nishitha import redact_pii

# ================== GLOBAL MODEL ==================
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# ================== STATE ==================
class AgentState(TypedDict):
    query: str
    tenant_id: str
    current_search_query: str
    retrieved_chunks: List[str]
    retrieval_trace: List[Dict[str, Any]]
    retrieval_history: List[Dict[str, Any]]
    confidence: str
    iteration_count: int
    routed_domain: str
    answer: str


# ================== FALLBACK ==================
def retrieve_local_fallback(query_text: str, domain: str, k: int = 3):
    candidate_chunks = []

    json_path = "data/dmrc/dmrc_Synthetic_Dataset_Nishitha.json"
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            for item in data:
                cat = item.get("category", "").lower()
                text = item.get("text", "")
                item_id = item.get("id", "unknown")

                mapped_domain = None
                if "contract" in cat:
                    mapped_domain = "contract_clause"
                elif "ncr" in cat:
                    mapped_domain = "ncr"
                elif "dpr" in cat:
                    mapped_domain = "dpr"

                if text:
                    candidate_chunks.append({
                        "id": f"json_{item_id}",
                        "domain": mapped_domain,
                        "content": text
                    })

    query_words = set(re.findall(r'\w+', query_text.lower()))
    ranked = []

    for chunk in candidate_chunks:
        words = set(re.findall(r'\w+', chunk["content"].lower()))
        score = len(query_words & words)

        if chunk["domain"] == domain:
            score += 3

        ranked.append((score, chunk))

    ranked.sort(key=lambda x: x[0], reverse=True)
    top = [c[1] for c in ranked[:k]]

    retrieved_chunks = [c["content"] for c in top]

    retrieval_trace = [
        {
            "id": c["id"],
            "content": c["content"],
            "distance": None,
            "source": "fallback",
            "router_domain": domain,
            "db_entity_type": c["domain"]
        }
        for c in top
    ]

    return retrieved_chunks, retrieval_trace


# ================== NODE 1 ==================
def query_analyzer_node(state: AgentState):
    query = state["query"]
    domain = route_query(query)

    return {
        "routed_domain": domain,
        "tenant_id": state.get("tenant_id", "default_strategy"),
        "current_search_query": query,
        "retrieval_trace": [],
        "retrieval_history": [],
        "iteration_count": 0,
        "retrieved_chunks": []
    }


# ================== NODE 2 (FIXED RETRIEVER) ==================
def retriever_node(state: AgentState):
    domain = state["routed_domain"]
    search_query = state["current_search_query"]
    tenant = state["tenant_id"]

    chunks = []
    retrieval_trace = []

    try:
        q_emb = embed_model.encode(search_query).tolist()

        # 🔥 FIX 1: use entity mapper correctly
        entity_types = resolve_entity_types(domain)

        tenants = [tenant, "default_strategy", "default"]

        for t in tenants:
            for etype in entity_types:
                results = retrieve_similar(q_emb, t, etype, k=3)

                if results:
                    retrieval_trace = [
                        {
                            "id": r[0],
                            "content": redact_pii(r[1]),
                            "distance": r[2],
                            "tenant_id": t,
                            "entity_type": etype,
                            "router_domain": domain,
                            "db_entity_type": etype,
                            "source": "pgvector"
                        }
                        for r in results
                    ]

                    chunks = [redact_pii(r[1]) for r in results]
                    break

            if chunks:
                break

    except Exception as e:
        print(f"[DB ERROR] {e}")

    # ================== FALLBACK ==================
    if not chunks:
        fallback_chunks, fallback_trace = retrieve_local_fallback(search_query, domain)
        chunks = [redact_pii(c) for c in fallback_chunks]
        retrieval_trace = [
            {**t, "content": redact_pii(t["content"])} 
            for t in fallback_trace
        ]

    return {
        "retrieved_chunks": chunks,
        "retrieval_trace": retrieval_trace
    }


# ================== NODE 3 (FIXED EVALUATOR) ==================
def evaluator_node(state: AgentState):
    query = state["query"]
    chunks = state["retrieved_chunks"]
    context = "\n\n".join(chunks)

    prompt = [
        {
            "role": "system",
            "content": "Reply only: sufficient or insufficient"
        },
        {
            "role": "user",
            "content": f"{query}\n\n{context}"
        }
    ]

    res = query_llm(prompt).strip().lower()

    # 🔥 FIX 2: safer matching
    is_sufficient = "sufficient" in res and "insufficient" not in res

    if is_sufficient:
        return {
            "confidence": "high",
            "iteration_count": state["iteration_count"] + 1
        }

    return {
        "confidence": "low",
        "iteration_count": state["iteration_count"] + 1,
        "current_search_query": query
    }


# ================== NODE 4 ==================
def answer_generator_node(state: AgentState):
    chunks = state["retrieved_chunks"]

    if not chunks:
        return {"answer": "I cannot answer this question based on available documents in the system. Please contact the administrator."}

    context = "\n\n".join(chunks)

    prompt = [
        {"role": "system", "content": "Answer using ONLY the provided context. Do not add external knowledge."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {state['query']}"}
    ]

    return {"answer": query_llm(prompt)}


# ================== ROUTER ==================
def route_after_evaluation(state: AgentState):
    if state["confidence"] == "high" or state["iteration_count"] >= 3:
        return "generate"
    return "loop"


# ================== GRAPH ==================
def build_agent():
    g = StateGraph(AgentState)

    g.add_node("query_analyzer", query_analyzer_node)
    g.add_node("retriever", retriever_node)
    g.add_node("evaluator", evaluator_node)
    g.add_node("answer_generator", answer_generator_node)

    g.set_entry_point("query_analyzer")

    g.add_edge("query_analyzer", "retriever")
    g.add_edge("retriever", "evaluator")

    g.add_conditional_edges(
        "evaluator",
        route_after_evaluation,
        {"generate": "answer_generator", "loop": "retriever"}
    )

    g.add_edge("answer_generator", END)

    return g.compile()


agent_app = build_agent()


# ================== RUN ==================
def run_agentic_query(query_text: str, tenant_id: str = "default_strategy"):
    state = {
        "query": query_text,
        "tenant_id": tenant_id,
        "current_search_query": query_text,
        "retrieved_chunks": [],
        "retrieval_trace": [],
        "retrieval_history": [],
        "confidence": "low",
        "iteration_count": 0,
        "routed_domain": "",
        "answer": ""
    }

    return agent_app.invoke(state)