"""Runner for RAGAS evaluation with environment validation.

This script validates environment/dependencies and then invokes `scripts/eval_ragas.py`.
It is a convenience wrapper to make RAGAS runs reproducible and documented for reviewers.
"""
import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL_SCRIPT = ROOT / 'scripts' / 'eval_ragas.py'


def check_deps():
    try:
        import ragas  # type: ignore
        import datasets  # type: ignore
        return True, []
    except Exception as e:
        return False, [str(e)]


def main():
    ok, errors = check_deps()
    if not ok:
        print('[ERROR] Missing RAGAS dependencies. Install with: pip install -r requirements-ragas.txt')
        for e in errors:
            print('  ', e)
        sys.exit(1)

    if not EVAL_SCRIPT.exists():
        print(f'[ERROR] Expected script not found: {EVAL_SCRIPT}')
        sys.exit(1)

    # Basic environment checks
    ds_path = ROOT / 'evaluation' / 'dataset' / 'evaluation_dataset.json'
    if not ds_path.exists():
        print(f'[WARN] Canonical dataset not found at {ds_path}. Falling back to BALU dataset.')

    # Forward args to eval_ragas.py
    cmd = [sys.executable, str(EVAL_SCRIPT)]
    cmd.extend(sys.argv[1:])
    print('[INFO] Running:', ' '.join(cmd))
    rv = subprocess.run(cmd)
    sys.exit(rv.returncode)


if __name__ == '__main__':
    main()

