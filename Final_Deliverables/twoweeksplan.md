Enterprise RAG Bootcamp
2-Week Intensive Implementation Plan
100% Open Source Stack | AI-PMS Context
From AntiGravity IDE to Production-Grade RAG in 10 Working Days

For: K. Bala Chowdappa & NLP Team, GPREC
Project: AI-PMS | Client: DMRC | March 2026 | v1.0
CONFIDENTIAL — Kernex Microsystems / TEL Internal

1. Reality Check: What 2 Weeks Can and Cannot Do
Two weeks is an intense bootcamp, not a mastery program. Here is what is achievable and what is not:
Achievable in 2 Weeks
NOT Achievable — Deferred
Working end-to-end RAG pipeline on pgvector
3–4 retrieval strategies tested head-to-head
Domain-specific chunkers for 3–4 AI-PMS document types
Hybrid search (BM25 + vector + RRF)
Cross-encoder reranking benchmarked
Basic agentic RAG with LangGraph
Manual evaluation on 50+ queries
GraphRAG proof-of-concept on Systems Taxonomy
Clear evidence-based strategy recommendations
Production-hardened deployment
200+ query golden evaluation dataset
Full RAGAS automated evaluation suite
Fine-tuned domain embeddings
Complete multi-agent integration
Load testing at scale
Monitoring and alerting infrastructure
CI/CD pipeline for RAG components

⚠️ CRITICAL: Synthetic Data Reminder
The DMRC Mega Metro dataset is AI-generated. Valid ONLY for pipeline testing, UI development, and pipeline validation. NOT for ML model training, rule calibration, or threshold validation. Label every experiment clearly: SYNTHETIC DATA.

2. Complete Open Source Tech Stack
Every single tool in this plan is open source and free. Zero API costs. Zero licensing concerns. Fully deployable on GPREC HPC on-prem.
Layer
Tool
License
Install
Vector Store (Primary)
PostgreSQL + pgvector
PostgreSQL License + Apache 2.0
apt install postgresql; CREATE EXTENSION vector;
Vector Store (Dev/Rapid)
ChromaDB
Apache 2.0
pip install chromadb
Vector Store (Benchmark)
FAISS (Meta)
MIT
pip install faiss-cpu (or faiss-gpu)
Graph Store
Apache AGE (PostgreSQL extension)
Apache 2.0
Build from source or apt; CREATE EXTENSION age;
Sparse Search (BM25)
PostgreSQL pg_trgm + tsvector (built-in)
PostgreSQL License
CREATE EXTENSION pg_trgm; (already in PostgreSQL)
Embedding Model A
sentence-transformers/all-MiniLM-L6-v2 (384-dim)
Apache 2.0
pip install sentence-transformers
Embedding Model B
BAAI/bge-large-en-v1.5 (1024-dim)
MIT
HuggingFace download, ~1.3 GB
Embedding Model C
nomic-ai/nomic-embed-text-v1.5 (768-dim)
Apache 2.0
HuggingFace download, ~550 MB
Reranker A
cross-encoder/ms-marco-MiniLM-L-12-v2
Apache 2.0
pip install sentence-transformers
Reranker B
BAAI/bge-reranker-v2-m3
MIT
HuggingFace download, ~1.1 GB
LLM (Primary)
Meta Llama 3.1 8B Instruct (via vLLM)
Llama 3.1 Community License
pip install vllm; download from HuggingFace
LLM (Lightweight)
Microsoft Phi-3-mini-4k-instruct (3.8B)
MIT
HuggingFace, ~7.6 GB. Fits on smaller GPUs.
LLM (Alternative)
Mistral 7B Instruct v0.3
Apache 2.0
HuggingFace download
LLM Serving
vLLM
Apache 2.0
pip install vllm. Serves OpenAI-compatible API.
Orchestration
LangGraph + LangChain
MIT
pip install langgraph langchain
Orchestration (Alt)
LlamaIndex
MIT
pip install llama-index
Evaluation
RAGAS
Apache 2.0
pip install ragas
Experiment Tracking
MLflow
Apache 2.0
pip install mlflow
Visualization
UMAP + Matplotlib
BSD-3 + PSF
pip install umap-learn matplotlib
Document Parsing
Unstructured.io
Apache 2.0
pip install unstructured
PDF Parsing
PyMuPDF (fitz) + pdfplumber
AGPL-3.0 + MIT
pip install pymupdf pdfplumber
Notebook
Jupyter Lab
BSD-3
pip install jupyterlab

