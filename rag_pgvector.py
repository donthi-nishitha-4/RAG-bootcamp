#!/usr/bin/env python3
"""
RAG Pipeline using PostgreSQL + pgvector (Production-Ready)
Replaces ChromaDB-based rag_chroma.py
"""

from sentence_transformers import SentenceTransformer, CrossEncoder
from openai import OpenAI
import psycopg2
from psycopg2.extras import execute_values
import sys
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
TOP_K = 3
FINAL_K = 2

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "user": os.getenv("DB_USER", "rag_user"),
    "password": os.getenv("DB_PASSWORD", "rag_password"),
    "database": os.getenv("DB_NAME", "rag_bootcamp")
}

# ---- SETUP MODELS ----
try:
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")
    print("[INFO] Models loaded")
except Exception as e:
    print(f"[ERROR] Model load failed: {e}")
    sys.exit(1)

# ---- INITIALIZE PGVECTOR ----
def init_pgvector():
    """Initialize pgvector table with schema"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
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
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] pgvector init failed: {e}")
        return False

# ---- LOAD DOCUMENTS INTO PGVECTOR ----
def load_documents(documents, entity_type="general", tenant_id="default"):
    """
    Load documents into pgvector
    
    Args:
        documents: list of strings
        entity_type: type of document (contract_clause, ncr, dpr, etc.)
        tenant_id: tenant identifier for multi-tenancy
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Generate embeddings
        embeddings = embed_model.encode(documents)
        
        # Prepare data
        data = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            data.append((
                tenant_id,
                entity_type,
                f"{entity_type}_{i}",  # source_id
                doc,
                embedding.tolist(),
                i,  # chunk_index
                None  # parent_chunk_id (not hierarchical yet)
            ))
        
        # Insert
        insert_query = """
            INSERT INTO rag_documents 
            (tenant_id, entity_type, source_id, content, embedding, chunk_index, parent_chunk_id)
            VALUES %s
            RETURNING id, source_id
        """
        results = execute_values(cur, insert_query, data, fetch=True)
        
        conn.commit()
        print(f"[INFO] Loaded {len(results)} documents into pgvector")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] Document load failed: {e}")
        return False

