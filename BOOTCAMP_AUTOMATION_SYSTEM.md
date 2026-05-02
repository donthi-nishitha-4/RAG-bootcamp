# 🤖 BOOTCAMP DELIVERABLES AUTO-UPDATE SYSTEM v1.0
## Role-Based Prompts + Automatic Document Management
**For: AI-PMS DMRC RAG Bootcamp (2-Week Intensive)**

---

## 📋 SYSTEM OVERVIEW

**Three Roles:**
1. **Balu (Lead)** — Architecture decisions, final sign-offs
2. **Antigravity (Dev)** — Experimental results, latency benchmarks, code proofs
3. **[TO FILL] (Support)** — Security testing, adversarial cases, hallucination checks

**How it works:**
- Each person fills their role-specific template below
- They provide: **VALUE | CONTRIBUTOR | DATE | PROOF FILE | REASON**
- Claude agent automatically updates DELIVERABLES.md
- Audit trail preserved forever
- No deletions, no overwrites, only [TO FILL] replacements

---

# 🎯 ROLE TEMPLATES & RULES

## RULE SET #1: UNIVERSAL RULES (ALL ROLES)

```
✅ DO:
  • Fill [TO FILL] fields ONLY with verified, measured data
  • Always cite proof files (experiments/, src/, scripts/)
  • Include contributor name + date + brief reasoning
  • Format: VALUE (Contributor | YYYY-MM-DD | Proof: path/to/file)
  • If unsure, ask — don't guess
  • Keep values factual, measurable, traceable

❌ DON'T:
  • Delete or move template sections
  • Edit already-filled fields (mark as "REVISED" instead)
  • Leave [TO FILL] when you have data
  • Cite sources without line numbers or function names
  • Make up metrics — always run experiments
  • Change document structure
  • Remove audit log entries
```

---

## ROLE #1: BALU (TEAM LEAD) — Architecture & Decisions

### YOUR MISSION
- Make architecture decisions based on team's experimental evidence
- Fill D1 (Architecture), D11 (Final Recommendations)
- Sign off on embedding model, retrieval strategy, deployment decisions
- Keep audit trail of *why* each choice was made

### TEMPLATE: BALU'S DECISION SUBMISSION

```
# BALU'S ARCHITECTURE DECISION REPORT
Date: YYYY-MM-DD
Contributor: K. Bala Chowdappa (GPREC)

## DECISION: [Decision Name]
Example: "Primary Vector Store Selection"

**Options Evaluated:**
- pgvector
- ChromaDB
- FAISS
- Weaviate

**Decision & Rationale:**
[CHOSEN OPTION]: **[NAME]**
Reason: [2-3 sentences explaining why this wins]

**Evidence (Experiments):**
- EXP-XXX: [Metric that supports this]
- EXP-YYY: [Another supporting metric]

**Proof Files:**
- docker-compose.yml (setup verification)
- src/retriever.py:retrieve_hybrid() (implementation)
- experiments/exp_XX_vector_comparison.json (metrics)

**Trade-offs & Risks:**
[What are we sacrificing? What could fail in production?]

**Production Implication for AI-PMS:**
[How does this affect DMRC's system?]

---

## AUTO-UPDATE INSTRUCTIONS FOR CLAUDE:

```yaml
updates:
  - section: "D1.1"
    field: "Primary Vector Store"
    value: "[CHOSEN OPTION]"
    contributor: "K. Bala Chowdappa"
    date: "YYYY-MM-DD"
    reasoning: "[2-3 word reason: e.g., WSL Portability, Hybrid Support, etc.]"
    proof: "docker-compose.yml, src/retriever.py:line_XX"
  
  - section: "D1.1"
    field: "Rationale"
    value: "[Full rationale text]"
    contributor: "K. Bala Chowdappa"
    date: "YYYY-MM-DD"
    reasoning: "Decision justified by experimental evidence"
    proof: "experiments/exp_XX_XXX.json"
```

---
```

### BALU'S CHECKLIST
- [ ] I have reviewed all relevant experiments (EXP-01 through EXP-15)
- [ ] I can cite specific metrics supporting this decision
- [ ] I understand the trade-offs and have documented them
- [ ] This decision aligns with DMRC's NFRs (5s latency, 0% tenant leakage, etc.)
- [ ] Proof files are committed to Git and referenced with line numbers

---

## ROLE #2: ANTIGRAVITY (DEV/EXPERIMENTS) — Metrics & Implementation

