#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
for path in list(ROOT.rglob("__pycache__")):
    if path.is_dir(): shutil.rmtree(path)
for path in ROOT.rglob("*.pyc"):
    path.unlink(missing_ok=True)
for rel in ("release","evidence/test","evidence/security"):
    path=ROOT/rel
    if path.exists(): shutil.rmtree(path)
print("CLEAN: PASS")
