import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.retriever import load_documents, retrieve_similar
from src.core.pipeline import embed_model

def run_test():
    print("Testing Long Document Summary Bias...")
    
    # 1. Ingest a document with 10 distinct sections spread out semantically
    sections = [
        "Section 1: Site preparation and mobilization.",
        "Section 2: Foundation work and piling.",
        "Section 3: Structural steel erection.",
        "Section 4: Electrical cabling and OHE setup.",
        "Section 5: Signalling and telecommunication.",
        "Section 6: Interior finishing and architecture.",
        "Section 7: Testing and commissioning.",
        "Section 8: Safety audit and certification.",
        "Section 9: Handover to operations.",
        "Section 10: Maintenance and defects liability."
    ]
    embs = embed_model.encode(sections).tolist()
    load_documents(sections, embs, entity_type="summary_test", tenant_id="summary_test")

    # 2. Ask for a summary of ALL activities
    query = "Summarize the entire scope of work from section 1 to 10."
    q_emb = embed_model.encode([query])[0].tolist()
    
    print(f"\nQuery: {query}")
    results = retrieve_similar(q_emb, tenant_id="summary_test", k=3) # Use small K to emphasize bias
    
    print(f"\n--- RETRIEVED CHUNKS (K=3) ---")
    retrieved_sections = []
    for r in results:
        print(f"Retrieved: {r[1]}")
        retrieved_sections.append(r[1])

    # Check which sections are missing
    found_indices = []
    for i, s in enumerate(sections):
        for r in retrieved_sections:
            if s[:20] in r:
                found_indices.append(i+1)
                break
    
    missing = [i+1 for i in range(10) if i+1 not in found_indices]
    
    print(f"\nResults: Found {len(found_indices)}/10 sections.")
    if missing:
        print(f"!!! SUMMARY BIAS DETECTED !!!")
        print(f"The retriever missed sections: {missing}")
        print("Conclusion: Standard RAG is biased towards chunks that match the 'summary' keywords but ignores the rest of the document.")

if __name__ == "__main__":
    run_test()
