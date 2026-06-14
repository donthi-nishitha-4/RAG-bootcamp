import sys, os
from src.core.retriever import get_connection

conn = get_connection()
if conn:
    cur = conn.cursor()
    cur.execute("SELECT id, content FROM rag_documents LIMIT 5;")
    for row in cur.fetchall():
        print("DB CHUNK:", row[1][:100].replace('\n', ' '))
else:
    print("NO DB CONNECTION")
