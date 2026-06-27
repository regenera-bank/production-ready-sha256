#!/usr/bin/env python3
import pathlib, shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
for p in list(ROOT.rglob('__pycache__')):
    if p.is_dir(): shutil.rmtree(p)
for p in ROOT.rglob('*.pyc'): p.unlink(missing_ok=True)
