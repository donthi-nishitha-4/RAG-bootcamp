import os
import psycopg2
from psycopg2.extras import execute_values
from src.utils.config import settings

DB_CONFIG = {
    "host": settings.DB_HOST,
    "port": settings.DB_PORT,
    "user": os.getenv("DB_USER", "rag_user"),
    "password": os.getenv("DB_PASSWORD", "rag_password"),
    "database": os.getenv("DB_NAME", "rag_bootcamp")
}

def get_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"[ERROR] DB Connection failed: {e}")
        return None

def check_table_exists():
    """Returns True if rag_documents table exists and has rows."""
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'rag_documents'
            );
        """)
        table_exists = cur.fetchone()[0]
        if not table_exists:
            print("[WARN] Table 'rag_documents' does not exist. Run ingest_data.py first.")
            return False
        cur.execute("SELECT COUNT(*) FROM rag_documents;")
        count = cur.fetchone()[0]
        print(f"[INFO] rag_documents has {count} rows.")
        return count > 0
    except Exception as e:
        print(f"[ERROR] Table check failed: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def init_pgvector():
    """Initialize pgvector and pg_trgm extensions and table schema.
    Uses CREATE TABLE IF NOT EXISTS — safe to call multiple times.
    The ivfflat vector index is deferred to build_vector_index() which
    must be called AFTER data is loaded (ivfflat requires rows to exist).
    """
    conn = get_connection()
    if not conn:
        return False
        
    try:
        cur = conn.cursor()
        
        # Enable extensions
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        
        # Create table only if it does not already exist (safe re-run)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rag_documents (
                id SERIAL PRIMARY KEY,
                tenant_id VARCHAR(255) DEFAULT 'default',
                entity_type VARCHAR(100),
                contract_standard VARCHAR(100),
                source_id VARCHAR(255),
                content TEXT NOT NULL,
                embedding vector(384) NOT NULL,
                chunk_index INT DEFAULT 0,
                parent_chunk_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # GIN index for pg_trgm is safe to create on empty tables
        cur.execute("""
            CREATE INDEX IF NOT EXISTS rag_content_trgm_idx 
            ON rag_documents USING gin (content gin_trgm_ops);
        """)
        
        print("[INFO] pgvector schema initialized (table + trgm index ready).")
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] Init failed: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def build_vector_index():
    """Build ivfflat vector index. MUST be called after data is loaded.
    ivfflat requires at least 1 row to exist before index creation.
    """
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM rag_documents;")
        count = cur.fetchone()[0]
        if count == 0:
            print("[WARN] Cannot build ivfflat index on empty table. Load data first.")
            return False
        # Lists = min(count/2, 100) to avoid ivfflat error on small datasets
        lists = max(1, min(count // 2, 100))
        cur.execute(f"""
            CREATE INDEX IF NOT EXISTS rag_embedding_idx 
            ON rag_documents USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = {lists});
        """)
        conn.commit()
        print(f"[INFO] ivfflat vector index built (lists={lists}, rows={count}).")
        return True
    except Exception as e:
        print(f"[ERROR] Vector index build failed: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def load_documents(documents, embeddings, entity_type="general", tenant_id="default", contract_standard=None):
    """
    Load documents and their embeddings into pgvector.
    """
    if len(documents) != len(embeddings):
        print("[ERROR] Mismatch between documents and embeddings count")
        return False
        
    if not documents:
        print("[WARN] No documents to load")
        return False
        
    print(f"[DEBUG] load_documents called with tenant_id: {tenant_id}")

    conn = get_connection()
    if not conn:
        return False
        
    try:
        cur = conn.cursor()
        
        # Prepare data
        data = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            data.append((
                tenant_id,
                entity_type,
                contract_standard,
                f"{entity_type}_{i}",  # source_id
                doc,
                embedding,
                i,  # chunk_index
                None  # parent_chunk_id
            ))
            
        if data:
            print(f"[DEBUG] First row to insert: {data[0][0]}, {data[0][1]}")
        
        # Insert
        insert_query = """
            INSERT INTO rag_documents 
            (tenant_id, entity_type, contract_standard, source_id, content, embedding, chunk_index, parent_chunk_id)
            VALUES %s
            RETURNING id, source_id
        """
        results = execute_values(cur, insert_query, data, fetch=True)
        
        conn.commit()
        print(f"[INFO] Loaded {len(results)} documents into pgvector")
        return True
    except Exception as e:
        print(f"[ERROR] Document load failed: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def retrieve_similar(query_embedding, tenant_id="default", entity_type=None, contract_standard=None, k=3):
    """
    Retrieve similar documents from pgvector.
    """
    conn = get_connection()
    if not conn:
        return []
        
    try:
        cur = conn.cursor()
        query_sql = """
            SELECT id, content, embedding <-> %s::vector as distance 
            FROM rag_documents 
            WHERE tenant_id = %s
        """
        params = [query_embedding, tenant_id]

        if entity_type:
            query_sql += " AND entity_type = %s"
            params.append(entity_type)
            
        if contract_standard:
            query_sql += " AND contract_standard = %s"
            params.append(contract_standard)

        query_sql += " ORDER BY distance ASC LIMIT %s;"
        params.append(k)

        cur.execute(query_sql, tuple(params))
        raw_results = cur.fetchall()

        print(
            f"[DEBUG][retriever] raw_results_count={len(raw_results)} "
            f"tenant_id={tenant_id} entity_type={entity_type} "
            f"contract_standard={contract_standard} threshold={settings.RETRIEVAL_DISTANCE_THRESHOLD}"
        )

        filtered = [r for r in raw_results if r[2] is not None and r[2] < settings.RETRIEVAL_DISTANCE_THRESHOLD]
        if filtered:
            print(f"[DEBUG][retriever] filtered_results_count={len(filtered)}")
            return filtered

        if raw_results:
            print(
                "[WARN][retriever] Distance threshold removed all candidates; "
                "returning raw top-k results to preserve recall."
            )
            return raw_results

        return []
        
    except Exception as e:
        print(f"[ERROR] Vector retrieval failed: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def retrieve_trgm(query_text, tenant_id="default", entity_type=None, contract_standard=None, k=3):
    """
    Retrieve similar documents using pg_trgm (text-based).
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        
        query_sql = "SELECT id, content, similarity(content, %s) as distance FROM rag_documents WHERE tenant_id = %s AND content %% %s"
        params = [query_text, tenant_id, query_text]
        
        if entity_type:
            query_sql += " AND entity_type = %s"
            params.append(entity_type)
            
        if contract_standard:
            query_sql += " AND contract_standard = %s"
            params.append(contract_standard)
            
        query_sql += " ORDER BY distance DESC LIMIT %s;"
        params.append(k)
        
        cur.execute(query_sql, tuple(params))
        return cur.fetchall()
    except Exception as e:
        print(f"[ERROR] Trgm retrieval failed: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def retrieve_hybrid(query_text, query_embedding, tenant_id="default", entity_type=None, contract_standard=None, k=5, rrf_k=60):
    """
    Hybrid Search: Combine Vector and Trigram results using Reciprocal Rank Fusion (RRF).
    """
    vec_results = retrieve_similar(query_embedding, tenant_id, entity_type, contract_standard, k=k)
    trgm_results = retrieve_trgm(query_text, tenant_id, entity_type, contract_standard, k=k)
    
    combined = {}
    
    # Rank vectors
    for rank, (doc_id, content, distance) in enumerate(vec_results):
        if doc_id not in combined:
            combined[doc_id] = {"content": content, "rrf_score": 0}
        combined[doc_id]["rrf_score"] += 1.0 / (rrf_k + rank + 1)
        
    # Rank trgm
    for rank, (doc_id, content, similarity) in enumerate(trgm_results):
        if doc_id not in combined:
            combined[doc_id] = {"content": content, "rrf_score": 0}
        combined[doc_id]["rrf_score"] += 1.0 / (rrf_k + rank + 1)
        
    # Sort by descending RRF score
    sorted_res = sorted(combined.items(), key=lambda x: x[1]["rrf_score"], reverse=True)
    return [(doc_id, data["content"], data["rrf_score"]) for doc_id, data in sorted_res[:k]]

def retrieve_graph(chunk_id):
    """
    Mock Graph RAG: Retrieve neighbors/parent of a chunk.
    Demonstrates 'Graph Layer' capability without Apache AGE.
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        query_sql = "SELECT id, content FROM rag_documents WHERE parent_chunk_id = (SELECT parent_chunk_id FROM rag_documents WHERE id = %s) OR id = %s"
        cur.execute(query_sql, (chunk_id, chunk_id))
        return cur.fetchall()
    except Exception as e:
        print(f"[ERROR] Graph retrieval failed: {e}")
        return []
    finally:
        cur.close()
        conn.close()
