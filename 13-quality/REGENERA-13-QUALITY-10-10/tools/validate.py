#!/usr/bin/env python3
import json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
required=['README.md','LICENSE','release.json','config/quality-policy.json','config/control-matrix.json','src/regenera_quality/gates.py','tests/test_gates.py']
missing=[p for p in required if not (ROOT/p).is_file()]
if missing: raise SystemExit('missing:'+','.join(missing))
for p in ROOT.rglob('*.json'): json.loads(p.read_text())
for p in ROOT.rglob('*'):
    if p.is_file() and (p.name in {'.DS_Store'} or '__MACOSX' in p.parts or p.suffix in {'.pyc'} or '__pycache__' in p.parts):
        raise SystemExit('forbidden_entry:'+str(p.relative_to(ROOT)))
print('VALIDATION: PASS')
