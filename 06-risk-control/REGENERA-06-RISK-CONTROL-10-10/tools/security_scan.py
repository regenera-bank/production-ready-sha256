from pathlib import Path
import json, re
ROOT=Path(__file__).resolve().parents[1]
patterns=[
 ('PRIVATE_KEY',re.compile(r'BEGIN [A-Z ]*PRIVATE KEY')),
 ('AWS_ACCESS_KEY',re.compile(r'AKIA[0-9A-Z]{16}')),
 ('PASSWORD_ASSIGNMENT',re.compile(r'(?i)(password|passwd)\s*[:=]\s*["\'][^"\']{8,}["\']')),
 ('TOKEN_ASSIGNMENT',re.compile(r'(?i)(api[_-]?key|secret[_-]?token)\s*[:=]\s*["\'][^"\']{12,}["\']')),
]
findings=[]
scan_ext={'.py','.md','.json','.toml','.csv','.yml','.yaml','.sh'}
for p in ROOT.rglob('*'):
    if not p.is_file() or p.suffix.lower() not in scan_ext: continue
    if p.name=='security_scan.py' or 'evidence' in p.parts: continue
    text=p.read_text(encoding='utf-8',errors='replace')
    for name,pattern in patterns:
        if pattern.search(text): findings.append({'rule':name,'file':str(p.relative_to(ROOT))})
report={'status':'PASS' if not findings else 'FAIL','findings':findings}
(ROOT/'evidence').mkdir(exist_ok=True)
(ROOT/'evidence'/'SECURITY-REPORT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
raise SystemExit(0 if not findings else 1)
