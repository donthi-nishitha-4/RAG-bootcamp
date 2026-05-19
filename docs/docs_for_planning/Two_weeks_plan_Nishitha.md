# Enterprise RAG Bootcamp

## 2-Week Intensive Implementation Plan
### 100% Open Source Stack | AI-PMS Context

#### For: K. Bala Chowdappa & NLP Team, GPREC

Project: AI-PMS | Client: DMRC | March 2026 | v1.0
CONFIDENTIAL     - Kernex Microsystems / TELInternal


Kernex Microsystems / TEL — Confidential | Page


## 1. Reality Check: What 2 Weeks Can and Cannot Do

Two weeks is an intense bootcamp, not a mastery program. Here is what is achievable and what is not:






|Achievable in 2 Weeks|NOT Achievable — Deferred|
|---|---|
|Working end-to-end RAG pipeline on pgvector<br>3–4 retrieval strategies tested head-to-head<br>Domain-specific<br>chunkers<br>for<br>3–4<br>AI-PMS<br>document types<br>Hybrid search (BM25 + vector + RRF)<br>Cross-encoder reranking benchmarked<br>Basic agentic RAG with LangGraph<br>Manual evaluation on 50+ queries<br>GraphRAG<br>proof-of-concept<br>on<br>Systems<br>Taxonomy<br>Clear evidence-based strategy recommendations|Production-hardened deployment<br>200+ query golden evaluation dataset<br>Full RAGAS automated evaluation suite<br>Fine-tuned domain embeddings<br>Complete multi-agent integration<br>Load testing at scale<br>Monitoring and alerting infrastructure<br>CI/CD pipeline for RAG components|



CRITICAL: Synthetic Data Reminder
The DMRC Mega Metro dataset is AI-generated. Valid ONLY for pipeline testing, UI development, and
pipeline validation. NOT for ML model training, rule calibration, or threshold validation. Label every
experiment clearly: SYNTHETIC DATA.


## 2. Complete Open Source Tech Stack

Every single tool in this plan is open source and free. Zero API costs. Zero licensing concerns. Fully
deployable on GPREC HPC on-prem.







































|Layer|Tool|License|Install|
|---|---|---|---|
|Vector<br>Store<br>(Primary)|PostgreSQL + pgvector|PostgreSQL<br>License<br>+<br>Apache 2.0|apt install postgresql;<br>CREATE<br>EXTENSION<br>vector;|
|Vector<br>Store<br>(Dev/Rapid)|ChromaDB|Apache 2.0|pip install chromadb|
|Vector<br>Store<br>(Benchmark)|FAISS (Meta)|MIT|pip install faiss-cpu (or<br>faiss-gpu)|
|Graph Store|Apache AGE (PostgreSQL extension)|Apache 2.0|Build from source or<br>apt;<br>CREATE<br>EXTENSION age;|
|Sparse<br>Search<br>(BM25)|PostgreSQL pg_trgm + tsvector (built-in)|PostgreSQL<br>License|CREATE<br>EXTENSION<br>pg_trgm;<br>(already<br>in<br>PostgreSQL)|
|Embedding<br>Model A|sentence-transformers/all-MiniLM-L6-v2<br>(384-dim)|Apache 2.0|pip<br>install<br>sentence-transformers|
|Embedding<br>Model B|BAAI/bge-large-en-v1.5 (1024-dim)|MIT|HuggingFace<br>download, ~1.3 GB|
|Embedding<br>Model C|nomic-ai/nomic-embed-text-v1.5<br>(768-dim)|Apache 2.0|HuggingFace<br>download, ~550 MB|
|Reranker A|cross-encoder/ms-marco-MiniLM-L-12-v2|Apache 2.0|pip<br>install<br>sentence-transformers|
|Reranker B|BAAI/bge-reranker-v2-m3|MIT|HuggingFace<br>download, ~1.1 GB|
|LLM<br>(Primary)|Meta Llama 3.1 8B Instruct (via vLLM)|Llama<br>3.1<br>Community<br>License|pip<br>install<br>vllm;<br>download<br>from<br>HuggingFace|
|LLM<br>(Lightweight)|Microsoft Phi-3-mini-4k-instruct (3.8B)|MIT|HuggingFace,<br>~7.6<br>GB.<br>Fits<br>on<br>smaller<br>GPUs.|
|LLM<br>(Alternative)|Mistral 7B Instruct v0.3|Apache 2.0|HuggingFace<br>download|
|LLM Serving|vLLM|Apache 2.0|pip install vllm. Serves<br>OpenAI-compatible<br>API.|
|Orchestration|LangGraph + LangChain|MIT|pip<br>install<br>langgraph|


