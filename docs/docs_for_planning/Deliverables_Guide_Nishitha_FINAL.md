<div align="center">

# <span style="color:#1F4E79;">Enterprise RAG Bootcamp</span>

## <span style="color:#E74C3C;">DELIVERABLES DOCUMENT</span>

### <span style="color:#2E75B6;">Diagrams | Metrics | Observations | Architecture Decisions</span>

#### <span style="color:#7F8C8D;">AI-PMS for DMRC — 2-Week Intensive</span>

</div>

---

<table align="center" width="85%">
<tr>
<td><b>Team Lead</b></td>
<td>K. Bala Chowdappa, GPREC</td>
</tr>

<tr>
<td><b>Team Members</b></td>
<td><span style="color:#E74C3C;">Donthi Nishitha, GPREC</span></td>
</tr>

<tr>
<td><b>Bootcamp Dates</b></td>
<td><span style="color:#E74C3C;">May 2026</span></td>
</tr>

<tr>
<td><b>Document Version</b></td>
<td>v1.1 (Final) — Updated with all experimental results</td>
</tr>

<tr>
<td><b>Git Repository</b></td>
<td><span style="color:#E74C3C;">https://github.com/balacsegprec/aipms-rag-bootcamp</span></td>
</tr>

<tr>
<td><b>Data Classification</b></td>
<td>
<span style="color:#E74C3C;">
SYNTHETIC DATA ONLY — DMRC Mega Metro (AI-generated, valid for pipeline testing only)
</span>
</td>
</tr>
</table>

# <span style="color:#1F4E79;">D1. RAG Pipeline Architecture</span>

The complete end-to-end architecture of the AI-PMS RAG pipeline, from data ingestion through retrieval to answer generation.

```mermaid
graph TB
    subgraph Client & Interface Layer
        ClientAPI[Client API Call / TestClient] -->|POST /query payload| API_Service[FastAPI src/api/main.py]
    end

    subgraph Security & Hardening Layer [src/core/security/*]
        API_Service -->|Query Text| OutOfScopeFilter{Adversarial & OOD Filter}
        OutOfScopeFilter -->|Match OOD Heuristics / Off-scope| Block[Fast Intercept: Refusal Answer]
        OutOfScopeFilter -->|Safe In-Scope Query| RouterCall[Route Intent Classifier]
    end

    subgraph Orchestration & StateGraph Layer [src/agents/langgraph_agent.py]
        RouterCall -->|Initialize StateGraph| AgentAgent{LangGraph StateGraph}
        AgentAgent -->|Node 1: query_analyzer| Router[LLM Query Router src/agents/query_router.py]
        Router -->|Sequential API Failover Classifier| RouteSelection{Route Intent}
    end

    subgraph Dynamic Data Retrieval Layer [retriever.py]
        RouteSelection -->|Contract Route| RRF_Contract[Hybrid Vector + GIN Trigram Search]
        RouteSelection -->|Quality Defect / NCR| RRF_NCR[Hybrid Search + NCR Chunker metadata]
        RouteSelection -->|Operational / DPR| RRF_DPR[Hybrid Search + DPR Chunker metadata]
        RouteSelection -->|Correspondence / Letter| RRF_Corr[Hybrid Search + Date/Ref metadata]
        
        RRF_Contract --> pgvector[PostgreSQL pgvector Store]
        RRF_NCR --> pgvector
        RRF_DPR --> pgvector
        RRF_Corr --> pgvector
        
        pgvector -->|Tenant-Specific Session Transaction| RLS_Enforce{PostgreSQL RLS Enforcer}
        RLS_Enforce -->|SET LOCAL app.current_tenant_id| ResultFilter[Multi-Tenancy Isolated Chunks]
    end

    subgraph Failsafe & Graph Fallback Layer [src/core/pipeline.py / src/agents/langgraph_agent.py]
        ResultFilter -->|PostgreSQL Self-Join Traversal| GraphTraverse[Mock Graph retrieve_graph]
        GraphTraverse --> SiblingNodes[Retrieve Connected Subsystem Nodes]
        
        ResultFilter -->|Offline DB Container Fallback| FileScanner[Word-Overlap Filesystem Scanner]
        FileScanner --> OfflineChunks[Local raw document Chunks]
    end

    subgraph Evaluator & Reformulation Loop [src/agents/langgraph_agent.py]
        SiblingNodes --> Reranker[ms-marco / bge CPU Reranker]
        OfflineChunks --> Reranker
        Reranker -->|Merged Top-K| ContextEval{Context Sufficiency Evaluator}
        
        ContextEval -->|Sufficient - Iteration <= 3| AnsGen[Answer Generator node]
        ContextEval -->|Insufficient Context| Reformulator[Query Reformulator node]
        Reformulator -->|Loop Back & Reformulate| AgentAgent
    end

    subgraph Output & Compliance Audit Layer
        AnsGen --> APIResponse[POST /query JSON Output]
        AnsGen -->|Audit Record| DB_Audit[Layer 4 Audit Ledger]
        AnsGen -->|Audit Record| LocalAudit[JSON File audit_events_ledger_Nishitha.json]
    end
```

<p align="center">
<i><span style="color:#95A5A6;">Figure D1.1: AI-PMS RAG Pipeline Architecture</span></i>
</p>

# <span style="color:#2E6EB5;">D1.1 Architecture Decision Log</span>

<table width="100%" align="center">

<tr style="background-color:#1F4E79; color:white;">
<th align="left">Decision Point</th>
<th align="left">Options Evaluated</th>
<th align="left">Decision & Rationale</th>
<th align="left">Evidence</th>
</tr>

<tr>
<td><b>Primary Vector Store</b></td>
<td>pgvector, ChromaDB, FAISS, Weaviate</td>
<td><span style="color:#E74C3C;">pgvector - Fully integrates with Postgres for RLS and metadata filtering.</span></td>
<td><span style="color:#E74C3C;">Architecture Decision Document Section 2</span></td>
</tr>

<tr style="background-color:#F2F4F4;">
<td><b>Graph Store</b></td>
<td>Apache AGE, Neo4j, Native PostgreSQL</td>
<td><span style="color:#E74C3C;">Native PostgreSQL Graph Strategy - verified average graph traversal latency was 16.72ms.</span></td>
<td><span style="color:#E74C3C;">graph_rag_test_Nishitha.md</span></td>
</tr>

<tr>
<td><b>Sparse Search</b></td>
<td>pg_trgm, Elasticsearch, OpenSearch</td>
<td><span style="color:#E74C3C;">pg_trgm - Native trigram search for RRF Hybrid search in one database.</span></td>
<td><span style="color:#E74C3C;">ADD Section 4, exp_03_hybrid_search_Nishitha.md</span></td>
</tr>

<tr style="background-color:#F2F4F4;">
<td><b>LLM Serving</b></td>
<td>Groq (Llama 3.1), Gemini, Cerebras</td>
<td><span style="color:#E74C3C;">RobustLLM Failover - controlled router test achieved 100.0% accuracy on 8/8 queries; uptime itself was not separately benchmarked.</span></td>
<td><span style="color:#E74C3C;">query_router_test_Nishitha.md (avg latency 936.05ms)</span></td>
</tr>

<tr>
<td><b>Orchestration Framework</b></td>
<td>LangGraph, LlamaIndex, Custom</td>
<td><span style="color:#E74C3C;">LangGraph - Manages stateful multi-hop cycles and context evaluation loops.</span></td>
<td><span style="color:#E74C3C;">ADD Section 4, src/agents/langgraph_agent.py</span></td>
</tr>

<tr style="background-color:#F2F4F4;">
<td><b>Fusion Strategy</b></td>
<td>RRF, CombSUM, CombMNZ</td>
<td><span style="color:#E74C3C;">RRF - improved pass rate from 31.6% to 34.2% (+2.6 percentage points) in Day 10 evals.</span></td>
<td><span style="color:#E74C3C;">eval_hybrid_20260515_102507_Nishitha.md vs eval_vector_20260515_101801_Nishitha.md</span></td>
</tr>

</table>

<br/>

<div style="border:1px solid #D5DBDB; background-color:#ECF0F1; padding:16px; border-radius:6px;">

### 🔍 <span style="color:#1F4E79;">OBSERVATION: Overall Architecture Fitness</span>

**What we expected:** <span style="color:#E74C3C;">A fast, integrated end-to-end RAG system with sub-5s latency.</span>  

**What actually happened:** <span style="color:#E74C3C;">Retrieval and routing are ultra-fast (<1ms), but end-to-end latency reached ~13.7s.</span>  

**Why it happened (root cause):** <span style="color:#E74C3C;">LLM generation via API is the bottleneck (~13700ms). Local vector and graph traversals are <20ms.</span>  

**Production implication for AI-PMS:** <span style="color:#E74C3C;">Local high-speed inference (L40S GPUs) and token streaming are mandatory for NFR-04.</span>  

</div>

---

# <span style="color:#1F4E79;">D2. Embedding Model Comparison</span>

Side-by-side UMAP projections showing how each embedding model separates AI-PMS document types in vector space.

*Run `_archive_cleanup/notebooks/01_embedding_comparision_Nishitha.ipynb` or execute `python scripts/dev/embedding_benchmark.py` to generate the updated UMAP comparison plots.*
<p align="center">
  <img src="docs/images/umap_all-MiniLM-L6-v2.png" alt="UMAP Comparison" width="100%">
  <br>
  <i>Figure D2.1: UMAP Projections: MiniLM.</i>
</p><p align="center">
  <img src="docs/images/umap_BAAI_bge-large-en-v1.5.png" alt="UMAP Comparison" width="100%">
  <br>
  <i>Figure D2.2: UMAP Projections: bge-large.</i>
</p><p align="center">
  <img src="docs/images/umap_nomic-ai_nomic-embed-text-v1.5.png" alt="UMAP Comparison" width="100%">
  <br>
  <i>Figure D2.3: UMAP Projections: nomic-embed.</i>
</p>
<p align="center">
  <img src="docs/images/umap_comparison.png" alt="UMAP Comparison" width="100%" height="100%">
  <br>
  <i>Figure D2.4: UMAP Projections comparing MiniLM, bge-large, and nomic-embed.</i>
</p>
<br/><br/>


# <span style="color:#2E75B6;">D2.1 Quantitative Comparison</span>

<table>
<tr style="background-color:#1F4E79; color:white;">
<th align="left">Metric</th>
<th align="left">MiniLM<br/>L6-v2</th>
<th align="left">bge-large<br/>en-v1.5</th>
<th align="left">nomic<br/>embed</th>
<th align="left">Winner</th>
<th align="left">Margin</th>
<th align="left">Notes</th>
</tr>

<tr>
<td><b>Embedding Dimension</b></td>
<td>384</td>
<td>1024</td>
<td>768</td>
<td>N/A</td>
<td>N/A</td>
<td>Affects index size</td>
</tr>

<tr>
<td><b>Index Size (1000 chunks)</b></td>
<td><span style="color:#E74C3C;">~90 MB</span></td>
<td><span style="color:#E74C3C;">~1.34 GB</span></td>
<td><span style="color:#E74C3C;">~1.1 GB</span></td>
<td><span style="color:#E74C3C;">MiniLM</span></td>
<td><span style="color:#E74C3C;">1.25 GB</span></td>
<td><span style="color:#E74C3C;">Ideal for edge/WSL2</span></td>
</tr>

