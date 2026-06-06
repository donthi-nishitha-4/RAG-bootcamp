# src/core/security/audit.py
import hashlib
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from src.core.database.connection import get_connection
from src.utils.config import settings

def write_audit_log(tenant_id: str, query: str, chunk_ids: List[str], answer: str, latency_ms: float):
    query_hash = hashlib.sha256(query.encode('utf-8')).hexdigest()
    answer_hash = hashlib.sha256(answer.encode('utf-8')).hexdigest()
    
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO audit_events (tenant_id, query, retrieved_chunk_ids, final_answer, latency_ms)
                VALUES (%s, %s, %s, %s, %s);
            """, (tenant_id, query_hash, chunk_ids, answer_hash, latency_ms))
            conn.commit()
            cur.close()
            conn.close()
            return
        except Exception as e:
            print(f"[AUDIT LOG WARN] DB Audit insert failed: {e}")

    audit_event = {
        "event_type": "AuditEvent",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tenant_id": tenant_id,
        "query_hash": query_hash,
        "retrieved_chunk_ids": chunk_ids,
        "response_hash": answer_hash,
        "latency_ms": latency_ms
    }
    
    events = []
    if os.path.exists(settings.AUDIT_LOG_FILE):
        with open(settings.AUDIT_LOG_FILE, 'r', encoding='utf-8') as f:
            try: events = json.load(f)
            except: pass
    events.append(audit_event)
    with open(settings.AUDIT_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2)

def generate_hardened_citation_chain(retrieved_chunks: List[Dict[str, Any]]) -> str:
    if not retrieved_chunks:
        return ""
    citation_lines = ["\n### 🔗 Hardened Citation Chain (Traceable back to CDM):"]
    for chunk in retrieved_chunks:
        citation_lines.append(
            f"- **Chunk ID**: `{chunk.get('id')}` | **Tenant**: `{chunk.get('tenant_id', 'default').upper()}` | **Domain**: `{chunk.get('entity_type', 'general').upper()}`"
        )
    return "\n".join(citation_lines)