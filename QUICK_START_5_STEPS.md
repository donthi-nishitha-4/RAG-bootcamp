# ⚡ QUICK START: SUBMIT YOUR UPDATES (5 STEPS)

---

## 🎯 THE PROCESS

```
YOUR WORK → YAML → CLAUDE PROMPT → UPDATED DOC → GIT COMMIT → DONE
```

---

## 📝 STEP 1: DO YOUR WORK

### If you're Antigravity (Experiments)
```
• Run EXP-001 (embedding comparison)
• Measure metrics: P@5, latency, index size, etc.
• Save to: experiments/exp_001_embeddings.json
```

### If you're Balu (Architecture)
```
• Review all team experiments
• Make decision: e.g., "Which embedding model wins?"
• Document rationale
```

### If you're Uday/Nishitha (Testing)
```
• Run failure tests or security tests
• Record: Pass/Fail, why, root cause
• Save to: experiments/failure_test_XX.json
```

---

## 🌳 STEP 2: CREATE GIT BRANCH

```bash
# Use your name in branch
git checkout -b feature/[yourname]/[description]

# Examples:
# feature/antigravity/exp-001-embedding-comparison
# feature/balu/architecture-decisions-day-10
# feature/uday/failure-mode-testing
# feature/nishitha/tenant-isolation-validation
```

---

## 📊 STEP 3: CREATE YAML UPDATES

Copy this template, fill in YOUR data:

```yaml
branch_name: "feature/antigravity/exp-001-embedding-comparison"
date_submitted: "2026-05-03"

updates:
  - section: "D2.1"
    field: "Contract Clause P@5 — bge-large-en-v1.5"
    value: "0.91"
    reasoning: "Semantic depth on legal terminology"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L45, src/retriever.py:L65"
  
  - section: "D8.1"
    field: "p95 (ms) — Vector Search (pgvector)"
    value: "245"
    reasoning: "GiST index on 1000 chunks, top-5 retrieval"
    proof: "experiments/latency_benchmark_exp_001.json:L67, scripts/benchmark_latency.py:L210"
  
  - section: "D10"
    field: "Experiment EXP-001 — Hypothesis"
    value: "Hybrid search (BM25 + Vector + RRF) outperforms pure vector search on contract clauses"
    reasoning: "Experimental justification"
    proof: "experiments/exp_001_hybrid_vs_vector.json"
```

**Key Rules:**
- ✅ `proof` must have line number: `file.json:L45` or `src/function.py:L123`
- ✅ `value` is the actual measured number or text
- ✅ `reasoning` is 2-3 words max
- ✅ `field` must match EXACTLY what's in DELIVERABLES.md
- ❌ DON'T guess — only put metrics you actually measured

---

## 💬 STEP 4: SEND TO CLAUDE

### Option A: Full Message (Recommended)

Go to Claude chat, copy-paste this:

```
Use the MASTER_SUBMISSION_PROMPT.md file and process my submission:

**Branch Name:**
feature/antigravity/exp-001-embedding-comparison

**YAML Updates:**
```yaml
branch_name: "feature/antigravity/exp-001-embedding-comparison"
date_submitted: "2026-05-03"

updates:
  - section: "D2.1"
    field: "Contract Clause P@5 — bge-large-en-v1.5"
    value: "0.91"
    reasoning: "Semantic depth on legal terminology"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L45"
```
[PASTE ALL YOUR YAML UPDATES HERE]
```

**Current DELIVERABLES.md:**
[PASTE THE ENTIRE CURRENT DELIVERABLES.md HERE]
```

### Option B: Quick Message (If you're in a hurry)

```
Auto-update DELIVERABLES.md with these updates:

Branch: feature/antigravity/exp-001-embedding
Date: 2026-05-03

Field: "Contract Clause P@5 — bge-large-en-v1.5"
Section: D2.1
Value: "0.91"
Proof: experiments/exp_001.json:L45

[MORE UPDATES]

[PASTE DELIVERABLES.md]
```

---

## ✅ STEP 5: REVIEW & COMMIT

Claude returns:
```
✅ DELIVERABLES_v1.X_UPDATED.md
✅ CHANGE SUMMARY
✅ VALIDATION REPORT
✅ REMAINING [TO FILL] FIELDS
```

Review it. If good:

```bash
# Copy the updated document from Claude
# Save to DELIVERABLES.md in your repo

# Commit
git add DELIVERABLES.md
git commit -m "EXP-001: Embedding metrics (D2.1, D8.1, D10)"
git push origin feature/antigravity/exp-001-embedding-comparison

# Optional: Create pull request for review
# Then merge to main
```

---

# 🔥 REAL EXAMPLE: START TO FINISH

## Antigravity's Submission (Day 3)

### 1. Do Work
```
✅ Run experiment: bge-large-en-v1.5 embedding on 1000 contract chunks
✅ Measured: P@5=0.91, Latency p95=245ms, Index size=5.8MB
✅ Saved to: experiments/exp_001_hybrid_vs_vector.json
```

### 2. Create Branch
```bash
git checkout -b feature/antigravity/exp-001-embedding-comparison
```

### 3. Create YAML
```yaml
branch_name: "feature/antigravity/exp-001-embedding-comparison"
date_submitted: "2026-05-03"

