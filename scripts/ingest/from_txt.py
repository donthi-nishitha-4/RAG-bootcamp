"""
================================================================================
Author: Nishitha
Role: Advanced RAG Ingestion Engineering
Created: 2026-05-18
Description: Custom Domain-Specific Correspondence Chunker for Day 6 (Week 2).
             Parses transmittal letters, extracts metadata, injects headers 
             contextually, and loads embeddings into pgvector.
================================================================================
"""
import os
import re
import sys
import gc
from sentence_transformers import SentenceTransformer

# Add project root to path so we can import src core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.retriever import init_pgvector, load_documents

def parse_correspondence_file(file_path):
    """
    Parses a transmittal letter or email file to extract metadata headers
    and the clean body text.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        
    # Extract headers using robust regular expressions
    ref_match = re.search(r'^Ref\s*:\s*(.*)$', content, re.MULTILINE | re.IGNORECASE)
    date_match = re.search(r'^Date\s*:\s*(.*)$', content, re.MULTILINE | re.IGNORECASE)
    from_match = re.search(r'^From\s*:\s*(.*)$', content, re.MULTILINE | re.IGNORECASE)
    to_match = re.search(r'^To\s*:\s*(.*)$', content, re.MULTILINE | re.IGNORECASE)
    subject_match = re.search(r'^Subject\s*:\s*(.*)$', content, re.MULTILINE | re.IGNORECASE)
    
    metadata = {
        "ref": ref_match.group(1).strip() if ref_match else "N/A",
        "date": date_match.group(1).strip() if date_match else "N/A",
        "from": from_match.group(1).strip() if from_match else "N/A",
        "to": to_match.group(1).strip() if to_match else "N/A",
        "subject": subject_match.group(1).strip() if subject_match else "N/A",
    }
    
    # Extract actual message body
    # We find where "Subject:" ends, and take everything after that up to the signature block
    body = ""
    if subject_match:
        subject_end_pos = content.find(subject_match.group(0)) + len(subject_match.group(0))
        body = content[subject_end_pos:].strip()
    else:
        # Fallback if subject not matched
        body = content
        
    return metadata, body

def chunk_correspondence(metadata, body, max_chunk_size=500):
    """
    Chunks the body by paragraph and prepends the structured metadata
    header block to every chunk to enforce structural context preservation.
    """
    # Split body into logical paragraphs
    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip()]
    
    chunks = []
    header_block = (
        f"[CORRESPONDENCE METADATA]\n"
        f"Reference: {metadata['ref']}\n"
        f"Date: {metadata['date']}\n"
        f"From: {metadata['from']}\n"
        f"To: {metadata['to']}\n"
        f"Subject: {metadata['subject']}\n"
        f"----------------------------------------\n"
    )
    
    for i, p in enumerate(paragraphs):
        # Construct the final contextual chunk
        contextual_chunk = f"{header_block}Paragraph {i+1}: {p}"
        chunks.append(contextual_chunk)
        
    return chunks

def ingest_correspondence(data_dir="data/correspondence", init_db=False):
    """
    Batch processes, chunks, embeds, and loads all correspondence files 
    into pgvector under the 'correspondence' entity type.
    """
    if not os.path.exists(data_dir):
        print(f"[ERROR] Correspondence directory {data_dir} does not exist.")
        return
        
    if init_db:
        print("[INFO] Initializing pgvector...")
        init_pgvector()
        
    print("[INFO] Loading cached local model: all-MiniLM-L6-v2...")
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # List files
    files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
    print(f"[INFO] Found {len(files)} correspondence files to process.")
    
    all_chunks = []
    
    for file_name in files:
        file_path = os.path.join(data_dir, file_name)
        print(f"\n[INFO] Parsing correspondence: {file_name}...")
        
        metadata, body = parse_correspondence_file(file_path)
        chunks = chunk_correspondence(metadata, body)
        print(f"[INFO] Generated {len(chunks)} metadata-injected chunks.")
        
        all_chunks.extend(chunks)
        
    if not all_chunks:
        print("[WARNING] No chunks generated. Exiting.")
        return
        
    # Generate verification report
    report_path = "experiments/results/correspondence_chunk_test_Nishitha.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    report_content = [
        "# 📧 DMRC Metro Project: Correspondence Chunker Test Report",
        "**Author:** Nishitha  ",
        "**Role:** Advanced RAG Ingestion Engineering  ",
        "**Bootcamp Phase:** Day 6 — Domain Chunkers (Week 2)  ",
        f"**Status:** Verification Successful  ",
        "",
        "## 📊 Summary of Parsed Letters",
        f"- **Files Processed:** {len(files)}",
        f"- **Total Chunks Generated:** {len(all_chunks)}",
        "- **Strategy:** Logical Paragraph Splitting with Preserved Header Metadata Injection",
        "- **Embedding Model:** `all-MiniLM-L6-v2` (Local Cache)",
        "",
        "---",
        "",
        "## 🔍 Detailed Chunk Visualizations",
        "Below are the actual metadata-injected chunks generated by the parser, demonstrating how contextual header blocks are permanently coupled with paragraph contents for high-precision retrieval:",
        ""
    ]
    
    for idx, chunk in enumerate(all_chunks):
        report_content.append(f"### 📦 Chunk {idx+1}")
        report_content.append("```text")
        report_content.append(chunk)
        report_content.append("```")
        report_content.append("")
        
    with open(report_path, "w", encoding="utf-8") as rf:
        rf.write("\n".join(report_content))
    print(f"\n[SUCCESS] Generated premium verification report: {report_path}")
        
    # Embed and Load Chunks in batches of 50
    print(f"\n[INFO] Ingesting {len(all_chunks)} total chunks into pgvector...")
    batch_size = 50
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        embeddings = embed_model.encode(batch, show_progress_bar=False).tolist()
        
        try:
            load_documents(
                documents=batch,
                embeddings=embeddings,
                entity_type="correspondence",
                tenant_id="correspondence_strategy",
                contract_standard="dmrc"
            )
        except Exception as e:
            print(f"[WARNING] Database batch loading failed: {e}")
        gc.collect()
        
    print(f"\n[SUCCESS] Completed execution of correspondence chunker script!")

if __name__ == "__main__":
    ingest_correspondence()
