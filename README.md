# 📚 BOOTCAMP AUTOMATION SYSTEM — COMPLETE GUIDE

## 🎯 OVERVIEW

This system automates the deliverables document updates for the **DMRC AI-PMS RAG Bootcamp** (2-week intensive).

**Problem Solved:**
- ❌ Manual editing of deliverables = mistakes, overwrites, lost history
- ❌ Multiple people = merge conflicts, version chaos
- ✅ **This system** = automatic updates + full audit trail + git-based version control

---

## 📁 FILES IN THIS SYSTEM

### **Core Files (What to Use)**

| File | Purpose | When to Use |
|------|---------|-----------|
| **QUICK_START_5_STEPS.md** | ⭐ **START HERE** — Simple 5-step process | Every time you have metrics to submit |
| **MASTER_SUBMISSION_PROMPT.md** | Full Claude prompt with branch detection | When sending updates to Claude |
| **BOOTCAMP_AUTOMATION_SYSTEM.md** | Complete system documentation (from earlier) | Read once for full understanding |
| **EXAMPLE_ANTIGRAVITY_SUBMISSION_DAY3.md** | Real example with filled template | Learn by seeing a complete example |
| **TEAM_QUICK_REFERENCE.md** | 1-page cheat sheet for team | Print/pin in Slack |

### **Reference Files**

| File | What It Is |
|------|-----------|
| DELIVERABLES.md | The main document (template at top, [TO FILL] to update) |
| experiments/ | Your experiment results (where proofs go) |
| src/ | Your code (functions you reference in proofs) |
| scripts/ | Benchmark/eval scripts (latency, RAGAS, etc.) |

---

## 🚀 HOW TO GET STARTED (RIGHT NOW)

### 1. **Read This** (2 min)
You're reading it! 

### 2. **Read QUICK_START_5_STEPS.md** (3 min)
Gets you from zero to submission in 5 steps.

### 3. **Read EXAMPLE_ANTIGRAVITY_SUBMISSION_DAY3.md** (5 min)
See a real, filled-out example so you understand the format.

### 4. **Do Your First Experiment/Task**
Run your work, get metrics, save proof files.

### 5. **Follow QUICK_START_5_STEPS.md**
Create branch → YAML → Send to Claude → Commit → Done.

---

## 🎓 WHO DOES WHAT

### **Balu (Team Lead)**
- **Role**: Make final architecture decisions
- **Sections**: D1 (Architecture), D11 (Final Recommendations)
- **Branch pattern**: `feature/balu/architecture-*`
- **Frequency**: ~3-4 times (after reviewing experiments)
- **Use this**: QUICK_START_5_STEPS.md (with MASTER_SUBMISSION_PROMPT.md for Claude)

### **Antigravity (Dev/Experiments)**
- **Role**: Run RAG experiments, measure all metrics
- **Sections**: D2, D3, D5, D7, D8, D10 (embedding, chunking, retrieval, latency, etc.)
- **Branch pattern**: `feature/antigravity/exp-*`
- **Frequency**: ~15 experiments over 2 weeks
- **Use this**: QUICK_START_5_STEPS.md + EXAMPLE_ANTIGRAVITY_SUBMISSION_DAY3.md

### **Uday (Engineer/Testing)**
- **Role**: Test failure modes, edge cases, some latency
- **Sections**: D4 (Failures), D9.1 (Tenant isolation), D10 (Experiment log)
- **Branch pattern**: `feature/uday/test-*`
- **Frequency**: ~5-8 tests
- **Use this**: QUICK_START_5_STEPS.md

### **Nishitha (Engineer/Testing)**
- **Role**: Test multi-hop, hallucination, security validation
- **Sections**: D6 (Agentic RAG), D9.2 (Hallucination), D10 (Experiment log)
- **Branch pattern**: `feature/nishitha/test-*`
- **Frequency**: ~5-8 tests
- **Use this**: QUICK_START_5_STEPS.md

### **AI Agent (Auto)**
- **Role**: Automated benchmarks, latency measurements
- **Sections**: D8 (Latency), D10 (Auto experiment logs)
- **Branch pattern**: `feature/ai/auto-*`
- **Frequency**: ~5-10 times (daily runs)
- **Use this**: CI/CD pipeline integration (see MASTER_SUBMISSION_PROMPT.md for format)

---

## 📊 SUBMISSION WORKFLOW (EVERY TIME)

