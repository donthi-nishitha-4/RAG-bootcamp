# 🤖 MASTER SUBMISSION PROMPT FOR DELIVERABLES AUTO-UPDATE
## **Branch-Based Contributor Detection + Template Preservation**

---

## 📋 HOW THIS WORKS

**You send this prompt to Claude with:**
1. **Current DELIVERABLES.md** (at top, never changes)
2. **Your updates in YAML** (who did what, with proof)
3. **Branch name** (git branch name auto-identifies contributor)

**Claude returns:**
- ✅ Updated DELIVERABLES.md (template preserved, [TO FILL] replaced)
- ✅ Audit log entry (auto-filled with branch name)
- ✅ Change summary (what was updated)
- ✅ Validation report (any errors)

---

## 🔑 KEY FEATURE: BRANCH-BASED CONTRIBUTOR MAPPING

```
Git Branch Name          → Auto-Detected Contributor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
feature/balu/*           → K. Bala Chowdappa (GPREC) [LEAD]
feature/antigravity/*    → Antigravity [DEV]
feature/uday/*           → Uday [ENGINEER]
feature/nishitha/*       → Nishitha [ENGINEER]
feature/ai/*             → AI Agent [AUTO]
main / develop           → Ask user for name
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

# 🚀 COPY-PASTE THIS PROMPT TO CLAUDE

```
[START PROMPT]

# BOOTCAMP DELIVERABLES AUTO-UPDATE v2.0
## Smart Branch Detection + Template Preservation

---

## YOUR TASK (READ CAREFULLY)

You are Claude, serving as the automation agent for DMRC AI-PMS RAG Bootcamp.

**Input**: Current DELIVERABLES.md + YAML updates
**Output**: Updated DELIVERABLES.md (template preserved) + audit log entry

---

## STEP 0: IDENTIFY CONTRIBUTOR (FROM BRANCH NAME)

User provided a **git branch name**. Use this mapping:

