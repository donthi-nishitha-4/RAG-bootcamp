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
import logging
from typing import Optional, List, Dict, Any
from collections import defaultdict
from pydantic import BaseModel, Field, constr

# Set up structured, neat error logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("api_security.log")
    ]
)
logger = logging.getLogger("api_security")

# Check and dynamically import/install FastAPI if needed
try:
    from fastapi import FastAPI, HTTPException, Security, Request, Depends
    from fastapi.security.api_key import APIKeyHeader
    from fastapi.responses import JSONResponse
except ImportError:
    class FastAPI:
        def __init__(self, **kwargs): self.routes = []
        def post(self, path, **kwargs): return lambda func: func
        def exception_handler(self, exc): return lambda func: func
    class HTTPException(Exception): pass
    class Request:
        @property
        def url(self): return type('obj', (object,), {'path': ''})
        @property
        def client(self): return type('obj', (object,), {'host': '127.0.0.1'})
    def Security(*args, **kwargs): return None
    def Depends(*args, **kwargs): return None
    APIKeyHeader = lambda *args, **kwargs: None
    class JSONResponse: pass

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.langgraph_agent import run_agentic_query
from src.core.security import (
    check_query_out_of_scope,
    generate_hardened_citation_chain,
    write_audit_log,
    retrieve_with_rls,
    sanitize_query
)

# ==================== LATENCY CONFIG ====================
MAX_LATENCY_MS = 5000  # 5 seconds budget

# Initialize FastAPI App
app = FastAPI(
    title="DMRC Metro Project: Agentic RAG API",
    description="Production-hardened, tenant-isolated query service for AI-PMS.",
    version="1.0.0"
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {str(exc)} | Path: {request.url.path} | Client IP: {request.client.host if getattr(request, 'client', None) else 'Unknown'}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error. Please check logs for more details."}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP Exception: {exc.detail} | Path: {request.url.path} | Client IP: {request.client.host if getattr(request, 'client', None) else 'Unknown'}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# --------------------------------------------------------------------------
# Authentication & Rate Limiting
# --------------------------------------------------------------------------
VALID_API_KEYS = {"super_secret_key_123"}
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key or api_key not in VALID_API_KEYS:
        logger.warning("Failed authentication attempt - Invalid or missing API Key")
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")
    return api_key

# In-memory rate limiting (Strict: 10/min per IP, 50/min per tenant)
request_counts = defaultdict(list)

def enforce_rate_limits(request: Request, tenant_id: str):
    now = time.time()
    ip_address = request.client.host if request and hasattr(request, 'client') and request.client else "127.0.0.1"
    
    ip_key = f"ip_{ip_address}"
    request_counts[ip_key] = [t for t in request_counts[ip_key] if now - t < 60]
    if len(request_counts[ip_key]) >= 10:
        logger.warning(f"IP Rate limit exceeded for {ip_address}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded for IP (10/min)")
    request_counts[ip_key].append(now)

    tenant_key = f"tenant_{tenant_id}"
    request_counts[tenant_key] = [t for t in request_counts[tenant_key] if now - t < 60]
    if len(request_counts[tenant_key]) >= 50:
        logger.warning(f"Tenant Rate limit exceeded for {tenant_id}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded for Tenant (50/min)")
    request_counts[tenant_key].append(now)

# --------------------------------------------------------------------------
# Request & Response Schemas
# --------------------------------------------------------------------------
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500, description="The user's search query.")
    tenant_id: str = Field("metro_tenant", min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$", description="Tenant isolation identifier.")
    entity_type_filter: Optional[str] = Field(
        None, pattern="^(contract_clause|ncr|dpr|correspondence)$", description="Optional domain constraint (contract_clause | ncr | dpr | correspondence)."
    )

class QueryResponse(BaseModel):
    query: str
    tenant_id: str
    answer: str
    citations: str
    confidence: str
    retrieval_trace: List[Dict[str, Any]]
    latency_ms: float
    latency_status: str
    latency_budget_ms: int

# --------------------------------------------------------------------------
# API Route handler
# --------------------------------------------------------------------------
@app.post("/query", response_model=QueryResponse)
def execute_query(request: QueryRequest, http_request: Request = None, api_key: str = Security(api_key_header)):
    """
    Executes a production-hardened RAG query.
    """
    start_time = time.time()

    # 1. Authenticate & Rate Limit
    verify_api_key(api_key)
    enforce_rate_limits(http_request, request.tenant_id)

    # 2. Sanitize Query against Prompt Injection
    try:
        query = sanitize_query(request.query)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    tenant = request.tenant_id
    domain_filter = request.entity_type_filter

    # ----------------------------------------------------------------------
    # 1. Out-of-Scope Check
    # ----------------------------------------------------------------------
    if check_query_out_of_scope(query):
        fallback_answer = "Insufficient data to answer this query."
        latency_ms = (time.time() - start_time) * 1000

        latency_status = "PASSED" if latency_ms <= MAX_LATENCY_MS else f"FAILED (cloud API bottleneck, exceeds by {int(latency_ms - MAX_LATENCY_MS)}ms)"

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