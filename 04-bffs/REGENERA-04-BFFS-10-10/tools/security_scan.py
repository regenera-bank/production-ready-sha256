#!/usr/bin/env python3
from pathlib import Path
import json, re, sys

ROOT = Path(__file__).resolve().parents[1]
findings = []
patterns = [
    ('private-key', re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
    ('aws-access-key', re.compile(r'AKIA[0-9A-Z]{16}')),
    ('github-token', re.compile(r'gh[pousr]_[A-Za-z0-9_]{30,}')),
    ('hardcoded-password', re.compile(r'(?i)(?:password|passwd)\s*[:=]\s*["\'][^"\']{8,}["\']')),
]
for path in ROOT.rglob('*'):
    if not path.is_file(): continue
    if any(part in {'dist', '.git'} for part in path.parts): continue
    if path.suffix not in {'.mjs', '.py', '.json', '.md', '.yml', '.yaml', '.sh'}: continue
    text = path.read_text(encoding='utf-8', errors='ignore')
    if path.name == 'security_scan.py': continue
    for name, pattern in patterns:
        if pattern.search(text): findings.append({'rule': name, 'path': path.relative_to(ROOT).as_posix()})
report = {'status': 'PASS' if not findings else 'FAIL', 'findings': findings}
(ROOT / 'evidence').mkdir(exist_ok=True)
(ROOT / 'evidence/SECURITY-REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
sys.exit(0 if not findings else 1)