Kernex Microsystems / TEL — Confidential | Page


|Col1|Col2|Col3|langchain|
|---|---|---|---|
|Orchestration<br>(Alt)|LlamaIndex|MIT|pip install llama-index|
|Evaluation|RAGAS|Apache 2.0|pip install ragas|
|Experiment<br>Tracking|MLflow|Apache 2.0|pip install mlflow|
|Visualization|UMAP + Matplotlib|BSD-3 + PSF|pip install umap-learn<br>matplotlib|
|Document<br>Parsing|Unstructured.io|Apache 2.0|pip install unstructured|
|PDF Parsing|PyMuPDF (fitz) + pdfplumber|AGPL-3.0<br>+<br>MIT|pip<br>install<br>pymupdf<br>pdfplumber|
|Notebook|Jupyter Lab|BSD-3|pip install jupyterlab|


LICENSING NOTE: PyMuPDF
PyMuPDF uses AGPL-3.0 which has copyleft implications if distributed. Fine for internal development
and research. For production AI-PMS, evaluate whether pdfplumber (MIT) alone is sufficient, or budget
for a commercial MuPDF license if needed.


## 3. Week 1: Foundations → Naive RAG → Break It (Days 1–5)

### Day 1 (Monday): Environment Setup + Embedding Fundamentals

#### Morning (4 hrs): Infrastructure


  - Install PostgreSQL + pgvector + pg_trgm + Apache AGE on GPREC HPC node


  - Install vLLM, load Llama 3.1 8B Instruct, verify it serves on localhost:8000


  - Install ChromaDB for rapid prototyping (students use this while pgvector is being configured)


  - Set up shared Jupyter Lab server for team. Create Git repo: aipms-rag-bootcamp


  - Install all Python packages: sentence-transformers, langchain, langgraph, llama-index, ragas, mlflow,
umap-learn, unstructured, pdfplumber

#### Afternoon (4 hrs): Embeddings From First Principles


  - Prepare test corpus: 50 synthetic FIDIC contract clauses + 30 NCR descriptions + 20 DPR
narratives from the synthetic DMRC dataset


  - Embed with all-MiniLM-L6-v2 (384d). Visualize with UMAP. Observe: Do contract clauses cluster
separately from NCRs? From DPRs?


  - Repeat with bge-large-en-v1.5 (1024d) and nomic-embed-text (768d). Side-by-side UMAP
comparison.


Record: Which model best separates metro-rail domain terms (OHE catenary, ballastless track, tunnel
boring machine) from generic text?


PITFALL: Skipping Embedding Comparison
If you pick all-MiniLM-L6-v2 because it is small and fast without comparing, you may spend weeks
debugging bad retrieval caused by a weak embedding model. This 2-hour comparison on Day 1 saves
days later.

#### Day 1 Exit: Each team member has a running notebook with 3-model UMAP comparison. Git committed.

### Day 2 (Tuesday): Chunking Experiments + Naive RAG Pipeline

#### Morning (4 hrs): Chunking Strategies


Test ALL of these on the same FIDIC chapter. Record retrieved chunk quality for 10 test queries per strategy:






