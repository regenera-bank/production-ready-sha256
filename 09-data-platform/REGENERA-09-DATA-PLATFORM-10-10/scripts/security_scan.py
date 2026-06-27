from pathlib import Path
import re, sys
from common import ROOT, EVIDENCE, FIXED_ISO, write_json

findings=[]
private_key = "-----BEGIN " + "PRIVATE KEY-----"
aws = re.compile(r"AKIA[0-9A-Z]{16}")
credential_url = re.compile(r"https?://[^\s/:]+:[^\s/@]+@")
assignment = re.compile(r"(?i)(password|api[_-]?key|access[_-]?token)\s*[:=]\s*['\"]([^'\"]{8,})['\"]")
for path in ROOT.rglob('*'):
    if not path.is_file() or 'dist' in path.parts or path.suffix in {'.pyc','.zip'}: continue
    if path.name == 'security_scan.py': continue
    text=path.read_text(encoding='utf-8',errors='ignore')
    if private_key in text: findings.append({"file":str(path.relative_to(ROOT)),"kind":"private-key"})
    if aws.search(text): findings.append({"file":str(path.relative_to(ROOT)),"kind":"aws-key"})
    if credential_url.search(text): findings.append({"file":str(path.relative_to(ROOT)),"kind":"credential-url"})
    for match in assignment.finditer(text):
        value=match.group(2).lower()
        if not any(x in value for x in ('example','placeholder','test-only')):
            findings.append({"file":str(path.relative_to(ROOT)),"kind":"credential-assignment"})
status='PASS' if not findings else 'FAIL'
write_json(EVIDENCE/'security-report.json',{"generated_at":FIXED_ISO,"status":status,"findings":findings})
print(f"security: {status} ({len(findings)} achados)")
if findings: sys.exit(1)
