#!/usr/bin/env python3
import json,re,sys
from common import ROOT
patterns={
 'private-key':re.compile(r'BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY',re.I),
 'aws-access-key':re.compile(r'AKIA[0-9A-Z]{16}'),
 'github-token':re.compile(r'ghp_[A-Za-z0-9]{30,}'),
 'slack-token':re.compile(r'xox[baprs]-[A-Za-z0-9-]{20,}'),
 'credential-in-url':re.compile(r'https?://[^/\s:@]+:[^/\s@]+@',re.I),
}
findings=[]
for path in ROOT.rglob('*'):
    if not path.is_file() or any(part in {'.git','release','__pycache__'} for part in path.parts) or path.name=='security_scan.py': continue
    try: text=path.read_text(encoding='utf-8')
    except UnicodeDecodeError: continue
    for rule,pattern in patterns.items():
        if pattern.search(text): findings.append({'file':path.relative_to(ROOT).as_posix(),'rule':rule})
out={'status':'PASS' if not findings else 'FAIL','high_confidence_findings':findings}
p=ROOT/'evidence/security/SECURITY-REPORT.json'; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
if findings: print(json.dumps(out,indent=2)); sys.exit(1)
print('SECURITY: PASS (0 high-confidence findings)')