🚨 LICENSING NOTE: PyMuPDF
PyMuPDF uses AGPL-3.0 which has copyleft implications if distributed. Fine for internal development and research. For production AI-PMS, evaluate whether pdfplumber (MIT) alone is sufficient, or budget for a commercial MuPDF license if needed.

3. Week 1: Foundations → Naive RAG → Break It (Days 1–5)
Day 1 (Monday): Environment Setup + Embedding Fundamentals
Morning (4 hrs): Infrastructure
    • Install PostgreSQL + pgvector + pg_trgm + Apache AGE on GPREC HPC node
    • Install vLLM, load Llama 3.1 8B Instruct, verify it serves on localhost:8000
    • Install ChromaDB for rapid prototyping (students use this while pgvector is being configured)
    • Set up shared Jupyter Lab server for team. Create Git repo: aipms-rag-bootcamp
    • Install all Python packages: sentence-transformers, langchain, langgraph, llama-index, ragas, mlflow, umap-learn, unstructured, pdfplumber
Afternoon (4 hrs): Embeddings From First Principles
    • Prepare test corpus: 50 synthetic FIDIC contract clauses + 30 NCR descriptions + 20 DPR narratives from the synthetic DMRC dataset
    • Embed with all-MiniLM-L6-v2 (384d). Visualize with UMAP. Observe: Do contract clauses cluster separately from NCRs? From DPRs?
    • Repeat with bge-large-en-v1.5 (1024d) and nomic-embed-text (768d). Side-by-side UMAP comparison.
Record: Which model best separates metro-rail domain terms (OHE catenary, ballastless track, tunnel boring machine) from generic text?
🚨 PITFALL: Skipping Embedding Comparison
If you pick all-MiniLM-L6-v2 because it is small and fast without comparing, you may spend weeks debugging bad retrieval caused by a weak embedding model. This 2-hour comparison on Day 1 saves days later.
Day 1 Exit: Each team member has a running notebook with 3-model UMAP comparison. Git committed.
Day 2 (Tuesday): Chunking Experiments + Naive RAG Pipeline
Morning (4 hrs): Chunking Strategies
Test ALL of these on the same FIDIC chapter. Record retrieved chunk quality for 10 test queries per strategy:
Strategy
Tool
Known Failure Mode
Fixed-size 512 tokens
LangChain CharacterTextSplitter
Cuts mid-clause, mid-sentence. Loses legal meaning.
Recursive character
LangChain RecursiveCharacterTextSplitter
Better but still clause-structure-unaware.
Semantic chunking
LlamaIndex SemanticSplitterNodeParser
Good for narrative. Poor for numbered legal clauses.
Document-structure-aware
Custom parser: split on clause headings (20.1, 20.1.1)
Best for contracts. Cannot generalize to DPRs/NCRs.
Parent-child hierarchical
LlamaIndex AutoMergingRetriever (child=256, parent=1024)
Needs careful parent/child size calibration.

Afternoon (4 hrs): Build Naive RAG End-to-End
Build the simplest possible pipeline. NO frameworks. Plain Python only:
Documents → RecursiveCharacterTextSplitter (512, overlap=50) → Best embedding model from Day 1 → pgvector → Top-K retrieval (K=5) → Llama 3.1 8B (via vLLM) → Answer
    • Load 200+ synthetic chunks covering contract clauses, NCRs, DPRs, correspondence
    • Write 20 test queries by hand (5 per entity type). Run each. Record: query, retrieved chunks, answer, your human judgment of quality (1–5 scale)
Record: Baseline Precision@5 and subjective answer quality. This is the number you will beat.
Day 2 Exit: Working naive RAG pipeline. Chunking comparison table. Baseline metrics on 20 queries. Git committed.
Day 3 (Wednesday): Break the Naive Pipeline + Metadata Filtering
Morning (4 hrs): The Breaking Experiments
Run each of these experiments. Document what goes wrong. This builds the intuition that no tutorial can give you.
Experiment
What To Do
Expected Failure & Lesson
Cross-Entity Confusion
Mix NCRs + contract clauses in same vector space. Query: ‘corrective action for concrete honeycombing?’
Retriever mixes NCR fixes with legal defect liability clauses. Answer blends operations with legal obligations.
Wrong Contract Version
Load FIDIC Red + Yellow Book. Query about Yellow Book time-bar.
System retrieves Red Book clauses and presents them as Yellow Book. LLM will NOT say ‘I don’t know.’
Long Document Summary
Load 100-page contract. Ask ‘Summarize contractor obligations.’
Top-5 retrieval covers 2% of document. ‘Summary’ is actually sampling bias. Completely misleading.
Adversarial Out-of-Scope
Query about something NOT in corpus: ‘What is the Bitcoin price forecast?’
System retrieves whatever is closest (garbage) and confidently answers. No fallback behavior.
Tenant Leakage
Load data tagged as Metro AND IR/DFCC. Query as Metro. Check if IR/DFCC data appears.
Without metadata filtering, cross-tenant data leaks freely. This is a security violation.