|Strategy|Tool|Known Failure Mode|
|---|---|---|
|Fixed-size 512 tokens|LangChain<br>CharacterTextSplitter|Cuts mid-clause, mid-sentence. Loses<br>legal meaning.|
|Recursive character|LangChain<br>RecursiveCharacterTextSplitter|Better<br>but<br>still<br>clause-structure-unaware.|
|Semantic chunking|LlamaIndex<br>SemanticSplitterNodeParser|Good for narrative. Poor for numbered<br>legal clauses.|
|Document-structure-aware|Custom parser: split on clause<br>headings (20.1, 20.1.1)|Best for contracts. Cannot generalize to<br>DPRs/NCRs.|



Kernex Microsystems / TEL — Confidential | Page


#### Afternoon (4 hrs): Build Naive RAGEnd-to-End





Build the simplest possible pipeline. NO frameworks. Plain Python only:


Documents → RecursiveCharacterTextSplitter (512, overlap=50) → Best embedding model from Day 1 →
pgvector → Top-K retrieval (K=5) → Llama 3.1 8B (via vLLM) → Answer


  - Load 200+ synthetic chunks covering contract clauses, NCRs, DPRs, correspondence


  - Write 20 test queries by hand (5 per entity type). Run each. Record: query, retrieved chunks,
answer, your human judgment of quality (1–5 scale)

Record: Baseline Precision@5 and subjective answer quality. This is the number you will beat.

#### Day 2 Exit: Working naiveRAG pipeline. Chunking comparison table. Baseline metrics on 20 queries. Git committed.

### Day 3 (Wednesday): Break the Naive Pipeline + Metadata Filtering

#### Morning (4 hrs): The Breaking Experiments


Run each of these experiments. Document what goes wrong. This builds the intuition that no tutorial can give
you.











|Experiment|What To Do|Expected Failure & Lesson|
|---|---|---|
|Cross-Entity Confusion|Mix NCRs + contract clauses in same<br>vector<br>space.<br>Query:<br>‘corrective<br>action for concrete honeycombing?’|Retriever mixes NCR fixes with legal<br>defect<br>liability<br>clauses.<br>Answer<br>blends<br>operations<br>with<br>legal<br>obligations.|
|Wrong Contract Version|Load FIDIC Red + Yellow Book. Query<br>about Yellow Book time-bar.|System retrieves Red Book clauses<br>and presents them as Yellow Book.<br>LLM will NOT say ‘I don’t know.’|
|Long<br>Document<br>Summary|Load<br>100-page<br>contract.<br>Ask<br>‘Summarize contractor obligations.’|Top-5<br>retrieval<br>covers<br>2%<br>of<br>document. ‘Summary’ is actually<br>sampling<br>bias.<br>Completely<br>misleading.|
|Adversarial Out-of-Scope|Query<br>about<br>something<br>NOT<br>in<br>corpus: ‘What is the Bitcoin price<br>forecast?’|System<br>retrieves<br>whatever<br>is<br>closest (garbage) and confidently<br>answers. No fallback behavior.|
|Tenant Leakage|Load data tagged as Metro AND<br>IR/DFCC. Query as Metro. Check if<br>IR/DFCC data appears.|Without<br>metadata<br>filtering,<br>cross-tenant data leaks freely. This<br>is a security violation.|

#### Afternoon (4 hrs): Implement Metadata Filtering



Fix the problems you just discovered. Add mandatory metadata to every chunk:


  - tenant_id (multi-tenancy isolation — enforced via PostgreSQL RLS)


  - entity_type (contract_clause | correspondence | dpr | ncr | meeting_minutes | drawing |
incident_report)


  - package_id (which contract package)


  - source_document_id (traceable back to CDM)


  - contract_standard (Red/Yellow/Silver — for contract clauses only)


  - chunk_index + parent_chunk_id (for ordering and hierarchical retrieval)


