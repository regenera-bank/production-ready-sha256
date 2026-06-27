#!/usr/bin/env python3
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
for name in ('dist.tmp',):
    p=ROOT/name
    if p.exists(): shutil.rmtree(p)
for p in list(ROOT.rglob('__pycache__')):
    if p.is_dir(): shutil.rmtree(p)
for p in list(ROOT.rglob('*.pyc')):
    p.unlink()
print('clean: PASS')
