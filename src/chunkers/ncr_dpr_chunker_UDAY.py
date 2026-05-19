"""Chunkers for NCR and DPR document types (UDAY)

Add document-type specific heuristics here. Intended to be called by ingestion pipeline.
"""
from typing import List

def chunk_ncr(text: str) -> List[str]:
    """Chunk NCRs: keep header (NCR id, supplier), root cause, corrective action, verification."""
    # TODO: implement real chunking rules using regex / PDF parsing
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    return paragraphs

def chunk_dpr(text: str) -> List[str]:
    """Chunk DPRs: separate metadata, metrics table, commentary, action items."""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    return paragraphs

def detect_and_chunk(path: str, doc_text: str) -> List[str]:
    """Detect doc type by path or content and apply appropriate chunker."""
    if 'ncr' in path.lower():
        return chunk_ncr(doc_text)
    if 'dpr' in path.lower():
        return chunk_dpr(doc_text)
    # fallback: simple paragraph split
    return [p.strip() for p in doc_text.split('\n\n') if p.strip()]