### YOUR MISSION
- Run experiments: embedding comparisons, chunking, retrieval strategies, latency benchmarks
- Measure everything: P@5, P@10, MRR, NDCG, latency (p50/p95/p99), faithfulness, hallucination rate
- Prove your code with function signatures and file paths
- Document failures as thoroughly as successes

### TEMPLATE: ANTIGRAVITY'S EXPERIMENT SUBMISSION

```
# ANTIGRAVITY'S EXPERIMENT REPORT
Date: YYYY-MM-DD
Experimenter: Antigravity
Experiment ID: EXP-###

## HYPOTHESIS
"[What I expected to happen]"
Example: "Hybrid search (BM25 + Vector) outperforms pure vector search on contract clauses"

## STRATEGY / CONFIG
[What you actually tested]
Example:
- Retrieval: BM25 (pg_trgm) + pgvector + RRF fusion
- Top-K: 5 documents
- Reranking: None
- LLM: Llama 3.1 (Groq API)
- Dataset: 500 synthetic DMRC contracts + 200 NCRs

## DATASET USED
- Size: [number of docs/chunks]
- Type: [contracts, NCRs, DPRs, correspondence, etc.]
- Location: data/synthetic_dmrc_v1/
- Sampling: [random, stratified, adversarial, etc.]

## RESULTS - RETRIEVAL METRICS

| Metric | Value | Proof File | Line # |
|--------|-------|-----------|--------|
| P@5    | X.XX  | experiments/exp_XX_results.json | L:45 |
| P@10   | X.XX  | experiments/exp_XX_results.json | L:46 |
| MRR    | X.XX  | experiments/exp_XX_results.json | L:47 |
| NDCG@10| X.XX  | experiments/exp_XX_results.json | L:48 |

## RESULTS - ANSWER QUALITY METRICS

| Metric | Value | Proof File | Function |
|--------|-------|-----------|----------|
| Faithfulness | X.XX | experiments/ragas_eval_XX.py | ragas.evaluate() L:120 |
| Answer Relevancy | X.XX | experiments/ragas_eval_XX.py | ragas.evaluate() L:125 |
| Context Precision | X.XX | experiments/ragas_eval_XX.py | ragas.evaluate() L:130 |
| Context Recall | X.XX | experiments/ragas_eval_XX.py | ragas.evaluate() L:135 |

## RESULTS - LATENCY (milliseconds)

| Component | p50 (ms) | p95 (ms) | p99 (ms) | Proof File | Query Count |
|-----------|----------|----------|----------|-----------|-------------|
| Metadata Filtering | XX | XX | XX | experiments/latency_XX.json | 1000 |
| Vector Search (pgvector) | XX | XX | XX | experiments/latency_XX.json | 1000 |
| BM25 Search (pg_trgm) | XX | XX | XX | experiments/latency_XX.json | 1000 |
| RRF Fusion | XX | XX | XX | experiments/latency_XX.json | 1000 |
| LLM Generation | XX | XX | XX | experiments/latency_XX.json | 1000 |
| TOTAL END-TO-END | XX | XX | XX | experiments/latency_XX.json | 1000 |

## WHAT ACTUALLY HAPPENED
[Did it match your hypothesis? What surprised you?]

## ROOT CAUSE ANALYSIS
[Why did it happen this way? What does the data show?]

## CODE PROOF REFERENCES
```python
# Vector search implementation
File: src/retriever.py
Function: retrieve_hybrid()
Lines: 45-78

# Retrieval metrics calculation
File: experiments/eval_baseline.py
Function: calculate_p_at_k()
Lines: 120-145