Re-run the breaking experiments WITH metadata filtering. Document the improvement.

#### Day 3 Exit: 5 failure experiments documented withroot cause analysis. Metadata-filtered retrieval working. Git committed.


Deliverable: 1-page writeup — ‘Why Naive RAG Is Not Production-Ready for AI-PMS’

### Day 4 (Thursday): Hybrid Search + Reranking

#### Morning (4 hrs): Hybrid Search (BM25 + Vector + RRF)


Pure vector search misses exact-match queries. ‘Force Majeure’ is a specific legal term — you want BM25
exact match AND semantic similarity.


  - Implement BM25 using PostgreSQL tsvector + ts_rank (zero new infrastructure)


  - Implement Reciprocal Rank Fusion (RRF): score = 1/(k + rank_bm25) + 1/(k + rank_vector), where
k=60

  - Compare on 20 queries: vector-only vs. BM25-only vs. hybrid (RRF). Record Precision@5 and MRR
for each.


Observation: On which query TYPES does BM25 win? (Expect: exact legal terms, clause numbers, proper
nouns). On which does vector win? (Expect: paraphrased questions, conceptual queries).

#### Afternoon (4 hrs): Cross-Encoder Reranking


  - Implement: Retrieve top-30 with hybrid search → Rerank with
cross-encoder/ms-marco-MiniLM-L-12-v2 → Return top-5


  - Also test: BAAI/bge-reranker-v2-m3 (multilingual, larger, potentially better for domain text)

  - Measure: Precision@5 improvement AND latency cost (p50, p95) on GPREC hardware


PITFALL: Reranking Without Latency Budget
NFR-04 requires search and retrieval within 5 seconds (p95). If reranking adds 800ms on top of 3s
retrieval + 2s generation, you are already over budget. Measure latency from Day 1. Budget: retrieval
1.5s, reranking 0.5s, generation 3s = 5s total.

#### Day 4 Exit: Hybrid search + reranking pipeline working. Quantitativecomparison: naive vs. hybrid vs. hybrid+rerank. Git committed.

### Day 5 (Friday): Advanced Retrieval Strategies + Week 1 Review

#### Morning (4 hrs): Test 3 More Strategies


Split the team. Each person/pair implements one strategy on the SAME 50-query evaluation set:


Strategy Implementation AI-PMS Use Case


Kernex Microsystems / TEL — Confidential | Page


|HyDE|LLM generates hypothetical answer<br>→ embed that → retrieve with it. Use<br>Llama 3.1 for generation.|Vague queries from non-technical site<br>engineers: ‘What should I do about the<br>delay?’|
|---|---|---|
|Multi-Query|LLM<br>rewrites<br>user<br>query<br>into<br>3<br>variations →retrieve for each →<br>union + deduplicate results.|Ambiguous<br>queries<br>where<br>user<br>terminology does not match document<br>terminology.|
|Contextual Retrieval|Prepend LLM-generated context to<br>each<br>chunk<br>BEFORE<br>embedding<br>(‘situating’<br>the<br>chunk<br>in<br>its<br>document).|DPRs and NCRs where<br>chunks lose<br>meaning without surrounding context.|

#### Afternoon (3 hrs): Week 1 Consolidated Review





Every team member presents their results. As a team, build the consolidated comparison:













|Strategy|P@5|MRR|Latency<br>p95|Extra Infra|Verdict|
|---|---|---|---|---|---|
|Naive (vector only)|[fill]|[fill]|[fill]|None|Baseline|
|+ Metadata filtering|[fill]|[fill]|[fill]|None|[fill]|
|Hybrid<br>(BM25<br>+<br>vector)|[fill]|[fill]|[fill]|pg_trgm|[fill]|
|+<br>Cross-encoder<br>rerank|[fill]|[fill]|[fill]|GPU<br>for<br>reranker|[fill]|
|HyDE|[fill]|[fill]|[fill]|Extra LLM call|[fill]|
|Multi-Query|[fill]|[fill]|[fill]|3x LLM calls|[fill]|
|Contextual Retrieval|[fill]|[fill]|[fill]|Preprocessing<br>LLM|[fill]|