Afternoon (4 hrs): Implement Metadata Filtering
Fix the problems you just discovered. Add mandatory metadata to every chunk:
    • tenant_id (multi-tenancy isolation — enforced via PostgreSQL RLS)
    • entity_type (contract_clause | correspondence | dpr | ncr | meeting_minutes | drawing | incident_report)
    • package_id (which contract package)
    • source_document_id (traceable back to CDM)
    • contract_standard (Red/Yellow/Silver — for contract clauses only)
    • chunk_index + parent_chunk_id (for ordering and hierarchical retrieval)
Re-run the breaking experiments WITH metadata filtering. Document the improvement.
Day 3 Exit: 5 failure experiments documented with root cause analysis. Metadata-filtered retrieval working. Git committed.
Deliverable: 1-page writeup — ‘Why Naive RAG Is Not Production-Ready for AI-PMS’
Day 4 (Thursday): Hybrid Search + Reranking
Morning (4 hrs): Hybrid Search (BM25 + Vector + RRF)
Pure vector search misses exact-match queries. ‘Force Majeure’ is a specific legal term — you want BM25 exact match AND semantic similarity.
    • Implement BM25 using PostgreSQL tsvector + ts_rank (zero new infrastructure)
    • Implement Reciprocal Rank Fusion (RRF): score = 1/(k + rank_bm25) + 1/(k + rank_vector), where k=60
    • Compare on 20 queries: vector-only vs. BM25-only vs. hybrid (RRF). Record Precision@5 and MRR for each.
Observation: On which query TYPES does BM25 win? (Expect: exact legal terms, clause numbers, proper nouns). On which does vector win? (Expect: paraphrased questions, conceptual queries).
Afternoon (4 hrs): Cross-Encoder Reranking
    • Implement: Retrieve top-30 with hybrid search → Rerank with cross-encoder/ms-marco-MiniLM-L-12-v2 → Return top-5
    • Also test: BAAI/bge-reranker-v2-m3 (multilingual, larger, potentially better for domain text)
    • Measure: Precision@5 improvement AND latency cost (p50, p95) on GPREC hardware
🚨 PITFALL: Reranking Without Latency Budget
NFR-04 requires search and retrieval within 5 seconds (p95). If reranking adds 800ms on top of 3s retrieval + 2s generation, you are already over budget. Measure latency from Day 1. Budget: retrieval 1.5s, reranking 0.5s, generation 3s = 5s total.
Day 4 Exit: Hybrid search + reranking pipeline working. Quantitative comparison: naive vs. hybrid vs. hybrid+rerank. Git committed.
Day 5 (Friday): Advanced Retrieval Strategies + Week 1 Review
Morning (4 hrs): Test 3 More Strategies
Split the team. Each person/pair implements one strategy on the SAME 50-query evaluation set:
Strategy
Implementation
AI-PMS Use Case
HyDE
LLM generates hypothetical answer → embed that → retrieve with it. Use Llama 3.1 for generation.
Vague queries from non-technical site engineers: ‘What should I do about the delay?’
Multi-Query
LLM rewrites user query into 3 variations → retrieve for each → union + deduplicate results.
Ambiguous queries where user terminology does not match document terminology.
Contextual Retrieval
Prepend LLM-generated context to each chunk BEFORE embedding (‘situating’ the chunk in its document).
DPRs and NCRs where chunks lose meaning without surrounding context.

Afternoon (3 hrs): Week 1 Consolidated Review
Every team member presents their results. As a team, build the consolidated comparison:
Strategy
P@5
MRR
Latency p95
Extra Infra
Verdict
Naive (vector only)
[fill]
[fill]
[fill]
None
Baseline
+ Metadata filtering
[fill]
[fill]
[fill]
None
[fill]
Hybrid (BM25 + vector)
[fill]
[fill]
[fill]
pg_trgm
[fill]
+ Cross-encoder rerank
[fill]
[fill]
[fill]
GPU for reranker
[fill]
HyDE
[fill]
[fill]
[fill]
Extra LLM call
[fill]
Multi-Query
[fill]
[fill]
[fill]
3x LLM calls
[fill]
Contextual Retrieval
[fill]
[fill]
[fill]
Preprocessing LLM
[fill]

