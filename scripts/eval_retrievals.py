import os
import sys
import json
from statistics import mean
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.pipeline import embed_model, reranker
from src.core.llm import query_llm
from src.core.retriever import retrieve_similar, retrieve_hybrid

TOP_K = 5
RETRIEVE_K = 30

def load_queries(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Queries file not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def precision_at_k(retrieved_chunks, expected_contexts, k=TOP_K):
    if not expected_contexts:
        return 0.0
    expected_text = " ".join(expected_contexts).lower()
    expected_words = set(re.findall(r'\w+', expected_text))
    if not expected_words:
        return 0.0
    count = 0
    for _, content, _ in retrieved_chunks[:k]:
        content_words = set(re.findall(r'\w+', content.lower()))
        overlap = expected_words.intersection(content_words)
        if len(overlap) >= 0.3 * len(expected_words):
            count += 1
    return count / k

def run_evaluation(queries, tenant_id='default_strategy'):
    scores = {
        'naive': [],
        'metadata': [],
        'hybrid': [],
        'hybrid_rerank': [],
        'hyde': [],
        'multi': []
    }

    for item in queries:
        q = item.get('query')
        expected_contexts = item.get('contexts', [])
        entity_type = item.get('entity_type', None)
        print(f"Evaluating: {q}")
        
        q_emb = embed_model.encode([q])[0].tolist()

        # 1. Naive (Vector only, no metadata)
        naive_res = retrieve_similar(q_emb, tenant_id=tenant_id, k=TOP_K)
        scores['naive'].append(precision_at_k(naive_res, expected_contexts))

        # 2. Metadata filtering (Vector + Metadata)
        meta_res = retrieve_similar(q_emb, tenant_id=tenant_id, entity_type=entity_type, k=TOP_K)
        scores['metadata'].append(precision_at_k(meta_res, expected_contexts))

        # 3. Hybrid (BM25 + Vector)
        hybrid_res = retrieve_hybrid(q, q_emb, tenant_id=tenant_id, entity_type=entity_type, k=TOP_K)
        scores['hybrid'].append(precision_at_k(hybrid_res, expected_contexts))

        # 4. Hybrid + Reranker (Retrieve 30, rerank to 5)
        hybrid_30 = retrieve_hybrid(q, q_emb, tenant_id=tenant_id, entity_type=entity_type, k=RETRIEVE_K)
        if hybrid_30:
            top_docs = [r[1] for r in hybrid_30]
            chunk_ids = [r[0] for r in hybrid_30]
            pairs = [(q, doc) for doc in top_docs]
            rerank_scores = reranker.predict(pairs)
            ranked = sorted(zip(rerank_scores, top_docs, chunk_ids), reverse=True)
            hybrid_rerank_res = [(cid, doc, score) for score, doc, cid in ranked[:TOP_K]]
        else:
            hybrid_rerank_res = []
        scores['hybrid_rerank'].append(precision_at_k(hybrid_rerank_res, expected_contexts))

        # 5. HyDE
        prompt = [{"role": "system", "content": "Generate a short hypothetical document that would answer the question concisely."}, {"role": "user", "content": q}]
        hyde_doc = query_llm(prompt)
        if hyde_doc and not hyde_doc.startswith('[ERROR]'):
            hyde_emb = embed_model.encode([hyde_doc])[0].tolist()
            hyde_res = retrieve_similar(hyde_emb, tenant_id=tenant_id, entity_type=entity_type, k=TOP_K)
        else:
            hyde_res = []
        scores['hyde'].append(precision_at_k(hyde_res, expected_contexts))

        # 6. Multi-Query
        paraphrase_prompt = [{"role": "system", "content": "Produce 3 concise paraphrases of the user's question, one per line."}, {"role": "user", "content": q}]
        resp = query_llm(paraphrase_prompt)
        paras = [line.strip() for line in (resp.splitlines() if resp else []) if line.strip()] or [q]
        combined = {}
        for p in paras:
            emb = embed_model.encode([p])[0].tolist()
            res = retrieve_similar(emb, tenant_id=tenant_id, entity_type=entity_type, k=TOP_K)
            for r in res:
                combined[r[0]] = (r[1], r[2])
        multi_res = [(cid, data[0], data[1]) for cid, data in combined.items()][:TOP_K]
        scores['multi'].append(precision_at_k(multi_res, expected_contexts))

    summary = {k: mean(v) if v else 0.0 for k, v in scores.items()}
    return summary


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/eval_retrievals.py <queries.json>")
        sys.exit(1)
    qpath = sys.argv[1]
    queries = load_queries(qpath)
    summary = run_evaluation(queries)

    # Print markdown table
    md = "| Method | Precision@5 | Notes |\n|---|---:|---|\n"
    md += f"| Naive (Vector Only) | {summary['naive']:.2f} | Baseline vector search |\n"
    md += f"| + Metadata Filtering | {summary['metadata']:.2f} | Vector + Entity Type filtering |\n"
    md += f"| Hybrid (BM25 + Vector) | {summary['hybrid']:.2f} | Reciprocal Rank Fusion |\n"
    md += f"| Hybrid + Cross-Encoder | {summary['hybrid_rerank']:.2f} | Retrieve 30 -> Rerank to 5 |\n"
    md += f"| HyDE | {summary['hyde']:.2f} | Hypothetical doc embeddings |\n"
    md += f"| Multi-query | {summary['multi']:.2f} | Union of paraphrase retrievals |\n"

    print('\nEvaluation Summary:\n')
    print(md)

    os.makedirs('Final_Deliverables', exist_ok=True)
    out_path = 'Final_Deliverables/retrieval_comparison.md'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('# Retrieval Comparison\n\n')
        f.write(md)
    print(f"Saved summary to {out_path}")


if __name__ == '__main__':
    main()
