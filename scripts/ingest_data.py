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

def run_ingestion(data_dir="data", tenant_id="default", init_db=True):
    if not os.path.exists(data_dir): 
        print(f"[ERROR] Directory {data_dir} does not exist.")
        return
        
    if init_db:
        print("[INFO] Initializing pgvector...")
        init_pgvector()
        
    print("[INFO] Loading embedding model...")
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Find all PDF and JSON files recursively in data_dir
    data_paths = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.pdf') or file.endswith('.json'):
                data_paths.append(os.path.join(root, file))
                
    data_paths = sorted(data_paths)
    print(f"[INFO] Found {len(data_paths)} files to process.")
    
    for file_path in data_paths:
        file_name = os.path.basename(file_path)
        base_name = os.path.splitext(file_name)[0]
        entity_type = "contract"
        contract_standard = "gcc" if "gcc" in base_name.lower() else "unknown"
        
        print(f"\n[INFO] Processing {file_name} with strategy: {tenant_id}...")
        
        chunks = []
        if file_name.endswith('.pdf'):
            raw_text = extract_text_from_pdf(file_path)
            if raw_text:
                chunks = chunk_text(raw_text, strategy=tenant_id)
        elif file_name.endswith('.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    if isinstance(json_data, list):
                        for item in json_data:
                            if "text" in item and item["text"].strip():
                                # In a real scenario we could also extract 'id', 'source', 'category' into metadata
                                chunks.append(item["text"].strip())
            except Exception as e:
                print(f"[ERROR] JSON load failed for {file_name}: {e}")
                
        if not chunks:
            continue
            
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
            
        print(f"[SUCCESS] Ingested {file_name}")
        del chunks
        gc.collect()

if __name__ == "__main__":
    run_ingestion()
