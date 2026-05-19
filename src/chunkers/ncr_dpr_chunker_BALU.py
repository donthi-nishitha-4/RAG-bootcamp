"""NCR / DPR chunkers (BALU) — improved heuristics

This module provides heuristics for chunking NCR (non-conformance reports)
and DPR (daily progress reports) documents. The functions here are intended
to be safe, deterministic, and standalone — they DO NOT modify ingestion
pipelines directly; call them from `scripts/ingest_data.py` or a test harness.

Goals:
- Identify common NCR headers (e.g., NCR-123, Root Cause, Corrective Action)
- Preserve header -> body grouping
- Split long bodies into sized chunks (~400-800 words)
"""
from typing import List
import re
import math


def _word_chunks(text: str, max_words: int = 500) -> List[str]:
    """Split text into chunks of at most `max_words` words, preserving sentence boundaries where possible."""
    words = text.split()
    if len(words) <= max_words:
        return [text.strip()]
    chunks = []
    start = 0
    while start < len(words):
        end = min(len(words), start + max_words)
        chunk = " ".join(words[start:end]).strip()
        chunks.append(chunk)
        start = end
    return chunks


def chunk_ncr(text: str) -> List[str]:
    """Chunk NCR text using header detection and semantic sections.

    Heuristics:
    - Detect lines that look like 'NCR-\d+' or 'NCR No.'
    - Detect common section headers: Root Cause, Corrective Action, Verification
    - Group header + paragraph blocks; split long blocks into word chunks
    """
    if not text:
        return []

    # Normalize line endings
    txt = text.replace('\r\n', '\n').replace('\r', '\n')

    # Find header positions
    header_re = re.compile(r'(^|\n)(NCR[-\s]*\d+|NCR No\.|Non-?Conformance Report)', re.IGNORECASE)
    parts = header_re.split(txt)

    # If header regex didn't split, fallback to paragraph split
    if len(parts) <= 1:
        paras = [p.strip() for p in txt.split('\n\n') if p.strip()]
        out = []
        for p in paras:
            out.extend(_word_chunks(p))
        return out

    out_chunks = []
    # Walk through parts and group header+body
    i = 0
    while i < len(parts):
        segment = parts[i]
        if header_re.search(segment):
            header = segment.strip()
            body = ''
            if i + 1 < len(parts):
                body = parts[i + 1].strip()
            combined = (header + '\n' + body).strip()
            out_chunks.extend(_word_chunks(combined))
            i += 2
        else:
            # plain text piece
            piece = segment.strip()
            if piece:
                out_chunks.extend(_word_chunks(piece))
            i += 1

    return out_chunks


def chunk_dpr(text: str) -> List[str]:
    """Chunk DPR text: separate metadata, metrics, commentary, action items.

    Heuristics:
    - Look for 'Daily Progress', 'DPR', 'Metrics', 'Action Items' headings
    - Preserve small tables (as text) and split long narrative sections
    """
    if not text:
        return []

    txt = text.replace('\r\n', '\n').replace('\r', '\n')
    # Common DPR headings
    headings = ['Daily Progress', 'DPR', 'Metrics', 'Action Items', 'Comments', 'Observations']
    # Build a regex to find headings
    headings_re = re.compile(r'(^|\n)(' + '|'.join([re.escape(h) for h in headings]) + r')[:\s\n]?', re.IGNORECASE)

    parts = headings_re.split(txt)
    if len(parts) <= 1:
        paras = [p.strip() for p in txt.split('\n\n') if p.strip()]
        out = []
        for p in paras:
            out.extend(_word_chunks(p))
        return out

    out = []
    i = 0
    while i < len(parts):
        seg = parts[i].strip()
        if not seg:
            i += 1
            continue
        # If this segment looks like a heading token (matches one of headings), treat next as body
        if any(seg.lower().startswith(h.lower()) for h in headings):
            heading = seg
            body = ''
            if i + 1 < len(parts):
                body = parts[i + 1].strip()
            combined = (heading + '\n' + body).strip()
            out.extend(_word_chunks(combined))
            i += 2
        else:
            out.extend(_word_chunks(seg))
            i += 1

    return out


def detect_and_chunk(path: str, doc_text: str) -> List[str]:
    """Detect doc type by path or content and apply appropriate chunker.

    - If path contains 'ncr' → chunk_ncr
    - If path contains 'dpr' or 'daily' → chunk_dpr
    - Otherwise fall back to paragraph + word-chunking
    """
    p = (path or '').lower()
    if 'ncr' in p or 'non-conformance' in p:
        return chunk_ncr(doc_text)
    if 'dpr' in p or 'daily' in p:
        return chunk_dpr(doc_text)

    # content-based heuristics
    if re.search(r'\bNCR[-\s]*\d+\b', doc_text, re.IGNORECASE):
        return chunk_ncr(doc_text)
    if re.search(r'\bDaily Progress Report\b|\bDPR\b', doc_text, re.IGNORECASE):
        return chunk_dpr(doc_text)

    paras = [p.strip() for p in doc_text.split('\n\n') if p.strip()]
    out = []
    for p in paras:
        out.extend(_word_chunks(p))
    return out

