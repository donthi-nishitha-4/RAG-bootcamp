import os
import json
import fitz  # PyMuPDF
import sys
import re
import gc

# Add project root to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.retriever import init_pgvector, load_documents
from sentence_transformers import SentenceTransformer

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += (page.get_text() or "") + "\n"
        doc.close()
        return text
    except Exception as e:
        print(f"[ERROR] PDF load failed: {e}")
        return ""

def chunk_text(text, strategy="semantic", max_chunk_size=800, overlap=100):
    if not text: return []
    
    if strategy == "simple":
        chunks = []
        for i in range(0, len(text), max_chunk_size - overlap):
            chunks.append(text[i:i + max_chunk_size])
        return chunks
        
    elif strategy == "paragraph":
        return [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
        
    else: # semantic
        heading_pattern = r'\n(?=(?:CHAPTER|CLAUSE|SECTION|PART|\d+\.\d+)\s+)'
        sections = re.split(heading_pattern, text, flags=re.IGNORECASE)
        final_chunks = []
        for section in sections:
            section = section.strip()
            if not section: continue
            paragraphs = [p.strip() for p in section.split('\n\n') if p.strip()]
            current_chunk = ""
            for p in paragraphs:
                if len(p) > max_chunk_size:
                    sentences = re.split(r'(?<=[.!?])\s+', p)
                    for s in sentences:
                        if len(current_chunk) + len(s) > max_chunk_size and current_chunk:
                            final_chunks.append(current_chunk.strip())
                            current_chunk = current_chunk[-overlap:] + " " + s if overlap > 0 and len(current_chunk) >= overlap else s
                        else:
                            current_chunk = current_chunk + " " + s if current_chunk else s
                else:
                    if len(current_chunk) + len(p) > max_chunk_size and current_chunk:
                        final_chunks.append(current_chunk.strip())
                        current_chunk = current_chunk[-overlap:] + "\n\n" + p if overlap > 0 and len(current_chunk) >= overlap else p
                    else:
                        current_chunk = current_chunk + "\n\n" + p if current_chunk else p
            if current_chunk:
                final_chunks.append(current_chunk.strip())
        return [c for c in final_chunks if len(c.strip()) > 10]

def run_ingestion(raw_dir="data/raw", processed_dir="data/processed", tenant_id="default", init_db=True):
    if not os.path.exists(raw_dir): return
    os.makedirs(processed_dir, exist_ok=True)
    pdf_files = sorted([f for f in os.listdir(raw_dir) if f.endswith('.pdf')])
    
    if init_db:
        print("[INFO] Initializing pgvector...")
        init_pgvector()
        
    print("[INFO] Loading embedding model...")
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(raw_dir, pdf_file)
        base_name = os.path.splitext(pdf_file)[0]
        entity_type = "contract"
        contract_standard = "gcc" if "gcc" in base_name.lower() else "unknown"
        
        print(f"\n[INFO] Processing {pdf_file} with strategy: {tenant_id}...")
        raw_text = extract_text_from_pdf(pdf_path)
        if not raw_text: continue
        chunks = chunk_text(raw_text, strategy=tenant_id)
        print(f"[INFO] Generated {len(chunks)} chunks.")
        
        # Batch Embed & Load
        batch_size = 50
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            embeddings = embed_model.encode(batch_chunks, show_progress_bar=False).tolist()
            load_documents(
                documents=batch_chunks, 
                embeddings=embeddings, 
                entity_type=entity_type, 
                tenant_id=f"{tenant_id}_strategy", 
                contract_standard=contract_standard
            )
            gc.collect() # Force GC
            
        print(f"[SUCCESS] Ingested {pdf_file}")
        del raw_text, chunks
        gc.collect()

if __name__ == "__main__":
    run_ingestion()
