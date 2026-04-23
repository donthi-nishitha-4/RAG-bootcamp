#!/usr/bin/env python3
"""
Test pgvector connection and basic operations
"""
import psycopg2
from psycopg2.extras import execute_values
import numpy as np

# Connection parameters
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "user": "rag_user",
    "password": "rag_password",
    "database": "rag_bootcamp"
}

def test_connection():
    """Test basic PostgreSQL connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"✅ PostgreSQL Connected: {version[0]}")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def setup_pgvector():
    """Enable pgvector extension and create test table"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Enable vector extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("✅ pgvector extension enabled")
        
        # Create test table with vector column
        cur.execute("""
            DROP TABLE IF EXISTS test_embeddings;
            CREATE TABLE test_embeddings (
                id SERIAL PRIMARY KEY,
                content TEXT,
                embedding vector(384)
            );
        """)
        print("✅ Test table created: test_embeddings (384-dim vectors)")
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

def insert_test_data():
    """Insert test embeddings"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Create 3 test embeddings
        test_data = [
            ("AI is used in healthcare for diagnosis", np.random.randn(384).tolist()),
            ("Machine learning improves with data", np.random.randn(384).tolist()),
            ("Deep learning uses neural networks", np.random.randn(384).tolist()),
        ]
        
        insert_query = "INSERT INTO test_embeddings (content, embedding) VALUES %s"
        execute_values(cur, insert_query, test_data)
        
        conn.commit()
        print(f"✅ Inserted {len(test_data)} test embeddings")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Insert failed: {e}")
        return False

def test_similarity_search():
    """Test vector similarity search"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Create a query vector (random for now)
        query_vector = np.random.randn(384).tolist()
        
        # Search for most similar embeddings
        query = """
            SELECT id, content, embedding <-> %s::vector as distance
            FROM test_embeddings
            ORDER BY embedding <-> %s::vector
            LIMIT 2;
        """
        
        cur.execute(query, (query_vector, query_vector))
        results = cur.fetchall()
        
        print("\n✅ Similarity Search Results:")
        for row in results:
            print(f"   ID: {row[0]}, Content: {row[1]}, Distance: {row[2]:.4f}")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False

def main():
    print("=" * 60)
    print("Testing pgvector Setup")
    print("=" * 60)
    
    print("\n[1/4] Testing connection...")
    if not test_connection():
        return False
    
    print("\n[2/4] Setting up pgvector...")
    if not setup_pgvector():
        return False
    
    print("\n[3/4] Inserting test data...")
    if not insert_test_data():
        return False
    
    print("\n[4/4] Testing similarity search...")
    if not test_similarity_search():
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED! pgvector is ready.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    main()