#### Week 1 Exit Criteria (ALL must be met before starting Week 2):

1. Working end-to-end RAG pipeline with pgvector and metadata filtering

2. 3+ embedding models compared with visual evidence (UMAP)


3. 5+ chunking strategies compared with retrieval quality data


4. 5 documented failure experiments with root cause analysis

5. Hybrid search + reranking implemented and benchmarked


6. 6–7 retrieval strategies compared on same query set (table above filled)


7. All code in Git with experiment logs




## 4. Week 2: Domain RAG → Agentic RAG → Evaluation (Days 6– 10)

### Day 6 (Monday): Domain-Specific Chunkers for AI-PMS

Stop using generic chunkers. Build document-type-specific parsers for AI-PMS entities:








|Document Type|Chunking Logic|Metadata Extracted|Assigned To|
|---|---|---|---|
|FIDIC Contract|Hierarchical:<br>Clause<br>→<br>Sub-clause. Preserve numbering.<br>Parent-child linkage.|contract_standard,<br>clause_number,<br>section_title|Student A|
|NCR|Form-field extraction. Root cause<br>+ corrective action as separate<br>retrievable chunks.|ncr_number, severity,<br>root_cause_category,<br>status|Student B|
|DPR|Section-based: separate progress<br>narrative from tables. Tables →<br>structured, not chunked.|date,<br>package_id,<br>activities_referenced|Student C|
|Correspondence|Full letter as chunk (most < 512<br>tokens).<br>If<br>longer,<br>split<br>by<br>paragraph.|sender, receiver, date,<br>notice_type,<br>reference_number|Chowdappa|



Re-ingest the synthetic corpus with new chunkers. Re-run the 50-query evaluation. Compare against Day 2
naive chunking baseline.

#### Day 6 Exit: 4 document-type-specific chunkers. Re-evaluationshowing improvement over generic chunking. Git committed.

### Day 7 (Tuesday): GraphRAG + Query Routing

#### Morning (4 hrs): GraphRAG on Metro Rail Systems Taxonomy


  - Load the 383-entry Metro Rail Systems Taxonomy into Apache AGE as a knowledge graph


  - Create nodes for systems, subsystems, components. Edges for interface relationships (195
interfaces).


  - Write 10 queries that NEED graph traversal (cross-subsystem dependencies, interface impact
analysis)


  - Write 10 queries that do NOT need graph (factoid lookup, semantic search)


  - Show: graph queries answered correctly by GraphRAG but FAILED by vector search; and vice versa.

#### Afternoon (4 hrs): Query Router


Not every query should go to vector search. Build a router that selects the right strategy:

|Query Pattern|Route To|Example|
|---|---|---|
|Quantitative / aggregation|SQL query on PostgreSQL|‘What is the CPI for Package<br>CC-07?’|



Kernex Microsystems / TEL — Confidential | Page


|Relationship / dependency|Apache AGE graph traversal|‘Which signalling activities<br>depend on civil works in CC-07?’|
|---|---|---|
|Semantic / conceptual|Hybrid vector search + reranking|‘Find NCRs similar to concrete<br>honeycombing’|
|Legal / contract clause|Hybrid search + metadata filter<br>(entity_type=contract_clause)|‘What is the time-bar period for<br>delay claims?’|
|Multi-hop / complex|Agentic RAG (Day 8)|‘Is the contractor at risk of a<br>time-bar miss on CC-07?’|


Implement the router as a simple LLM-based classifier using Llama 3.1 with a system prompt that classifies
the query intent.


