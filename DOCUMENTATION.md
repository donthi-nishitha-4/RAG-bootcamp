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
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>

<tr>
<td><b>Bootcamp Dates</b></td>
<td><span style="color:#E74C3C;">May 2026</span></td>
</tr>

<tr>
<td><b>Document Version</b></td>
<td>v1.0 (Template) — Update as experiments are completed</td>
</tr>

<tr>
<td><b>Git Repository</b></td>
<td><span style="color:#E74C3C;">AIPMS/aipms-rag-bootcamp</span></td>
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
        ClientAPI[Client API Call / TestClient] -->|POST /query payload| API_Service[FastAPI api_Nishitha.py]
    end

    subgraph Security & Hardening Layer
        API_Service -->|Query Text| OutOfScopeFilter{Adversarial & OOD Filter}
        OutOfScopeFilter -->|Match OOD Heuristics / Off-scope| Block[Fast Intercept: Refusal Answer]
        OutOfScopeFilter -->|Safe In-Scope Query| RouterCall[Route Intent Classifier]
    end

    subgraph Orchestration & StateGraph Layer
        RouterCall -->|Initialize StateGraph| AgentAgent{LangGraph StateGraph}
        AgentAgent -->|Node 1: query_analyzer| Router[LLM Query Router query_router_Nishitha.py]
        Router -->|Sequential API Failover Classifier| RouteSelection{Route Intent}
    end

    subgraph Dynamic Data Retrieval Layer
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

    subgraph Failsafe & Graph Fallback Layer
        ResultFilter -->|PostgreSQL Self-Join Traversal| GraphTraverse[Mock Graph retrieve_graph]
        GraphTraverse --> SiblingNodes[Retrieve Connected Subsystem Nodes]
        
        ResultFilter -->|Offline DB Container Fallback| FileScanner[Word-Overlap Filesystem Scanner]
        FileScanner --> OfflineChunks[Local raw document Chunks]
    end

    subgraph Evaluator & Reformulation Loop
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
<td><span style="color:#E74C3C;">Architecture Decision Document</span></td>
</tr>

<tr style="background-color:#F2F4F4;">
<td><b>Graph Store</b></td>
<td>Apache AGE, Neo4j, None</td>
<td><span style="color:#E74C3C;">Native PostgreSQL Graph Strategy - Recursive CTEs give sub-20ms latency.</span></td>
<td><span style="color:#E74C3C;">ADD Section 5</span></td>
</tr>

<tr>
<td><b>Sparse Search</b></td>
<td>pg_trgm, Elasticsearch, OpenSearch</td>
<td><span style="color:#E74C3C;">pg_trgm - Integrates natively with pgvector for Hybrid Search without additional infrastructure.</span></td>
<td><span style="color:#E74C3C;">ADD Section 4</span></td>
</tr>

<tr style="background-color:#F2F4F4;">
<td><b>LLM Serving</b></td>
<td>vLLM, Ollama, TGI</td>
<td><span style="color:#E74C3C;">API Dependent (Llama 3.1) - Best performance for inference.</span></td>
<td><span style="color:#E74C3C;">ADD Section 6</span></td>
</tr>

<tr>
<td><b>Orchestration Framework</b></td>
<td>LangGraph, LlamaIndex, Custom</td>
<td><span style="color:#E74C3C;">LangGraph - Allows complex state graphs, routing, and reformulations.</span></td>
<td><span style="color:#E74C3C;">ADD Section 4</span></td>
</tr>

<tr style="background-color:#F2F4F4;">
<td><b>Fusion Strategy</b></td>
<td>RRF, CombSUM, CombMNZ</td>
<td><span style="color:#E74C3C;">RRF - Reciprocal Rank Fusion provided best baseline combination of BM25 and Vector.</span></td>
<td><span style="color:#E74C3C;">Deliverables Guide Filled</span></td>
</tr>

</table>

<br/>

<div style="border:1px solid #D5DBDB; background-color:#ECF0F1; padding:16px; border-radius:6px;">

### 🔍 <span style="color:#1F4E79;">OBSERVATION: Overall Architecture Fitness</span>

**What we expected:** <span style="color:#E74C3C;">A fast, integrated end-to-end RAG system with sub-5s latency.</span>  

