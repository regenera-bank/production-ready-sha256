#!/usr/bin/env python3
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
for p in list(root.rglob("__pycache__")):
    if p.is_dir(): shutil.rmtree(p)
for p in root.rglob("*.pyc"):
    p.unlink(missing_ok=True)
for rel in ["release","evidence/test","evidence/security"]:
    p=root/rel
    if p.exists(): shutil.rmtree(p)
