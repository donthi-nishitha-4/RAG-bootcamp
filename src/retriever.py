import os
import psycopg2
from psycopg2.extras import execute_values

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
    """Initialize pgvector table with schema"""
    conn = get_connection()
    if not conn:
        return False
        
    try:
        cur = conn.cursor()
        
        # Enable vector extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
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
        
        # Create index for vector similarity search
        cur.execute("""
            CREATE INDEX IF NOT EXISTS rag_embedding_idx 
            ON rag_documents USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """)
        
        print("[INFO] pgvector table initialized: rag_documents")
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] pgvector init failed: {e}")
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
    Retrieve similar documents from pgvector with metadata filtering.
    """
    conn = get_connection()
    if not conn:
        return []
        
    try:
        cur = conn.cursor()
        
        # Build dynamic query based on filters
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
        results = cur.fetchall()
        
        return results  # [(id, content, distance), ...]
    except Exception as e:
        print(f"[ERROR] Retrieval failed: {e}")
        return []
    finally:
        cur.close()
        conn.close()
