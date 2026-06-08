#!/bin/bash
echo "--- Running Final Audit ---"
echo "1. DB Integrity:"
PYTHONPATH=. python3 -c "from src.core.database.connection import get_connection; cur = get_connection().cursor(); cur.execute('SELECT count(*) FROM rag_documents'); print(f'Chunks: {cur.fetchone()[0]}')"
echo "2. Security Tests:"
PYTHONPATH=. python3 tests/unit/test_security.py
echo "3. Legacy File Audit:"
find . -name "*_Nishitha.py" -o -name "*_BALU.py"
echo "4. Dependency Hack Check:"
grep -r "sys.path.append" src/ tests/ scripts/
echo "--- Audit Complete ---"