PITFALL: Overbuilding GraphRAG
If only 15% of queries need graph traversal, do not spend 50% of your engineering time on it. The graph
should COMPLEMENT vector search, not replace it. Prove the need with data before building more
infrastructure.

#### Day 7 Exit: GraphRAG prototype on Systems Taxonomy. Query router classifying 5 query types. Git committed.

### Day 8 (Wednesday): Agentic RAG with LangGraph

#### Morning (4 hrs): Build Agentic RAG Pipeline


Replace the single-shot retrieve-generate with an iterative agent:


  - LangGraph StateGraph with state: {query, retrieved_chunks, retrieval_history, confidence,
iteration_count}

  - Nodes: query_analyzer (classifies + routes), retriever (calls appropriate tool), evaluator (checks if
context is sufficient), answer_generator (produces cited answer)

  - Edges: evaluator → retriever (loop if insufficient, max 3 iterations) OR evaluator →
answer_generator


  - Tools available to agent: vector_search(), sql_query(), graph_traverse(), document_fetch()

#### Afternoon (4 hrs): Multi-Hop Query Demonstrations


Test with these multi-hop queries that require iterative retrieval:






|Query|Expected Retrieval Steps|
|---|---|
|‘Is the contractor at risk of a time-bar<br>miss on CC-07?’|Step 1: Retrieve notices for CC-07 (metadata filter). Step 2:<br>Retrieve FIDIC time-bar clauses (contract_standard filter).<br>Step 3: Compare dates. Step 4: Generate risk assessment.|
|‘What NCRs are linked to critical path<br>activities?’|Step 1: SQL query for critical path activities. Step 2:<br>Metadata-filtered search for NCRs linked to those activities.<br>Step 3: Vector search for NCR context.|
|‘Compare civil works progress across all<br>packages this month’|Step 1: SQL query for latest DPR per package. Step 2:<br>Retrieve DPR narrative chunks per package. Step 3: Generate|


comparison.


Key observation: Log the full retrieval trace for each query. Can you explain WHY the agent chose each
step? If the agent’s reasoning is opaque, the HITL approval step becomes meaningless.

#### Day 8 Exit: LangGraph agentic RAG withmulti-hop retrieval. 3+ multi-hop queries demonstrated withfull trace. Git committed.

### Day 9 (Thursday): Evaluation + Hardening

#### Morning (4 hrs): Build Evaluation Pipeline


  - Expand query set to 80+ queries: 20% factoid, 20% multi-hop, 20% adversarial/out-of-scope, 20%
contract-legal, 20% metadata-dependent


  - Set up RAGAS evaluation: faithfulness, answer_relevancy, context_precision, context_recall


  - Run RAGAS across the full query set using Llama 3.1 as the evaluation LLM


  - Log all results to MLflow for experiment tracking

Target metrics: Faithfulness > 0.85 on contract queries. Context Precision > 0.75 after reranking. If not met,
identify which query category is failing and why.

#### Afternoon (4 hrs): Production Hardening Essentials

|Requirement|Implementation|
|---|---|
|Tenant isolation|PostgreSQL RLS on vector table. Test: query as Metro tenant, verify<br>zero IR/DFCC chunks returned.|
|Fallback behavior|When retrieval confidence < threshold, return ‘Insufficient data to<br>answer this query’ instead of hallucinating. Test with 10 out-of-scope<br>queries.|
|Citation chain|Every answer includes: source chunk IDs, source document IDs,<br>retrieval scores. Traceable back to CDM entities.|
|Idempotent ingestion|Re-ingesting same document must not create duplicate chunks. Use<br>content hash for deduplication.|
|Latency compliance|End-to-end < 5 seconds (p95) per NFR-04. Measure on GPREC<br>hardware. Log breakdown: retrieval, reranking, generation.|
|Audit logging|Log every query: input, retrieved chunks, reranking scores, final<br>answer, timestamp. For CDM Layer 4 AuditEvent.|


