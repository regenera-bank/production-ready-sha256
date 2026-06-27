#!/usr/bin/env python3
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
for relative in ("build",):
    target = root / relative
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

evidence = root / "evidence"
evidence.mkdir(parents=True, exist_ok=True)
for child in evidence.iterdir():
    if child.is_file():
        child.unlink()
    elif child.is_dir():
        shutil.rmtree(child)
print("CLEAN PASS")