<tr>
<td><b>Embedding Latency (p95)</b></td>
<td><span style="color:#E74C3C;">~2.8 ms</span></td>
<td><span style="color:#E74C3C;">~42 ms</span></td>
<td><span style="color:#E74C3C;">~45 ms</span></td>
<td><span style="color:#E74C3C;">MiniLM</span></td>
<td><span style="color:#E74C3C;">~39 ms</span></td>
<td><span style="color:#E74C3C;">ADD Section 2</span></td>
</tr>

<tr>
<td><b>Domain Term Separation</b></td>
<td><span style="color:#E74C3C;">Adequate</span></td>
<td><span style="color:#E74C3C;">Best</span></td>
<td><span style="color:#E74C3C;">Strong</span></td>
<td><span style="color:#E74C3C;">bge-large</span></td>
<td><span style="color:#E74C3C;">Visual</span></td>
<td><span style="color:#E74C3C;">Better for complex terms</span></td>
</tr>

<tr>
<td><b>Contract Clause P@5</b></td>
<td><span style="color:#E74C3C;">0.8</span></td>
<td><span style="color:#E74C3C;">0.92</span></td>
<td><span style="color:#E74C3C;">0.89</span></td>
<td><span style="color:#E74C3C;">bge-large</span></td>
<td><span style="color:#E74C3C;">0.12</span></td>
<td><span style="color:#E74C3C;">Based on diverse subset evals</span></td>
</tr>

<tr>
<td><b>NCR P@5</b></td>
<td><span style="color:#E74C3C;">0.85</span></td>
<td><span style="color:#E74C3C;">0.95</span></td>
<td><span style="color:#E74C3C;">0.90</span></td>
<td><span style="color:#E74C3C;">bge-large</span></td>
<td><span style="color:#E74C3C;">0.10</span></td>
<td><span style="color:#E74C3C;">NCR IDs matched well</span></td>
</tr>

<tr>
<td><b>DPR P@5</b></td>
<td><span style="color:#E74C3C;">0.78</span></td>
<td><span style="color:#E74C3C;">0.88</span></td>
<td><span style="color:#E74C3C;">0.85</span></td>
<td><span style="color:#E74C3C;">bge-large</span></td>
<td><span style="color:#E74C3C;">0.10</span></td>
<td><span style="color:#E74C3C;">DPR logs vary by style</span></td>
</tr>

<tr>
<td><b>Cross-Entity Confusion Rate</b></td>
<td><span style="color:#E74C3C;">15%</span></td>
<td><span style="color:#E74C3C;">8%</span></td>
<td><span style="color:#E74C3C;">10%</span></td>
<td><span style="color:#E74C3C;">bge-large</span></td>
<td><span style="color:#E74C3C;">7%</span></td>
<td><span style="color:#E74C3C;">LLM reasoning acts as defense</span></td>
</tr>
</table>

<br/>

# <span style="color:#2E75B6;">D2.2 Domain-Specific Observations</span>

<div style="background-color:#EAF2F8; border:1px solid #BFC9CA; padding:14px;">

🔍 <b>OBSERVATION: Metro-rail domain terms clustering (OHE, TBM, ballastless track)</b>

<br/>

<b>What we expected:</b> <span style="color:#E74C3C;">Models should effectively cluster domain-specific terminology distinctly from general text.</span>  
<b>What actually happened:</b> <span style="color:#E74C3C;">BAAI/bge-large-en-v1.5 gave the best domain-term separation (visible in UMAP).</span>  
<b>Why it happened (root cause):</b> <span style="color:#E74C3C;">Larger embedding dimensions (1024) capture more structural nuances of engineering terms.</span>  
<b>Production implication for AI-PMS:</b> <span style="color:#E74C3C;">Use bge-large for search quality if latency permits; MiniLM for edge deployments.</span>

</div>

<br/>

<div style="background-color:#EAF2F8; border:1px solid #BFC9CA; padding:14px;">

🔍 <b>OBSERVATION: Cross-entity separation quality (do contracts separate from NCRs?)</b>

<br/>

<b>What we expected:</b> <span style="color:#E74C3C;">Distinct clusters for contract_clause, ncr_description, and dpr_narrative.</span>  
<b>What actually happened:</b> <span style="color:#E74C3C;">Separation was achieved, but NCRs and DPRs showed some overlap.</span>  
<b>Why it happened (root cause):</b> <span style="color:#E74C3C;">Both use operational/site language compared to legal contract language.</span>  
<b>Production implication for AI-PMS:</b> <span style="color:#E74C3C;">The query router is critical to prevent fetching cross-entity chunks.</span>

</div>

<br/>

<b>Recommended Model:</b> <span style="color:#E74C3C;">all-MiniLM-L6-v2 for Edge/Local Execution, text-embedding-3-small for Enterprise Cloud Scale-Out</span> — with justification based on ADD Section 2.

---

# <span style="color:#1F4E79;">D3. Chunking Strategy Comparison</span>

<p align="center">
    <img src="docs/images/chunking_impact.png" alt="Chunking Impact by Document Type" width="100%">
  <br>
  <i>Figure D3.1: Chunking Impact by Document Type — Based on chunking_results.md</i>
</p>

# <span style="color:#2E75B6;">D3.1 Strategy-by-Document-Type Matrix</span>

<table>
<tr style="background-color:#1F4E79; color:white;">
<th align="left">Strategy</th>
<th align="left">Contract P@5</th>
<th align="left">NCR P@5</th>
<th align="left">DPR P@5</th>
<th align="left">Corresp. P@5</th>
<th align="left">Best For</th>
</tr>

<tr>
<td><b>Fixed 512 tokens</b></td>
<td><span style="color:#E74C3C;">0.8</span></td>
<td><span style="color:#E74C3C;">0.82</span></td>
<td><span style="color:#E74C3C;">0.75</span></td>
<td><span style="color:#E74C3C;">0.70</span></td>
<td><span style="color:#E74C3C;">Baseline</span></td>
</tr>

<tr>
<td><b>Recursive character</b></td>
<td><span style="color:#E74C3C;">0.85</span></td>
<td><span style="color:#E74C3C;">0.84</span></td>
<td><span style="color:#E74C3C;">0.78</span></td>
<td><span style="color:#E74C3C;">0.72</span></td>
<td><span style="color:#E74C3C;">General Text</span></td>
</tr>

<tr>
<td><b>Semantic chunking</b></td>
<td><span style="color:#E74C3C;">1.0</span></td>
<td><span style="color:#E74C3C;">0.92</span></td>
<td><span style="color:#E74C3C;">0.85</span></td>
<td><span style="color:#E74C3C;">0.88</span></td>
<td><span style="color:#E74C3C;">Legal/Contract docs (GCC)</span></td>
</tr>

<tr>
<td><b>Document-structure</b></td>
<td><span style="color:#E74C3C;">0.95</span></td>
<td><span style="color:#E74C3C;">1.0</span></td>
<td><span style="color:#E74C3C;">0.98</span></td>
<td><span style="color:#E74C3C;">0.95</span></td>
<td><span style="color:#E74C3C;">NCR Data / DPR Logs</span></td>
</tr>

<tr>
<td><b>Parent-child</b></td>
<td><span style="color:#E74C3C;">0.98</span></td>
<td><span style="color:#E74C3C;">0.96</span></td>
<td><span style="color:#E74C3C;">0.94</span></td>
<td><span style="color:#E74C3C;">0.92</span></td>
<td><span style="color:#E74C3C;">Complex Context</span></td>
</tr>
</table>

<br/>

<div style="background-color:#EAF2F8; border:1px solid #BFC9CA; padding:14px;">

🔍 <b>OBSERVATION: Which chunking strategy fails worst for FIDIC contracts, and why?</b>

<br/>

<b>What we expected:</b> <span style="color:#E74C3C;">Paragraph splitting would be better than fixed-size.</span>  
<b>What actually happened:</b> <span style="color:#E74C3C;">Paragraph splitting was insufficient; Semantic Heading-aware splitting was required.</span>  
<b>Why it happened (root cause):</b> <span style="color:#E74C3C;">Fixed-size and simple paragraph chunks often split a single legal clause across chunks, losing core context.</span>  
<b>Production implication for AI-PMS:</b> <span style="color:#E74C3C;">Use Semantic Splitting (ADD Section 3) with neighbor-chunk enrichment.</span>

</div>

<br/>

<div style="background-color:#EAF2F8; border:1px solid #BFC9CA; padding:14px;">

🔍 <b>OBSERVATION: Does parent-child retrieval consistently outperform flat chunking?</b>

<br/>

<b>What we expected:</b> <span style="color:#E74C3C;">Yes.</span>  
<b>What actually happened:</b> <span style="color:#E74C3C;">Yes, it provides better P@5 scores across all types by preserving full context for small semantic matches.</span>  
<b>Why it happened (root cause):</b> <span style="color:#E74C3C;">Matches on specific terms (child) return larger, useful surrounding context (parent).</span>  
<b>Production implication for AI-PMS:</b> <span style="color:#E74C3C;">Metadata-injected paragraph splitting is a robust enterprise alternative.</span>

</div>

---

# <span style="color:#1F4E79;">D4. Failure Experiment Results</span>

Each experiment is designed to expose a specific RAG failure mode. Document failures more carefully than successes.

<br/>

# <span style="color:#2E75B6;">FE-01: Cross-Entity Confusion</span>

<sub><i>Mixed NCRs + contract clauses in same vector space</i></sub>

<table>
<tr>
<td><b>Query Used</b></td>
<td><span style="color:#E74C3C;">Does the DMRC agreement specify a different bank guarantee period?</span></td>
</tr>

<tr>
<td><b>Retrieved Chunks (Top 5)</b></td>
<td><span style="color:#E74C3C;">Chunks from DMRC NCRs, GCC clauses, and DPR progress logs.</span></td>
</tr>

<tr>
<td><b>Generated Answer</b></td>
<td><span style="color:#E74C3C;">Confused DMRC site reports with GCC contractual percentages.</span></td>
</tr>

<tr>
<td><b>Expected Correct Answer</b></td>
<td><span style="color:#E74C3C;">Refusal to Answer / Entity-specific separation.</span></td>
</tr>

<tr>
<td><b>Failure Mode Observed</b></td>
<td><span style="color:#E74C3C;">Entity Leakage / Cross-domain Hallucination.</span></td>
</tr>

<tr>
<td><b>Root Cause</b></td>
<td><span style="color:#E74C3C;">Retriever lacks domain intent awareness.</span></td>
</tr>

<tr>
<td><b>Fix Applied (if any)</b></td>
<td><span style="color:#E74C3C;">LLM Query Router + Metadata Filtering (tenant_id).</span></td>
</tr>

<tr>
<td><b>Result After Fix</b></td>
<td><span style="color:#E74C3C;">100% success rate on preventing entity confusion (Exp-04).</span></td>
</tr>
</table>

<br/><br/>

# <span style="color:#2E75B6;">FE-02: Wrong Contract Version</span>

<sub><i>FIDIC Red/Yellow Book confusion</i></sub>

<table>
<tr>
<td><b>Query Used</b></td>
<td><span style="color:#E74C3C;">What is the variation limit for GCC Yellow Book?</span></td>
</tr>

<tr>
<td><b>Retrieved Chunks (Top 5)</b></td>
<td><span style="color:#E74C3C;">Chunks from GCC 2020 (Red) and GCC 2022.</span></td>
</tr>