**What actually happened:** <span style="color:#E74C3C;">Achieved excellent retrieval routing but total end-to-end pipeline latency reached ~13.7s due to network bottlenecks.</span>  

**Why it happened (root cause):** <span style="color:#E74C3C;">LLM Generation via API takes ~13000ms. Local vector search/traversals are fast (<20ms).</span>  

**Production implication for AI-PMS:** <span style="color:#E74C3C;">Token streaming to UI and high-speed local inference are required for production.</span>  

</div>

---

# <span style="color:#1F4E79;">D2. Embedding Model Comparison</span>

Side-by-side UMAP projections showing how each embedding model separates AI-PMS document types in vector space.

*Run `notebooks/01_embedding_comparision_Nishitha.ipynb` or execute `python scripts/compare_embeddings_Nishitha.py` to generate the updated UMAP comparison plots.*
*Image Generation Prompt:* "Generate a UMAP scatter plot comparing document embeddings across three models (MiniLM, BGE-Large, Nomic) showing cluster separation of Contract Clauses, NCR Descriptions, and DPR Narratives."

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

<sub><i>Figure D2.1: UMAP Projections — Generated at docs/images/umap_comparison.png</i></sub>

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
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">MiniLM</span></td>
<td><span style="color:#E74C3C;">1.25 GB</span></td>
<td><span style="color:#E74C3C;">MiniLM requires zero GPU setup</span></td>
</tr>

<tr>
<td><b>Embedding Latency (p95)</b></td>
<td><span style="color:#E74C3C;">7.03 ms</span></td>
<td><span style="color:#E74C3C;">54.28 ms</span></td>
<td><span style="color:#E74C3C;">43.74 ms</span></td>
<td><span style="color:#E74C3C;">MiniLM</span></td>
<td><span style="color:#E74C3C;">36.71 ms</span></td>
<td><span style="color:#E74C3C;">Local CPU Latency</span></td>
</tr>

<tr>
<td><b>Domain Term Separation</b></td>
<td><span style="color:#E74C3C;">Adequate</span></td>
<td><span style="color:#E74C3C;">Best</span></td>
<td><span style="color:#E74C3C;">Strong</span></td>
<td><span style="color:#E74C3C;">bge-large</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">Observed via UMAP</span></td>
</tr>

<tr>
<td><b>Contract Clause P@5</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>NCR P@5</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>DPR P@5</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Cross-Entity Confusion Rate</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">LLM reasoning acts as defense</span></td>
</tr>
</table>

<br/>

# <span style="color:#2E75B6;">D2.2 Domain-Specific Observations</span>

<div style="background-color:#EAF2F8; border:1px solid #BFC9CA; padding:14px;">

🔍 <b>OBSERVATION: Metro-rail domain terms clustering (OHE, TBM, ballastless track)</b>

<br/>

<b>What we expected:</b> <span style="color:#E74C3C;">Models should effectively cluster domain-specific terminology distinctly from general text.</span>  
<b>What actually happened:</b> <span style="color:#E74C3C;">BAAI/bge-large-en-v1.5 gave the best domain-term separation based on UMAP plots.</span>  
<b>Why it happened (root cause):</b> <span style="color:#E74C3C;">Larger embedding dimensions (1024) provide better granularity for complex domain vocabularies.</span>  
<b>Production implication for AI-PMS:</b> <span style="color:#E74C3C;">For pure semantic search, a larger model is better, though MiniLM handles latency efficiently.</span>

</div>

<br/>

<div style="background-color:#EAF2F8; border:1px solid #BFC9CA; padding:14px;">

🔍 <b>OBSERVATION: Cross-entity separation quality (do contracts separate from NCRs?)</b>

<br/>

<b>What we expected:</b> <span style="color:#E74C3C;">Distinct clusters for contract_clause, ncr_description, and dpr_narrative.</span>  
<b>What actually happened:</b> <span style="color:#E74C3C;">Separation was achieved, with NCRs closer to live incident language.</span>  
<b>Why it happened (root cause):</b> <span style="color:#E74C3C;">Difference in writing style: legal formalism vs daily reporting structures.</span>  
<b>Production implication for AI-PMS:</b> <span style="color:#E74C3C;">The router logic is essential as purely vector-based retrieval can still retrieve adjacent entity chunks.</span>

</div>

<br/>

