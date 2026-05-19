# 🚀 QUICK REFERENCE CARD — For Your Team

---

## 📌 THE 5-MINUTE PROCESS

### YOU (Balu Sir / Balu / Nishitha)
1. **Run your experiment or make your decision**
2. **Fill the template** (BOOTCAMP_AUTOMATION_SYSTEM.md, your role)
3. **Get the YAML updates** (copy from examples or your filled template)
4. **Send to Claude** (copy-paste the master prompt + your YAML)
5. **Review & commit** (Claude gives you updated doc)

---

## 📋 TEMPLATES BY ROLE

### If you're BALU (Engineer/Experiments)

```
Copy from: BOOTCAMP_AUTOMATION_SYSTEM.md → ROLE #2
Fill in:
  - Hypothesis (what you expected)
  - Strategy / Config (what you tested)
  - Dataset Used (size, type, location)
  - All metrics (P@5, latency, etc.)
  - Proof files (with line numbers!)
  - Surprising findings
  - Production implications

Generate YAML:
  - Section: D2, D3, D5, D7, D8, D10
  - Run ~15 experiments over 2 weeks
  - Each experiment = 1 YAML block
```

### If you're **BALU** (Architecture Decisions)

```
Copy from: BOOTCAMP_AUTOMATION_SYSTEM.md → ROLE #1
Fill in:
  - Decision name (e.g., "Vector Store Selection")
  - Options evaluated
  - Your choice + why
  - Evidence (cite experiments: EXP-001, EXP-005, etc.)
  - Trade-offs & risks
  - Production implications

Generate YAML:
  - Section: D1, D11
  - Fill after reviewing all team experiments
  - Each decision = 1-3 YAML blocks
```

### If you're NISHITHA (Engineer/Testing)

```
Copy from: BOOTCAMP_AUTOMATION_SYSTEM.md → ROLE #3
Fill in:
  - Test scenario (what you're validating)
  - Expected vs. actual results
  - Pass/fail status
  - Root cause analysis (if failure)
  - Proof files (test logs, query results, etc.)

Generate YAML:
  - Section: D4, D6, D9, D10
  - Test failure modes + security
  - Run 5+ tests per failure type
```

---

## 🎯 BEFORE YOU SUBMIT TO CLAUDE

### ✅ Checklist

- [ ] All [TO FILL] fields in my template are filled
- [ ] Every metric has a proof file reference (path:line_number)
- [ ] Code proofs have function names (e.g., `src/retriever.py:retrieve_hybrid():L45`)
- [ ] Dates are YYYY-MM-DD format
- [ ] Contributor name is YOUR full name
- [ ] Reasoning is 2-3 words max (e.g., "Hybrid superiority", "Security validation")
- [ ] YAML syntax is valid (use YAML linter: https://www.yamllint.com/)
- [ ] No [TO FILL] left in my section
- [ ] All values are measured, not guessed

---

## 💬 HOW TO SEND TO CLAUDE

### Option A: Full Send (Recommended)

1. Open Claude chat
2. Copy-paste this block:

```
[START]

Use the BOOTCAMP_AUTOMATION_SYSTEM.md file.
I am submitting updates as [ROLE: BALU / BALU / NISHITHA].

[PASTE YOUR FILLED TEMPLATE HERE]

---

[PASTE YOUR YAML UPDATES HERE]

---

[PASTE CURRENT Final_Deliverables/Documentation.md HERE]

[END]
```

3. Send to Claude
4. Claude returns updated document

### Option B: Quick Update (For hurried times)

Just send YAML block + current deliverables:

```
Please update DELIVERABLES.md with these updates:

```yaml
updates:
  - section: "D2.1"
    field: "Index Size (1000 chunks) — MiniLM L6-v2"
    value: "~2.1 MB"
    contributor: "Balu Sir"
    date: "2026-05-03"
    reasoning: "384-dim embeddings, GiST index"
    proof: "experiments/exp_001.json:L12"
```

[PASTE Final_Deliverables/Documentation.md]
```

---

## 📊 WHAT CLAUDE RETURNS

```
✅ DELIVERABLES_v1.X_UPDATED.md (full updated document)
✅ CHANGE SUMMARY (what was updated, by section)
✅ REMAINING [TO FILL] FIELDS (list of still-pending fields)
✅ VALIDATION REPORT (any rejected updates + why)
```

**Next step**: Review, commit to Git, move on.

---

## 🔗 GIT WORKFLOW

```bash
# After Claude updates:
git add DELIVERABLES.md experiments/
git commit -m "Day X: [Your Name] — EXP-001 metrics (D2, D5, D8)"
git push

# Check audit log:
git log --oneline | head -10
```

---

## ⚠️ COMMON MISTAKES

| Mistake | Fix |
|---------|-----|
| "experiments/exp_01.json" (no line number) | "experiments/exp_01.json:L45" |
| Proof file doesn't exist yet | Run experiment first, save results, then update |
| [TO FILL] left in template | Copy-paste exact values, don't summarize |
| YAML syntax error | Validate at https://www.yamllint.com/ |
| Value is a guess, not measured | Only metrics from actual experiments |
| "Contributed by Antigravity" (too verbose) | "Antigravity" (just name) |
| Section name wrong (e.g., "D2.2" when field is in "D2.1") | Check DELIVERABLES.md source |

---

## 📞 NEED HELP?

**Problem**: "I don't know what value to put"  
**Solution**: Run the experiment! Or ask team lead (Balu) if it's already been run.

**Problem**: "My proof file doesn't have line numbers"  
**Solution**: Add them! JSON files: line is the array index. Python files: use `print(f"Line {function.__code__.co_firstlineno}")`

**Problem**: "Claude rejected my update"  
**Solution**: Check VALIDATION REPORT. Likely: field name typo, field already filled, or proof file doesn't exist.

---

## 📈 PROGRESS TRACKING

```
Day 1-2:  Setup + EXP-001, EXP-002 (embedding, chunking)
Day 3-4:  EXP-003, EXP-004 (retrieval strategies)
Day 5-6:  EXP-005, EXP-006 (latency, multi-hop)
Day 7-8:  EXP-007, EXP-008 (failure modes, security)
Day 9-10: EXP-009-015 (final experiments + Balu sign-off)

By Day 10, all [TO FILL] in DELIVERABLES should be complete.
```

---

## 🎓 EXAMPLE TIMELINE

**Day 3 — Antigravity runs EXP-001**
```
Morning: Set up experiment infrastructure
Afternoon: Run embedding comparison (3 models, 1000 chunks)
Evening: Calculate metrics, measure latency
Night: Fill template, generate YAML

Send to Claude → 5 min → Updated doc → Commit ✅
```

**Day 8 — Balu reviews all experiments**
```
Morning: Read EXP-001 through EXP-007 results
Afternoon: Make architecture decisions
Evening: Fill D1 + D11 templates, generate YAML

Send to Claude → 10 min → Final architecture doc → Team review ✅
```

---

**Questions? Ask on team Slack. Everything is in BOOTCAMP_AUTOMATION_SYSTEM.md.**
