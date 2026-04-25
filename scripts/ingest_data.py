import os
import json
import fitz  # PyMuPDF
import sys
import re

# Add project root to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.retriever import init_pgvector, load_documents
from sentence_transformers import SentenceTransformer

def extract_text_from_pdf(pdf_path):
    """Safely extract text from PDF."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            page_text = page.get_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        print(f"[ERROR] PDF load failed for {pdf_path}: {e}")
        return ""

def chunk_text(text, max_chunk_size=800, overlap=100):
    """
    Robust chunking logic (Phase 4).
    Step 1: Split by common Headings (CHAPTER, CLAUSE, SECTION, numbers).
    Step 2: Paragraph split.
    Step 3: Sentence fallback for long paragraphs.
    Step 4: 100-character overlap.
    Handles: very long paragraphs, empty text, noisy OCR.
    """
    if not text or not text.strip():
        return []
        
    # Step 1: Split by potential headings
    # Pattern looks for lines starting with Chapter, Clause, Section, or numeric patterns like 1.1
    heading_pattern = r'\n(?=(?:CHAPTER|CLAUSE|SECTION|PART|\d+\.\d+)\s+)'
    sections = re.split(heading_pattern, text, flags=re.IGNORECASE)
    
    final_chunks = []
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        # Step 2: Paragraph split within sections
        paragraphs = [p.strip() for p in section.split('\n\n') if p.strip()]
        
        current_chunk = ""
        
        for p in paragraphs:
            # Step 3: Sentence fallback if paragraph is too long
            if len(p) > max_chunk_size:
                sentences = re.split(r'(?<=[.!?])\s+', p)
                for s in sentences:
                    if len(current_chunk) + len(s) > max_chunk_size and current_chunk:
                        final_chunks.append(current_chunk.strip())
                        # Step 4: Overlap
                        current_chunk = current_chunk[-overlap:] + " " + s if overlap > 0 and len(current_chunk) >= overlap else s
                    else:
                        current_chunk = current_chunk + " " + s if current_chunk else s
            else:
                if len(current_chunk) + len(p) > max_chunk_size and current_chunk:
                    final_chunks.append(current_chunk.strip())
                    # Step 4: Overlap
                    current_chunk = current_chunk[-overlap:] + "\n\n" + p if overlap > 0 and len(current_chunk) >= overlap else p
                else:
                    current_chunk = current_chunk + "\n\n" + p if current_chunk else p
                    
        if current_chunk:
            final_chunks.append(current_chunk.strip())
            
    # Final safety cleanup for noisy OCR / empty strings
    return [c for c in final_chunks if len(c.strip()) > 10]

def run_ingestion(raw_dir="data/raw", processed_dir="data/processed", tenant_id="default"):
    """
    End-to-end ingestion pipeline.
    """
    if not os.path.exists(raw_dir):
        print(f"[ERROR] Raw directory not found: {raw_dir}")
        return
        
    os.makedirs(processed_dir, exist_ok=True)
    
    pdf_files = [f for f in os.listdir(raw_dir) if f.endswith('.pdf')]
    if not pdf_files:
        print(f"[WARN] No PDF files found in {raw_dir}")
        return
        
    # Initialize DB and Models
    print("[INFO] Initializing pgvector...")
    if not init_pgvector():
        print("[ERROR] Failed to initialize DB. Aborting.")
        return
        
    print("[INFO] Loading embedding model...")
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(raw_dir, pdf_file)
        base_name = os.path.splitext(pdf_file)[0]
        
        # Derive metadata heuristically or pass explicitly
        # For bootcamp, we assume filename patterns like "GCC-2022.pdf"
        entity_type = "contract"
        contract_standard = "gcc" if "gcc" in base_name.lower() else "unknown"
        
        print(f"\n[INFO] Processing {pdf_file}...")
        
        # 1. Extract
        raw_text = extract_text_from_pdf(pdf_path)
        if not raw_text:
            continue
            
        # 2. Chunk
        chunks = chunk_text(raw_text)
        print(f"[INFO] Generated {len(chunks)} chunks.")
        
        if not chunks:
            continue
            
        # 3. Save JSON
        json_path = os.path.join(processed_dir, f"{base_name}_chunks.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({"metadata": {"tenant_id": tenant_id, "entity_type": entity_type, "contract_standard": contract_standard}, "chunks": chunks}, f, indent=2)
        print(f"[INFO] Saved intermediate chunks to {json_path}")
        
        # 4. Embed
        print("[INFO] Generating embeddings...")
        embeddings = embed_model.encode(chunks).tolist()
        
        # 5. Load to DB
        print("[INFO] Loading into pgvector...")
        success = load_documents(
            documents=chunks, 
            embeddings=embeddings,
            entity_type=entity_type, 
            tenant_id=tenant_id,
            contract_standard=contract_standard
        )
        
        if success:
            print(f"[SUCCESS] Ingested {pdf_file} into pgvector!")
        else:
            print(f"[ERROR] Failed to insert {pdf_file} into DB.")

if __name__ == "__main__":
    run_ingestion()