<b>Recommended Model:</b> <span style="color:#E74C3C;">all-MiniLM-L6-v2 for Edge/Local Execution, text-embedding-3-small for Enterprise Cloud Scale-Out</span> — with justification based on above data

---

# <span style="color:#1F4E79;">D3. Chunking Strategy Comparison</span>

*Execute graphing script or draw Python plots utilizing `docs/chunking_results.md` to visualize impact.*

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

<sub><i>Figure D3.1: Chunking Impact by Document Type — Based on chunking_results.md</i></sub>

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
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">Baseline</span></td>
</tr>

<tr>
<td><b>Recursive character</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Semantic chunking</b></td>
<td><span style="color:#E74C3C;">1.0</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">Legal/Contract docs (GCC)</span></td>
</tr>

<tr>
<td><b>Document-structure</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">NCR Data / DPR Logs</span></td>
</tr>

<tr>
<td><b>Parent-child</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>
</table>

<br/>

<div style="background-color:#EAF2F8; border:1px solid #BFC9CA; padding:14px;">

🔍 <b>OBSERVATION: Which chunking strategy fails worst for FIDIC contracts, and why?</b>

<br/>

<b>What we expected:</b> <span style="color:#E74C3C;">Naive chunking should degrade retrieval.</span>  
<b>What actually happened:</b> <span style="color:#E74C3C;">Heading-based (Semantic) chunking fails when answers span multiple clauses. Simple/Paragraph was insufficient for precise lookups.</span>  
<b>Why it happened (root cause):</b> <span style="color:#E74C3C;">Fixed-size chunks disrupt legal clause continuity.</span>  
<b>Production implication for AI-PMS:</b> <span style="color:#E74C3C;">Use Semantic Splitting tailored to exact occurrences of clauses.</span>

</div>

<br/>

<div style="background-color:#EAF2F8; border:1px solid #BFC9CA; padding:14px;">

🔍 <b>OBSERVATION: Does parent-child retrieval consistently outperform flat chunking?</b>

<br/>

<b>What we expected:</b> <span style="color:#E74C3C;">Yes.</span>  
<b>What actually happened:</b> <span style="color:#E74C3C;">Metadata injected paragraph splitting ensures higher recall.</span>  
<b>Why it happened (root cause):</b> <span style="color:#E74C3C;">Preserves parent context in the child vector space.</span>  
<b>Production implication for AI-PMS:</b> <span style="color:#E74C3C;">Metadata filtering is mandatory to guarantee context.</span>

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
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Generated Answer</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Expected Correct Answer</b></td>
<td><span style="color:#E74C3C;">Refusal to Answer (Entity restriction)</span></td>
</tr>

<tr>
<td><b>Failure Mode Observed</b></td>
<td><span style="color:#E74C3C;">Entity Leakage</span></td>
</tr>

<tr>
<td><b>Root Cause</b></td>
<td><span style="color:#E74C3C;">Mixed tenants in vector space</span></td>
</tr>

<tr>
<td><b>Fix Applied (if any)</b></td>
<td><span style="color:#E74C3C;">LLM zero-shot filter / Metadata filtering</span></td>
</tr>

<tr>
<td><b>Result After Fix</b></td>
<td><span style="color:#E74C3C;">100% success rate on preventing entity confusion</span></td>
</tr>
</table>

<br/><br/>

# <span style="color:#2E75B6;">FE-02: Wrong Contract Version</span>

<sub><i>FIDIC Red/Yellow Book confusion</i></sub>

<table>
<tr>
<td><b>Query Used</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Retrieved Chunks (Top 5)</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Generated Answer</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Expected Correct Answer</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Failure Mode Observed</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Root Cause</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Fix Applied (if any)</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Result After Fix</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>
</table>

<br/><br/>

# <span style="color:#2E75B6;">FE-03: Long Document Summary Bias</span>

<sub><i>Top-K sampling on 100-page contract</i></sub>

<table>
<tr>
<td><b>Query Used</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Retrieved Chunks (Top 5)</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Generated Answer</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Expected Correct Answer</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Failure Mode Observed</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Root Cause</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Fix Applied (if any)</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Result After Fix</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
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
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Generated Answer</b></td>
<td><span style="color:#E74C3C;">Refusal</span></td>
</tr>