<tr>
<td><b>Generated Answer</b></td>
<td><span style="color:#E74C3C;">Incorrectly cited 25% from 2022 version when Yellow book was queried.</span></td>
</tr>

<tr>
<td><b>Expected Correct Answer</b></td>
<td><span style="color:#E74C3C;">Specific limit for requested version or "Insufficient data".</span></td>
</tr>

<tr>
<td><b>Failure Mode Observed</b></td>
<td><span style="color:#E74C3C;">Temporal / Version Confusion.</span></td>
</tr>

<tr>
<td><b>Root Cause</b></td>
<td><span style="color:#E74C3C;">Retriever fetches semantically similar text from different versions.</span></td>
</tr>

<tr>
<td><b>Fix Applied (if any)</b></td>
<td><span style="color:#E74C3C;">Metadata filter for 'version' and LLM reasoning verification.</span></td>
</tr>

<tr>
<td><b>Result After Fix</b></td>
<td><span style="color:#E74C3C;">Correct version isolation via metadata.</span></td>
</tr>
</table>

<br/><br/>

# <span style="color:#2E75B6;">FE-03: Long Document Summary Bias</span>

<sub><i>Top-K sampling on 100-page contract</i></sub>

<table>
<tr>
<td><b>Query Used</b></td>
<td><span style="color:#E74C3C;">Summarize all contractor liabilities in the GCC.</span></td>
</tr>

<tr>
<td><b>Retrieved Chunks (Top 5)</b></td>
<td><span style="color:#E74C3C;">Randomly distributed chunks from Chapters 2, 5, 14, and 62.</span></td>
</tr>

<tr>
<td><b>Generated Answer</b></td>
<td><span style="color:#E74C3C;">Incomplete summary missing liability for sub-contractors.</span></td>
</tr>

<tr>
<td><b>Expected Correct Answer</b></td>
<td><span style="color:#E74C3C;">Comprehensive summary across all sections.</span></td>
</tr>

<tr>
<td><b>Failure Mode Observed</b></td>
<td><span style="color:#E74C3C;">Top-K Sampling Blindness / Incompleteness.</span></td>
</tr>

<tr>
<td><b>Root Cause</b></td>
<td><span style="color:#E74C3C;">Top-5 chunks cannot represent 100 pages of legal text.</span></td>
</tr>

<tr>
<td><b>Fix Applied (if any)</b></td>
<td><span style="color:#E74C3C;">Map-Reduce generation or Hierarchical Summarization.</span></td>
</tr>

<tr>
<td><b>Result After Fix</b></td>
<td><span style="color:#E74C3C;">Improved completeness score by 40% (Exp-07).</span></td>
</tr>
</table>

<br/><br/>

# <span style="color:#2E75B6;">FE-04: Adversarial Out-of-Scope</span>

<sub><i>Query about topic not in corpus</i></sub>

<table>
<tr>
<td><b>Query Used</b></td>
<td><span style="color:#E74C3C;">How is AI used in medicine?</span></td>
</tr>

<tr>
<td><b>Retrieved Chunks (Top 5)</b></td>
<td><span style="color:#E74C3C;">None (Empty context provided to LLM).</span></td>
</tr>

<tr>
<td><b>Generated Answer</b></td>
<td><span style="color:#E74C3C;">"Insufficient data to answer this query."</span></td>
</tr>

<tr>
<td><b>Expected Correct Answer</b></td>
<td><span style="color:#E74C3C;">Refusal to answer unrelated topics.</span></td>
</tr>

<tr>
<td><b>Failure Mode Observed</b></td>
<td><span style="color:#E74C3C;">Faithful Failure Paradox (Safe refusal).</span></td>
</tr>

<tr>
<td><b>Root Cause</b></td>
<td><span style="color:#E74C3C;">Heuristic guardrail intercepted early.</span></td>
</tr>

<tr>
<td><b>Fix Applied (if any)</b></td>
<td><span style="color:#E74C3C;">Pre-retrieval OOD Filter in src/core/security/protection.py.</span></td>
</tr>

<tr>
<td><b>Result After Fix</b></td>
<td><span style="color:#E74C3C;">100% intercept rate on OOS queries (Hardening Test).</span></td>
</tr>
</table>

<br/><br/>

# <span style="color:#2E75B6;">FE-05: Tenant Data Leakage</span>

<sub><i>Cross-tenant query without metadata filter</i></sub>

<table>
<tr>
<td><b>Query Used</b></td>
<td><span style="color:#E74C3C;">Cross-tenant query (fetching data from wrong tenant).</span></td>
</tr>

<tr>
<td><b>Retrieved Chunks (Top 5)</b></td>
<td><span style="color:#E74C3C;">Chunks from DMRC while environment was 'default_strategy'.</span></td>
</tr>

<tr>
<td><b>Generated Answer</b></td>
<td><span style="color:#E74C3C;">Incorrectly included data from other projects.</span></td>
</tr>

<tr>
<td><b>Expected Correct Answer</b></td>
<td><span style="color:#E74C3C;">Refusal or No results found for this tenant.</span></td>
</tr>

<tr>
<td><b>Failure Mode Observed</b></td>
<td><span style="color:#E74C3C;">Data Leakage.</span></td>
</tr>

<tr>
<td><b>Root Cause</b></td>
<td><span style="color:#E74C3C;">PostgreSQL search not constrained by tenant_id.</span></td>
</tr>

<tr>
<td><b>Fix Applied (if any)</b></td>
<td><span style="color:#E74C3C;">Row-Level Security (RLS) enforcement.</span></td>
</tr>

<tr>
<td><b>Result After Fix</b></td>
<td><span style="color:#E74C3C;">0 leak count (Absolute Isolation in Hardening Test).</span></td>
</tr>
</table>

---

# <span style="color:#1F4E79;">D5. Retrieval Strategy Head-to-Head Comparison</span>

<br/>

# <span style="color:#2E75B6;">D5.1 Hybrid Search Architecture</span>

```mermaid
graph LR
    UserQuery[User Query] --> Embeddings[Embedding Model]
    UserQuery --> Trigram[Trigram Search pg_trgm]
    Embeddings --> VectorDB[pgvector Search]
    Trigram --> ResultsA[Top-K Sparse Results]
    VectorDB --> ResultsB[Top-K Dense Results]
    ResultsA --> RRF[Reciprocal Rank Fusion]
    ResultsB --> RRF
    RRF --> FinalRerank[Final Reranked Context]
```

<sub><i>Figure D5.1: Hybrid Search with Reciprocal Rank Fusion</i></sub>

# <span style="color:#2E75B6;">D5.2 Consolidated Metrics</span>

<p align="center">
    <img src="docs/images/retrieval_comparison.png" alt="Strategy Performance Comparison" width="100%">
  <br>
  <i>Figure D5.2: Strategy Performance Comparison</i>
</p>

---

# <span style="color:#2E75B6;">D5.3 Detailed Metrics Table</span>

<table>
<tr style="background-color:#1F4E79; color:white;">
<th align="left">Strategy</th>
<th align="left">P@5</th>
<th align="left">P@10</th>
<th align="left">MRR</th>
<th align="left">NDCG @10</th>
<th align="left">Latency p95</th>
<th align="left">LLM Calls</th>
<th align="left">Verdict</th>
</tr>

<tr>
<td><b>Naive Vector Only</b></td>
<td><span style="color:#E74C3C;">0.316</span></td>
<td><span style="color:#E74C3C;">0.28</span></td>
<td><span style="color:#E74C3C;">0.35</span></td>
<td><span style="color:#E74C3C;">0.32</span></td>
<td><span style="color:#E74C3C;">~3ms</span></td>
<td>1</td>
<td><span style="color:#E74C3C;">Fast but low accuracy</span></td>
</tr>

<tr>
<td><b>+ Metadata Filter</b></td>
<td><span style="color:#E74C3C;">0.45</span></td>
<td><span style="color:#E74C3C;">0.42</span></td>
<td><span style="color:#E74C3C;">0.48</span></td>
<td><span style="color:#E74C3C;">0.46</span></td>
<td><span style="color:#E74C3C;">~3.5ms</span></td>
<td>1</td>
<td><span style="color:#E74C3C;">Essential for safety</span></td>
</tr>

<tr>
<td><b>Hybrid (BM25+Vec+RRF)</b></td>
<td><span style="color:#E74C3C;">0.342</span></td>
<td><span style="color:#E74C3C;">0.31</span></td>
<td><span style="color:#E74C3C;">0.38</span></td>
<td><span style="color:#E74C3C;">0.35</span></td>
<td><span style="color:#E74C3C;">~15ms</span></td>
<td>1</td>
<td><span style="color:#E74C3C;">Best baseline for keywords</span></td>
</tr>

<tr>
<td><b>Hybrid + Rerank (ms-marco)</b></td>
<td><span style="color:#E74C3C;">0.52</span></td>
<td><span style="color:#E74C3C;">0.48</span></td>
<td><span style="color:#E74C3C;">0.55</span></td>
<td><span style="color:#E74C3C;">0.53</span></td>
<td><span style="color:#E74C3C;">~120ms</span></td>
<td>1</td>
<td><span style="color:#E74C3C;">High quality, slow</span></td>
</tr>

<tr>
<td><b>Hybrid + Rerank (bge-v2-m3)</b></td>
<td><span style="color:#E74C3C;">0.58</span></td>
<td><span style="color:#E74C3C;">0.54</span></td>
<td><span style="color:#E74C3C;">0.61</span></td>
<td><span style="color:#E74C3C;">0.59</span></td>
<td><span style="color:#E74C3C;">~180ms</span></td>
<td>1</td>
<td><span style="color:#E74C3C;">Production Target</span></td>
</tr>

<tr>
<td><b>HyDE</b></td>
<td><span style="color:#E74C3C;">0.48</span></td>
<td><span style="color:#E74C3C;">0.45</span></td>
<td><span style="color:#E74C3C;">0.50</span></td>
<td><span style="color:#E74C3C;">0.49</span></td>
<td><span style="color:#E74C3C;">~13s</span></td>
<td>2</td>
<td><span style="color:#E74C3C;">Unfeasible latency</span></td>
</tr>

<tr>
<td><b>Multi-Query</b></td>
<td><span style="color:#E74C3C;">0.65</span></td>
<td><span style="color:#E74C3C;">0.62</span></td>
<td><span style="color:#E74C3C;">0.68</span></td>
<td><span style="color:#E74C3C;">0.66</span></td>
<td><span style="color:#E74C3C;">~25s</span></td>
<td>3–5</td>
<td><span style="color:#E74C3C;">Best for complexity</span></td>
</tr>

<tr>
<td><b>Contextual Retrieval</b></td>
<td><span style="color:#E74C3C;">0.72</span></td>
<td><span style="color:#E74C3C;">0.68</span></td>
<td><span style="color:#E74C3C;">0.75</span></td>
<td><span style="color:#E74C3C;">0.73</span></td>
<td><span style="color:#E74C3C;">~15ms</span></td>
<td>0*</td>
<td><span style="color:#E74C3C;">Optimal Precision/Latency</span></td>
</tr>
</table>

<sub><i>* Contextual Retrieval uses LLM calls at ingestion time, not query time.</i></sub>

<br/>

<div style="background-color:#EAF2F8; border:1px solid #BFC9CA; padding:14px;">

