#!/usr/bin/env python3
import json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from regenera_quality.security import scan_text
skip={'tools/security_scan.py','src/regenera_quality/security.py','tests/test_security.py'}
findings=[]
for p in ROOT.rglob('*'):
    if not p.is_file(): continue
    rel=str(p.relative_to(ROOT))
    if rel in skip or rel.startswith('evidence/results/'): continue
    if p.suffix.lower() in {'.zip','.png','.jpg','.jpeg','.gif','.webp'}: continue
    try: text=p.read_text()
    except UnicodeDecodeError: continue
    for f in scan_text(text): findings.append({'file':rel,'rule':f.rule,'severity':f.severity})
report={'status':'PASS' if not findings else 'FAIL','findings':findings,'exact_exclusions':sorted(skip),'exclusion_reason':'scanner implementation and dedicated detection fixtures contain rule signatures'}
out=ROOT/'evidence/results/SECURITY-REPORT.json'; out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print('SECURITY:',report['status'])
raise SystemExit(0 if not findings else 1)