<tr>
<td><b>Expected Correct Answer</b></td>
<td><span style="color:#E74C3C;">I cannot answer this from the context.</span></td>
</tr>

<tr>
<td><b>Failure Mode Observed</b></td>
<td><span style="color:#E74C3C;">Faithful Failure Paradox</span></td>
</tr>

<tr>
<td><b>Root Cause</b></td>
<td><span style="color:#E74C3C;">Empty context</span></td>
</tr>

<tr>
<td><b>Fix Applied (if any)</b></td>
<td><span style="color:#E74C3C;">Lightweight pre-retrieval classifier</span></td>
</tr>

<tr>
<td><b>Result After Fix</b></td>
<td><span style="color:#E74C3C;">Successfully handles out-of-scope queries before database layer</span></td>
</tr>
</table>

<br/><br/>

# <span style="color:#2E75B6;">FE-05: Tenant Data Leakage</span>

<sub><i>Cross-tenant query without metadata filter</i></sub>

<table>
<tr>
<td><b>Query Used</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Retrieved Chunks (Top 5)</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Generated Answer</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Expected Correct Answer</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Failure Mode Observed</b></td>
<td><span style="color:#E74C3C;">Tenant ID mismatch bug</span></td>
</tr>

<tr>
<td><b>Root Cause</b></td>
<td><span style="color:#E74C3C;">Postgres populated with "default_strategy" while searching for "default"</span></td>
</tr>

<tr>
<td><b>Fix Applied (if any)</b></td>
<td><span style="color:#E74C3C;">Updated script's default tenant to align</span></td>
</tr>

<tr>
<td><b>Result After Fix</b></td>
<td><span style="color:#E74C3C;">Correct retrieval using RLS</span></td>
</tr>
</table>

---

# <span style="color:#1F4E79;">D5. Retrieval Strategy Head-to-Head Comparison</span>

<br/>

# <span style="color:#2E75B6;">D5.1 Hybrid Search Architecture</span>

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

<sub><i>Figure D5.1: Hybrid Search with Reciprocal Rank Fusion</i></sub>

# <span style="color:#2E75B6;">D5.2 Consolidated Metrics</span>

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

---

<sub><i>Figure D5.2: Strategy Performance Comparison — Replace with actual data</i></sub>

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
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td>1</td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>+ Metadata Filter</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td>1</td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Hybrid (BM25+Vec+RRF)</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td>1</td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Hybrid + Rerank (ms-marco)</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td>1</td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Hybrid + Rerank (bge-v2-m3)</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td>1</td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>HyDE</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td>2</td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Multi-Query</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td>3–5</td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Contextual Retrieval</b></td>
<td><span style="color:#E74C3C;">Best</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td>0*</td>
<td><span style="color:#E74C3C;">Provides best precision</span></td>
</tr>
</table>

<sub><i>* Contextual Retrieval uses LLM calls at ingestion time, not query time.</i></sub>

<br/>

<div style="background-color:#EAF2F8; border:1px solid #BFC9CA; padding:14px;">

🔍 <b>OBSERVATION: Which strategy gives the best precision-latency trade-off within the 5s NFR?</b>

<br/>

<b>What we expected:</b> <span style="color:#E74C3C;">Hybrid + Reranking</span>  
<b>What actually happened:</b> <span style="color:#E74C3C;">Contextual + Hybrid provides best precision</span>  
<b>Why it happened (root cause):</b> <span style="color:#E74C3C;">Contextual retrieval enriches the metadata efficiently.</span>  
<b>Production implication for AI-PMS:</b> <span style="color:#E74C3C;">Requires robust pipeline ingestion setup.</span>

</div>

<br/>

<div style="background-color:#EAF2F8; border:1px solid #BFC9CA; padding:14px;">

🔍 <b>OBSERVATION: Does HyDE help or hurt on precise legal terminology queries?</b>

<br/>

<b>What we expected:</b> <span style="color:#E74C3C;">HyDE may struggle with exact terms.</span>  
<b>What actually happened:</b> <span style="color:#E74C3C;">N/A</span>  
<b>Why it happened (root cause):</b> <span style="color:#E74C3C;">N/A</span>  
<b>Production implication for AI-PMS:</b> <span style="color:#E74C3C;">N/A</span>

</div>

---

