import sys, os
sys.path.append(os.path.abspath('.'))
from src.core.pipeline import embed_model
from src.core.retriever import retrieve_hybrid

q = "What clause governs contractor claims in GCC?"
q_emb = embed_model.encode([q])[0].tolist()
res = retrieve_hybrid(q, q_emb, tenant_id='default', k=2)
print("RETRIEVED:", res)