# ---- RETRIEVE FROM PGVECTOR ----
def retrieve_similar(query, tenant_id="default", k=TOP_K):
    """
    Retrieve similar documents from pgvector
    
    Args:
        query: query string
        tenant_id: filter by tenant
        k: number of results
        
    Returns:
        list of (id, content) tuples
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Embed query
        query_embedding = embed_model.encode([query])[0].tolist()
        
        # Search with metadata filtering
        query_sql = """
            SELECT id, content, embedding <-> %s::vector as distance
            FROM rag_documents
            WHERE tenant_id = %s
            ORDER BY embedding <-> %s::vector
            LIMIT %s;
        """
        
        cur.execute(query_sql, (query_embedding, tenant_id, query_embedding, k))
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return results  # (id, content, distance)
    except Exception as e:
        print(f"[ERROR] Retrieval failed: {e}")
        return []

# ---- FALLBACK LLM FUNCTION ----
def query_llm(messages):
    """Query LLM with fallback providers"""
    providers = [
        {
            "name": "groq",
            "base_url": "https://api.groq.com/openai/v1",
            "api_key": os.getenv("GROQ_API_KEY"),
            "model": "llama-3.3-70b-versatile"
        },
        {
            "name": "openrouter",
            "base_url": "https://openrouter.ai/api/v1",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "model": "deepseek/deepseek-chat-v3-0324:free"
        },
        {
            "name": "cerebras",
            "base_url": "https://api.cerebras.ai/v1",
            "api_key": os.getenv("CEREBRAS_API_KEY"),
            "model": "llama3.1-70b"
        },
        {
            "name": "google",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "api_key": os.getenv("GEMINI_API_KEY"),
            "model": "gemini-1.5-pro"
        }
    ]
    for p in providers:
        if not p["api_key"]:
            continue
        try:
            client = OpenAI(
                base_url=p["base_url"],
                api_key=p["api_key"]
            )
            response = client.chat.completions.create(
                model=p["model"],
                messages=messages,
                temperature=0.1
            )
            print(f"[INFO] Used provider: {p['name']}")
            return response.choices[0].message.content
        except Exception as e:
            print(f"[WARN] {p['name']} failed: {e}")
            time.sleep(1)
    return "[ERROR] All LLM providers failed"

# ---- RAG FUNCTION (pgvector-based) ----
def ask_rag(query, tenant_id="default"):
    """
    RAG pipeline using pgvector
    
    Returns:
        dict with query, context, answer, chunk_ids, sources
    """
    if not query or not query.strip():
        return {
            "query": query,
            "retrieved_chunks": [],
            "context": "",
            "answer": "[ERROR] Empty query",
            "chunk_ids": [],
            "sources": []
        }
    
    try:
        # Retrieve from pgvector
        results = retrieve_similar(query, tenant_id=tenant_id, k=TOP_K)
        
        if not results:
            return {
                "query": query,
                "retrieved_chunks": [],
                "context": "",
                "answer": "[ERROR] No documents retrieved",
                "chunk_ids": [],
                "sources": []
            }
        
        top_docs = [r[1] for r in results]
        chunk_ids = [str(r[0]) for r in results]
        
    except Exception as e:
        return {
            "query": query,
            "retrieved_chunks": [],
            "context": "",
            "answer": f"[ERROR] Retrieval failed: {e}",
            "chunk_ids": [],
            "sources": []
        }
    
    print("\n[INFO] Top-K retrieved from pgvector:")
    for i, (doc_id, doc, dist) in enumerate(results):
        print(f"{i+1}. [ID: {doc_id}, Distance: {dist:.4f}] {doc}")
    
    # ---- RERANK ----
    try:
        pairs = [(query, doc) for doc in top_docs]
        scores = reranker.predict(pairs)
        ranked = sorted(zip(scores, top_docs, chunk_ids), reverse=True)
        final_docs = [doc for _, doc, _ in ranked[:FINAL_K]]
        final_chunk_ids = [cid for _, _, cid in ranked[:FINAL_K]]
        
        if not final_docs:
            return {
                "query": query,
                "retrieved_chunks": top_docs,
                "context": "",
                "answer": "[ERROR] Reranking returned empty results",
                "chunk_ids": chunk_ids,
                "sources": []
            }
    except Exception as e:
        return {
            "query": query,
            "retrieved_chunks": top_docs,
            "context": "",
            "answer": f"[ERROR] Reranking failed: {e}",
            "chunk_ids": chunk_ids,
            "sources": []
        }
    
    print("\n[INFO] After reranking:")
    for i, d in enumerate(final_docs):
        print(f"{i+1}. {d}")
    
    combined_context = "\n".join(final_docs)
    
    # ---- LLM CALL ----
    answer = query_llm([
        {"role": "system", "content": "Answer using the given context."},
        {"role": "user", "content": f"Context:\n{combined_context}\n\nQuestion: {query}"}
    ])
    
    return {
        "query": query,
        "retrieved_chunks": final_docs,
        "context": combined_context,
        "answer": answer,
        "chunk_ids": final_chunk_ids,
        "sources": [{"chunk_id": cid, "text": doc} for cid, doc in zip(final_chunk_ids, final_docs)]
    }

# ---- MAIN ----
if __name__ == "__main__":
    print("[INFO] RAG Pipeline with pgvector\n")
    
    # Initialize
    if not init_pgvector():
        sys.exit(1)
    
    # Load sample documents
    documents = [
        "AI is used in healthcare for diagnosis",
        "Machine learning improves with data",
        "Deep learning uses neural networks",
        "Python is widely used for AI development"
    ]
    
    if not load_documents(documents, entity_type="sample", tenant_id="default"):
        sys.exit(1)
    
    # Test query
    print("\n" + "="*60)
    print("Testing pgvector RAG Pipeline")
    print("="*60)
    
    query = "How is AI used in medicine?"
    result = ask_rag(query)
    
    print("\n[FINAL ANSWER]")
    print(result["answer"])
    
    print("\n[SOURCES]")
    for source in result["sources"]:
        print(f"  Chunk {source['chunk_id']}: {source['text']}")
    
    print("\n" + "="*60)
    print("✅ pgvector RAG Pipeline Working!")
    print("="*60)