Week 1 Exit Criteria (ALL must be met before starting Week 2):
    1. Working end-to-end RAG pipeline with pgvector and metadata filtering
    2. 3+ embedding models compared with visual evidence (UMAP)
    3. 5+ chunking strategies compared with retrieval quality data
    4. 5 documented failure experiments with root cause analysis
    5. Hybrid search + reranking implemented and benchmarked
    6. 6–7 retrieval strategies compared on same query set (table above filled)
    7. All code in Git with experiment logs

4. Week 2: Domain RAG → Agentic RAG → Evaluation (Days 6–10)
Day 6 (Monday): Domain-Specific Chunkers for AI-PMS
Stop using generic chunkers. Build document-type-specific parsers for AI-PMS entities:
Document Type
Chunking Logic
Metadata Extracted
Assigned To
FIDIC Contract
Hierarchical: Clause → Sub-clause. Preserve numbering. Parent-child linkage.
contract_standard, clause_number, section_title
Student A
NCR
Form-field extraction. Root cause + corrective action as separate retrievable chunks.
ncr_number, severity, root_cause_category, status
Student B
DPR
Section-based: separate progress narrative from tables. Tables → structured, not chunked.
date, package_id, activities_referenced
Student C
Correspondence
Full letter as chunk (most < 512 tokens). If longer, split by paragraph.
sender, receiver, date, notice_type, reference_number
Chowdappa

Re-ingest the synthetic corpus with new chunkers. Re-run the 50-query evaluation. Compare against Day 2 naive chunking baseline.
Day 6 Exit: 4 document-type-specific chunkers. Re-evaluation showing improvement over generic chunking. Git committed.
Day 7 (Tuesday): GraphRAG + Query Routing
Morning (4 hrs): GraphRAG on Metro Rail Systems Taxonomy
    • Load the 383-entry Metro Rail Systems Taxonomy into Apache AGE as a knowledge graph
    • Create nodes for systems, subsystems, components. Edges for interface relationships (195 interfaces).
    • Write 10 queries that NEED graph traversal (cross-subsystem dependencies, interface impact analysis)
    • Write 10 queries that do NOT need graph (factoid lookup, semantic search)
    • Show: graph queries answered correctly by GraphRAG but FAILED by vector search; and vice versa.
Afternoon (4 hrs): Query Router
Not every query should go to vector search. Build a router that selects the right strategy:
Query Pattern
Route To
Example
Quantitative / aggregation
SQL query on PostgreSQL
‘What is the CPI for Package CC-07?’
Relationship / dependency
Apache AGE graph traversal
‘Which signalling activities depend on civil works in CC-07?’
Semantic / conceptual
Hybrid vector search + reranking
‘Find NCRs similar to concrete honeycombing’
Legal / contract clause
Hybrid search + metadata filter (entity_type=contract_clause)
‘What is the time-bar period for delay claims?’
Multi-hop / complex
Agentic RAG (Day 8)
‘Is the contractor at risk of a time-bar miss on CC-07?’

Implement the router as a simple LLM-based classifier using Llama 3.1 with a system prompt that classifies the query intent.
🚨 PITFALL: Overbuilding GraphRAG
If only 15% of queries need graph traversal, do not spend 50% of your engineering time on it. The graph should COMPLEMENT vector search, not replace it. Prove the need with data before building more infrastructure.
Day 7 Exit: GraphRAG prototype on Systems Taxonomy. Query router classifying 5 query types. Git committed.
Day 8 (Wednesday): Agentic RAG with LangGraph
Morning (4 hrs): Build Agentic RAG Pipeline
Replace the single-shot retrieve-generate with an iterative agent:
    • LangGraph StateGraph with state: {query, retrieved_chunks, retrieval_history, confidence, iteration_count}
    • Nodes: query_analyzer (classifies + routes), retriever (calls appropriate tool), evaluator (checks if context is sufficient), answer_generator (produces cited answer)
    • Edges: evaluator → retriever (loop if insufficient, max 3 iterations) OR evaluator → answer_generator
    • Tools available to agent: vector_search(), sql_query(), graph_traverse(), document_fetch()
