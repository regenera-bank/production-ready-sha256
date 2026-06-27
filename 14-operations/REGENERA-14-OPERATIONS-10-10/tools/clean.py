from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
for p in sorted(ROOT.rglob("__pycache__"),reverse=True): shutil.rmtree(p,ignore_errors=True)
for p in ROOT.rglob("*.pyc"):
    try: p.unlink()
    except FileNotFoundError: pass
for name in (".pytest_cache",".mypy_cache",".ruff_cache"):
    shutil.rmtree(ROOT/name,ignore_errors=True)
print("CLEAN: PASS")
