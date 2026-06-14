# Review Spec 30 - Current Status

This file now tracks the current state of the migration and review findings.

## Status Summary

- Retrieval logging and evaluation output handling have been improved so `retrieved_chunks` is now carried through the pipeline instead of being dropped at the evaluation layer.
- The citation path has been updated to use retrieval results from the current query flow rather than a static or reused set of chunk IDs.
- The hallucination issue on empty context has been guarded in the agent path so the system can stop instead of fabricating an answer when no supporting context is available.
- The latency report still needs a final verification pass so the reported status matches the measured end-to-end latency.
- The out-of-scope keyword filter still needs careful review because keyword-only matching can create false positives for valid domain queries.

## Findings

1. **retrieved_chunks previously appeared empty in evaluation output**

   Status: **addressed in the staged pipeline**, but should be smoke-tested after the final code cleanup.

   What changed: the eval path now preserves retrieval data in the result payload instead of dropping it before JSON generation.

2. **Citation chain reused the same chunk IDs across unrelated queries**

   Status: **addressed in the staged retrieval/citation flow**, but should be re-verified with fresh queries.

   What changed: citation generation now follows the current retrieval results instead of relying on a fixed or cached chunk list.

3. **Latency report showed PASSED even when measured latency exceeded the budget**

   Status: **still needs final report verification**.

   What to check: ensure the latency label reflects the actual measured time and the budget threshold used by the report.

4. **The agent produced generic advice when context was empty**

   Status: **addressed in the staged agent logic**.

   What changed: the answer path now has a strict no-context guard so the model does not continue with unsupported advice.

5. **The OOS keyword filter can block legitimate queries**

   Status: **still open**.

   What to improve: replace or supplement keyword-only checks with a more robust domain mapping or similarity-based approach.

## Documentation and restructuring

- The new structure notes are now tracked in `docs/STRUCTURE.md` and `docs/MIGRATION_NOTES_migration-production-structure.md`.
- Old file names and module paths still need cleanup in the remaining docs and tests.
- This review file should be treated as a living status record until the migration tree is fully consistent.