Afternoon (4 hrs): Multi-Hop Query Demonstrations
Test with these multi-hop queries that require iterative retrieval:
Query
Expected Retrieval Steps
‘Is the contractor at risk of a time-bar miss on CC-07?’
Step 1: Retrieve notices for CC-07 (metadata filter). Step 2: Retrieve FIDIC time-bar clauses (contract_standard filter). Step 3: Compare dates. Step 4: Generate risk assessment.
‘What NCRs are linked to critical path activities?’
Step 1: SQL query for critical path activities. Step 2: Metadata-filtered search for NCRs linked to those activities. Step 3: Vector search for NCR context.
‘Compare civil works progress across all packages this month’
Step 1: SQL query for latest DPR per package. Step 2: Retrieve DPR narrative chunks per package. Step 3: Generate comparison.

Key observation: Log the full retrieval trace for each query. Can you explain WHY the agent chose each step? If the agent’s reasoning is opaque, the HITL approval step becomes meaningless.
Day 8 Exit: LangGraph agentic RAG with multi-hop retrieval. 3+ multi-hop queries demonstrated with full trace. Git committed.
Day 9 (Thursday): Evaluation + Hardening
Morning (4 hrs): Build Evaluation Pipeline
    • Expand query set to 80+ queries: 20% factoid, 20% multi-hop, 20% adversarial/out-of-scope, 20% contract-legal, 20% metadata-dependent
    • Set up RAGAS evaluation: faithfulness, answer_relevancy, context_precision, context_recall
    • Run RAGAS across the full query set using Llama 3.1 as the evaluation LLM
    • Log all results to MLflow for experiment tracking
Target metrics: Faithfulness > 0.85 on contract queries. Context Precision > 0.75 after reranking. If not met, identify which query category is failing and why.
Afternoon (4 hrs): Production Hardening Essentials
Requirement
Implementation
Tenant isolation
PostgreSQL RLS on vector table. Test: query as Metro tenant, verify zero IR/DFCC chunks returned.
Fallback behavior
When retrieval confidence < threshold, return ‘Insufficient data to answer this query’ instead of hallucinating. Test with 10 out-of-scope queries.
Citation chain
Every answer includes: source chunk IDs, source document IDs, retrieval scores. Traceable back to CDM entities.
Idempotent ingestion
Re-ingesting same document must not create duplicate chunks. Use content hash for deduplication.
Latency compliance
End-to-end < 5 seconds (p95) per NFR-04. Measure on GPREC hardware. Log breakdown: retrieval, reranking, generation.
Audit logging
Log every query: input, retrieved chunks, reranking scores, final answer, timestamp. For CDM Layer 4 AuditEvent.

Day 9 Exit: RAGAS evaluation running. Per-category metrics documented. Hardening checklist items implemented. Git committed.
Day 10 (Friday): Integration Demo + Architecture Decision Document
Morning (4 hrs): End-to-End Demo Build
Build a simple FastAPI service that wraps the entire RAG pipeline into a queryable API:
    • POST /query → {query, tenant_id, entity_type_filter (optional)} → {answer, citations, confidence, retrieval_trace}
    • Demo 10 diverse queries live: factoid, multi-hop, contract, adversarial, cross-entity
    • Show the audit log for each query
Afternoon (3 hrs): Architecture Decision Document
The team produces a 3–5 page document with evidence-based recommendations:
    1. Best embedding model for AI-PMS (with data)
    2. Recommended chunking strategy per document type (with comparison data)
    3. Retrieval strategy recommendation: hybrid search + reranking as default, with query router for SQL/graph
    4. GraphRAG: use cases that justify it, use cases that do not
    5. Latency budget breakdown that meets NFR-04
    6. Open questions and deferred items (what needs real data, what needs more time)

5. Student Assignment Matrix
Each student gets a clear track. Tracks run in parallel. Chowdappa supervises and handles the highest-complexity items.
Person
Track
Week 1 Deliverables
Week 2 Deliverables
Chowdappa
Architecture + Agent RAG
Naive pipeline, breaking experiments, overall design decisions
Agentic RAG with LangGraph, query router, architecture decision doc
Student A
Retrieval Strategies
Hybrid search (BM25+vector+RRF), HyDE implementation, comparison metrics
Reranking benchmarks, contextual retrieval, strategy comparison table
Student B
Evaluation Pipeline
Manual evaluation framework, 50-query test set creation, baseline metrics
RAGAS integration, MLflow tracking, expand to 80+ queries, per-category analysis
Student C
Document Parsers
Chunking experiments (all 5 strategies), FIDIC contract parser, NCR parser
DPR parser, correspondence parser, metadata schema enforcement, ingestion pipeline
Student D
Infrastructure + GraphRAG
pgvector + pg_trgm setup, embedding model comparison, UMAP visualizations
Apache AGE + taxonomy graph, graph queries, FastAPI service wrapper, audit logging
Students E–F
Query Dataset + Testing
Write 50 test queries (10/entity type) with expected answers and manual relevance labels
Expand to 80+ queries, adversarial test cases, tenant isolation tests, demo support