# Latency profiling
File: scripts/benchmark_latency.py
Function: profile_components()
Lines: 200-250
```

## SURPRISING FINDINGS
[What was unexpected? What could be optimized?]

## PRODUCTION IMPLICATION
[How does this affect the final AI-PMS system?]

---

## AUTO-UPDATE INSTRUCTIONS FOR CLAUDE:

```yaml
updates:
  - section: "D2.1"
    field: "Embedding Latency (p95) — MiniLM L6-v2"
    value: "12ms"
    contributor: "Antigravity"
    date: "YYYY-MM-DD"
    reasoning: "CPU-optimized model on synthetic 1000-chunk dataset"
    proof: "experiments/exp_01_embeddings.json:L45, scripts/compare_embeddings.py:L89"
  
  - section: "D2.1"
    field: "Index Size (1000 chunks) — MiniLM L6-v2"
    value: "~2.1 MB"
    contributor: "Antigravity"
    date: "YYYY-MM-DD"
    reasoning: "384-dim embeddings with pgvector GiST index"
    proof: "experiments/exp_01_embeddings.json:L12, src/index_builder.py:L234"
  
  - section: "D8.1"
    field: "p95 (ms) — Vector Search (pgvector)"
    value: "245ms"
    contributor: "Antigravity"
    date: "YYYY-MM-DD"
    reasoning: "GiST index on 50K chunks, top-5 retrieval"
    proof: "experiments/latency_benchmark_XX.json:L67, scripts/benchmark_latency.py:L210"
  
  - section: "D7.1"
    field: "Faithfulness — Day 10 Final"
    value: "0.92"
    contributor: "Antigravity"
    date: "YYYY-MM-DD"
    reasoning: "Hybrid retrieval + Llama 3.1 on synthetic contracts"
    proof: "experiments/ragas_eval_exp_XX.py:L120, results/ragas_final_metrics.json"

  - section: "D10"
    field: "Experiment EXP-### — Hypothesis"
    value: "[Your hypothesis exactly]"
    contributor: "Antigravity"
    date: "YYYY-MM-DD"
    reasoning: "Experimental justification"
    proof: "experiments/exp_XX_XXXXX.json"
```

---
```

### ANTIGRAVITY'S CHECKLIST
- [ ] All metrics come from actual experimental runs (not estimates)
- [ ] Each metric has a proof file with line number reference
- [ ] Code implementation cited with function name + line range
- [ ] Latency measured over at least 100+ queries (statistical validity)
- [ ] Dataset composition documented (size, type, source)
- [ ] Surprising findings explained with root cause analysis
- [ ] Production implications are specific to AI-PMS use case
- [ ] All files committed to Git repo

---

## ROLE #3: [SUPPORT TEAM] (SECURITY/TESTING) — Validation & Edge Cases

### YOUR MISSION
- Test failure modes, adversarial cases, security (D4, D9)
- Run out-of-scope queries and document hallucinations
- Test cross-tenant isolation, data leakage scenarios
- Run RAGAS on edge cases (legal terms, complex multi-hop, etc.)

### TEMPLATE: SECURITY/TEST SUBMISSION

```
# [SUPPORT TEAM] VALIDATION REPORT
Date: YYYY-MM-DD
Tester: [Name]
Test ID: TEST-### or FE-### (for failures)

## TEST PURPOSE
[What are we validating? Which NFR or risk does this address?]

## TEST SCENARIO
[Detailed setup: queries, data, conditions]

## TEST EXECUTION
- Tools Used: [RAGAS, custom script, manual review, etc.]
- Sample Size: [number of queries/cases]
- Environment: [Dev, staging, synthetic data]

## RESULTS

| Test Case | Input | Expected Output | Actual Output | Pass/Fail | Notes |
|-----------|-------|-----------------|---------------|-----------|-------|
| [Name] | [Query] | [Expected] | [Actual] | [Y/N] | [Why?] |

## FAILURE ANALYSIS (if applicable)
- Root Cause: [Why did it fail?]
- Severity: [Critical / High / Medium / Low]
- Fix Applied: [What changed to fix it?]
- Result After Fix: [Did it work?]

## CODE PROOF
File: [path]
Function: [name]
Lines: [range]

---

## AUTO-UPDATE INSTRUCTIONS FOR CLAUDE:

```yaml
updates:
  - section: "D4"
    field: "FE-01: Cross-Entity Confusion — Query Used"
    value: "[Your test query]"
    contributor: "[Name]"
    date: "YYYY-MM-DD"
    reasoning: "Adversarial test for vector space confusion"
    proof: "experiments/failure_tests_cross_entity.json:L12"
  
  - section: "D4"
    field: "FE-01: Cross-Entity Confusion — Failure Mode Observed"
    value: "[What failed exactly?]"
    contributor: "[Name]"
    date: "YYYY-MM-DD"
    reasoning: "[Root cause]"
    proof: "experiments/failure_tests_cross_entity.json:L45"
  
  - section: "D9.1"
    field: "Test 1 — Chunks From Wrong Tenant"
    value: "No (PASS)"
    contributor: "[Name]"
    date: "YYYY-MM-DD"
    reasoning: "Metadata filter enforced correctly"
    proof: "experiments/tenant_isolation_test_XX.json:L34"

  - section: "D9.2"
    field: "Test 1 — Hallucinated?"
    value: "No (PASS)"
    contributor: "[Name]"
    date: "YYYY-MM-DD"
    reasoning: "System correctly refused out-of-scope query"
    proof: "experiments/hallucination_test_XX.json:L23"