# <span style="color:#1F4E79;">D6. Agentic RAG & Multi-Hop Retrieval</span>

<br/>

# <span style="color:#2E75B6;">D6.1 LangGraph Architecture</span>

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

---

<sub><i>Figure D6.1: Agentic RAG with LangGraph State Graph</i></sub>

# <span style="color:#2E75B6;">D6.2 Query Router</span>

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

---

<sub><i>Figure D6.2: Query Router — Strategy Selection Logic</i></sub>

# <span style="color:#2E75B6;">D6.3 Multi-Hop Query Trace Log</span>

For each multi-hop query, document the complete retrieval trace:

<br/>

# <span style="color:#3498DB;">MH-01: "Is the contractor at risk of a time-bar miss on Package CC-07?"</span>

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
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
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
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>
</table>

<br/><br/>

# <span style="color:#3498DB;">MH-02: "What NCRs are linked to critical path activities?"</span>

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
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
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
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>
</table>

<br/><br/>

# <span style="color:#3498DB;">MH-03: "Compare civil works progress across all packages this month"</span>

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
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
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
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
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
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Quantitative / SQL</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Relationship / Graph</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Legal / Contract</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Complex / Multi-Hop</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>
</table>

<br/>

<div style="background-color:#EAF2F8; border:1px solid #BFC9CA; padding:14px;">

🔍 <b>OBSERVATION: Does the LLM-based router reliably distinguish SQL vs. vector queries?</b>

<br/>

<b>What we expected:</b> <span style="color:#E74C3C;">N/A</span>  
<b>What actually happened:</b> <span style="color:#E74C3C;">N/A</span>  
<b>Why it happened (root cause):</b> <span style="color:#E74C3C;">N/A</span>  
<b>Production implication for AI-PMS:</b> <span style="color:#E74C3C;">N/A</span>

</div>

---

# <span style="color:#1F4E79;">D7. RAGAS Evaluation Results</span>

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

---

# <span style="color:#2E75B6;">D7.1 Overall Metrics</span>

<table>
<tr style="background-color:#1F4E79; color:white;">
<th align="left">Metric</th>
<th align="left">Day 2 Baseline</th>
<th align="left">Day 10 Final</th>
<th align="left">Target</th>
<th align="left">Met?</th>
<th align="left">Notes</th>
</tr>

<tr>
<td><b>Faithfulness</b></td>
<td><span style="color:#E74C3C;">0.375</span></td>
<td><span style="color:#E74C3C;">1.00</span></td>
<td>&gt; 0.85</td>
<td><span style="color:#E74C3C;">Yes</span></td>
<td><span style="color:#E74C3C;">Excellent on in-scope, zero-shot refuses OOD queries</span></td>
</tr>

<tr>
<td><b>Answer Relevancy</b></td>
<td><span style="color:#E74C3C;">0.398</span></td>
<td><span style="color:#E74C3C;">1.00</span></td>
<td>&gt; 0.80</td>
<td><span style="color:#E74C3C;">Yes</span></td>
<td><span style="color:#E74C3C;">High quality answers for successful retrievals</span></td>
</tr>

<tr>
<td><b>Context Precision</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td>&gt; 0.75</td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Context Recall</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td>&gt; 0.70</td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
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
<td><b>Contract / Legal (n = 10)</b></td>
<td><span style="color:#E74C3C;">1.0</span></td>
<td><span style="color:#E74C3C;">1.0</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">Chunk size overlap</span></td>
</tr>

<tr>
<td><b>Multi-Hop (n = )</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Adversarial / OOS (n = 5)</b></td>
<td><span style="color:#E74C3C;">1.0</span></td>
<td><span style="color:#E74C3C;">0.0</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">Relevance penalised for refusal</span></td>
</tr>

<tr>
<td><b>Metadata-Dependent (n = )</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>General Factoid (n = )</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
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

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

---

<sub><i>Figure D8.1: Latency Budget Breakdown — Based on Realized WSL2 Latency</i></sub>

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
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">0.01ms</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td>50ms</td>
<td><span style="color:#E74C3C;">Pass</span></td>
</tr>

<tr>
<td><b>Vector Search (pgvector)</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">0.02ms</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td>300ms</td>
<td><span style="color:#E74C3C;">Pass</span></td>
</tr>

