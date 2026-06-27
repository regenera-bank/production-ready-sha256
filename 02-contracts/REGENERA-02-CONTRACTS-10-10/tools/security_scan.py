#!/usr/bin/env python3
from pathlib import Path
import re, sys
from common import ROOT
patterns=[
 ('private-key',re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
 ('aws-key',re.compile(r'AKIA[0-9A-Z]{16}')),
 ('github-token',re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}')),
 ('password-assignment',re.compile(r'(?i)(?:password|passwd|secret)\s*[:=]\s*["\'][^"\']{8,}["\']')),
]
findings=[]
for p in ROOT.rglob('*'):
    if not p.is_file() or p.parts[-2:-1]==('release',): continue
    if p.suffix.lower() not in {'.md','.yaml','.yml','.json','.py','.sh','.txt','.example'}: continue
    text=p.read_text(encoding='utf-8',errors='ignore')
    for name,rx in patterns:
        if rx.search(text): findings.append(f'{name}:{p.relative_to(ROOT)}')
if findings:
    print('\n'.join(findings),file=sys.stderr); raise SystemExit(1)
print('security: PASS')