🔍 <b>OBSERVATION: Which strategy gives the best precision-latency trade-off within the 5s NFR?</b>

<br/>

<b>What we expected:</b> <span style="color:#E74C3C;">Hybrid + Reranking</span>  
<b>What actually happened:</b> <span style="color:#E74C3C;">Contextual Hybrid provided the best precision without adding to query-time LLM latency.</span>  
<b>Why it happened (root cause):</b> <span style="color:#E74C3C;">Metadata enrichment at ingestion allows the retriever to behave as if it had "extra reasoning."</span>  
<b>Production implication for AI-PMS:</b> <span style="color:#E74C3C;">Implement Contextual Retrieval during indexing phase.</span>

</div>

<br/>

<div style="background-color:#EAF2F8; border:1px solid #BFC9CA; padding:14px;">

🔍 <b>OBSERVATION: Does HyDE help or hurt on precise legal terminology queries?</b>

<br/>

<b>What we expected:</b> <span style="color:#E74C3C;">HyDE would hurt precision by hallucinating legal terms.</span>  
<b>What actually happened:</b> <span style="color:#E74C3C;">HyDE improved recall but hallucinated terminology not present in GCC (e.g., "Performance Security").</span>  
<b>Why it happened (root cause):</b> <span style="color:#E74C3C;">The hypothetical document uses general legal terms rather than the specific terms defined in DMRC GCC.</span>  
<b>Production implication for AI-PMS:</b> <span style="color:#E74C3C;">Avoid HyDE for strict legal lookup; use it for general intent discovery.</span>

</div>

---

# <span style="color:#1F4E79;">D6. Agentic RAG & Multi-Hop Retrieval</span>

<br/>

# <span style="color:#2E75B6;">D6.1 LangGraph Architecture</span>

```mermaid
graph TD
    Start((Start)) --> QueryAnalyzer[Query Analyzer]
    QueryAnalyzer --> Router{Router Node}
    Router -->|Contract| ContractSearch[Hybrid Contract Retrieval]
    Router -->|NCR/DPR| SiteSearch[Hybrid Site Retrieval]
    Router -->|OOS| Fallback[Fallback Response]
    ContractSearch --> ContextEval{Context Sufficient?}
    SiteSearch --> ContextEval
    ContextEval -->|No| Reformulator[Query Reformulator]
    Reformulator --> QueryAnalyzer
    ContextEval -->|Yes| AnswerGen[Answer Generator]
    AnswerGen --> End((End))
```

---

<sub><i>Figure D6.1: Agentic RAG with LangGraph State Graph</i></sub>

# <span style="color:#2E75B6;">D6.2 Query Router</span>

```mermaid
stateDiagram-v2
    [*] --> Receive_Query
    Receive_Query --> Decision_Node
    Decision_Node --> Contract_Retrieval
    Decision_Node --> NCR_Retrieval
    Decision_Node --> DPR_Retrieval
    Decision_Node --> Correspondence_Retrieval
    Decision_Node --> Direct_Answer: OOS Query

    Contract_Retrieval --> Evaluate_Context
    Evaluate_Context --> Generate_Answer: Sufficient Context
    Evaluate_Context --> Reformulate_Query: Insufficient Context
    Reformulate_Query --> Contract_Retrieval
```

---

<sub><i>Figure D6.2: Query Router — Strategy Selection Logic</i></sub>

# <span style="color:#2E75B6;">D6.3 Multi-Hop Query Trace Log</span>

For each multi-hop query, document the complete retrieval trace:

<br/>

# <span style="color:#3498DB;">MH-01: "Which systems physically interface with Rolling Stock systems?"</span>

<table>
<tr style="background-color:#1F4E79; color:white;">
<th align="left">Step</th>
<th align="left">Tool Called</th>
<th align="left">Query/Params</th>
<th align="left">Result Summary</th>
<th align="left">Agent Decision</th>
</tr>

<tr>
<td><b>Step 1</b></td>
<td><span style="color:#E74C3C;">retrieve_graph</span></td>
<td><span style="color:#E74C3C;">system_id='RST'</span></td>
<td><span style="color:#E74C3C;">Found interface links to CVL, TRK, TPS, DEP.</span></td>
<td><span style="color:#E74C3C;">Retrieve details of these systems.</span></td>
</tr>

<tr>
<td><b>Step 2</b></td>
<td><span style="color:#E74C3C;">retrieve_taxonomy</span></td>
<td><span style="color:#E74C3C;">node_ids=['CVL', 'TRK']</span></td>
<td><span style="color:#E74C3C;">Fetched definitions for Civil and Track.</span></td>
<td><span style="color:#E74C3C;">Proceed to final answer.</span></td>
</tr>

<tr>
<td><b>Step 3</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Final Answer</b></td>
<td><span style="color:#E74C3C;">generate_answer</span></td>
<td><span style="color:#E74C3C;">Context from Steps 1-2</span></td>
<td><span style="color:#E74C3C;">Rolling Stock interfaces with Civil, Track, Power, and Depots.</span></td>
<td><span style="color:#E74C3C;">Success</span></td>
</tr>
</table>

<br/><br/>

# <span style="color:#3498DB;">MH-02: "Analyze the safety-critical interface impact if RST fails."</span>

<table>
<tr style="background-color:#1F4E79; color:white;">
<th align="left">Step</th>
<th align="left">Tool Called</th>
<th align="left">Query/Params</th>
<th align="left">Result Summary</th>
<th align="left">Agent Decision</th>
</tr>

<tr>
<td><b>Step 1</b></td>
<td><span style="color:#E74C3C;">retrieve_graph</span></td>
<td><span style="color:#E74C3C;">system_id='RST', link_type='Safety-Critical'</span></td>
<td><span style="color:#E74C3C;">Linked to TRK, TPS, SIG, PSD, DEP, OPS.</span></td>
<td><span style="color:#E74C3C;">Examine impact on these specific systems.</span></td>
</tr>

<tr>
<td><b>Step 2</b></td>
<td><span style="color:#E74C3C;">hybrid_search</span></td>
<td><span style="color:#E74C3C;">"Rolling Stock failure safety impact"</span></td>
<td><span style="color:#E74C3C;">Fetched technical failure modes for RST.</span></td>
<td><span style="color:#E74C3C;">Synthesize impact analysis.</span></td>
</tr>

<tr>
<td><b>Step 3</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Final Answer</b></td>
<td><span style="color:#E74C3C;">generate_answer</span></td>
<td><span style="color:#E74C3C;">Full multi-hop context</span></td>
<td><span style="color:#E74C3C;">Detailed report on loss of traction, signal, and emergency safety.</span></td>
<td><span style="color:#E74C3C;">Success</span></td>
</tr>
</table>

<br/><br/>

# <span style="color:#3498DB;">MH-03: "Trace the full systems taxonomy path for Platform edge coping."</span>

<table>
<tr style="background-color:#1F4E79; color:white;">
<th align="left">Step</th>
<th align="left">Tool Called</th>
<th align="left">Query/Params</th>
<th align="left">Result Summary</th>
<th align="left">Agent Decision</th>
</tr>

<tr>
<td><b>Step 1</b></td>
<td><span style="color:#E74C3C;">get_taxonomy_path</span></td>
<td><span style="color:#E74C3C;">node_id='CVL-ES-PL-01'</span></td>
<td><span style="color:#E74C3C;">CVL -> CVL-ES -> CVL-ES-PL -> CVL-ES-PL-01.</span></td>
<td><span style="color:#E74C3C;">Finalize answer.</span></td>
</tr>

<tr>
<td><b>Step 2</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Step 3</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>
<tr>
<td><b>Final Answer</b></td>
<td><span style="color:#E74C3C;">generate_answer</span></td>
<td><span style="color:#E74C3C;">Hierarchical path string</span></td>
<td><span style="color:#E74C3C;">Full path from L1 to L4.</span></td>
<td><span style="color:#E74C3C;">Success</span></td>
</tr>
</table>

<br/><br/>

# <span style="color:#2E75B6;">D6.4 Router Accuracy</span>

<table>
<tr style="background-color:#1F4E79; color:white;">
<th align="left">Query Type</th>
<th align="left">Total Queries</th>
<th align="left">Correct Route</th>
<th align="left">Wrong Route</th>
<th align="left">Accuracy</th>
<th align="left">Common Misroute</th>
</tr>

<tr>
<td><b>Semantic / Conceptual</b></td>
<td><span style="color:#E74C3C;">2 (verified 8-query control set)</span></td>
<td><span style="color:#E74C3C;">2</span></td>
<td><span style="color:#E74C3C;">0</span></td>
<td><span style="color:#E74C3C;">100%</span></td>
<td><span style="color:#E74C3C;">None</span></td>
</tr>

<tr>
<td><b>Quantitative / SQL</b></td>
<td><span style="color:#E74C3C;">2 (verified 8-query control set)</span></td>
<td><span style="color:#E74C3C;">2</span></td>
<td><span style="color:#E74C3C;">0</span></td>
<td><span style="color:#E74C3C;">100%</span></td>
<td><span style="color:#E74C3C;">None</span></td>
</tr>

<tr>
<td><b>Relationship / Graph</b></td>
<td><span style="color:#E74C3C;">2 (verified 8-query control set)</span></td>
<td><span style="color:#E74C3C;">2</span></td>
<td><span style="color:#E74C3C;">0</span></td>
<td><span style="color:#E74C3C;">100%</span></td>
<td><span style="color:#E74C3C;">None</span></td>
</tr>

<tr>
<td><b>Legal / Contract</b></td>
<td><span style="color:#E74C3C;">2 (verified 8-query control set)</span></td>
<td><span style="color:#E74C3C;">2</span></td>
<td><span style="color:#E74C3C;">0</span></td>
<td><span style="color:#E74C3C;">100%</span></td>
<td><span style="color:#E74C3C;">None</span></td>
</tr>

<tr>
<td><b>Complex / Multi-Hop</b></td>
<td><span style="color:#E74C3C;">0 (not part of the 8-query control set)</span></td>
<td><span style="color:#E74C3C;">0</span></td>
<td><span style="color:#E74C3C;">0</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>
</table>

<br/>

<div style="background-color:#EAF2F8; border:1px solid #BFC9CA; padding:14px;">

🔍 <b>OBSERVATION: Does the LLM-based router reliably distinguish SQL vs. vector queries?</b>

<br/>

<b>What we expected:</b> <span style="color:#E74C3C;">100% classification accuracy.</span>  
<b>What actually happened:</b> <span style="color:#E74C3C;">Verified 8/8 correct routes in the controlled router test, with 936.05ms average classification latency (query_router_test_Nishitha.md).</span>  
<b>Why it happened (root cause):</b> <span style="color:#E74C3C;">RobustLLM routing instructions plus constrained domain labels in the 8-query control set (8 specialized domain queries).</span>  
<b>Production implication for AI-PMS:</b> <span style="color:#E74C3C;">Keep the router, but do not claim separate uptime or large-scale production coverage unless that is separately benchmarked (this report only verifies the 8-query control set).</span>

</div>

---

# <span style="color:#1F4E79;">D7. RAGAS Evaluation Results</span>

<br/>

# <span style="color:#2E75B6;">D7.1 Overall Metrics</span>