```
┌─────────────────────┐
│  DO YOUR WORK       │  (Run experiment, collect metrics)
│ (Antigravity, etc.) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ CREATE BRANCH       │  (feature/yourname/description)
│ & SAVE PROOF FILES  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ FILL YAML           │  (section, field, value, proof:linenum)
│ (See QUICK_START)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ SEND TO CLAUDE      │  (Copy MASTER_SUBMISSION_PROMPT.md)
│                     │  (+ Your YAML + Current deliverables)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ REVIEW OUTPUT       │  (Check updated doc, audit log, validation)
│                     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ GIT COMMIT & PUSH   │  (Add DELIVERABLES.md, commit, push branch)
│                     │
└─────────────────────┘
           │
           ▼
        DONE ✅
```

---

## 📝 BRANCH NAMING CONVENTION

Your branch name tells Claude WHO you are. Use these patterns:

```
feature/[contributor]/[description]

Examples:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
feature/balu/architecture-decisions-day-10
feature/antigravity/exp-001-embedding-comparison
feature/antigravity/exp-002-chunking-strategies
feature/uday/failure-mode-cross-entity-confusion
feature/nishitha/tenant-isolation-validation
feature/ai/auto-latency-benchmark-2026-05-04
```

---

## 🔑 KEY CONCEPTS

### **[TO FILL]**
Placeholder in template for fields without data yet.
```
Before: [TO FILL]
After:  "0.91 (Antigravity | 2026-05-03 | Semantic depth | experiments/exp_001.json:L45)"
```

### **Proof File**
Where your metric actually came from, with exact line:
```
✅ GOOD: experiments/exp_001.json:L45, src/retriever.py:L65
❌ BAD:  experiments/exp_001.json (no line number)
```

### **Audit Log**
Automatic record of every change:
```
| Date | Contributor | Section | Reason |
| 2026-05-03 | Antigravity | D2.1, D8.1 | EXP-001 metrics (feature/antigravity/exp-001) |
```

### **Version Bump**
Document version increments automatically:
```
Before: v1.0 (Template)
After:  v1.1 (Antigravity | 2026-05-03)
```

---

## ✅ BEFORE YOU SUBMIT

**Checklist:**
- [ ] Branch created with your name: `feature/yourname/...`
- [ ] All metrics measured (not guessed)
- [ ] Proof files saved: `experiments/`, `src/`, `scripts/`
- [ ] Proof file paths include line numbers: `file.json:L45`
- [ ] Field names match DELIVERABLES.md exactly (copy-paste!)
- [ ] YAML syntax valid (no typos)
- [ ] No [TO FILL] left in your values
- [ ] Reasoning is 2-3 words max
- [ ] Current DELIVERABLES.md ready to paste

---

## 🎯 DAILY WORKFLOW (2-WEEK BOOTCAMP)

### **Day 1-2: Setup**
- [ ] Balu: Create `feature/balu/architecture-decisions` branch (no updates yet)
- [ ] Antigravity: Set up experiment infrastructure
- [ ] Uday/Nishitha: Prepare test scenarios
- [ ] All: Commit initial code to repo

### **Day 3-5: Early Experiments**
- [ ] Antigravity: Submit EXP-001, EXP-002 (embedding, chunking)
- [ ] Uday/Nishitha: Run initial failure tests
- [ ] Balu: Monitor experiments, suggest directions

### **Day 6-8: Mid-Phase Experiments**
- [ ] Antigravity: Submit EXP-003 through EXP-007 (retrieval, latency, RAGAS)
- [ ] Uday/Nishitha: Submit failure modes (FE-01 through FE-03)
- [ ] Balu: Start architecture decision drafts

### **Day 9: Final Experiments**
- [ ] Antigravity: Submit remaining experiments (EXP-008 through EXP-015)
- [ ] Uday/Nishitha: Finish security/multi-hop tests
- [ ] AI Agent: Run final latency benchmarks

### **Day 10: Delivery**
- [ ] Balu: Submit final D1 + D11 (architecture decisions)
- [ ] All: Final review of complete deliverables
- [ ] All: Merge all feature branches to main
- [ ] **DELIVERABLES COMPLETE** ✅

---

## 🔍 HOW CLAUDE DETECTS YOUR CONTRIBUTION

When you send Claude the prompt with your branch name, Claude automatically:

1. **Parses branch**: `feature/antigravity/exp-001-...`
2. **Extracts contributor**: `Antigravity`
3. **Formats audit entry**: `Antigravity | 2026-05-03 | Submitted via feature/antigravity/exp-001`
4. **Updates document**: Only [TO FILL] fields, preserves structure
5. **Returns**: Updated doc + audit log + validation report

No manual entry of names needed! Just the branch name does it.

---

## 📊 EXPECTED DOCUMENT COMPLETION

After all submissions, DELIVERABLES will look like:

