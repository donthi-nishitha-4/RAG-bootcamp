# Migration Audit Log: Bootcamp to Production

## 1. Overview
The repository has been reworked from contributor-scoped experimental filenames into a cleaner production-style layout.

## 2. Key Structural Changes
- Security logic is currently centralized in `src/core/security.py`.
- Agent logic lives in `src/agents/langgraph_agent.py`.
- Query routing lives in `src/agents/query_router.py`.
- API entrypoint lives in `src/api/main.py`.

## 3. Dependency Cleanup
- The active runtime uses package imports from `src.*`.
- The current docs and tests should reference the new module names rather than the old `_Nishitha` runtime files.

## 4. Behavior and Dependencies
- Import resolution is handled through the package layout under `src/`.
- Configuration is expected through `src/utils/config.py` and `.env`.
- The deployment path should point to `uvicorn src.api.main:app`.

## 5. Remaining Cleanup
- Historical documentation artifacts may still preserve contributor names for traceability.
- A final pass is still needed to make every documentation reference match the current source tree exactly.