#### Day 9 Exit: RAGAS evaluationrunning. Per-category metrics documented. Hardening checklist items implemented. Git committed.

### Day 10 (Friday): Integration Demo + Architecture Decision Document

#### Morning (4 hrs): End-to-End Demo Build


Build a simple FastAPI service that wraps the entire RAG pipeline into a queryable API:


Kernex Microsystems / TEL — Confidential | Page


  - POST /query → {query, tenant_id, entity_type_filter (optional)} → {answer, citations, confidence,
retrieval_trace}


  - Demo 10 diverse queries live: factoid, multi-hop, contract, adversarial, cross-entity


  - Show the audit log for each query

#### Afternoon (3 hrs): Architecture Decision Document


The team produces a 3–5 page document with evidence-based recommendations:


1. Best embedding model for AI-PMS (with data)


2. Recommended chunking strategy per document type (with comparison data)

3. Retrieval strategy recommendation: hybrid search + reranking as default, with query router for
SQL/graph


4. GraphRAG: use cases that justify it, use cases that do not


5. Latency budget breakdown that meets NFR-04


6. Open questions and deferred items (what needs real data, what needs more time)


## 5. Student Assignment Matrix

Each student gets a clear track. Tracks run in parallel. Chowdappa supervises and handles the
highest-complexity items.












|Person|Track|Week 1 Deliverables|Week 2 Deliverables|
|---|---|---|---|
|Chowdappa|Architecture<br>+<br>Agent RAG|Naive<br>pipeline,<br>breaking<br>experiments,<br>overall<br>design<br>decisions|Agentic RAG with LangGraph,<br>query<br>router,<br>architecture<br>decision doc|
|Student A|Retrieval<br>Strategies|Hybrid<br>search<br>(BM25+vector+RRF),<br>HyDE<br>implementation,<br>comparison<br>metrics|Reranking<br>benchmarks,<br>contextual<br>retrieval,<br>strategy<br>comparison table|
|Student B|Evaluation<br>Pipeline|Manual evaluation framework,<br>50-query<br>test<br>set<br>creation,<br>baseline metrics|RAGAS<br>integration,<br>MLflow<br>tracking, expand to 80+ queries,<br>per-category analysis|
|Student C|Document<br>Parsers|Chunking<br>experiments<br>(all<br>5<br>strategies),<br>FIDIC<br>contract<br>parser, NCR parser|DPR<br>parser,<br>correspondence<br>parser,<br>metadata<br>schema<br>enforcement, ingestion pipeline|
|Student D|Infrastructure<br>+<br>GraphRAG|pgvector<br>+<br>pg_trgm<br>setup,<br>embedding model comparison,<br>UMAP visualizations|Apache AGE + taxonomy graph,<br>graph queries, FastAPI service<br>wrapper, audit logging|
|Students E–<br>F|Query Dataset +<br>Testing|Write 50 test queries (10/entity<br>type) with expected answers<br>and manual relevance labels|Expand<br>to<br>80+<br>queries,<br>adversarial<br>test<br>cases, tenant<br>isolation tests, demo support|


### 5.1 Daily Rhythm (Non-Negotiable)


  - 9:00 AM — 15-min standup: What I built yesterday, what I am building today, what is blocking me


  - 1:00 PM — Midday sync: Quick experiment results sharing. Adjust priorities if something unexpected
surfaces.


  - 5:00 PM — Git commit deadline: All code and experiment logs committed before end of day. No
exceptions.


  - 5:30 PM — Chowdappa reviews commits, plans next day’s assignments


Kernex Microsystems / TEL — Confidential | Page


## 6. Master Pitfall Catalog




