```
D1  ✅ 6/6 Architecture decisions filled (Balu)
D2  ✅ All embedding metrics filled (Antigravity EXP-001)
D3  ✅ Chunking strategies filled (Antigravity EXP-002)
D4  ✅ Failure modes documented (Uday/Nishitha FE-01 through FE-05)
D5  ✅ Retrieval strategy comparison filled (Antigravity EXP-003 through EXP-005)
D6  ✅ Multi-hop traces filled (Nishitha tests)
D7  ✅ RAGAS metrics filled (Antigravity EXP-006)
D8  ✅ Latency analysis filled (Antigravity EXP-007, AI Agent auto-runs)
D9  ✅ Security validation filled (Uday/Nishitha tests)
D10 ✅ 15+ experiment logs filled (All contributors)
D11 ✅ Final recommendations filled (Balu + evidence references)

NO [TO FILL] REMAINING ✅
AUDIT LOG: 20+ entries ✅
VERSION: v1.15+ ✅
```

---

## 🎓 LEARNING PATH

**New to this system?** Read in this order:

1. **THIS FILE** (README) — 10 min — Understand the big picture
2. **QUICK_START_5_STEPS.md** — 5 min — Learn the process
3. **EXAMPLE_ANTIGRAVITY_SUBMISSION_DAY3.md** — 10 min — See a real example
4. **Do your first submission** — 30 min — Get hands-on experience
5. **MASTER_SUBMISSION_PROMPT.md** — 5 min — Understand Claude's role

**Experienced? Just use:**
- QUICK_START_5_STEPS.md (when submitting)
- Branch naming convention (from this README)
- MASTER_SUBMISSION_PROMPT.md (to send to Claude)

---

## 🆘 TROUBLESHOOTING

### **Problem: "Field not found" error from Claude**
- **Solution**: Copy exact field name from DELIVERABLES.md template
- **Check**: Use Ctrl+F to find it in the document
- **Example**: Not "Embedding Latency" but "Embedding Latency (p95) — MiniLM L6-v2"

### **Problem: "Proof missing line number"**
- **Solution**: Every proof must have `:L45` or `:line_XX`
- **Format**: `experiments/exp_001.json:L12` or `src/retriever.py:L123`
- **Why**: Traceability — anyone can find the exact source

### **Problem: Claude rejected my entire submission**
- **Check**: Is your YAML syntax valid? (Use https://www.yamllint.com/)
- **Check**: Is your branch name in the correct format?
- **Check**: Are all required fields present in each update block?
- **Fix**: Correct the issues and resubmit

### **Problem: "This field is already filled"**
- **Solution**: That field already has a value, not [TO FILL]
- **Choose**: Either update a different field, or note it as "REVISED" in reasoning
- **Ask**: Balu if you need to overwrite an earlier value

### **Problem: Multiple people working on same section**
- **Solution**: Use different branches (e.g., `feature/antigravity/...`, `feature/uday/...`)
- **Merge**: One at a time to main; second person pulls and rebases
- **Git**: Use `git pull --rebase origin main` before pushing

---

## 📞 QUICK REFERENCE

### **Contributor Mapping**
```
You                 → Branch Pattern
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Balu                feature/balu/*
Antigravity         feature/antigravity/*
Uday                feature/uday/*
Nishitha            feature/nishitha/*
AI Agent            feature/ai/*
```

### **Section Owners**
```
D1, D11             → Balu (Architecture)
D2, D3, D5, D7, D8  → Antigravity (Experiments)
D4, D9.1, D10       → Uday (Failure modes, tests)
D6, D9.2, D10       → Nishitha (Multi-hop, hallucination)
D8 (auto)           → AI Agent (Latency benchmarks)
```

### **When to Submit**
```
Antigravity: After each experiment (EXP-001, EXP-002, ..., EXP-015+)
Balu:        After reviewing all experiments (Day 9-10)
Uday:        After each failure/security test (5+ times)
Nishitha:    After each multi-hop/hallucination test (5+ times)
AI Agent:    Automatically via CI/CD (daily)
```

---

## 🎉 YOU'RE SET!

Everything is in place:
- ✅ System documentation (this README + 5 other files)
- ✅ Branch-based contributor detection
- ✅ Automatic audit logging
- ✅ Template preservation (no deletions)
- ✅ Git-based version control
- ✅ Claude auto-update agent

**All you need to do:**
1. Create branch with your name
2. Do your work
3. Fill YAML (5 fields per update)
4. Send to Claude
5. Commit

**No manual editing. No overwrites. No confusion.**

---

**Questions?** Check the specific file for your role:
- Antigravity → EXAMPLE_ANTIGRAVITY_SUBMISSION_DAY3.md
- Balu → BOOTCAMP_AUTOMATION_SYSTEM.md (ROLE #1 section)
- Uday/Nishitha → BOOTCAMP_AUTOMATION_SYSTEM.md (ROLE #3 section)

**Ready to start?** → **QUICK_START_5_STEPS.md** ⚡