updates:
  - section: "D2.1"
    field: "Index Size (1000 chunks) — bge-large-en-v1.5"
    value: "~5.8 MB"
    reasoning: "1024-dim embeddings with pgvector"
    proof: "experiments/exp_001_embeddings.json:L12, src/index_builder.py:L234"
  
  - section: "D2.1"
    field: "Embedding Latency (p95) — bge-large-en-v1.5"
    value: "45ms"
    reasoning: "GPU-accelerated model, good throughput"
    proof: "experiments/exp_001_embeddings.json:L45, scripts/compare_embeddings.py:L89"
  
  - section: "D2.1"
    field: "Contract Clause P@5 — bge-large-en-v1.5"
    value: "0.91"
    reasoning: "Semantic depth on legal terminology"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L45, src/retriever.py:L65"
  
  - section: "D5.3"
    field: "Hybrid (BM25+Vec+RRF) — P@5"
    value: "0.89"
    reasoning: "Excellent precision on contract clauses"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L50, src/retriever.py:L65"
  
  - section: "D8.1"
    field: "p95 (ms) — Vector Search (pgvector)"
    value: "245"
    reasoning: "GiST index on 1000 chunks, top-5 retrieval"
    proof: "experiments/latency_benchmark_exp_001.json:L67, scripts/benchmark_latency.py:L210"
  
  - section: "D10"
    field: "Experiment EXP-001 — Date"
    value: "2026-05-03"
    reasoning: "Completion date"
    proof: "experiments/exp_001_hybrid_vs_vector.json"
  
  - section: "D10"
    field: "Experiment EXP-001 — Experimenter"
    value: "Antigravity"
    reasoning: "Person who ran the experiment"
    proof: "experiments/exp_001_hybrid_vs_vector.json"
  
  - section: "D10"
    field: "Experiment EXP-001 — Hypothesis"
    value: "Hybrid search (BM25 + Vector + RRF) outperforms pure vector search on contract clause retrieval"
    reasoning: "Core hypothesis"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L1"
```

### 4. Send to Claude
```
[Copy MASTER_SUBMISSION_PROMPT.md text]
[Add branch name: feature/antigravity/exp-001-embedding-comparison]
[Paste YAML above]
[Paste current DELIVERABLES.md]
[Send]
```

### 5. Review & Commit
```bash
# Claude returns updated doc
# Review changes (should see all values filled)
# Save to DELIVERABLES.md

git add DELIVERABLES.md experiments/exp_001_hybrid_vs_vector.json
git commit -m "EXP-001: Embedding comparison metrics (D2.1, D5.3, D8.1, D10)"
git push origin feature/antigravity/exp-001-embedding-comparison

# Done! ✅
```

---

# 🎯 CHECKLIST BEFORE SENDING TO CLAUDE

- [ ] Branch name created: `feature/[yourname]/[description]`
- [ ] All metrics are measured, not guessed
- [ ] Every proof file has line number: `file.json:L45`
- [ ] Every field name matches DELIVERABLES.md exactly
- [ ] YAML syntax is valid (no typos)
- [ ] `branch_name` field filled in YAML
- [ ] `date_submitted` in YYYY-MM-DD format
- [ ] No [TO FILL] left in your section
- [ ] You have current DELIVERABLES.md ready to paste

---

# 🚨 COMMON MISTAKES (DON'T DO THESE)

| ❌ Wrong | ✅ Right |
|---------|----------|
| Proof: "experiments/exp_01.json" | Proof: "experiments/exp_01.json:L45" |
| Value: "[TO FILL]" or "TBD" | Value: "0.91" (actual metric) |
| Field: "Embedding Latency" | Field: "Embedding Latency (p95) — bge-large-en-v1.5" |
| Branch: "exp-001" | Branch: "feature/antigravity/exp-001-embedding" |
| Reasoning: "This is a good embedding model" | Reasoning: "Semantic depth, legal terms" |

---

# 📞 NEED HELP?

**Q: Where's the template?**  
A: At top of DELIVERABLES.md. Copy exact field names from there.

**Q: What's my branch name?**  
A: `feature/yourname/description`. Examples:
- `feature/antigravity/exp-001-embedding`
- `feature/balu/architecture-decisions`
- `feature/uday/failure-testing`

**Q: Can I submit multiple experiments at once?**  
A: Yes! Just add more update blocks to YAML. Claude will process all of them.

**Q: What if Claude rejects my update?**  
A: Check VALIDATION REPORT. Usually: field name typo, proof missing line number, or field already filled. Fix and resubmit.

**Q: When do I commit?**  
A: After Claude returns and you review the changes. Then: `git add DELIVERABLES.md` + `git commit` + `git push`

---

**YOU'RE READY! 🚀**

Your branch → Your metrics → YAML → Claude → Auto-update → Commit → DONE

Each person, each experiment, each test = one branch = one submission = automatic doc update.

No confusion. No manual editing. No overwriting. Just clean, traceable updates.

Go build! 💪