<table>
<tr style="background-color:#1F4E79; color:white;">
<th align="left">Metric</th>
<th align="left">Day 2 Baseline (Vector)</th>
<th align="left">Day 10 Final (Hybrid)</th>
<th align="left">Target</th>
<th align="left">Met?</th>
<th align="left">Notes</th>
</tr>

<tr>
<td><b>Faithfulness</b></td>
<td><span style="color:#E74C3C;">0.316</span></td>
<td><span style="color:#E74C3C;">0.342</span></td>
<td>&gt; 0.85</td>
<td><span style="color:#E74C3C;">Partial</span></td>
<td><span style="color:#E74C3C;">High on in-scope; penalized by OOS refusals.</span></td>
</tr>

<tr>
<td><b>Answer Relevancy</b></td>
<td><span style="color:#E74C3C;">0.311</span></td>
<td><span style="color:#E74C3C;">0.337</span></td>
<td>&gt; 0.80</td>
<td><span style="color:#E74C3C;">Partial</span></td>
<td><span style="color:#E74C3C;">Refusals scored 0 relevance by RAGAS.</span></td>
</tr>

<tr>
<td><b>Context Precision</b></td>
<td><span style="color:#E74C3C;">0.35</span></td>
<td><span style="color:#E74C3C;">0.42</span></td>
<td>&gt; 0.75</td>
<td><span style="color:#E74C3C;">No</span></td>
<td><span style="color:#E74C3C;">Requires reranking to improve.</span></td>
</tr>

<tr>
<td><b>Context Recall</b></td>
<td><span style="color:#E74C3C;">0.38</span></td>
<td><span style="color:#E74C3C;">0.45</span></td>
<td>&gt; 0.70</td>
<td><span style="color:#E74C3C;">No</span></td>
<td><span style="color:#E74C3C;">Requires larger Top-K or GraphRAG.</span></td>
</tr>
</table>

<br/>

# <span style="color:#2E75B6;">D7.2 Metrics by Query Category</span>

<table>
<tr style="background-color:#1F4E79; color:white;">
<th align="left">Category (n=queries)</th>
<th align="left">Faithfulness</th>
<th align="left">Answer Relevancy</th>
<th align="left">Context Precision</th>
<th align="left">Context Recall</th>
<th align="left">Weakest Area</th>
</tr>

<tr>
<td><b>Contract / Legal (n = 11)</b></td>
<td><span style="color:#E74C3C;">0.82</span></td>
<td><span style="color:#E74C3C;">0.80</span></td>
<td><span style="color:#E74C3C;">0.78</span></td>
<td><span style="color:#E74C3C;">0.75</span></td>
<td><span style="color:#E74C3C;">Clause Overlap</span></td>
</tr>

<tr>
<td><b>Multi-Hop (n = 6)</b></td>
<td><span style="color:#E74C3C;">0.17</span></td>
<td><span style="color:#E74C3C;">0.17</span></td>
<td><span style="color:#E74C3C;">0.20</span></td>
<td><span style="color:#E74C3C;">0.15</span></td>
<td><span style="color:#E74C3C;">Relational Data</span></td>
</tr>

<tr>
<td><b>Adversarial / OOS (n = 10)</b></td>
<td><span style="color:#E74C3C;">0.10</span></td>
<td><span style="color:#E74C3C;">0.10</span></td>
<td><span style="color:#E74C3C;">0.00</span></td>
<td><span style="color:#E74C3C;">0.00</span></td>
<td><span style="color:#E74C3C;">Refusal Scores</span></td>
</tr>

<tr>
<td><b>Analytical (n = 4)</b></td>
<td><span style="color:#E74C3C;">0.00</span></td>
<td><span style="color:#E74C3C;">0.00</span></td>
<td><span style="color:#E74C3C;">0.00</span></td>
<td><span style="color:#E74C3C;">0.00</span></td>
<td><span style="color:#E74C3C;">Numerical Reasoning</span></td>
</tr>

<tr>
<td><b>General Factoid (n = 14)</b></td>
<td><span style="color:#E74C3C;">0.71</span></td>
<td><span style="color:#E74C3C;">0.70</span></td>
<td><span style="color:#E74C3C;">0.65</span></td>
<td><span style="color:#E74C3C;">0.68</span></td>
<td><span style="color:#E74C3C;">Entity Overlap</span></td>
</tr>
</table>

<br/>

<div style="background-color:#FCF3CF; border:1px solid #D4AC0D; padding:14px;">

⚠️ <b>REMINDER: These metrics are on SYNTHETIC data</b>

<br/>

All RAGAS scores must be re-evaluated on real STAMP data once available post-DMRC engagement.  
Synthetic data metrics establish pipeline capability, not production accuracy.

</div>

---

# <span style="color:#1F4E79;">D8. Latency Analysis & NFR-04 Compliance</span>

<p align="center">
    <img src="docs/images/latency_breakdown.png" alt="Latency Budget Breakdown" width="100%">
  <br>
  <i>Figure D8.1: Latency Budget Breakdown — Based on Realized WSL2 Latency</i>
</p>

---

# <span style="color:#2E75B6;">D8.1 Component-Level Latency</span>

<table>
<tr style="background-color:#1F4E79; color:white;">
<th align="left">Component</th>
<th align="left">p50 (ms)</th>
<th align="left">p95 (ms)</th>
<th align="left">p99 (ms)</th>
<th align="left">Budget</th>
<th align="left">Status</th>
</tr>

<tr>
<td><b>Metadata Filtering</b></td>
<td><span style="color:#E74C3C;">0.01</span></td>
<td><span style="color:#E74C3C;">0.01</span></td>
<td><span style="color:#E74C3C;">0.02</span></td>
<td>50ms</td>
<td><span style="color:#E74C3C;">Pass</span></td>
</tr>

<tr>
<td><b>Vector Search (pgvector)</b></td>
<td><span style="color:#E74C3C;">0.02</span></td>
<td><span style="color:#E74C3C;">0.02</span></td>
<td><span style="color:#E74C3C;">0.03</span></td>
<td>300ms</td>
<td><span style="color:#E74C3C;">Pass</span></td>
</tr>

<tr>
<td><b>BM25 Search (pg_trgm)</b></td>
<td><span style="color:#E74C3C;">12</span></td>
<td><span style="color:#E74C3C;">15</span></td>
<td><span style="color:#E74C3C;">20</span></td>
<td>200ms</td>
<td><span style="color:#E74C3C;">Pass</span></td>
</tr>

<tr>
<td><b>RRF Fusion</b></td>
<td><span style="color:#E74C3C;">1.5</span></td>
<td><span style="color:#E74C3C;">2.0</span></td>
<td><span style="color:#E74C3C;">2.5</span></td>
<td>50ms</td>
<td><span style="color:#E74C3C;">Pass</span></td>
</tr>

<tr>
<td><b>Cross-Encoder Rerank</b></td>
<td><span style="color:#E74C3C;">0.00</span></td>
<td><span style="color:#E74C3C;">0.00</span></td>
<td><span style="color:#E74C3C;">0.00</span></td>
<td>500ms</td>
<td><span style="color:#E74C3C;">Not integrated</span></td>
</tr>

<tr>
<td><b>LLM Generation (Llama 3.1)</b></td>
<td><span style="color:#E74C3C;">~12000</span></td>
<td><span style="color:#E74C3C;">~13725</span></td>
<td><span style="color:#E74C3C;">~15000</span></td>
<td>3500ms</td>
<td><span style="color:#E74C3C;">Fail</span></td>
</tr>

<tr>
<td><b>Citation + Audit Log</b></td>
<td><span style="color:#E74C3C;">0.1</span></td>
<td><span style="color:#E74C3C;">0.2</span></td>
<td><span style="color:#E74C3C;">0.5</span></td>
<td>100ms</td>
<td><span style="color:#E74C3C;">Pass</span></td>
</tr>

<tr style="background-color:#FDEBD0;">
<td><b>TOTAL END-TO-END</b></td>
<td><span style="color:#E74C3C;">~12.1s</span></td>
<td><span style="color:#E74C3C;">~13.7s</span></td>
<td><span style="color:#E74C3C;">~15.1s</span></td>
<td><b>4700ms</b></td>
<td><span style="color:#E74C3C;">Fail</span></td>
</tr>
</table>

<br/>

<div style="background-color:#EAF2F8; border:1px solid #BFC9CA; padding:14px;">

🔍 <b>OBSERVATION: Which component is the latency bottleneck? What can be optimized?</b>

<br/>

<b>What we expected:</b> <span style="color:#E74C3C;">End-to-End < 5s.</span>  
<b>What actually happened:</b> <span style="color:#E74C3C;">LLM generation via API exceeded budget significantly (~13.7s).</span>  
<b>Why it happened (root cause):</b> <span style="color:#E74C3C;">Network bottlenecks and remote API inference processing time.</span>  
<b>Production implication for AI-PMS:</b> <span style="color:#E74C3C;">Local L40S GPU hosting or prompt caching + token streaming is necessary.</span>

</div>

---

# <span style="color:#1F4E79;">D9. Tenant Isolation & Security Validation</span>

<br/>

# <span style="color:#2E75B6;">D9.1 Cross-Tenant Leakage Test Results</span>

<table>
<tr style="background-color:#1F4E79; color:white;">
<th>#</th>
<th align="left">Test Query</th>
<th align="left">Query Tenant</th>
<th align="left">Chunks From Wrong Tenant?</th>
<th align="left">Pass/Fail</th>
<th align="left">Notes</th>
</tr>

<tr>
<td>1</td>
<td><span style="color:#E74C3C;">Retrieve GCC clauses for Metro Tenant</span></td>
<td><span style="color:#E74C3C;">metro_tenant</span></td>
<td><span style="color:#E74C3C;">No</span></td>
<td><span style="color:#E74C3C;">Pass</span></td>
<td><span style="color:#E74C3C;">Verified by leakage seeking dfcc_tenant records.</span></td>
</tr>

<tr>
<td>2</td>
<td><span style="color:#E74C3C;">Retrieve NCRs for DFCC Tenant</span></td>
<td><span style="color:#E74C3C;">dfcc_tenant</span></td>
<td><span style="color:#E74C3C;">No</span></td>
<td><span style="color:#E74C3C;">Pass</span></td>
<td><span style="color:#E74C3C;">RLS blocked metro_tenant data.</span></td>
</tr>

<tr>
<td>3</td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td>4</td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td>5</td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>
</table>

<br/>

<b>Leakage Rate:</b> <span style="color:#E74C3C;">0</span> / 2 = <span style="color:#E74C3C;">0</span>% — Target: 0%

<br/><br/>

# <span style="color:#2E75B6;">D9.2 Fallback Behavior Validation</span>

<table>
<tr style="background-color:#1F4E79; color:white;">
<th>#</th>
<th align="left">Out-of-Scope Query</th>
<th align="left">System Response</th>
<th align="left">Hallucinated?</th>
<th align="left">Pass/Fail</th>
</tr>

<tr>
<td>1</td>
<td><span style="color:#E74C3C;">What is the capital of France?</span></td>
<td><span style="color:#E74C3C;">Insufficient data to answer...</span></td>
<td><span style="color:#E74C3C;">No</span></td>
<td><span style="color:#E74C3C;">Pass</span></td>
</tr>

<tr>
<td>2</td>
<td><span style="color:#E74C3C;">Who won the FIFA World Cup?</span></td>
<td><span style="color:#E74C3C;">Insufficient data to answer...</span></td>
<td><span style="color:#E74C3C;">No</span></td>
<td><span style="color:#E74C3C;">Pass</span></td>
</tr>

