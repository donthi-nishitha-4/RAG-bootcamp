import sys
import os
from src.core.database.connection import load_documents, retrieve_similar
from src.core.pipeline import embed_model

def run_test():
    print("Testing Contract Version Confusion...")
    
    # 1. Ingest Red Book clause (28 days time-bar)
    red_text = "FIDIC RED BOOK Clause 20.1: The Contractor shall give notice to the Engineer within 28 days of the event giving rise to the claim."
    red_emb = embed_model.encode([red_text])[0].tolist()
    load_documents([red_text], [red_emb], entity_type="contract_clause", tenant_id="version_test", contract_standard="red")

    # 2. Ingest Yellow Book clause (42 days time-bar - mocked for test)
    yellow_text = "FIDIC YELLOW BOOK Clause 20.1: The Contractor shall give notice to the Engineer within 42 days of the event giving rise to the claim."
    yellow_emb = embed_model.encode([yellow_text])[0].tolist()
    load_documents([yellow_text], [yellow_emb], entity_type="contract_clause", tenant_id="version_test", contract_standard="yellow")

    # 3. Query without metadata filter
    query = "What is the time-bar period for claims under the Yellow Book?"
    q_emb = embed_model.encode([query])[0].tolist()
    
    print(f"\nQuery: {query}")
    print("\n--- RESULTS WITHOUT METADATA FILTERING ---")
    # This might return both or Red Book first depending on similarity
    results = retrieve_similar(q_emb, tenant_id="version_test", k=2)
    for r in results:
        print(f"Retrieved: {r[1]}")

    # 4. Query WITH metadata filter
    print("\n--- RESULTS WITH METADATA FILTERING (contract_standard='yellow') ---")
    results_filtered = retrieve_similar(q_emb, tenant_id="version_test", contract_standard="yellow", k=1)
    for r in results_filtered:
        print(f"Retrieved: {r[1]}")

if __name__ == "__main__":
    run_test()
