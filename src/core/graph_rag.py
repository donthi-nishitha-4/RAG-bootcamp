"""
================================================================================
Author: Nishitha / Antigravity
Role: Advanced RAG Ingestion Engineering
Created: 2026-05-20
Description: GraphRAG Core Module. Handles schema initialization, semantic node 
             lookup, edge traversals, and interface impact analysis.
================================================================================
"""
import os
import sys
import psycopg2
from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer

# Add project root to path so we can import src core modules

from src.core.retriever import get_connection, DB_CONFIG

def init_taxonomy_schema():
    """
    Initialize taxonomy nodes and edges tables inside PostgreSQL.
    Drops existing tables first to ensure clean ingestion.
    """
    conn = get_connection()
    if not conn:
        print("[ERROR] Database connection failed for schema init.")
        return False
        
    try:
        cur = conn.cursor()
        
        # Drop tables in dependency order
        print("[INFO] Dropping existing taxonomy tables if they exist...")
        cur.execute("DROP TABLE IF EXISTS taxonomy_edges CASCADE;")
        cur.execute("DROP TABLE IF EXISTS taxonomy_nodes CASCADE;")
        
        # Create taxonomy_nodes
        print("[INFO] Creating taxonomy_nodes table...")
        cur.execute("""
            CREATE TABLE taxonomy_nodes (
                id VARCHAR(100) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                level INT NOT NULL,
                parent_id VARCHAR(100) REFERENCES taxonomy_nodes(id) ON DELETE CASCADE,
                description TEXT,
                key_equipment TEXT,
                responsible_dept VARCHAR(255),
                standards TEXT,
                phase VARCHAR(100),
                criticality VARCHAR(50),
                capex_opex_tag VARCHAR(50),
                embedding vector(384)
            );
        """)
        
        # Create taxonomy_edges
        print("[INFO] Creating taxonomy_edges table...")
        cur.execute("""
            CREATE TABLE taxonomy_edges (
                id SERIAL PRIMARY KEY,
                from_node_id VARCHAR(100) REFERENCES taxonomy_nodes(id) ON DELETE CASCADE,
                to_node_id VARCHAR(100) REFERENCES taxonomy_nodes(id) ON DELETE CASCADE,
                relationship_type VARCHAR(100) NOT NULL,
                CONSTRAINT unique_edge UNIQUE(from_node_id, to_node_id, relationship_type)
            );
        """)
        
        # Index on parent_id and node embeddings
        cur.execute("CREATE INDEX IF NOT EXISTS idx_taxonomy_parent ON taxonomy_nodes(parent_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_taxonomy_level ON taxonomy_nodes(level);")
        
        conn.commit()
        print("[SUCCESS] Taxonomy schema successfully initialized.")
        return True
    except Exception as e:
        print(f"[ERROR] Schema init failed: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def retrieve_graph_nodes(query_text, k=3):
    """
    Performs semantic vector search on the taxonomy_nodes table.
    """
    conn = get_connection()
    if not conn:
        return []
        
    try:
        embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        q_emb = embed_model.encode(query_text).tolist()
        
        cur = conn.cursor()
        query_sql = """
            SELECT id, name, level, description, key_equipment, responsible_dept, criticality,
                   embedding <-> %s::vector as distance
            FROM taxonomy_nodes
            ORDER BY embedding <-> %s::vector
            LIMIT %s;
        """
        cur.execute(query_sql, (q_emb, q_emb, k))
        results = cur.fetchall()
        
        formatted = []
        for r in results:
            formatted.append({
                "id": r[0],
                "name": r[1],
                "level": r[2],
                "description": r[3],
                "key_equipment": r[4],
                "responsible_dept": r[5],
                "criticality": r[6],
                "score": 1.0 - r[7] # Cosine similarity representation
            })
        return formatted
    except Exception as e:
        print(f"[ERROR] Node semantic retrieval failed: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def get_node_neighbors(node_id, relation_type=None):
    """
    Traverses edges and retrieves all neighbor nodes connected to/from a node.
    """
    conn = get_connection()
    if not conn:
        return []
        
    try:
        cur = conn.cursor()
        query_sql = """
            SELECT e.relationship_type, n.id, n.name, n.level, n.description, 'TO' as direction
            FROM taxonomy_edges e
            JOIN taxonomy_nodes n ON e.to_node_id = n.id
            WHERE e.from_node_id = %s
        """
        params = [node_id]
        if relation_type:
            query_sql += " AND e.relationship_type = %s"
            params.append(relation_type)
            
        query_sql += """
            UNION ALL
            SELECT e.relationship_type, n.id, n.name, n.level, n.description, 'FROM' as direction
            FROM taxonomy_edges e
            JOIN taxonomy_nodes n ON e.from_node_id = n.id
            WHERE e.to_node_id = %s
        """
        params.append(node_id)
        if relation_type:
            query_sql += " AND e.relationship_type = %s"
            params.append(relation_type)
            
        cur.execute(query_sql, tuple(params))
        results = cur.fetchall()
        
        neighbors = []
        for r in results:
            neighbors.append({
                "relationship_type": r[0],
                "id": r[1],
                "name": r[2],
                "level": r[3],
                "description": r[4],
                "direction": r[5]
            })
        return neighbors
    except Exception as e:
        print(f"[ERROR] Neighbor retrieval failed: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def get_hierarchical_path(node_id):
    """
    Retrieves the hierarchical backtrace path for a node up to L1 (e.g. L4 -> L3 -> L2 -> L1).
    """
    conn = get_connection()
    if not conn:
        return []
        
    try:
        cur = conn.cursor()
        # Recursive CTE to build path
        query_sql = """
            WITH RECURSIVE path_cte AS (
                SELECT id, name, level, parent_id
                FROM taxonomy_nodes
                WHERE id = %s
                UNION ALL
                SELECT p.id, p.name, p.level, p.parent_id
                FROM taxonomy_nodes p
                JOIN path_cte c ON c.parent_id = p.id
            )
            SELECT id, name, level FROM path_cte ORDER BY level ASC;
        """
        cur.execute(query_sql, (node_id,))
        results = cur.fetchall()
        return [{"id": r[0], "name": r[1], "level": r[2]} for r in results]
    except Exception as e:
        print(f"[ERROR] Hierarchical path query failed: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def get_interface_impact_analysis(system_code):
    """
    Day 7 Interface Impact Analysis: Finds all systems interfacing with a specific system 
    code, and returns the relationship counts/details.
    """
    conn = get_connection()
    if not conn:
        return []
        
    try:
        cur = conn.cursor()
        query_sql = """
            SELECT e.relationship_type, n.id, n.name, e.to_node_id, n2.name, 'OUTGOING' as direction
            FROM taxonomy_edges e
            JOIN taxonomy_nodes n ON e.from_node_id = n.id
            JOIN taxonomy_nodes n2 ON e.to_node_id = n2.id
            WHERE e.from_node_id = %s
            UNION ALL
            SELECT e.relationship_type, n2.id, n2.name, e.from_node_id, n.name, 'INCOMING' as direction
            FROM taxonomy_edges e
            JOIN taxonomy_nodes n ON e.from_node_id = n.id
            JOIN taxonomy_nodes n2 ON e.to_node_id = n2.id
            WHERE e.to_node_id = %s;
        """
        cur.execute(query_sql, (system_code, system_code))
        results = cur.fetchall()
        
        impacts = []
        for r in results:
            impacts.append({
                "relationship_type": r[0],
                "source_id": r[1],
                "source_name": r[2],
                "target_id": r[3],
                "target_name": r[4],
                "direction": r[5]
            })
        return impacts
    except Exception as e:
        print(f"[ERROR] Interface impact analysis failed: {e}")
        return []
    finally:
        cur.close()
        conn.close()
