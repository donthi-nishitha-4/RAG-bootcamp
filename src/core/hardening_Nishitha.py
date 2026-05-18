"""
================================================================================
Author: Nishitha
Role: Advanced RAG Ingestion Engineering
Created: 2026-05-18
Description: Custom Day 9 Production Hardening Essentials.
             Implements PostgreSQL RLS policies, out-of-scope fallback,
             CDM Layer 4 AuditEvent logs, Idempotent SHA-256 ingestion,
             and trace-accurate Citation Chains.
================================================================================
"""
import os
import sys
import hashlib
import time
import json
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path so we can import src core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.retriever import get_connection

# ==============================================================================
# 1. PostgreSQL Row-Level Security (RLS) & Table Hardening Setup
# ==============================================================================
def setup_database_hardening() -> bool:
    """
    Applies production security policies to PostgreSQL:
    - Adds content_hash column with a UNIQUE constraint for idempotent ingestion.
    - Enables Row-Level Security (RLS) on rag_documents.
    - Sets up RLS tenant isolation policy.
    - Creates the CDM Layer 4 AuditEvent table.
    """
    conn = get_connection()
    if not conn:
        print("[RLS Setup Warn] Database connection unavailable. Using simulated hardening.")
        return False
        
    try:
        cur = conn.cursor()
        
        # 1. Idempotency column & unique constraint
        cur.execute("""
            ALTER TABLE rag_documents 
            ADD COLUMN IF NOT EXISTS content_hash VARCHAR(64);
        """)
        
        # Add unique constraint to content_hash if it doesn't exist
        cur.execute("""
            SELECT count(*) FROM pg_constraint WHERE conname = 'uq_content_hash';
        """)
        if cur.fetchone()[0] == 0:
            cur.execute("""
                ALTER TABLE rag_documents 
                ADD CONSTRAINT uq_content_hash UNIQUE (content_hash);
            """)
            print("[HARDENING] Added Unique Content Hash Constraint.")
            
        # 2. Enable Row-Level Security (RLS)
        cur.execute("ALTER TABLE rag_documents ENABLE ROW LEVEL SECURITY;")
        
        # 3. Create Tenant Isolation Policy (tied to app session tenant variable)
        cur.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON rag_documents;")
        cur.execute("""
            CREATE POLICY tenant_isolation_policy ON rag_documents
            FOR ALL
            USING (tenant_id = current_setting('app.current_tenant_id', true));
        """)
        print("[HARDENING] Enabled PostgreSQL Row-Level Security Policy.")
        
        # 4. Create AuditEvent Table (CDM Layer 4 Audit Event specification)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(100) DEFAULT 'AuditEvent',
                tenant_id VARCHAR(255),
                query TEXT,
                retrieved_chunk_ids VARCHAR(255)[],
                final_answer TEXT,
                latency_ms DOUBLE PRECISION,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("[HARDENING] Initialized CDM Layer 4 Audit Logging Schema.")
        
        conn.commit()
        return True
    except Exception as e:
        print(f"[HARDENING ERROR] Schema hardening failed: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

# ==============================================================================
# 2. Idempotent Ingestion (SHA-256 Hash Deduplication)
# ==============================================================================
def calculate_content_hash(text: str) -> str:
    """
    Calculates SHA-256 checksum of the text content to prevent duplicate chunk ingestion.
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def load_documents_idempotent(documents: List[str], embeddings: List[List[float]], entity_type="general", tenant_id="default") -> int:
    """
    Ingests documents idempotently. Skips duplicates using SHA-256 content hashes.
    """
    inserted_count = 0
    conn = get_connection()
    if not conn:
        print("[INGESTION FAILSAFE] Database offline. Simulating idempotent load.")
        return len(documents) # simulation fallback
        
    try:
        cur = conn.cursor()
        for idx, (doc, emb) in enumerate(zip(documents, embeddings)):
            doc_hash = calculate_content_hash(doc)
            source_id = f"{entity_type}_{int(time.time())}_{idx}"
            
            # Use ON CONFLICT DO NOTHING to guarantee idempotency!
            cur.execute("""
                INSERT INTO rag_documents 
                (tenant_id, entity_type, source_id, content, embedding, content_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (content_hash) DO NOTHING;
            """, (tenant_id, entity_type, source_id, doc, emb, doc_hash))
            
            inserted_count += cur.rowcount
            
        conn.commit()
        return inserted_count
    except Exception as e:
        print(f"[INGESTION ERROR] Idempotent load failed: {e}")
        conn.rollback()
        return 0
    finally:
        cur.close()
        conn.close()

# ==============================================================================
# 3. Row-Level Security (RLS) Query Executor
# ==============================================================================
def retrieve_with_rls(query_embedding: List[float], tenant_id: str, k: int = 3) -> List[Dict[str, Any]]:
    """
    Retrieves vector documents using PostgreSQL RLS policies.
    Executes SET LOCAL app.current_tenant_id in transaction blocks to isolate data.
    """
    conn = get_connection()
    if not conn:
        print("[RLS FAILSAFE] Database offline. Simulating RLS Isolation.")
        return []
        
    try:
        cur = conn.cursor()
        
        # Start a local transaction and apply the tenant identifier session variable
        cur.execute("BEGIN;")
        cur.execute("SET LOCAL app.current_tenant_id = %s;", (tenant_id,))
        
        # Perform retrieval - the RLS policy will automatically filter out any other tenants!
        cur.execute("""
            SELECT id, tenant_id, entity_type, content, embedding <-> %s::vector as distance
            FROM rag_documents
            ORDER BY distance LIMIT %s;
        """, (query_embedding, k))
        
        rows = cur.fetchall()
        cur.execute("COMMIT;")
        
        results = []
        for r in rows:
            results.append({
                "id": r[0],
                "tenant_id": r[1],
                "entity_type": r[2],
                "content": r[3],
                "distance": r[4]
            })
        return results
    except Exception as e:
        print(f"[RLS RETRIEVAL ERROR] RLS query failed: {e}")
        return []
    finally:
        cur.close()
        conn.close()

# ==============================================================================
# 4. Out-of-Scope Fallback & Citation Chain Generator
# ==============================================================================
OUT_OF_SCOPE_WORDS = [
    "france", "paris", "canada", "cricket", "football", "weather", 
    "recipe", "movie", "celebrity", "song", "joke", "politics",
    "president", "japan", "tokyo", "capital", "united states", "america", "usa"
]

def check_query_out_of_scope(query: str) -> bool:
    """
    Simple check to identify completely out-of-scope adversarial questions.
    """
    q_lower = query.lower()
    return any(word in q_lower for word in OUT_OF_SCOPE_WORDS)

def generate_hardened_citation_chain(retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    Constructs a deterministic, 100% accurate, un-hallucinated citation block.
    """
    if not retrieved_chunks:
        return ""
        
    citation_lines = ["\n### 🔗 Hardened Citation Chain (Traceable back to CDM):"]
    for chunk in retrieved_chunks:
        chunk_id = chunk.get("id", "N/A")
        tenant = chunk.get("tenant_id", "default")
        domain = chunk.get("entity_type", "general")
        score = chunk.get("distance", 0.0)
        
        citation_lines.append(
            f"- **Chunk ID**: `{chunk_id}` | **Tenant Domain**: `{tenant.upper()}` | **Domain**: `{domain.upper()}` | **Cosine Distance**: `{score:.4f}`"
        )
    return "\n".join(citation_lines)

# ==============================================================================
# 5. CDM Layer 4 Audit Logging
# ==============================================================================
def write_audit_log(tenant_id: str, query: str, chunk_ids: List[str], answer: str, latency_ms: float):
    """
    Saves RAG queries and metadata following the CDM Layer 4 AuditEvent schema.
    Falls back to a local JSON audit ledger when the database is offline.
    """
    # 1. Attempt Database audit insert
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO audit_events (tenant_id, query, retrieved_chunk_ids, final_answer, latency_ms)
                VALUES (%s, %s, %s, %s, %s);
            """, (tenant_id, query, chunk_ids, answer, latency_ms))
            conn.commit()
            cur.close()
            conn.close()
            print("[AUDIT LOG] Audit log committed successfully to PostgreSQL.")
            return
        except Exception as e:
            print(f"[AUDIT LOG WARN] DB Audit insert failed: {e}. Writing to JSON fallback.")
            
    # 2. Local Fallback JSON Ledger
    audit_file = "experiments/results/audit_events_ledger_Nishitha.json"
    audit_event = {
        "event_type": "AuditEvent",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tenant_id": tenant_id,
        "query": query,
        "retrieved_chunk_ids": chunk_ids,
        "final_answer": answer,
        "latency_ms": latency_ms
    }
    
    events = []
    if os.path.exists(audit_file):
        try:
            with open(audit_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
        except Exception:
            pass
            
    events.append(audit_event)
    try:
        with open(audit_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2)
        print(f"[AUDIT LOG] Audit event saved locally to: {audit_file}")
    except Exception as e:
        print(f"[AUDIT LOG ERROR] Failed to write local audit file: {e}")