<tr>
<td><b>BM25 Search (pg_trgm)</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td>200ms</td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>RRF Fusion</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td>50ms</td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>Cross-Encoder Rerank</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">0.00ms</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td>500ms</td>
<td><span style="color:#E74C3C;">Pass (Bypassed)</span></td>
</tr>

<tr>
<td><b>LLM Generation (Llama 3.1)</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">~13000ms</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td>3500ms</td>
<td><span style="color:#E74C3C;">Fail</span></td>
</tr>

<tr>
<td><b>Citation + Audit Log</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td>100ms</td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr style="background-color:#FDEBD0;">
<td><b>TOTAL END-TO-END</b></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">~13.7s</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><b>4700ms</b></td>
<td><span style="color:#E74C3C;">Fail</span></td>
</tr>
</table>

<br/>

<div style="background-color:#EAF2F8; border:1px solid #BFC9CA; padding:14px;">

🔍 <b>OBSERVATION: Which component is the latency bottleneck? What can be optimized?</b>

<br/>

<b>What we expected:</b> <span style="color:#E74C3C;">Overall <5s End-to-End Latency.</span>  
<b>What actually happened:</b> <span style="color:#E74C3C;">LLM generation via API exceeded budget significantly (~13s).</span>  
<b>Why it happened (root cause):</b> <span style="color:#E74C3C;">Network bottlenecks for remote API inference.</span>  
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
<td><span style="color:#E74C3C;">Cross-tenant query test</span></td>
<td><span style="color:#E74C3C;">DMRC</span></td>
<td><span style="color:#E74C3C;">No</span></td>
<td><span style="color:#E74C3C;">Pass</span></td>
<td><span style="color:#E74C3C;">RLS Enforced properly after default_strategy fix</span></td>
</tr>

<tr>
<td>2</td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
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

<b>Leakage Rate:</b> <span style="color:#E74C3C;">0</span> / 1 = <span style="color:#E74C3C;">0</span>% — Target: 0%

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
<td><span style="color:#E74C3C;">How is AI used in medicine?</span></td>
<td><span style="color:#E74C3C;">Refusal</span></td>
<td><span style="color:#E74C3C;">No</span></td>
<td><span style="color:#E74C3C;">Pass</span></td>
</tr>

<tr>
<td>2</td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td>3</td>
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
</tr>

<tr>
<td>5</td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>
</table>

<br/>

<b>Hallucination Rate on OOS Queries:</b> <span style="color:#E74C3C;">0</span>% — Target: 0%

---

# <span style="color:#1F4E79;">D10. Structured Experiment Log</span>

Minimum 15 experiment entries required across the bootcamp. Copy this template for each experiment.

<br/>

# <span style="color:#2E75B6;">Experiment EXP-001</span>

<table>
<tr>
<td><b>Date</b></td>
<td><span style="color:#E74C3C;">2026-04-25</span></td>
</tr>

<tr>
<td><b>Experimenter</b></td>
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>

<tr>
<td><b>Hypothesis</b></td>
<td><span style="color:#E74C3C;">Vector Baseline Evaluation</span></td>
</tr>

<tr>
<td><b>Strategy / Config</b></td>
<td><span style="color:#E74C3C;">Naive Vector Retrieval</span></td>
</tr>

<tr>
<td><b>Dataset Used</b></td>
<td><span style="color:#E74C3C;">Mixed</span></td>
</tr>

<tr>
<td><b>Retrieval Metrics</b></td>
<td>
<span style="color:#E74C3C;">
P@5: [ N/A ] &nbsp;|&nbsp;
P@10: [ N/A ] &nbsp;|&nbsp;
MRR: [ N/A ] &nbsp;|&nbsp;
NDCG@10: [ N/A ]
</span>
</td>
</tr>

<tr>
<td><b>Answer Metrics</b></td>
<td>
<span style="color:#E74C3C;">
Faithfulness: [ 1.00 ] &nbsp;|&nbsp;
Relevancy: [ 0.65 ] &nbsp;|&nbsp;
Completeness: [ N/A ]
</span>
</td>
</tr>

<tr>
<td><b>Latency</b></td>
<td>
<span style="color:#E74C3C;">
p50: [ N/A ]ms &nbsp;
p95: [ N/A ]ms &nbsp;
p99: [ N/A ]ms
</span>
</td>
</tr>