5.1 Daily Rhythm (Non-Negotiable)
    • 9:00 AM — 15-min standup: What I built yesterday, what I am building today, what is blocking me
    • 1:00 PM — Midday sync: Quick experiment results sharing. Adjust priorities if something unexpected surfaces.
    • 5:00 PM — Git commit deadline: All code and experiment logs committed before end of day. No exceptions.
    • 5:30 PM — Chowdappa reviews commits, plans next day’s assignments

6. Master Pitfall Catalog
#
Pitfall
Consequence
Prevention
1
Synthetic data treated as real
Overconfident metrics. Tuned to AI-generated patterns.
Label EVERY experiment: SYNTHETIC. Never train on it.
2
One chunker for all doc types
Contract clauses split mid-sentence. NCR context lost.
Document-type-specific chunkers (Day 6).
3
No metadata filtering
Cross-tenant leakage. Cross-entity confusion.
Enforce tenant_id + entity_type on every query.
4
Evaluating only easy queries
Inflated metrics. Fails on real users.
20% adversarial, 20% multi-hop in eval set.
5
No fallback behavior
Hallucination when it should say ‘I don’t know.’
Confidence thresholds. Test with OOS queries.
6
Ignoring latency budgets
Reranking + multi-hop exceeds 5s NFR.
Measure from Day 1. Budget: 1.5s + 0.5s + 3s.
7
No citation chain
Users cannot verify answers. HITL meaningless.
Every answer: chunk IDs + document references.
8
Framework before fundamentals
LangChain/LlamaIndex hides bugs. Cannot debug.
Plain Python first (Days 1–4). Frameworks Day 5+.
9
Overbuilding GraphRAG
Complex infra for queries vector search handles.
Prove need with 10 graph-only queries first.
10
AntiGravity IDE patterns
Black-box pipelines. Zero observability.
Code-first. Every component independently testable.
11
Skipping embedding comparison
Weeks debugging retrieval caused by weak model.
Day 1 UMAP comparison. 2 hours saves days.
12
Measuring retrieval not answers
Good retrieval, terrible answers (LLM position bias).
Measure BOTH retrieval metrics AND answer quality.

7. Bootcamp Exit Criteria (End of Day 10)
ALL of the following must be demonstrable. No partial credit.
#
Criterion
Evidence
1
Working end-to-end RAG pipeline with pgvector, hybrid search, reranking, metadata filtering
Live demo + code
2
3 embedding models compared with UMAP visualization and retrieval metrics
Jupyter notebook
3
5+ chunking strategies compared with per-strategy retrieval quality data
Comparison table
4
5 documented failure experiments with root cause analysis
Written report
5
6–7 retrieval strategies compared on same query set with metrics
Filled comparison table
6
4 document-type-specific chunkers (FIDIC, NCR, DPR, Correspondence)
Code + test results
7
GraphRAG prototype on Metro Rail Systems Taxonomy
10 graph queries answered
8
Query router correctly classifying 5 query types
Test results
9
LangGraph agentic RAG with multi-hop retrieval for 3+ complex queries
Full retrieval traces
10
RAGAS evaluation on 80+ queries with per-category metrics
MLflow dashboard
11
Tenant isolation tested: zero cross-tenant leakage
Adversarial test results
12
FastAPI service wrapping full pipeline with audit logging
Live API demo
13
Architecture Decision Document with evidence-based recommendations
3–5 page doc
14
15+ structured experiment logs in Git
Git repo

✅ WHAT HAPPENS AFTER THE BOOTCAMP
The 2-week bootcamp gives the team hands-on experience and evidence-based recommendations. Post-bootcamp, the deferred items kick in: production hardening, 200+ golden eval dataset, CI/CD, monitoring, and — most critically — re-evaluation on real STAMP data once DMRC engagement begins. The bootcamp output directly feeds into the AI-PMS pre-pilot work streams.

End of Document