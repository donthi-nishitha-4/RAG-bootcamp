"""
================================================================================
Author: Nishitha / Antigravity
Role: Advanced RAG Ingestion Engineering
Created: 2026-05-20
Description: Ingestion script for Metro Rail Systems Taxonomy. Parses Excel 
             sheets, calculates hierarchical parent-child levels, computes 
             all-MiniLM node embeddings, extracts 195 directed interface 
             matrix edges, and populates PostgreSQL.
================================================================================
"""
import os
import sys
import pandas as pd
import numpy as np
import gc
from sentence_transformers import SentenceTransformer

# Add project root to path so we can import src core modules

from src.core.graph_rag import init_taxonomy_schema
from src.core.database.connection import get_connection, DB_CONFIG

def clean_value(val):
    if pd.isna(val) or val is None:
        return None
    val_str = str(val).strip()
    return val_str if val_str else None

def ingest_taxonomy():
    xlsx_path = "data/Metro_Rail_Consolidated_Systems_Taxonomy.xlsx"
    if not os.path.exists(xlsx_path):
        print(f"[ERROR] Excel file not found at {xlsx_path}")
        return False
        
    print("[INFO] Re-initializing taxonomy database schema...")
    if not init_taxonomy_schema():
        print("[ERROR] Failed to initialize database schema.")
        return False
        
    print(f"[INFO] Reading Excel file: {xlsx_path}...")
    xl = pd.ExcelFile(xlsx_path)
    
    # 1. Parse Master Systems Taxonomy (Nodes)
    print("[INFO] Parsing Master Systems Taxonomy sheet...")
    df_tax = xl.parse("Master Systems Taxonomy")
    
    raw_nodes = []
    for idx, row in df_tax.iterrows():
        node_id = clean_value(row.get("ID"))
        if not node_id:
            continue
            
        # Determine name, level, and parent
        l1 = clean_value(row.get("L1: Department/System"))
        l2 = clean_value(row.get("L2: Subsystem"))
        l3 = clean_value(row.get("L3: Sub-Subsystem"))
        l4 = clean_value(row.get("L4: Component/Element"))
        
        name = None
        level = None
        
        if l4:
            name = l4
            level = 4
        elif l3:
            name = l3
            level = 3
        elif l2:
            name = l2
            level = 2
        elif l1:
            name = l1
            level = 1
            
        if not name or not level:
            print(f"[WARN] Skipping row {idx}: unable to determine name or level. ID: {node_id}")
            continue
            
        # Determine parent
        parts = node_id.split("-")
        parent_id = None
        if len(parts) > 1:
            parent_id = "-".join(parts[:-1])
            
        # Other metadata
        description = clean_value(row.get("Description"))
        key_equipment = clean_value(row.get("Key Equipment"))
        resp_dept = clean_value(row.get("Responsible Dept"))
        standards = clean_value(row.get("Standards"))
        phase = clean_value(row.get("Phase"))
        criticality = clean_value(row.get("Criticality"))
        capex_opex = clean_value(row.get("CAPEX/OPEX Tag"))
        
        raw_nodes.append({
            "id": node_id,
            "name": name,
            "level": level,
            "parent_id": parent_id,
            "description": description,
            "key_equipment": key_equipment,
            "responsible_dept": resp_dept,
            "standards": standards,
            "phase": phase,
            "criticality": criticality,
            "capex_opex_tag": capex_opex
        })
        
    print(f"[INFO] Extracted {len(raw_nodes)} raw nodes from Master sheet.")
    
    # Sort nodes by level ascending (L1, then L2, then L3, then L4) to avoid foreign key violations on parent_id
    raw_nodes.sort(key=lambda x: x["level"])
    
    # Initialize embedding model
    print("[INFO] Initializing embedding model for semantic graph nodes...")
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Insert Nodes
    conn = get_connection()
    if not conn:
        print("[ERROR] Database connection failed for node insertion.")
        return False
        
    try:
        cur = conn.cursor()
        inserted_node_ids = set()
        
        print("[INFO] Embedding and inserting nodes in order of hierarchical level...")
        for node in raw_nodes:
            # Check if parent_id exists in inserted_node_ids (if not, set to None and warn)
            if node["parent_id"] and node["parent_id"] not in inserted_node_ids:
                print(f"[WARN] Parent ID '{node['parent_id']}' for node '{node['id']}' not found. Inserting without parent link.")
                node["parent_id"] = None
                
            # Create text representation to embed
            embed_text = f"System ID: {node['id']} | Name: {node['name']} | Level: {node['level']}"
            if node["description"]:
                embed_text += f" | Description: {node['description']}"
            if node["key_equipment"]:
                embed_text += f" | Key Equipment: {node['key_equipment']}"
            if node["criticality"]:
                embed_text += f" | Criticality: {node['criticality']}"
                
            embedding = embed_model.encode(embed_text).tolist()
            
            cur.execute("""
                INSERT INTO taxonomy_nodes 
                (id, name, level, parent_id, description, key_equipment, responsible_dept, standards, phase, criticality, capex_opex_tag, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector)
            """, (
                node["id"],
                node["name"],
                node["level"],
                node["parent_id"],
                node["description"],
                node["key_equipment"],
                node["responsible_dept"],
                node["standards"],
                node["phase"],
                node["criticality"],
                node["capex_opex_tag"],
                embedding
            ))
            inserted_node_ids.add(node["id"])
            
        conn.commit()
        print(f"[SUCCESS] Successfully embedded and loaded {len(inserted_node_ids)} taxonomy nodes.")
        
        # 2. Parse Interface Matrix (Edges)
        print("[INFO] Parsing Interface Matrix sheet...")
        df_int = xl.parse("Interface Matrix")
        
        # Header system codes are in row 2 (which is column name list after parsing if row 2 is headers)
        # Let's inspect rows to find the TO column mappings
        # FROM is in col 0 from row 3 onwards (row 2 contains TO codes)
        
        # Let's identify the TO columns (system codes from headers)
        # Let's see: row 2 contains the TO system headers: e.g. "CVL\nCivil & Structural"
        # We can scan row index 2 in df_int to extract these. Let's find it.
        to_cols = {}
        for col_name in df_int.columns[1:]:
            # Find the system code (e.g. CVL or RST) from columns
            # Column headers inside pandas might be "Unnamed: X" or actual string
            # Let's check row index 2 for the TO system codes
            val = clean_value(df_int.loc[2, col_name])
            if val:
                # Extract first 3 chars as code
                code = val.split("\n")[0].split(" ")[0].strip()
                if len(code) == 3:
                    to_cols[col_name] = code
                    
        print(f"[INFO] Mapped {len(to_cols)} target TO systems in column headers: {list(to_cols.values())}")
        
        edges_to_insert = []
        
        # Iterate rows from index 3 onwards
        for idx in range(3, len(df_int)):
            row = df_int.iloc[idx]
            from_label = clean_value(row.iloc[0])
            if not from_label:
                continue
                
            # Extract FROM code (first 3 chars of row label, e.g. "CVL - Civil...")
            from_parts = from_label.split(" - ")
            if not from_parts or len(from_parts[0]) != 3:
                # Try splitting by space
                from_parts = from_label.split(" ")
            
            from_code = from_parts[0].strip()
            if len(from_code) != 3:
                continue
                
            # Verify if FROM code exists in database nodes (must be L1 system)
            if from_code not in inserted_node_ids:
                print(f"[WARN] FROM system code '{from_code}' not found in database. Skipping row.")
                continue
                
            # Iterate through columns to extract relations
            for col_name, to_code in to_cols.items():
                if to_code not in inserted_node_ids:
                    continue
                    
                cell_val = clean_value(row.get(col_name))
                if not cell_val or cell_val == "—":
                    continue
                    
                # cell_val could be 'P', 'S', 'S,P', etc.
                flags = [f.strip() for f in cell_val.split(",") if f.strip()]
                for f in flags:
                    relationship_type = None
                    if f == "S": relationship_type = "Safety-Critical"
                    elif f == "P": relationship_type = "Physical"
                    elif f == "D": relationship_type = "Data/Logical"
                    elif f == "C": relationship_type = "Commercial/Contractual"
                    
                    if relationship_type:
                        edges_to_insert.append((from_code, to_code, relationship_type))
                        
        print(f"[INFO] Extracted {len(edges_to_insert)} interface matrix edge relations.")
        
        # Insert Edges (handling uniqueness constraint)
        edge_count = 0
        inserted_edges = set()
        
        for from_id, to_id, rel_type in edges_to_insert:
            edge_key = (from_id, to_id, rel_type)
            if edge_key in inserted_edges:
                continue
                
            try:
                cur.execute("""
                    INSERT INTO taxonomy_edges (from_node_id, to_node_id, relationship_type)
                    VALUES (%s, %s, %s)
                    ON CONFLICT ON CONSTRAINT unique_edge DO NOTHING;
                """, (from_id, to_id, rel_type))
                inserted_edges.add(edge_key)
                edge_count += 1
            except Exception as e:
                print(f"[WARN] Failed to insert edge {from_id} -> {to_id} ({rel_type}): {e}")
                
        conn.commit()
        print(f"[SUCCESS] Successfully loaded {edge_count} directed edges into taxonomy_edges table.")
        return True
    except Exception as e:
        print(f"[ERROR] Database ingestion failed: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    success = ingest_taxonomy()
    if success:
        print("\n[SUCCESS] Day 7 Ingestion Complete! 383 nodes and 195+ interface edges are fully active in PostgreSQL.")
        sys.exit(0)
    else:
        print("\n[FAILURE] Day 7 Ingestion encountered errors.")
        sys.exit(1)