<tr>
<td><b>Result (vs. baseline)</b></td>
<td><span style="color:#E74C3C;">66% Success Rate</span></td>
</tr>

<tr style="background-color:#FCF3CF;">
<td><b>Surprising Finding</b></td>
<td><span style="color:#E74C3C;">Faithful Failure Paradox: System accurately achieved 1.0 faithfulness by correctly refusing out of scope questions.</span></td>
</tr>

<tr style="background-color:#FDEBD0;">
<td><b>Production Implication</b></td>
<td><span style="color:#E74C3C;">Requires a pre-retrieval classifier to filter OOS queries early.</span></td>
</tr>
</table>

<br/><br/>

# <span style="color:#2E75B6;">Experiment EXP-002</span>

<table>
<tr>
<td><b>Date</b></td>
<td><span style="color:#E74C3C;">2026-04-25</span></td>
</tr>

<tr>
<td><b>Experimenter</b></td>
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>

<tr>
<td><b>Hypothesis</b></td>
<td><span style="color:#E74C3C;">Semantic Chunking Improvement</span></td>
</tr>

<tr>
<td><b>Strategy / Config</b></td>
<td><span style="color:#E74C3C;">Semantic Vector</span></td>
</tr>

<tr>
<td><b>Dataset Used</b></td>
<td><span style="color:#E74C3C;">GCC</span></td>
</tr>

<tr>
<td><b>Retrieval Metrics</b></td>
<td>
<span style="color:#E74C3C;">
P@5: [ N/A ] &nbsp;|&nbsp;
P@10: [ N/A ] &nbsp;|&nbsp;
MRR: [ N/A ] &nbsp;|&nbsp;
NDCG@10: [ N/A ]
</span>
</td>
</tr>

<tr>
<td><b>Answer Metrics</b></td>
<td>
<span style="color:#E74C3C;">
Faithfulness: [ 1.00 ] &nbsp;|&nbsp;
Relevancy: [ 0.66 ] &nbsp;|&nbsp;
Completeness: [ N/A ]
</span>
</td>
</tr>

<tr>
<td><b>Latency</b></td>
<td>
<span style="color:#E74C3C;">
p50: [ N/A ]ms &nbsp;
p95: [ N/A ]ms &nbsp;
p99: [ N/A ]ms
</span>
</td>
</tr>

<tr>
<td><b>Result (vs. baseline)</b></td>
<td><span style="color:#E74C3C;">66% Success Rate</span></td>
</tr>

<tr style="background-color:#FCF3CF;">
<td><b>Surprising Finding</b></td>
<td><span style="color:#E74C3C;">Heading-based chunking fails when answers span multiple clauses.</span></td>
</tr>

<tr style="background-color:#FDEBD0;">
<td><b>Production Implication</b></td>
<td><span style="color:#E74C3C;">Need context window enrichment (k=1 neighbor padding).</span></td>
</tr>
</table>

<br/><br/>

# <span style="color:#2E75B6;">Experiment EXP-003</span>

<table>
<tr>
<td><b>Date</b></td>
<td><span style="color:#E74C3C;">2026-04-25</span></td>
</tr>

<tr>
<td><b>Experimenter</b></td>
<td><span style="color:#E74C3C;">Nishitha</span></td>
</tr>

<tr>
<td><b>Hypothesis</b></td>
<td><span style="color:#E74C3C;">Hybrid Search improves exact match retrieval</span></td>
</tr>

<tr>
<td><b>Strategy / Config</b></td>
<td><span style="color:#E74C3C;">Hybrid Search</span></td>
</tr>

<tr>
<td><b>Dataset Used</b></td>
<td><span style="color:#E74C3C;">GCC</span></td>
</tr>

<tr>
<td><b>Retrieval Metrics</b></td>
<td>
<span style="color:#E74C3C;">
P@5: [ N/A ] &nbsp;|&nbsp;
P@10: [ N/A ] &nbsp;|&nbsp;
MRR: [ N/A ] &nbsp;|&nbsp;
NDCG@10: [ N/A ]
</span>
</td>
</tr>

<tr>
<td><b>Answer Metrics</b></td>
<td>
<span style="color:#E74C3C;">
Faithfulness: [ 1.00 ] &nbsp;|&nbsp;
Relevancy: [ 0.66 ] &nbsp;|&nbsp;
Completeness: [ N/A ]
</span>
</td>
</tr>

