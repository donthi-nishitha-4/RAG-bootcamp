import sys
from sentence_transformers import SentenceTransformer, CrossEncoder
from .retriever import retrieve_similar, init_pgvector, retrieve_hybrid
from .llm import query_llm

TOP_K = 20
FINAL_K = 5

# ---- SETUP MODELS ----
try:
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")
    print("[INFO] Embed & Rerank Models loaded successfully.")
except Exception as e:
    print(f"[ERROR] Model load failed: {e}")
    sys.exit(1)

def ask_rag(query, tenant_id="default", entity_type=None, contract_standard=None, search_type="vector"):
    """
    Core RAG pipeline.
    Always returns a dictionary with: query, retrieved_chunks, context, answer, chunk_ids, sources
    """
    # 1. Edge Case: Empty or invalid query
    if not query or not isinstance(query, str) or not query.strip():
        return {
            "query": query,
            "retrieved_chunks": [],
            "context": "",
            "answer": "[ERROR] Invalid or empty query",
            "chunk_ids": [],
            "sources": []
        }
        
    query = query.strip()
    
    try:
        # 2. Embed query or generate retrieval signals depending on search_type
        # Default: embed the query itself
        query_embedding = embed_model.encode([query])[0].tolist()

        # 3. Retrieve
        from .retriever import retrieve_similar, retrieve_hybrid

        if search_type == "hybrid":
            results = retrieve_hybrid(query, query_embedding, tenant_id=tenant_id, k=TOP_K)
        elif search_type == "hyde":
            # HyDE: generate hypothetical document, embed THAT, then retrieve
            prompt = [
                {"role": "system", "content": "You are a helpful assistant that writes a short hypothetical document that would answer the user's question. Keep it focused and factual."},
                {"role": "user", "content": f"Generate a concise hypothetical document that directly answers: {query}"}
            ]
            hyde_doc = query_llm(prompt)
            if not hyde_doc or hyde_doc.startswith("[ERROR]"):
                return {
                    "query": query,
                    "retrieved_chunks": [],
                    "context": "",
                    "answer": "[ERROR] HyDE generation failed",
                    "chunk_ids": [],
                    "sources": []
                }
            hyde_emb = embed_model.encode([hyde_doc])[0].tolist()
            results = retrieve_similar(hyde_emb, tenant_id=tenant_id, entity_type=entity_type, contract_standard=contract_standard, k=TOP_K)
        elif search_type == "multi":
            # Multi-query: generate N paraphrases, retrieve per paraphrase, union results
            # Ask LLM for 3 paraphrases by default
            prompt = [
                {"role": "system", "content": "You are a concise paraphraser. Produce 3 diverse rephrasings of the user's question, each on its own line."},
                {"role": "user", "content": f"Rephrase: {query}"}
            ]
            resp = query_llm(prompt)
            paraphrases = []
            if resp and not resp.startswith("[ERROR]"):
                for line in resp.splitlines():
                    line = line.strip()
                    if line:
                        paraphrases.append(line)
            # Fallback: simple variants if LLM unavailable
            if not paraphrases:
                paraphrases = [query, query + "?", query]

            # Retrieve for each paraphrase and union by id
            combined = {}
            for p in paraphrases:
                emb = embed_model.encode([p])[0].tolist()
                res = retrieve_similar(emb, tenant_id=tenant_id, entity_type=entity_type, contract_standard=contract_standard, k=TOP_K)
                for r in res:
                    combined[r[0]] = (r[1], r[2])

            # Produce a list similar to other retrieve functions: (id, content, score)
            results = [(cid, data[0], data[1]) for cid, data in combined.items()][:TOP_K]
        else:
            results = retrieve_similar(
                query_embedding, 
                tenant_id=tenant_id, 
                entity_type=entity_type, 
                contract_standard=contract_standard, 
                k=TOP_K
            )
        
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

    # 4. Rerank
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
        
    # 5. Build Context
    combined_context = "\n".join(final_docs)
    
    # 6. LLM Call
    messages = [
        {"role": "system", "content": "You are an expert AI assistant. Answer the user's question using ONLY the provided context. If the answer is not in the context, say 'I cannot answer this based on the provided context.'"},
        {"role": "user", "content": f"Context:\n{combined_context}\n\nQuestion: {query}"}
    ]
    
    answer = query_llm(messages)
    
    return {
        "query": query,
        "retrieved_chunks": final_docs,
        "context": combined_context, # Ensure context is correctly set
        "answer": answer, # Never context = answer
        "chunk_ids": final_chunk_ids,
        "sources": [{"chunk_id": cid, "text": doc} for cid, doc in zip(final_chunk_ids, final_docs)]
    }

if __name__ == "__main__":
    print("Testing RAG pipeline...")
    res = ask_rag("What is AI?", tenant_id="default")
    print(res)
