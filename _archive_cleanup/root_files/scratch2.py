import sys, os
from src.core.retriever import get_connection

conn = get_connection()
if conn:
    cur = conn.cursor()
    cur.execute("SELECT tenant_id, COUNT(*) FROM rag_documents GROUP BY tenant_id;")
    print("TENANTS:", cur.fetchall())
