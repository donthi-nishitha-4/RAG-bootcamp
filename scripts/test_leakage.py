import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.retriever import load_documents, retrieve_similar
from src.core.pipeline import embed_model

def run_test():
    print("Testing Tenant Leakage...")
    
    # 1. Ingest a secret document for 'ir_dfcc' tenant
    secret_text = "The IR-DFCC secret project code is PHANTOM-99. This should never be visible to Metro tenant."
    emb = embed_model.encode([secret_text])[0].tolist()
    # Note: load_documents internally appends '_strategy' to tenant_id? 
    # Let's check retriever.py load_documents
    load_documents([secret_text], [emb], entity_type="secret", tenant_id="ir_dfcc")

    # 2. Query as 'default_strategy' (Metro) and check if 'ir_dfcc' data leaks
    query = "What is the secret project code for IR-DFCC?"
    q_emb = embed_model.encode([query])[0].tolist()
    
    # We check both 'default_strategy' and 'contextual_strategy'
    for tenant in ["default_strategy", "contextual_strategy"]:
        print(f"\nChecking tenant: {tenant}")
        results = retrieve_similar(q_emb, tenant_id=tenant)
        
        leak = False
        for r in results:
            if "PHANTOM-99" in r[1]:
                print(f"!!! LEAKAGE DETECTED in {tenant} !!!")
                print(f"Leaked Content: {r[1]}")
                leak = True
        
        if not leak:
            print(f"PASS: No leakage in {tenant}.")

if __name__ == "__main__":
    run_test()
