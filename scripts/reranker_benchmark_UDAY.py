"""Reranker benchmarking harness (UDAY)

Runs multi-trial reranking latency measurements and computes Precision@5.
Saves results under `experiments/results/benchmarks/` as JSON.

Notes:
- Requires models to be available (CrossEncoder rerankers). If models are missing,
  the script will exit with an informative message rather than fabricating numbers.
"""
import os
import sys
import time
import json
import statistics
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.pipeline import embed_model, reranker as reranker_msmarco
from src.core.retriever import retrieve_hybrid
from sentence_transformers import CrossEncoder

OUT_DIR = 'experiments/results/benchmarks'
DEFAULT_QUERIES = 'evaluation/dataset/evaluation_dataset_UDAY_32.json'
TRIALS = 3
TOP_K = 5
RETRIEVE_K = 30


def load_queries(path):
    import json
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def precision_at_k(retrieved_chunks, expected_contexts, k=TOP_K):
    if not expected_contexts:
        return 0.0
    import re
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


def run_benchmark(queries_path=DEFAULT_QUERIES):
    os.makedirs(OUT_DIR, exist_ok=True)
    queries = load_queries(queries_path)

    # Load BGE reranker
    try:
        reranker_bge = CrossEncoder('BAAI/bge-reranker-base')
    except Exception as e:
        print('[ERROR] Could not load BGE reranker:', e)
        return 1

    results = {
        'timestamp': datetime.utcnow().isoformat(),
        'trials': TRIALS,
        'per_query': []
    }

    for qi, item in enumerate(queries[:30], 1):
        q = item.get('query')
        expected_contexts = item.get('contexts', [])
        q_emb = embed_model.encode([q])[0].tolist()

        # retrieve candidates
        candidates = retrieve_hybrid(q, q_emb, k=RETRIEVE_K)
        if not candidates:
            print(f'[WARN] No candidates for query: {q[:50]}')
            continue
        top_docs = [r[1] for r in candidates]
        chunk_ids = [r[0] for r in candidates]

        # Measure ms-marco reranker (from pipeline)
        ms_times = []
        for t in range(TRIALS):
            pairs = [(q, doc) for doc in top_docs]
            start = time.time()
            scores = reranker_msmarco.predict(pairs)
            ms_times.append(time.time() - start)

        # Measure BGE reranker
        bge_times = []
        for t in range(TRIALS):
            pairs = [(q, doc) for doc in top_docs]
            start = time.time()
            scores = reranker_bge.predict(pairs)
            bge_times.append(time.time() - start)

        # Build top-K results for precision computation (using last trial's scores)
        ms_ranked = sorted(zip(scores, top_docs, chunk_ids), reverse=True)
        ms_topk = [(cid, doc, score) for score, doc, cid in ms_ranked[:TOP_K]]

        # Compute precision
        prec = precision_at_k(ms_topk, expected_contexts)

        results['per_query'].append({
            'query': q,
            'num_candidates': len(top_docs),
            'precision_at_5': prec,
            'msmarco_median_latency_s': statistics.median(ms_times) if ms_times else None,
            'bge_median_latency_s': statistics.median(bge_times) if bge_times else None
        })

    out_path = os.path.join(OUT_DIR, f'reranker_benchmark_{int(time.time())}.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print('[DONE] Benchmark saved to', out_path)
    return 0


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--queries', type=str, default=DEFAULT_QUERIES)
    args = p.parse_args()
    sys.exit(run_benchmark(args.queries))
"""Reranker benchmark stub (UDAY)

Measures candidate reranking improvement (Precision@5) and approximate CPU latency.
Fill in the embedding/retrieval/reranker calls per your environment.
"""
import time
from typing import List

def rerank_and_score(candidates: List[str], query: str, reranker_name: str):
    """Placeholder: rerank candidates and compute Precision@5.
    Returns (precision_at_5, cpu_latency_seconds)
    """
    start = time.process_time()
    # TODO: call actual reranker model here
    time.sleep(0.01)
    cpu_latency = time.process_time() - start
    # placeholder precision
    precision_at_5 = 0.6 if 'ms-marco' in reranker_name else 0.62
    return precision_at_5, cpu_latency

def compare_rerankers(candidates, query):
    r1, l1 = rerank_and_score(candidates, query, 'ms-marco-MiniLM-L-12-v2')
    r2, l2 = rerank_and_score(candidates, query, 'bge-reranker-v2-m3')
    print(f"ms-marco: P@5={r1:.3f}, CPU={l1:.4f}s; bge: P@5={r2:.3f}, CPU={l2:.4f}s")

if __name__ == '__main__':
    # Example usage; replace with real retrieval pipeline
    sample_candidates = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5', 'doc6']
    compare_rerankers(sample_candidates, 'What is the notice period for termination?')