|#|Pitfall|Consequence|Prevention|
|---|---|---|---|
|1|Synthetic data treated<br>as real|Overconfident metrics. Tuned to<br>AI-generated patterns.|Label<br>EVERY<br>experiment:<br>SYNTHETIC. Never train on it.|
|2|One chunker for all doc<br>types|Contract<br>clauses<br>split<br>mid-sentence. NCR context lost.|Document-type-specific chunkers<br>(Day 6).|
|3|No metadata filtering|Cross-tenant leakage. Cross-entity<br>confusion.|Enforce tenant_id + entity_type on<br>every query.|
|4|Evaluating<br>only<br>easy<br>queries|Inflated metrics. Fails on real users.|20% adversarial, 20% multi-hop in<br>eval set.|
|5|No fallback behavior|Hallucination when it should say ‘I<br>don’t know.’|Confidence thresholds. Test with<br>OOS queries.|
|6|Ignoring<br>latency<br>budgets|Reranking + multi-hop exceeds 5s<br>NFR.|Measure from Day 1. Budget: 1.5s<br>+ 0.5s + 3s.|
|7|No citation chain|Users cannot verify answers. HITL<br>meaningless.|Every<br>answer:<br>chunk<br>IDs<br>+<br>document references.|
|8|Framework<br>before<br>fundamentals|LangChain/LlamaIndex hides bugs.<br>Cannot debug.|Plain<br>Python<br>first<br>(Days<br>1–4).<br>Frameworks Day 5+.|
|9|Overbuilding<br>GraphRAG|Complex infra for queries vector<br>search handles.|Prove need with 10 graph-only<br>queries first.|
|10|AntiGravity<br>IDE<br>patterns|Black-box<br>pipelines.<br>Zero<br>observability.|Code-first.<br>Every<br>component<br>independently testable.|
|11|Skipping<br>embedding<br>comparison|Weeks debugging retrieval caused<br>by weak model.|Day 1 UMAP comparison. 2 hours<br>saves days.|
|12|Measuring retrieval not<br>answers|Good retrieval, terrible<br>answers<br>(LLM position bias).|Measure BOTH retrieval metrics<br>AND answer quality.|


## 7. Bootcamp Exit Criteria (End of Day 10)

ALL of the following must be demonstrable. No partial credit.








|#|Criterion|Evidence|
|---|---|---|
|1|Working end-to-end RAG pipeline with pgvector, hybrid search,<br>reranking, metadata filtering|Live demo + code|
|2|3 embedding models compared with UMAP visualization and retrieval<br>metrics|Jupyter notebook|
|3|5+ chunking strategies compared with per-strategy retrieval quality data|Comparison table|


|4|5 documented failure experiments with root cause analysis|Written report|
|---|---|---|
|5|6–7 retrieval strategies compared on same query set with metrics|Filled comparison table|
|6|4<br>document-type-specific<br>chunkers<br>(FIDIC,<br>NCR,<br>DPR,<br>Correspondence)|Code + test results|
|7|GraphRAG prototype on Metro Rail Systems Taxonomy|10<br>graph<br>queries<br>answered|
|8|Query router correctly classifying 5 query types|Test results|
|9|LangGraph agentic RAG with multi-hop retrieval for 3+ complex queries|Full retrieval traces|
|10|RAGAS evaluation on 80+ queries with per-category metrics|MLflow dashboard|
|11|Tenant isolation tested: zero cross-tenant leakage|Adversarial test results|
|12|FastAPI service wrapping full pipeline with audit logging|Live API demo|
|13|Architecture<br>Decision<br>Document<br>with<br>evidence-based<br>recommendations|3–5 page doc|
|14|15+ structured experiment logs in Git|Git repo|


WHAT HAPPENS AFTER THE BOOTCAMP

The 2-week bootcamp gives the team hands-on experience and evidence-based recommendations.
Post-bootcamp, the deferred items kick in: production hardening, 200+ golden eval dataset, CI/CD,
monitoring, and — most critically — re-evaluation on real STAMP data once DMRC engagement begins.
The bootcamp output directly feeds into the AI-PMS pre-pilot work streams.


Kernex Microsystems / TEL — Confidential | Page