```

---
```

### SECURITY/TEST CHECKLIST
- [ ] Test covers a specific NFR or known risk
- [ ] Sample size is statistically meaningful (50+ cases for security)
- [ ] All edge cases documented (what fails, why)
- [ ] Root causes analyzed, not just symptoms
- [ ] Fixes verified with re-runs
- [ ] Proof files include exact line numbers/function names
- [ ] Tests are reproducible (can other people run them?)

---

# 🚀 HOW TO USE THIS SYSTEM (STEP-BY-STEP)

## WORKFLOW: You → Template → Claude → Auto-Updated Doc

### Step 1: You Do Your Work
```
Balu:
  • Reviews team's experiments
  • Decides on embedding model (e.g., "bge-large-en-v1.5")
  • Documents why (metrics from EXP-01, EXP-02)

Antigravity:
  • Runs experiment: Embedding comparison
  • Measures: P@5, latency, index size, etc.
  • Saves results to experiments/exp_01_embeddings.json

Support Team:
  • Tests: Cross-tenant isolation
  • Runs 50 adversarial queries
  • Documents pass/fail for each
```

### Step 2: Fill Your Template
```
Copy the template above for your role.
Fill in ALL fields with measured data.
Include proof file paths + line numbers.
```

### Step 3: Send to Claude (COPY-PASTE BELOW)

---

## 📌 **MASTER CLAUDE AUTO-UPDATE PROMPT** ⭐

```
[START PROMPT]

# BOOTCAMP DELIVERABLES AUTO-UPDATE REQUEST

You are Claude, serving as the automation agent for the DMRC AI-PMS RAG Bootcamp.

## YOUR INSTRUCTIONS (MANDATORY)

1. **VALIDATION**: Check each update below against the UNIVERSAL RULES
2. **MERGING**: Apply only valid updates to the DELIVERABLES document
3. **PRESERVATION**: DO NOT delete, move, or reformat any template sections
4. **AUDIT TRAIL**: Every change must follow format: VALUE (Contributor | Date | Reasoning | Proof)
5. **VERSION BUMP**: Increment Document Version and timestamp
6. **OUTPUT**: Return updated DELIVERABLES + summary of changes

## ROLE SUBMITTING
[Pick one: BALU (Architecture) | ANTIGRAVITY (Experiments) | [SUPPORT] (Testing)]

## CONTRIBUTOR INFO
**Name**: [Full Name]
**Date**: [YYYY-MM-DD]
**Role**: [Role]
**Team**: DMRC AI-PMS RAG Bootcamp

---

## UPDATES TO APPLY (YAML FORMAT)

```yaml
updates:
  - section: "D1.1"
    field: "[Exact field name from template]"
    value: "[Measured value or text]"
    contributor: "[Your name]"
    date: "[YYYY-MM-DD]"
    reasoning: "[2-3 words: e.g., 'Hybrid search superiority', 'CPU optimization', 'Security validation']"
    proof: "[File path:line_number, e.g., experiments/exp_01.json:L45, src/retriever.py:L78]"
  
  - section: "D2.1"
    field: "[Another field]"
    value: "[Value]"
    contributor: "[Your name]"
    date: "[YYYY-MM-DD]"
    reasoning: "[Why this value matters]"
    proof: "[Proof reference]"