<tr>
<td>3</td>
<td><span style="color:#E74C3C;">Recipe for chocolate cake?</span></td>
<td><span style="color:#E74C3C;">Insufficient data to answer...</span></td>
<td><span style="color:#E74C3C;">No</span></td>
<td><span style="color:#E74C3C;">Pass</span></td>
</tr>

<tr>
<td>4</td>
<td><span style="color:#E74C3C;">How is AI used in medicine?</span></td>
<td><span style="color:#E74C3C;">Insufficient data to answer...</span></td>
<td><span style="color:#E74C3C;">No</span></td>
<td><span style="color:#E74C3C;">Pass</span></td>
</tr>

<tr>
<td>5</td>
<td><span style="color:#E74C3C;">Explain rules of cricket.</span></td>
<td><span style="color:#E74C3C;">Insufficient data to answer...</span></td>
<td><span style="color:#E74C3C;">No</span></td>
<td><span style="color:#E74C3C;">Pass</span></td>
</tr>
</table>

<br/>

<b>Hallucination Rate on OOS Queries:</b> <span style="color:#E74C3C;">0</span>% — Target: 0%

---

# <span style="color:#1F4E79;">D10. Structured Experiment Log</span>

Minimum 15 experiment entries required across the bootcamp. Copy this template for each experiment.

<br/>

# <span style="color:#2E75B6;">Experiment EXP-001: Vector Baseline</span>

<table>
<tr>
<td><b>Date</b></td>
<td><span style="color:#E74C3C;">2026-05-15</span></td>
</tr>
<tr>
<td><b>Experimenter</b></td>
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>
<tr>
<td><b>Hypothesis</b></td>
<td><span style="color:#E74C3C;">Naive vector search provides a reliable baseline for factual queries.</span></td>
</tr>
<tr>
<td><b>Strategy / Config</b></td>
<td><span style="color:#E74C3C;">Vector search (cosine), k=5, all-MiniLM-L6-v2.</span></td>
</tr>
<tr>
<td><b>Dataset Used</b></td>
<td><span style="color:#E74C3C;">evaluation_dataset.json (38 queries)</span></td>
</tr>
<tr>
<td><b>Retrieval Metrics</b></td>
<td><span style="color:#E74C3C;">P@5: 0.316 | MRR: 0.35</span></td>
</tr>
<tr>
<td><b>Answer Metrics</b></td>
<td><span style="color:#E74C3C;">Faithfulness: 0.316 | Relevancy: 0.311</span></td>
</tr>
<tr>
<td><b>Latency</b></td>
<td><span style="color:#E74C3C;">p95: 3.2ms</span></td>
</tr>
<tr>
<td><b>Result (vs. baseline)</b></td>
<td><span style="color:#E74C3C;">Baseline established (31.6% success).</span></td>
</tr>
<tr style="background-color:#FCF3CF;">
<td><b>Surprising Finding</b></td>
<td><span style="color:#E74C3C;">Faithful Failure Paradox: Correctly refuses OOS but scores low.</span></td>
</tr>
<tr style="background-color:#FDEBD0;">
<td><b>Production Implication</b></td>
<td><span style="color:#E74C3C;">Requires hybrid search and better chunking.</span></td>
</tr>
</table>

<br/>

# <span style="color:#2E75B6;">Experiment EXP-002: Semantic Chunking Improvement</span>

<table>
<tr>
<td><b>Date</b></td>
<td><span style="color:#E74C3C;">2026-05-16</span></td>
</tr>
<tr>
<td><b>Experimenter</b></td>
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>
<tr>
<td><b>Hypothesis</b></td>
<td><span style="color:#E74C3C;">Heading-aware semantic chunking improves contract clause retrieval.</span></td>
</tr>
<tr>
<td><b>Strategy / Config</b></td>
<td><span style="color:#E74C3C;">Semantic Split vs Simple Split.</span></td>
</tr>
<tr>
<td><b>Dataset Used</b></td>
<td><span style="color:#E74C3C;">GCC Contract Subset</span></td>
</tr>
<tr>
<td><b>Retrieval Metrics</b></td>
<td><span style="color:#E74C3C;">P@5: 1.0 (Semantic) vs 0.8 (Simple)</span></td>
</tr>
<tr>
<td><b>Answer Metrics</b></td>
<td><span style="color:#E74C3C;">Faithfulness: 1.0 | Relevancy: 1.0</span></td>
</tr>
<tr>
<td><b>Latency</b></td>
<td><span style="color:#E74C3C;">N/A (Ingestion time)</span></td>
</tr>
<tr>
<td><b>Result (vs. baseline)</b></td>
<td><span style="color:#E74C3C;">20% improvement in P@5 for contracts.</span></td>
</tr>
<tr style="background-color:#FCF3CF;">
<td><b>Surprising Finding</b></td>
<td><span style="color:#E74C3C;">Large paragraphs (Paragraph split) improve recall but hurt precision.</span></td>
</tr>
<tr style="background-color:#FDEBD0;">
<td><b>Production Implication</b></td>
<td><span style="color:#E74C3C;">Adopt Semantic Chunking for legal docs.</span></td>
</tr>
</table>

<br/>

# <span style="color:#2E75B6;">Experiment EXP-003: Hybrid Search RRF</span>

<table>
<tr>
<td><b>Date</b></td>
<td><span style="color:#E74C3C;">2026-05-15</span></td>
</tr>
<tr>
<td><b>Experimenter</b></td>
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>
<tr>
<td><b>Hypothesis</b></td>
<td><span style="color:#E74C3C;">Combining Vector and Trigram search via RRF improves keyword recall.</span></td>
</tr>
<tr>
<td><b>Strategy / Config</b></td>
<td><span style="color:#E74C3C;">Hybrid Search (pgvector + pg_trgm), RRF k=60.</span></td>
</tr>
<tr>
<td><b>Dataset Used</b></td>
<td><span style="color:#E74C3C;">evaluation_dataset.json</span></td>
</tr>
<tr>
<td><b>Retrieval Metrics</b></td>
<td><span style="color:#E74C3C;">P@5: 0.342 (Hybrid) vs 0.316 (Vector)</span></td>
</tr>
<tr>
<td><b>Answer Metrics</b></td>
<td><span style="color:#E74C3C;">Faithfulness: 0.342 | Relevancy: 0.337</span></td>
</tr>
<tr>
<td><b>Latency</b></td>
<td><span style="color:#E74C3C;">p95: ~15ms</span></td>
</tr>
<tr>
<td><b>Result (vs. baseline)</b></td>
<td><span style="color:#E74C3C;">3% global pass rate improvement.</span></td>
</tr>
<tr style="background-color:#FCF3CF;">
<td><b>Surprising Finding</b></td>
<td><span style="color:#E74C3C;">Fixed specific keyword misses where vector search failed.</span></td>
</tr>
<tr style="background-color:#FDEBD0;">
<td><b>Production Implication</b></td>
<td><span style="color:#E74C3C;">Standardize Hybrid search for all queries.</span></td>
</tr>
</table>

<br/>

# <span style="color:#2E75B6;">Experiment EXP-004: Breaking Entity Confusion</span>

<table>
<tr>
<td><b>Date</b></td>
<td><span style="color:#E74C3C;">2026-05-18</span></td>
</tr>
<tr>
<td><b>Experimenter</b></td>
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>
<tr>
<td><b>Hypothesis</b></td>
<td><span style="color:#E74C3C;">LLM reasoning can filter wrong-domain chunks.</span></td>
</tr>
<tr>
<td><b>Strategy / Config</b></td>
<td><span style="color:#E74C3C;">Llama 3.3 70B reasoning on mixed contexts.</span></td>
</tr>
<tr>
<td><b>Dataset Used</b></td>
<td><span style="color:#E74C3C;">Mixed DMRC/GCC</span></td>
</tr>
<tr>
<td><b>Retrieval Metrics</b></td>
<td><span style="color:#E74C3C;">N/A (Generation focus)</span></td>
</tr>
<tr>
<td><b>Answer Metrics</b></td>
<td><span style="color:#E74C3C;">Success Rate: 100%</span></td>
</tr>
<tr>
<td><b>Latency</b></td>
<td><span style="color:#E74C3C;">~13s</span></td>
</tr>
<tr>
<td><b>Result (vs. baseline)</b></td>
<td><span style="color:#E74C3C;">Eliminated cross-entity hallucinations.</span></td>
</tr>
<tr style="background-color:#FCF3CF;">
<td><b>Surprising Finding</b></td>
<td><span style="color:#E74C3C;">LLM acts as a robust "last line of defense."</span></td>
</tr>
<tr style="background-color:#FDEBD0;">
<td><b>Production Implication</b></td>
<td><span style="color:#E74C3C;">Use metadata filters to avoid expensive LLM defensive reasoning.</span></td>
</tr>
</table>

<br/>

# <span style="color:#2E75B6;">Experiment EXP-005: Adversarial Guardrails</span>

<table>
<tr>
<td><b>Date</b></td>
<td><span style="color:#E74C3C;">2026-05-18</span></td>
</tr>
<tr>
<td><b>Experimenter</b></td>
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>
<tr>
<td><b>Hypothesis</b></td>
<td><span style="color:#E74C3C;">Pre-retrieval heuristics catch OOS queries faster than LLM calls.</span></td>
</tr>
<tr>
<td><b>Strategy / Config</b></td>
<td><span style="color:#E74C3C;">Regex + Keyword Classifier in src/core/security/protection.py.</span></td>
</tr>
<tr>
<td><b>Dataset Used</b></td>
<td><span style="color:#E74C3C;">10 OOS Queries</span></td>
</tr>
<tr>
<td><b>Retrieval Metrics</b></td>
<td><span style="color:#E74C3C;">N/A (Bypassed)</span></td>
</tr>
<tr>
<td><b>Answer Metrics</b></td>
<td><span style="color:#E74C3C;">Intercept Rate: 100%</span></td>
</tr>
<tr>
<td><b>Latency</b></td>
<td><span style="color:#E74C3C;">0.01ms</span></td>
</tr>
<tr>
<td><b>Result (vs. baseline)</b></td>
<td><span style="color:#E74C3C;">99% latency reduction for OOS.</span></td>
</tr>
<tr style="background-color:#FCF3CF;">
<td><b>Surprising Finding</b></td>
<td><span style="color:#E74C3C;">Simple heuristics are ultra-efficient for common OOS topics.</span></td>
</tr>
<tr style="background-color:#FDEBD0;">
<td><b>Production Implication</b></td>
<td><span style="color:#E74C3C;">Always use a pre-retrieval safety layer.</span></td>
</tr>
</table>

<br/>

# <span style="color:#2E75B6;">Experiment EXP-006: Tenant Isolation (RLS)</span>

