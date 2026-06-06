# src/core/security/database.py
from src.core.database.connection import get_connection
from typing import List, Dict, Any

def setup_database_hardening() -> bool:
    conn = get_connection()
    if not conn:
        print("[RLS Setup Warn] Database connection unavailable. Using simulated hardening.")
        return False
    try:
        cur = conn.cursor()
        cur.execute("""ALTER TABLE rag_documents ADD COLUMN IF NOT EXISTS content_hash VARCHAR(64);""")
        cur.execute("""SELECT count(*) FROM pg_constraint WHERE conname = 'uq_content_hash';""")
        if cur.fetchone()[0] == 0:
            cur.execute("""ALTER TABLE rag_documents ADD CONSTRAINT uq_content_hash UNIQUE (content_hash);""")
        cur.execute("ALTER TABLE rag_documents ENABLE ROW LEVEL SECURITY;")
        cur.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON rag_documents;")
        cur.execute("""
            CREATE POLICY tenant_isolation_policy ON rag_documents
            FOR ALL
            USING (tenant_id = current_setting('app.current_tenant_id', true));
        """)
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
        conn.commit()
        return True
    except Exception as e:
        print(f"[HARDENING ERROR] Schema hardening failed: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def retrieve_with_rls(query_embedding: List[float], tenant_id: str, k: int = 3) -> List[Dict[str, Any]]:
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute("BEGIN;")
        cur.execute("SET LOCAL app.current_tenant_id = %s;", (tenant_id,))
        cur.execute("""
            SELECT id, tenant_id, entity_type, content, embedding <-> %s::vector as distance
            FROM rag_documents
            ORDER BY distance LIMIT %s;
        """, (query_embedding, k))
        rows = cur.fetchall()
        cur.execute("COMMIT;")
        return [{"id": r[0], "tenant_id": r[1], "entity_type": r[2], "content": r[3], "distance": r[4]} for r in rows]
    finally:
        cur.close()
        conn.close()
# src/core/security/database.py (Add this to the end of the file)
import hashlib
import time

def calculate_content_hash(text: str) -> str:
    """Calculates SHA-256 checksum of the text content."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def load_documents_idempotent(documents: List[str], embeddings: List[List[float]], entity_type="general", tenant_id="default") -> int:
    """Ingests documents idempotently. Skips duplicates using SHA-256 content hashes."""
    inserted_count = 0
    conn = get_connection()
    if not conn:
        return len(documents)
        
    try:
        cur = conn.cursor()
        for idx, (doc, emb) in enumerate(zip(documents, embeddings)):
            doc_hash = calculate_content_hash(doc)
            source_id = f"{entity_type}_{int(time.time())}_{idx}"
            cur.execute("""
                INSERT INTO rag_documents 
                (tenant_id, entity_type, source_id, content, embedding, content_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (content_hash) DO NOTHING;
            """, (tenant_id, entity_type, source_id, doc, emb, doc_hash))
            inserted_count += cur.rowcount
        conn.commit()
        return inserted_count
    finally:
        cur.close()
        conn.close()