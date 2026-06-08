"""Utility: chunk a sample NCR/DPR text and save output to experiments/results/ingest_sample.

This is a small runnable helper to validate `src.chunkers.ncr_dpr_chunker` without
modifying the stable ingestion pipeline. It writes named JSON files for reviewer proof-of-work.
"""
import os
import json
import time
from src.chunkers import ncr_dpr_chunker as chunker

OUT_DIR = 'experiments/results/ingest_sample'

SAMPLE_TEXT = """
NCR-321
Supplier: ACME Supplies

Root Cause:
The joint assembly failed due to improper torqueing of bolts. Detailed inspection shows uneven preload across the flange.

Corrective Action:
Contractor to rework joint, replace gasket, retorque bolts to specification. Submit verification report within 14 days.

Verification:
QA to perform NDT and visual inspection and sign-off.
"""


def ensure_out():
    os.makedirs(OUT_DIR, exist_ok=True)


def main(sample=None, path_hint='sample_ncr.txt'):
    ensure_out()
    text = sample or SAMPLE_TEXT
    chunks = chunker.detect_and_chunk(path_hint, text)
    ts = time.strftime('%Y%m%d_%H%M%S')
    out_path = os.path.join(OUT_DIR, f'chunks_{ts}.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'path_hint': path_hint, 'num_chunks': len(chunks), 'chunks': chunks}, f, indent=2)
    print(f'[DONE] Wrote {len(chunks)} chunks to {out_path}')


if __name__ == '__main__':
    main()