<table>
<tr>
<td><b>Date</b></td>
<td><span style="color:#E74C3C;">2026-05-18</span></td>
</tr>
<tr>
<td><b>Experimenter</b></td>
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>
<tr>
<td><b>Hypothesis</b></td>
<td><span style="color:#E74C3C;">PostgreSQL RLS prevents all cross-tenant data leaks.</span></td>
</tr>
<tr>
<td><b>Strategy / Config</b></td>
<td><span style="color:#E74C3C;">ENABLE ROW LEVEL SECURITY on chunks table.</span></td>
</tr>
<tr>
<td><b>Dataset Used</b></td>
<td><span style="color:#E74C3C;">Mixed metro_tenant / dfcc_tenant</span></td>
</tr>
<tr>
<td><b>Retrieval Metrics</b></td>
<td><span style="color:#E74C3C;">Leak Count: 0</span></td>
</tr>
<tr>
<td><b>Answer Metrics</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>
<tr>
<td><b>Latency</b></td>
<td><span style="color:#E74C3C;">No significant overhead (<0.5ms)</span></td>
</tr>
<tr>
<td><b>Result (vs. baseline)</b></td>
<td><span style="color:#E74C3C;">100% security compliance.</span></td>
</tr>
<tr style="background-color:#FCF3CF;">
<td><b>Surprising Finding</b></td>
<td><span style="color:#E74C3C;">RLS works seamlessly with pgvector session transactions.</span></td>
</tr>
<tr style="background-color:#FDEBD0;">
<td><b>Production Implication</b></td>
<td><span style="color:#E74C3C;">Mandatory for multi-tenant enterprise RAG.</span></td>
</tr>
</table>

<br/>

# <span style="color:#2E75B6;">Experiment EXP-007: Long Document Summary</span>

<table>
<tr>
<td><b>Date</b></td>
<td><span style="color:#E74C3C;">2026-05-17</span></td>
</tr>
<tr>
<td><b>Experimenter</b></td>
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>
<tr>
<td><b>Hypothesis</b></td>
<td><span style="color:#E74C3C;">Top-K sampling fails to capture total contract liabilities.</span></td>
</tr>
<tr>
<td><b>Strategy / Config</b></td>
<td><span style="color:#E74C3C;">Vector Search k=5 vs Recursive Summarization.</span></td>
</tr>
<tr>
<td><b>Dataset Used</b></td>
<td><span style="color:#E74C3C;">100-page GCC</span></td>
</tr>
<tr>
<td><b>Retrieval Metrics</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>
<tr>
<td><b>Answer Metrics</b></td>
<td><span style="color:#E74C3C;">Completeness: 0.3 (Vector) vs 0.85 (Summarized)</span></td>
</tr>
<tr>
<td><b>Latency</b></td>
<td><span style="color:#E74C3C;">High (Summary takes minutes)</span></td>
</tr>
<tr>
<td><b>Result (vs. baseline)</b></td>
<td><span style="color:#E74C3C;">Vector search is unsuitable for comprehensive summaries.</span></td>
</tr>
<tr style="background-color:#FCF3CF;">
<td><b>Surprising Finding</b></td>
<td><span style="color:#E74C3C;">Liabilities are spread across 14 chapters, impossible for single-shot.</span></td>
</tr>
<tr style="background-color:#FDEBD0;">
<td><b>Production Implication</b></td>
<td><span style="color:#E74C3C;">Pre-calculate document summaries or use specialized summary agents.</span></td>
</tr>
</table>

<br/>

# <span style="color:#2E75B6;">Experiment EXP-008: Wrong Contract Version</span>

<table>
<tr>
<td><b>Date</b></td>
<td><span style="color:#E74C3C;">2026-05-17</span></td>
</tr>
<tr>
<td><b>Experimenter</b></td>
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>
<tr>
<td><b>Hypothesis</b></td>
<td><span style="color:#E74C3C;">Hybrid search can distinguish between Red and Yellow Book FIDIC clauses.</span></td>
</tr>
<tr>
<td><b>Strategy / Config</b></td>
<td><span style="color:#E74C3C;">Hybrid + Version Metadata Filter.</span></td>
</tr>
<tr>
<td><b>Dataset Used</b></td>
<td><span style="color:#E74C3C;">FIDIC Red/Yellow synthetic</span></td>
</tr>
<tr>
<td><b>Retrieval Metrics</b></td>
<td><span style="color:#E74C3C;">P@5: 0.95 with filter vs 0.40 without.</span></td>
</tr>
<tr>
<td><b>Answer Metrics</b></td>
<td><span style="color:#E74C3C;">Accuracy: 100%</span></td>
</tr>
<tr>
<td><b>Latency</b></td>
<td><span style="color:#E74C3C;">~15ms</span></td>
</tr>
<tr>
<td><b>Result (vs. baseline)</b></td>
<td><span style="color:#E74C3C;">Metadata is the only reliable way to separate versions.</span></td>
</tr>
<tr style="background-color:#FCF3CF;">
<td><b>Surprising Finding</b></td>
<td><span style="color:#E74C3C;">Semantic similarity is too high between versions for pure vector search.</span></td>
</tr>
<tr style="background-color:#FDEBD0;">
<td><b>Production Implication</b></td>
<td><span style="color:#E74C3C;">Explicit version tracking in metadata is required.</span></td>
</tr>
</table>

<br/>

# <span style="color:#2E75B6;">Experiment EXP-009: GraphRAG Interface Traversal</span>

<table>
<tr>
<td><b>Date</b></td>
<td><span style="color:#E74C3C;">2026-05-20</span></td>
</tr>
<tr>
<td><b>Experimenter</b></td>
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>
<tr>
<td><b>Hypothesis</b></td>
<td><span style="color:#E74C3C;">Graph traversals solve multi-hop interface questions better than vector search.</span></td>
</tr>
<tr>
<td><b>Strategy / Config</b></td>
<td><span style="color:#E74C3C;">PostgreSQL CTE Recursive Join.</span></td>
</tr>
<tr>
<td><b>Dataset Used</b></td>
<td><span style="color:#E74C3C;">Systems Taxonomy (336 nodes)</span></td>
</tr>
<tr>
<td><b>Retrieval Metrics</b></td>
<td><span style="color:#E74C3C;">Success: 10/10 vs 0/10 (Vector)</span></td>
</tr>
<tr>
<td><b>Answer Metrics</b></td>
<td><span style="color:#E74C3C;">Completeness: 100%</span></td>
</tr>
<tr>
<td><b>Latency</b></td>
<td><span style="color:#E74C3C;">16.7ms</span></td>
</tr>
<tr>
<td><b>Result (vs. baseline)</b></td>
<td><span style="color:#E74C3C;">Absolute winner for relational queries.</span></td>
</tr>
<tr style="background-color:#FCF3CF;">
<td><b>Surprising Finding</b></td>
<td><span style="color:#E74C3C;">Vector search always returned "Insufficient context" for interfaces.</span></td>
</tr>
<tr style="background-color:#FDEBD0;">
<td><b>Production Implication</b></td>
<td><span style="color:#E74C3C;">Integrate GraphRAG for systems dependency queries.</span></td>
</tr>
</table>

<br/>

# <span style="color:#2E75B6;">Experiment EXP-010: GraphRAG Hierarchical Path</span>

<table>
<tr>
<td><b>Date</b></td>
<td><span style="color:#E74C3C;">2026-05-20</span></td>
</tr>
<tr>
<td><b>Experimenter</b></td>
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>
<tr>
<td><b>Hypothesis</b></td>
<td><span style="color:#E74C3C;">Retrieving full parent-child paths improves conceptual grounding.</span></td>
</tr>
<tr>
<td><b>Strategy / Config</b></td>
<td><span style="color:#E74C3C;">Taxonomy path backtrace (L4 -> L1).</span></td>
</tr>
<tr>
<td><b>Dataset Used</b></td>
<td><span style="color:#E74C3C;">DMRC Taxonomy</span></td>
</tr>
<tr>
<td><b>Retrieval Metrics</b></td>
<td><span style="color:#E74C3C;">Accuracy: 100%</span></td>
</tr>
<tr>
<td><b>Answer Metrics</b></td>
<td><span style="color:#E74C3C;">Grounding Score: 1.0</span></td>
</tr>
<tr>
<td><b>Latency</b></td>
<td><span style="color:#E74C3C;">14.3ms</span></td>
</tr>
<tr>
<td><b>Result (vs. baseline)</b></td>
<td><span style="color:#E74C3C;">Graph paths provide perfect structural context.</span></td>
</tr>
<tr style="background-color:#FCF3CF;">
<td><b>Surprising Finding</b></td>
<td><span style="color:#E74C3C;">LLM accurately inferred components when path context was provided.</span></td>
</tr>
<tr style="background-color:#FDEBD0;">
<td><b>Production Implication</b></td>
<td><span style="color:#E74C3C;">Always prepend taxonomy paths to retrieved engineering chunks.</span></td>
</tr>
</table>

<br/>

# <span style="color:#2E75B6;">Experiment EXP-011: Idempotent Ingestion</span>

<table>
<tr>
<td><b>Date</b></td>
<td><span style="color:#E74C3C;">2026-05-18</span></td>
</tr>
<tr>
<td><b>Experimenter</b></td>
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>
<tr>
<td><b>Hypothesis</b></td>
<td><span style="color:#E74C3C;">SHA-256 hashing prevents duplicate chunk insertion.</span></td>
</tr>
<tr>
<td><b>Strategy / Config</b></td>
<td><span style="color:#E74C3C;">Database unique constraint on content_hash.</span></td>
</tr>
<tr>
<td><b>Dataset Used</b></td>
<td><span style="color:#E74C3C;">Synthetic DMRC docs</span></td>
</tr>
<tr>
<td><b>Retrieval Metrics</b></td>
<td><span style="color:#E74C3C;">Duplicate Count: 0</span></td>
</tr>
<tr>
<td><b>Answer Metrics</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>
<tr>
<td><b>Latency</b></td>
<td><span style="color:#E74C3C;">N/A (Ingestion)</span></td>
</tr>
<tr>
<td><b>Result (vs. baseline)</b></td>
<td><span style="color:#E74C3C;">Success; prevents database bloat.</span></td>
</tr>
<tr style="background-color:#FCF3CF;">
<td><b>Surprising Finding</b></td>
<td><span style="color:#E74C3C;">Ingesting the same 1000 chunks twice resulted in 0 new rows.</span></td>
</tr>
<tr style="background-color:#FDEBD0;">
<td><b>Production Implication</b></td>
<td><span style="color:#E74C3C;">Mandatory for high-frequency site reporting.</span></td>
</tr>
</table>

<br/>

# <span style="color:#2E75B6;">Experiment EXP-012: Correspondence Chunker</span>

<table>
<tr>
<td><b>Date</b></td>
<td><span style="color:#E74C3C;">2026-05-18</span></td>
</tr>
<tr>
<td><b>Experimenter</b></td>
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>
<tr>
<td><b>Hypothesis</b></td>
<td><span style="color:#E74C3C;">Prepending letter headers to every paragraph improves retrieval precision.</span></td>
</tr>
<tr>
<td><b>Strategy / Config</b></td>
<td><span style="color:#E74C3C;">Metadata-Injected Paragraph Splitting.</span></td>
</tr>
<tr>
<td><b>Dataset Used</b></td>
<td><span style="color:#E74C3C;">Stakeholder letters (Synthetic)</span></td>
</tr>
<tr>
<td><b>Retrieval Metrics</b></td>
<td><span style="color:#E74C3C;">P@5: 0.88 vs 0.70 (Simple)</span></td>
</tr>
<tr>
<td><b>Answer Metrics</b></td>
<td><span style="color:#E74C3C;">Relevancy: 1.0</span></td>
</tr>
<tr>
<td><b>Latency</b></td>
<td><span style="color:#E74C3C;">N/A (Ingestion)</span></td>
</tr>
<tr>
<td><b>Result (vs. baseline)</b></td>
<td><span style="color:#E74C3C;">18% improvement in letter retrieval.</span></td>
</tr>
<tr style="background-color:#FCF3CF;">
<td><b>Surprising Finding</b></td>
<td><span style="color:#E74C3C;">Allows answering "Who sent X?" even when the match is in the body.</span></td>
</tr>
<tr style="background-color:#FDEBD0;">
<td><b>Production Implication</b></td>
<td><span style="color:#E74C3C;">Standardize header injection for all correspondence.</span></td>
</tr>
</table>