[ADD MORE UPDATE BLOCKS AS NEEDED]
```

---

## REFERENCE DOCUMENT

[PASTE THE ENTIRE CURRENT DELIVERABLES.md DOCUMENT HERE]

---

## YOUR TASK

1. Parse each update above
2. For each update:
   - Validate field exists in document
   - Validate target is [TO FILL] (not already filled)
   - Format value as: VALUE (Contributor | Date | Reasoning | Proof)
   - Replace ONLY the [TO FILL] placeholder
3. Bump Document Version
4. Update SR. DEV AUDIT LOG table with entries
5. Return:
   - ✅ UPDATED DELIVERABLES.md (full document)
   - ✅ CHANGE SUMMARY (what was updated, section by section)
   - ✅ REMAINING [TO FILL] FIELDS (list of still-empty fields)
   - ✅ VALIDATION REPORT (any rejected updates + reasons)

---

## RULES CLAUDE MUST FOLLOW

✅ ONLY replace [TO FILL] placeholders
✅ Preserve all template structure (sections, headers, tables)
✅ Maintain exact formatting (markdown, tables, spacing)
✅ Include contributor + date + reasoning in every value
✅ Cite proof files with line numbers or function names
✅ NO creative rewording — use submitted text exactly
✅ Update audit log with each change
✅ Increment version number

❌ DO NOT delete sections
❌ DO NOT move template sections around
❌ DO NOT edit already-filled fields (note as "REVISION" instead)
❌ DO NOT merge or summarize proof files
❌ DO NOT assume context — only use what's explicitly provided

---

[END PROMPT]
```

---

### Step 4: Claude Returns Updated Document

Claude will output:
```
✅ DELIVERABLES_v1.1_UPDATED.md
✅ CHANGE SUMMARY
✅ REMAINING [TO FILL] FIELDS (16 remaining)
✅ VALIDATION REPORT (All 5 updates applied successfully)
```

### Step 5: You Review & Commit

```bash
# Review the changes
cat DELIVERABLES_v1.1_UPDATED.md

# If good, commit
git add DELIVERABLES.md experiments/
git commit -m "Day X: [Name] updates — D2.1 embedding metrics, D8.1 latency, etc."
git push
```

---

# 📊 EXAMPLE: ANTIGRAVITY'S SUBMISSION (FILLED)

```
# ANTIGRAVITY'S EXPERIMENT REPORT
Date: 2026-05-03
Experimenter: Antigravity
Experiment ID: EXP-001

## HYPOTHESIS
"Hybrid search (BM25 + Vector + RRF) outperforms pure vector search on legal contracts"

## STRATEGY / CONFIG
- Retrieval: BM25 (pg_trgm) + pgvector + RRF fusion
- Top-K: 5 documents
- Reranking: None
- LLM: Llama 3.1 (Groq API)
- Dataset: 500 synthetic DMRC contracts

## RESULTS - RETRIEVAL METRICS

| Metric | Value | Proof File |
|--------|-------|-----------|
| P@5    | 0.89  | experiments/exp_001_hybrid_vs_vector.json:L45 |
| P@10   | 0.92  | experiments/exp_001_hybrid_vs_vector.json:L46 |
| MRR    | 0.85  | experiments/exp_001_hybrid_vs_vector.json:L47 |

---

## AUTO-UPDATE INSTRUCTIONS FOR CLAUDE:

```yaml
updates:
  - section: "D2.1"
    field: "Contract Clause P@5 — bge-large-en-v1.5"
    value: "0.91"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Semantic depth on legal terminology"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L45"
  
  - section: "D5.3"
    field: "Hybrid (BM25+Vec+RRF) — P@5"
    value: "0.89"
    contributor: "Antigravity"
    date: "2026-05-03"
    reasoning: "Excellent precision on contract clauses"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L50"
```
```

---

# 📋 SUMMARY TABLE: WHO FILLS WHAT

| Role | Primary Sections | Key Responsibilities | Proof Sources |
|------|------------------|----------------------|---------------|
| **Balu** | D1, D11 | Architecture decisions, final recommendations | Experiment IDs, design docs, docker-compose.yml |
| **Antigravity** | D2, D3, D5, D7, D8, D10 | Metrics, latency, experiment logs | experiments/, scripts/, src/ with line numbers |
| **[Support]** | D4, D6, D9, D10 | Failure modes, security, testing, multi-hop | Test logs, adversarial queries, RAGAS output |

---

# 🎓 TIPS FOR SUCCESS

1. **Run experiments FIRST, then fill templates** — Don't guess
2. **Always cite proof files** — No metrics without evidence
3. **Use exact field names** — Copy-paste from template to avoid mismatches
4. **Include line numbers** — "experiments/file.json" is not enough; "experiments/file.json:L45" is
5. **Be specific in reasoning** — "Hybrid search superiority" not just "Good"
6. **Document failures thoroughly** — Root cause analysis is valuable
7. **Commit to Git after each update** — Keep history clean
8. **Review audit log** — Make sure all entries are accurate

---

**END OF BOOTCAMP AUTOMATION SYSTEM**

Last Updated: 2026-05-02
Version: 1.0 