<tr>
<td><b>Latency</b></td>
<td>
<span style="color:#E74C3C;">
p50: [ N/A ]ms &nbsp;
p95: [ N/A ]ms &nbsp;
p99: [ N/A ]ms
</span>
</td>
</tr>

<tr>
<td><b>Result (vs. baseline)</b></td>
<td><span style="color:#E74C3C;">66% Success Rate</span></td>
</tr>

<tr style="background-color:#FCF3CF;">
<td><b>Surprising Finding</b></td>
<td><span style="color:#E74C3C;">Trigram search fixes technical term misses but cannot fix small chunk issues.</span></td>
</tr>

<tr style="background-color:#FDEBD0;">
<td><b>Production Implication</b></td>
<td><span style="color:#E74C3C;">Parent Document Retrieval is required alongside Hybrid search.</span></td>
</tr>
</table>

<br/><br/>

<sub><i>[Continue for EXP-004 through EXP-015+ using same template]</i></sub>

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
<td><span style="color:#E74C3C;">ADD Section 2</span></td>
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
<td><span style="color:#E74C3C;">Structure-Aware Splitting</span></td>
<td><span style="color:#E74C3C;">ADD Section 3</span></td>
<td><span style="color:#E74C3C;">Requires strict regex alignment</span></td>
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
<td><span style="color:#E74C3C;">EXP-003</span></td>
<td><span style="color:#E74C3C;">Increases indexing time due to LLM calls</span></td>
</tr>

<tr>
<td><b>Reranking Model</b></td>
<td><span style="color:#E74C3C;">ms-marco / bge CPU Reranker</span></td>
<td><span style="color:#E74C3C;">ADD Section 4</span></td>
<td><span style="color:#E74C3C;">Introduces minor latency overhead</span></td>
</tr>

<tr>
<td><b>Fusion Method</b></td>
<td><span style="color:#E74C3C;">Reciprocal Rank Fusion (RRF)</span></td>
<td><span style="color:#E74C3C;">ADD Section 4</span></td>
<td><span style="color:#E74C3C;">N/A</span></td>
</tr>

<tr>
<td><b>GraphRAG Scope</b></td>
<td><span style="color:#E74C3C;">Native PostgreSQL Graph Strategy</span></td>
<td><span style="color:#E74C3C;">ADD Section 5</span></td>
<td><span style="color:#E74C3C;">Strict SQL implementation requires precise relation metadata</span></td>
</tr>

<tr>
<td><b>Query Routing</b></td>
<td><span style="color:#E74C3C;">Sequential API Failover Classifier</span></td>
<td><span style="color:#E74C3C;">ADD Section 4</span></td>
<td><span style="color:#E74C3C;">Slight delay prior to retrieval</span></td>
</tr>

<tr>
<td><b>LLM for Generation</b></td>
<td><span style="color:#E74C3C;">Llama 3.1 API (Streaming)</span></td>
<td><span style="color:#E74C3C;">ADD Section 6</span></td>
<td><span style="color:#E74C3C;">Current bottleneck for &lt;5s SLA</span></td>
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
<td>Post-pilot kickoff</td>
</tr>

<tr>
<td>Domain embedding fine-tuning</td>
<td>Sufficient real corpus</td>
<td>Phase 2 (Tier 1 maturity)</td>
</tr>

<tr>
<td>Production load testing</td>
<td>Hardware provisioning + L40S GPUs</td>
<td>Post-GPU procurement</td>
</tr>

<tr>
<td><span style="color:#E74C3C;">Scale-Out RLS Degradation</span></td>
<td><span style="color:#E74C3C;">Sufficient chunks (millions) ingestion</span></td>
<td><span style="color:#E74C3C;">Phase 2</span></td>
</tr>

<tr>
<td><span style="color:#E74C3C;">Dynamic Graph Auto-Ingestion</span></td>
<td><span style="color:#E74C3C;">LLM pipeline for unstructured relation extraction</span></td>
<td><span style="color:#E74C3C;">Phase 3</span></td>
</tr>
</table>

<br/><br/><br/>

<div align="center">

<span style="color:#E74C3C;"><b>End of Deliverables Document</b></span>

</div>