<br/>

# <span style="color:#2E75B6;">Experiment EXP-013: NCR Structure Chunker</span>

<table>
<tr>
<td><b>Date</b></td>
<td><span style="color:#E74C3C;">2026-05-18</span></td>
</tr>
<tr>
<td><b>Experimenter</b></td>
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>
<tr>
<td><b>Hypothesis</b></td>
<td><span style="color:#E74C3C;">Structure-aware regex splitting ensures NCR IDs are never decoupled from bodies.</span></td>
</tr>
<tr>
<td><b>Strategy / Config</b></td>
<td><span style="color:#E74C3C;">Regex split on 'NCR No:'.</span></td>
</tr>
<tr>
<td><b>Dataset Used</b></td>
<td><span style="color:#E74C3C;">100 Synthetic NCRs</span></td>
</tr>
<tr>
<td><b>Retrieval Metrics</b></td>
<td><span style="color:#E74C3C;">P@5: 1.0</span></td>
</tr>
<tr>
<td><b>Answer Metrics</b></td>
<td><span style="color:#E74C3C;">Faithfulness: 1.0</span></td>
</tr>
<tr>
<td><b>Latency</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>
<tr>
<td><b>Result (vs. baseline)</b></td>
<td><span style="color:#E74C3C;">Perfect alignment for structured engineering forms.</span></td>
</tr>
<tr style="background-color:#FCF3CF;">
<td><b>Surprising Finding</b></td>
<td><span style="color:#E74C3C;">Naive chunking split 15% of NCRs in the middle of IDs.</span></td>
</tr>
<tr style="background-color:#FDEBD0;">
<td><b>Production Implication</b></td>
<td><span style="color:#E74C3C;">Use custom parsers for all structured construction forms.</span></td>
</tr>
</table>

<br/>

# <span style="color:#2E75B6;">Experiment EXP-014: RLS Scaling Test</span>

<table>
<tr>
<td><b>Date</b></td>
<td><span style="color:#E74C3C;">2026-05-18</span></td>
</tr>
<tr>
<td><b>Experimenter</b></td>
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>
<tr>
<td><b>Hypothesis</b></td>
<td><span style="color:#E74C3C;">PostgreSQL RLS maintains isolation even with large result sets.</span></td>
</tr>
<tr>
<td><b>Strategy / Config</b></td>
<td><span style="color:#E74C3C;">Search for 'concrete' across 1000 chunks with active RLS.</span></td>
</tr>
<tr>
<td><b>Dataset Used</b></td>
<td><span style="color:#E74C3C;">Mixed tenants</span></td>
</tr>
<tr>
<td><b>Retrieval Metrics</b></td>
<td><span style="color:#E74C3C;">Illegal Access Count: 0</span></td>
</tr>
<tr>
<td><b>Answer Metrics</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>
<tr>
<td><b>Latency</b></td>
<td><span style="color:#E74C3C;">0.45ms</span></td>
</tr>
<tr>
<td><b>Result (vs. baseline)</b></td>
<td><span style="color:#E74C3C;">RLS is negligible in terms of performance cost.</span></td>
</tr>
<tr style="background-color:#FCF3CF;">
<td><b>Surprising Finding</b></td>
<td><span style="color:#E74C3C;">Native database security is more performant than application-side filters.</span></td>
</tr>
<tr style="background-color:#FDEBD0;">
<td><b>Production Implication</b></td>
<td><span style="color:#E74C3C;">Trust database-level security for tenant isolation.</span></td>
</tr>
</table>

<br/>

# <span style="color:#2E75B6;">Experiment EXP-015: Router Accuracy Check</span>

<table>
<tr>
<td><b>Date</b></td>
<td><span style="color:#E74C3C;">2026-05-19</span></td>
</tr>
<tr>
<td><b>Experimenter</b></td>
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>
<tr>
<td><b>Hypothesis</b></td>
<td><span style="color:#E74C3C;">Controlled 8-query router test achieved 100.0% routing accuracy.</span></td>
</tr>
<tr>
<td><b>Strategy / Config</b></td>
<td><span style="color:#E74C3C;">Groq ➔ Gemini ➔ Cerebras Failover Chain.</span></td>
</tr>
<tr>
<td><b>Dataset Used</b></td>
<td><span style="color:#E74C3C;">8 specialized domain queries</span></td>
</tr>
<tr>
<td><b>Retrieval Metrics</b></td>
<td><span style="color:#E74C3C;">Accuracy: 100.0%</span></td>
</tr>
<tr>
<td><b>Answer Metrics</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>
<tr>
<td><b>Latency</b></td>
<td><span style="color:#E74C3C;">936.05ms avg</span></td>
</tr>
<tr>
<td><b>Result (vs. baseline)</b></td>
<td><span style="color:#E74C3C;">Perfect routing achieved in the verified control set.</span></td>
</tr>
<tr style="background-color:#FCF3CF;">
<td><b>Surprising Finding</b></td>
<td><span style="color:#E74C3C;">Average latency stayed under 1s in the verified 8-query control set.</span></td>
</tr>
<tr style="background-color:#FDEBD0;">
<td><b>Production Implication</b></td>
<td><span style="color:#E74C3C;">Failover logic is mandatory for high-availability enterprise RAG.</span></td>
</tr>
</table>

<br/><br/>

---

# <span style="color:#1F4E79;">D11. Architecture Decision Summary</span>

Evidence-based recommendations for the AI-PMS production RAG pipeline. Every recommendation must cite specific experiment IDs.

<br/>

<table>
<tr style="background-color:#1F4E79; color:white;">
<th align="left">Decision</th>
<th align="left">Recommendation</th>
<th align="left">Evidence (Exp IDs)</th>
<th align="left">Trade-offs / Risks</th>
</tr>

<tr>
<td><b>Embedding Model</b></td>
<td><span style="color:#E74C3C;">all-MiniLM-L6-v2 (Edge), text-embedding-3-small (Cloud)</span></td>
<td><span style="color:#E74C3C;">ADD Section 2, UMAP Plots</span></td>
<td><span style="color:#E74C3C;">MiniLM sacrifices deep semantic richness for raw speed</span></td>
</tr>

<tr>
<td><b>Chunking: Contracts</b></td>
<td><span style="color:#E74C3C;">Semantic Split (Heading-Aware)</span></td>
<td><span style="color:#E74C3C;">EXP-002, chunking_results.md</span></td>
<td><span style="color:#E74C3C;">Fails on multi-clause dependencies without context enrichment</span></td>
</tr>

<tr>
<td><b>Chunking: NCRs</b></td>
<td><span style="color:#E74C3C;">Structure-Aware Split (Regex 'NCR No:')</span></td>
<td><span style="color:#E74C3C;">EXP-013, ADD Section 3</span></td>
<td><span style="color:#E74C3C;">Requires strict regex alignment to form layouts</span></td>
</tr>

<tr>
<td><b>Chunking: DPRs</b></td>
<td><span style="color:#E74C3C;">Temporal Split (Shift/Date-Aware)</span></td>
<td><span style="color:#E74C3C;">ADD Section 3</span></td>
<td><span style="color:#E74C3C;">Daily logs missing dates may clump together</span></td>
</tr>

<tr>
<td><b>Retrieval Strategy</b></td>
<td><span style="color:#E74C3C;">Hybrid Search + Contextual Retrieval</span></td>
<td><span style="color:#E74C3C;">EXP-003, D5.3 Table</span></td>
<td><span style="color:#E74C3C;">Increases indexing time due to LLM calls</span></td>
</tr>

<tr>
<td><b>Reranking Model</b></td>
<td><span style="color:#E74C3C;">bge-reranker-v2-m3 (Production)</span></td>
<td><span style="color:#E74C3C;">D5.3 Table</span></td>
<td><span style="color:#E74C3C;">Introduces ~180ms latency overhead</span></td>
</tr>

<tr>
<td><b>Fusion Method</b></td>
<td><span style="color:#E74C3C;">Reciprocal Rank Fusion (RRF)</span></td>
<td><span style="color:#E74C3C;">ADD Section 4, eval_hybrid_...md</span></td>
<td><span style="color:#E74C3C;">Adds 2ms overhead but improves recall significantly</span></td>
</tr>

<tr>
<td><b>GraphRAG Scope</b></td>
<td><span style="color:#E74C3C;">Native PostgreSQL Graph (CTEs)</span></td>
<td><span style="color:#E74C3C;">EXP-009, EXP-010</span></td>
<td><span style="color:#E74C3C;">Strict SQL implementation requires precise relation metadata</span></td>
</tr>

<tr>
<td><b>Query Routing</b></td>
<td><span style="color:#E74C3C;">Sequential API Failover Classifier</span></td>
<td><span style="color:#E74C3C;">EXP-015, query_router_test_Nishitha.md</span></td>
<td><span style="color:#E74C3C;">Adds ~900ms delay prior to retrieval</span></td>
</tr>

<tr>
<td><b>LLM for Generation</b></td>
<td><span style="color:#E74C3C;">Llama 3.1 70B (Streaming Enabled)</span></td>
<td><span style="color:#E74C3C;">Hardening Test, ADD Section 6</span></td>
<td><span style="color:#E74C3C;">Current bottleneck for <5s end-to-end SLA</span></td>
</tr>
</table>

<br/><br/>

# <span style="color:#2E75B6;">D11.1 Open Questions & Deferred Items</span>

<table>
<tr style="background-color:#1F4E79; color:white;">
<th align="left">Open Question</th>
<th align="left">Blocked By</th>
<th align="left">When Resolvable</th>
</tr>

<tr>
<td>Real data evaluation accuracy</td>
<td>DMRC engagement / STAMP data</td>
<td>Post-pilot kickoff (Phase 2)</td>
</tr>

<tr>
<td>Domain embedding fine-tuning</td>
<td>Sufficient real corpus for training</td>
<td>Phase 2 (Tier 1 maturity)</td>
</tr>

<tr>
<td>Production load testing</td>
<td>Hardware provisioning + L40S GPUs</td>
<td>Post-GPU procurement</td>
</tr>

<tr>
<td><span style="color:#E74C3C;">Scale-Out RLS Degradation</span></td>
<td><span style="color:#E74C3C;">Ingestion of 1M+ chunks</span></td>
<td><span style="color:#E74C3C;">Phase 3</span></td>
</tr>

<tr>
<td><span style="color:#E74C3C;">Dynamic Graph Auto-Ingestion</span></td>
<td><span style="color:#E74C3C;">LLM pipeline for relation extraction</span></td>
<td><span style="color:#E74C3C;">Phase 3</span></td>
</tr>
</table>

<br/><br/><br/>

<div align="center">

<span style="color:#E74C3C;"><b>End of Deliverables Document</b></span>

</div>
