import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "5432")),
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

def init_pgvector():
    """Initialize pgvector and pg_trgm table with schema"""
    conn = get_connection()
    if not conn:
        return False
        
    try:
        cur = conn.cursor()
        
        # Enable extensions
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        
        # Create embeddings table with metadata
        cur.execute("""
            DROP TABLE IF EXISTS rag_documents CASCADE;
            CREATE TABLE rag_documents (
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
        
        # Create vector index
        cur.execute("""
            CREATE INDEX IF NOT EXISTS rag_embedding_idx 
            ON rag_documents USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """)

        # Create GIN index for pg_trgm (BM25-like search)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS rag_content_trgm_idx 
            ON rag_documents USING gin (content gin_trgm_ops);
        """)
        
        print("[INFO] pgvector and pg_trgm initialized.")
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] Init failed: {e}")
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
        
        query_sql = "SELECT id, content, embedding <-> %s::vector as distance FROM rag_documents WHERE tenant_id = %s"
        params = [query_embedding, tenant_id]
        
        if entity_type:
            query_sql += " AND entity_type = %s"
            params.append(entity_type)
            
        if contract_standard:
            query_sql += " AND contract_standard = %s"
            params.append(contract_standard)
            
        query_sql += " ORDER BY embedding <-> %s::vector LIMIT %s;"
        params.extend([query_embedding, k])
        
        cur.execute(query_sql, tuple(params))
        return cur.fetchall()
    except Exception as e:
        print(f"[ERROR] Vector retrieval failed: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def retrieve_trgm(query_text, tenant_id="default", k=3):
    """
    Retrieve similar documents using pg_trgm (text-based).
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        query_sql = """
            SELECT id, content, similarity(content, %s) as distance
            FROM rag_documents 
            WHERE tenant_id = %s AND content %% %s
            ORDER BY distance DESC 
            LIMIT %s;
        """
        cur.execute(query_sql, (query_text, tenant_id, query_text, k))
        return cur.fetchall()
    except Exception as e:
        print(f"[ERROR] Trgm retrieval failed: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def retrieve_hybrid(query_text, query_embedding, tenant_id="default", k=5):
    """
    Simple Hybrid Search: Combine Vector and Trigram results.
    """
    vec_results = retrieve_similar(query_embedding, tenant_id, k=k)
    trgm_results = retrieve_trgm(query_text, tenant_id, k=k)
    
    # Combine results by ID
    combined = {}
    for r in vec_results:
        combined[r[0]] = {"content": r[1], "vec_score": r[2], "trgm_score": 0}
    for r in trgm_results:
        if r[0] in combined:
            combined[r[0]]["trgm_score"] = r[2]
        else:
            combined[r[0]] = {"content": r[1], "vec_score": 1.0, "trgm_score": r[2]} # 1.0 is max distance
            
    # Simple RRF-like sorting (just adding scores for now)
    sorted_res = sorted(combined.items(), key=lambda x: (1-x[1]["trgm_score"]) + x[1]["vec_score"])
    return [(id, data["content"], 0.0) for id, data in sorted_res[:k]]

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