| Branch Pattern | Contributor Name | Role |
|---|---|---|
| feature/balu/* | K. Bala Chowdappa | Lead / Architecture |
| feature/antigravity/* | Antigravity | Dev / Experiments |
| feature/uday/* | Uday | Engineer |
| feature/nishitha/* | Nishitha | Engineer |
| feature/ai/* | AI Agent | Auto-run |
| main / develop | [ASK USER] | [Ask for name] |

**Detected Contributor**: [CLAUDE FILLS THIS BASED ON BRANCH]

---

## STEP 1: VALIDATE RULES (MANDATORY)

Before applying ANY updates, verify:

✅ **UNIVERSAL RULES**
```
Rule 1: [TO FILL] fields ONLY — Never edit already-filled fields
Rule 2: Preserve template structure — No section deletion/movement
Rule 3: Every value includes: VALUE (Contributor | Date | Proof)
Rule 4: Proof files have line numbers: path/file.json:L45, src/func():L12
Rule 5: No guesses — Only measured metrics
Rule 6: Audit trail maintained — Every change logged
```

---

## STEP 2: PARSE UPDATES (YAML FORMAT)

Expect input like:

```yaml
branch_name: "feature/antigravity/exp-001-embedding-comparison"
date_submitted: "2026-05-03"

updates:
  - section: "D2.1"
    field: "Index Size (1000 chunks) — MiniLM L6-v2"
    value: "~2.1 MB"
    reasoning: "384-dim embeddings with pgvector GiST index"
    proof: "experiments/exp_001_embeddings.json:L12, scripts/compare_embeddings.py:L234"
  
  - section: "D2.1"
    field: "Embedding Latency (p95) — MiniLM L6-v2"
    value: "12ms"
    reasoning: "CPU-optimized model on synthetic data"
    proof: "experiments/exp_001_embeddings.json:L45, scripts/compare_embeddings.py:L89"
```

**Extract**:
- `branch_name` → Auto-detect contributor
- `date_submitted` → Audit log date (use current date if missing)
- `updates` → List of field updates

---

## STEP 3: VALIDATE EACH UPDATE

For every update block:

1. **Field existence**: Verify field name exists in DELIVERABLES.md
2. **[TO FILL] check**: Confirm target is `[TO FILL]`, not already filled
3. **Format value**: `VALUE (Contributor | Date | Reasoning | Proof)`
4. **Proof validation**: Ensure proof file path + line number provided

**Example**:
```
✅ VALID:
  Field: "Index Size (1000 chunks) — MiniLM L6-v2"
  Value: "~2.1 MB"
  Proof: "experiments/exp_001_embeddings.json:L12"
  → Formatted: "~2.1 MB (Antigravity | 2026-05-03 | 384-dim embeddings, pgvector GiST index | experiments/exp_001_embeddings.json:L12)"

❌ INVALID:
  Field: "Random Field Not in Template"
  → REJECT: "Field not found in document"

❌ INVALID:
  Proof: "experiments/exp_001.json" (no line number)
  → REJECT: "Proof missing line number. Format: path/file.json:L45"
```

---

## STEP 4: APPLY UPDATES TO DOCUMENT

For each validated update:

1. **Find exact field in DELIVERABLES.md**
2. **Verify next occurrence is `[TO FILL]`**
3. **Replace ONLY the `[TO FILL]` with formatted value**
4. **Preserve ALL markdown formatting**

**Example Replacement**:

BEFORE:
```
Index Size (1000 chunks)
[TO FILL]        [TO FILL]        [TO FILL]        [TO FILL]
```

AFTER:
```
Index Size (1000 chunks)
~2.1 MB (Antigravity | 2026-05-03 | 384-dim embeddings | experiments/exp_001_embeddings.json:L12)
[TO FILL]        [TO FILL]        [TO FILL]
```

---

## STEP 5: UPDATE AUDIT LOG

Add entry to SR. DEV AUDIT LOG table:

```
| Date | Contributor | Section Updated | Reason / Rationale |
| :--- | :--- | :--- | :--- |
| [DATE] | [Contributor Name] | [Section, e.g., D2.1, D8.1] | [Auto-generated from branch] |
```

Example:
```
| 2026-05-03 | Antigravity | D2.1, D8.1, D10 | Submitted via feature/antigravity/exp-001: embedding comparison & latency benchmarks |
```

---

## STEP 6: BUMP DOCUMENT VERSION

Update header:

BEFORE:
```
Document Version
v1.0 (Template) — Update as experiments are completed
```

AFTER:
```
Document Version
v1.1 (Antigravity | 2026-05-03) — Updates to D2.1 (embedding metrics), D8.1 (latency), D10 (EXP-001 log)
```

---

## STEP 7: RETURN OUTPUT

Return exactly these sections:

### ✅ UPDATED DELIVERABLES.md
[Full document with updates applied]

### 📊 CHANGE SUMMARY
```
Contributor: [Name from branch]
Branch: [Branch name]
Date: [Date submitted]
Sections Updated: [List all touched sections]

Updates Applied:
- D2.1 — Index Size (1000 chunks) — MiniLM L6-v2: ~2.1 MB
- D2.1 — Embedding Latency (p95) — MiniLM L6-v2: 12ms
- [Continue for each update]

Audit Log Entry:
[Auto-generated entry for audit log]
```

### ⚠️ VALIDATION REPORT
```
Total Updates: [N]
Accepted: [N]
Rejected: [0 or N with reasons]

If any rejected:
- Field: "[Name]"
  Reason: "[Why it was rejected]"
  Fix: "[What to do]"
```

### 📝 REMAINING [TO FILL] FIELDS
```
Total [TO FILL] remaining: [N]

Still pending:
- D3.1 — Fixed 512 tokens — Contract P@5
- D4 — FE-01 — Query Used
- [Continue...]
```

---

## VALIDATION RULES (STRICT)

❌ **REJECT if:**
- Field name doesn't exist in template
- Target is NOT [TO FILL] (already filled)
- Proof file missing line number
- Value is empty or just placeholder text
- Contributor name is missing/blank

✅ **ACCEPT if:**
- Field exists in template
- Field is [TO FILL]
- Proof has full path:line_number format
- Value is specific, measured data
- Contributor auto-detected from branch

---

## EXAMPLE FLOW

**USER SENDS:**
```
Branch: feature/antigravity/exp-001-embedding
Date: 2026-05-03

updates:
  - section: "D2.1"
    field: "Index Size (1000 chunks) — MiniLM L6-v2"
    value: "~2.1 MB"
    reasoning: "384-dim embeddings"
    proof: "experiments/exp_001.json:L12"

[PASTE DELIVERABLES.md]
```

**CLAUDE PROCESSES:**
1. Detects: `feature/antigravity/...` → Contributor = "Antigravity"
2. Validates: Field exists? ✅ [TO FILL]? ✅ Proof? ✅
3. Formats: "~2.1 MB (Antigravity | 2026-05-03 | 384-dim embeddings | experiments/exp_001.json:L12)"
4. Updates document
5. Adds audit log entry
6. Bumps version to v1.1
7. Returns updated doc + summaries

**CLAUDE RETURNS:**
```
✅ DELIVERABLES_v1.1.md
✅ CHANGE SUMMARY (1 section, 1 field updated)
✅ VALIDATION REPORT (1 accepted, 0 rejected)
✅ REMAINING [TO FILL] (67 remaining)
```

---

## NOW: YOUR ACTUAL SUBMISSION

[PROVIDE THESE THREE THINGS BELOW]

### 1️⃣ GIT BRANCH NAME
```
feature/[contributor]/[experiment-name]

Examples:
- feature/antigravity/exp-001-embedding-comparison
- feature/balu/architecture-decisions-final
- feature/uday/failure-mode-testing
- feature/nishitha/security-tenant-isolation
- feature/ai/auto-latency-benchmark-2026-05-04
```

**Your Branch:**
```
[PASTE YOUR BRANCH NAME HERE]
```

---

### 2️⃣ YAML UPDATES
```yaml
branch_name: "[BRANCH NAME]"
date_submitted: "[YYYY-MM-DD]"

updates:
  - section: "[Section, e.g., D2.1]"
    field: "[Exact field name from template]"
    value: "[Measured value]"
    reasoning: "[2-3 words why this matters]"
    proof: "[path/file.json:L45 or src/func():L12]"
  
  - section: "[Another section]"
    field: "[Field name]"
    value: "[Value]"
    reasoning: "[Reason]"
    proof: "[Proof]"

[ADD MORE UPDATES AS NEEDED]
```

**Your Updates:**
```
[PASTE YOUR YAML UPDATES HERE]
```

---

### 3️⃣ CURRENT DELIVERABLES.md
```
[PASTE THE ENTIRE CURRENT DELIVERABLES.md DOCUMENT HERE]
```

---

[END PROMPT]
```

---

# 📌 HOW TEAM MEMBERS USE THIS

## For Antigravity (Experiments)

```bash
# After finishing EXP-001, create branch
git checkout -b feature/antigravity/exp-001-embedding-comparison

# Run experiment, get metrics
# measurements: P@5=0.89, latency p95=245ms, etc.

# Send to Claude:
Branch: feature/antigravity/exp-001-embedding-comparison
Date: 2026-05-03

updates:
  - section: "D2.1"
    field: "Contract Clause P@5 — bge-large-en-v1.5"
    value: "0.91"
    reasoning: "Semantic depth on legal terminology"
    proof: "experiments/exp_001_hybrid_vs_vector.json:L45, src/retriever.py:L65"

[+ paste current deliverables]

# Claude returns updated doc
# You review + commit
git add DELIVERABLES.md
git commit -m "EXP-001: Embedding comparison metrics (D2.1)"
git push origin feature/antigravity/exp-001-embedding-comparison
```

---

## For Balu (Architecture Decisions)

```bash
# After reviewing all experiments
git checkout -b feature/balu/architecture-decisions-day-10

# Make final architecture decisions

# Send to Claude:
Branch: feature/balu/architecture-decisions-day-10
Date: 2026-05-10

updates:
  - section: "D1.1"
    field: "Primary Vector Store"
    value: "pgvector"
    reasoning: "WSL/Ubuntu Portability, low maintenance"
    proof: "docker-compose.yml, EXP-001:P@5=0.89, src/retriever.py:L45"
  
  - section: "D11"
    field: "Embedding Model — Recommendation"
    value: "bge-large-en-v1.5"
    reasoning: "Best precision-recall for legal domain"
    proof: "EXP-001, EXP-002, D2.1 metrics"

[+ paste current deliverables]

# Claude returns updated doc
git add DELIVERABLES.md
git commit -m "D1, D11: Final architecture decisions (Balu sign-off)"
git push origin feature/balu/architecture-decisions-day-10
```

---

## For Uday / Nishitha (Support/Testing)

```bash
# After running security tests
git checkout -b feature/uday/tenant-isolation-validation

# Run cross-tenant tests, adversarial queries

# Send to Claude:
Branch: feature/uday/tenant-isolation-validation
Date: 2026-05-07

updates:
  - section: "D9.1"
    field: "Test 1 — Chunks From Wrong Tenant?"
    value: "No (PASS)"
    reasoning: "Metadata filter correctly enforced"
    proof: "experiments/tenant_isolation_test_001.json:L34"
  
  - section: "D9.2"
    field: "Test 1 — Hallucinated?"
    value: "No (PASS)"
    reasoning: "System correctly refused OOS query"
    proof: "experiments/hallucination_test_001.json:L23"

[+ paste current deliverables]

git add DELIVERABLES.md
git commit -m "D9: Tenant isolation + hallucination tests (5/5 PASS)"
git push origin feature/uday/tenant-isolation-validation
```

---

## For AI Agent (Auto-Run Experiments)

```bash
# Git branch auto-created by CI/CD
Branch: feature/ai/auto-latency-benchmark-2026-05-04
Date: 2026-05-04

updates:
  - section: "D8.1"
    field: "p50 (ms) — Vector Search (pgvector)"
    value: "120"
    reasoning: "GiST index on 1000 chunks, automatic run"
    proof: "artifacts/latency_benchmark_20260504.json:L67, ci_logs/job_12345.log"

[Auto-generated updates from pipeline]

# Claude auto-updates
# Commit auto-triggered by CI/CD
git add DELIVERABLES.md
git commit -m "[AI AUTO] D8.1: Latency benchmarks (feature/ai/auto-latency-benchmark-2026-05-04)"
git push origin feature/ai/auto-latency-benchmark-2026-05-04
git pull-request —auto
```

---

# 🎯 SUMMARY TABLE: WHO USES WHAT

| Person | Branch Pattern | Sections | Frequency | Example |
|--------|---|---|---|---|
| **Balu** | `feature/balu/*` | D1, D11 | ~3-4 times (decisions) | `feature/balu/architecture-decisions-day-10` |
| **Antigravity** | `feature/antigravity/*` | D2, D3, D5, D7, D8, D10 | ~15 times (experiments) | `feature/antigravity/exp-001-embedding` |
| **Uday** | `feature/uday/*` | D4, D9.1, D10 | ~5-8 times (tests) | `feature/uday/failure-mode-testing` |
| **Nishitha** | `feature/nishitha/*` | D6, D9.2, D10 | ~5-8 times (tests) | `feature/nishitha/tenant-isolation` |
| **AI Agent** | `feature/ai/*` | D8 (auto) | ~5-10 times (daily) | `feature/ai/auto-latency-benchmark-2026-05-04` |

---

# 💾 GIT WORKFLOW (END-TO-END)

```bash
# 1. Create branch with contributor name
git checkout -b feature/antigravity/exp-001-embedding

# 2. Do your work (run experiments, collect metrics)
# Commit code/scripts to branch
git add experiments/exp_001.json
git commit -m "EXP-001: Embedding comparison complete"
git push origin feature/antigravity/exp-001-embedding

# 3. Create YAML updates (see template above)
# Copy this prompt to Claude
# Provide: branch name + YAML + current deliverables
# Claude returns: updated doc + audit log

# 4. Review Claude's output
# Make sure all [TO FILL] → VALUES are correct
# Check audit log entry is accurate

# 5. Commit updated deliverables
git add DELIVERABLES.md
git commit -m "EXP-001: Update metrics in D2.1, D8.1, D10"
git push origin feature/antigravity/exp-001-embedding

# 6. Create PR (optional, for review)
git pull-request \
  --title "EXP-001: Embedding comparison (D2.1, D8.1, D10)" \
  --description "Metrics via feature/antigravity/exp-001-embedding"

# 7. Merge to main when ready
git checkout main
git pull origin feature/antigravity/exp-001-embedding
git merge --no-ff feature/antigravity/exp-001-embedding
git push origin main
```

---

# 📋 AUDIT LOG EXAMPLE (AUTO-GENERATED)

After 5 submissions, audit log looks like:

```
| Date | Contributor | Section Updated | Reason / Rationale |
| :--- | :--- | :--- | :--- |
| 2026-05-02 | K. Bala Chowdappa | D1, D11 | Initial architecture decisions + rationale |
| 2026-05-03 | Antigravity | D2.1, D8.1, D10 | EXP-001 metrics (feature/antigravity/exp-001-embedding) |
| 2026-05-04 | Uday | D4, D9.1, D10 | Failure mode FE-01 + tenant isolation tests (feature/uday/failure-testing) |
| 2026-05-04 | AI Agent | D8.1 | Auto-latency benchmark via CI/CD (feature/ai/auto-latency-benchmark-2026-05-04) |
| 2026-05-05 | Nishitha | D9.2, D10 | Hallucination testing + OOS query validation (feature/nishitha/hallucination-tests) |
```

---

**That's it, man!** 🚀

Just:
1. Create branch with your name: `feature/yourname/description`
2. Do your work
3. Send **this prompt** + **your YAML** + **current deliverables** to Claude
4. Claude auto-updates + audits
5. You commit + push
6. Done!

No manual editing, no deletion accidents, no version conflicts — all tracked by git branch names.
