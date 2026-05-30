"""
================================================================================
Author: Nishitha
Role: Advanced RAG Ingestion Engineering
Created: 2026-05-18
Description: Custom Day 10 FastAPI Service Wrapper.
             Exposes POST /query to execute RAG operations with 
             integrated tenant isolation (RLS), fallback checks, 
             deterministic citation tracing, and CDM Layer 4 auditing.
================================================================================
"""
import os
import sys
import time
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# Check and dynamically import/install FastAPI if needed
try:
    from fastapi import FastAPI, HTTPException
except ImportError:
    class FastAPI:
        def __init__(self, **kwargs): self.routes = []
        def post(self, path): return lambda func: func
    class HTTPException(Exception): pass

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.agent_Nishitha import run_agentic_query
from src.core.hardening_Nishitha import (
    check_query_out_of_scope,
    generate_hardened_citation_chain,
    write_audit_log,
    retrieve_with_rls
)

# ==================== LATENCY CONFIG ====================
MAX_LATENCY_MS = 5000  # 5 seconds budget

# Initialize FastAPI App
app = FastAPI(
    title="DMRC Metro Project: Agentic RAG API",
    description="Production-hardened, tenant-isolated query service for AI-PMS.",
    version="1.0.0"
)

# --------------------------------------------------------------------------
# Request & Response Schemas
# --------------------------------------------------------------------------
class QueryRequest(BaseModel):
    query: str = Field(..., description="The user's search query.")
    tenant_id: str = Field("metro_tenant", description="Tenant isolation identifier.")
    entity_type_filter: Optional[str] = Field(
        None, description="Optional domain constraint (contract_clause | ncr | dpr | correspondence)."
    )

class QueryResponse(BaseModel):
    query: str
    tenant_id: str
    answer: str
    citations: str
    confidence: str
    retrieval_trace: List[Dict[str, Any]]
    latency_ms: float
    latency_status: str           # ✅ NEW
    latency_budget_ms: int        # ✅ NEW

# --------------------------------------------------------------------------
# API Route handler
# --------------------------------------------------------------------------
@app.post("/query", response_model=QueryResponse)
def execute_query(request: QueryRequest):
    """
    Executes a production-hardened RAG query.
    """
    start_time = time.time()

    query = request.query
    tenant = request.tenant_id
    domain_filter = request.entity_type_filter

    # ----------------------------------------------------------------------
    # 1. Out-of-Scope Check
    # ----------------------------------------------------------------------
    if check_query_out_of_scope(query):
        fallback_answer = "Insufficient data to answer this query."
        latency_ms = (time.time() - start_time) * 1000

        latency_status = "PASSED" if latency_ms <= MAX_LATENCY_MS else "FAILED"

        write_audit_log(tenant, query, [], fallback_answer, latency_ms)

        return QueryResponse(
            query=query,
            tenant_id=tenant,
            answer=fallback_answer,
            citations="None (Out-of-Scope Intercepted)",
            confidence="low",
            retrieval_trace=[{"action": "adversarial_fallback_intercept"}],
            latency_ms=latency_ms,
            latency_status=latency_status,
            latency_budget_ms=MAX_LATENCY_MS
        )

    # ----------------------------------------------------------------------
    # 2. Run Agentic Pipeline
    # ----------------------------------------------------------------------
    try:
        output = run_agentic_query(query, tenant_id=tenant)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG Execution Failed: {str(e)}")

    # ----------------------------------------------------------------------
    # 3. Generate Citations
    # ----------------------------------------------------------------------
    retrieval_trace = output.get("retrieval_trace", [])
    citation_block = generate_hardened_citation_chain(retrieval_trace)

    # ----------------------------------------------------------------------
    # 4. Compute Latency
    # ----------------------------------------------------------------------
    latency_ms = (time.time() - start_time) * 1000
    latency_status = "PASSED" if latency_ms <= MAX_LATENCY_MS else "FAILED"

    # ----------------------------------------------------------------------
    # 5. Attach Citations to Answer
    # ----------------------------------------------------------------------
    cited_answer = output["answer"]
    if citation_block:
        cited_answer += "\n" + citation_block

    # ----------------------------------------------------------------------
    # 6. Audit Logging
    # ----------------------------------------------------------------------
    chunk_ids = [str(c["id"]) for c in retrieval_trace if "id" in c]

    write_audit_log(
        tenant_id=tenant,
        query=query,
        chunk_ids=chunk_ids,
        answer=output["answer"],
        latency_ms=latency_ms
    )

    # ----------------------------------------------------------------------
    # 7. Final Response
    # ----------------------------------------------------------------------
    return QueryResponse(
        query=query,
        tenant_id=tenant,
        answer=cited_answer,
        citations=citation_block.strip(),
        confidence=output.get("confidence", "high"),
        retrieval_trace=retrieval_trace,
        latency_ms=latency_ms,
        latency_status=latency_status,
        latency_budget_ms=MAX_LATENCY_MS
    )