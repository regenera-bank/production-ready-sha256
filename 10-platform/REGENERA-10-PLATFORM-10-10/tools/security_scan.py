#!/usr/bin/env python3
from pathlib import Path
import re, json, sys
from common import ROOT
patterns=[re.compile(x,re.I) for x in [r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY",r"AKIA[0-9A-Z]{16}",r"ghp_[A-Za-z0-9]{30,}",r"xox[baprs]-[A-Za-z0-9-]{20,}"]]
findings=[]
for p in ROOT.rglob("*"):
    if not p.is_file() or any(x in p.parts for x in [".git","release","__pycache__"]): continue
    if p.name=="security_scan.py": continue
    try: text=p.read_text(encoding="utf-8")
    except UnicodeDecodeError: continue
    for pattern in patterns:
        if pattern.search(text): findings.append({"file":p.relative_to(ROOT).as_posix(),"rule":pattern.pattern})
out={"status":"PASS" if not findings else "FAIL","findings":findings}
(ROOT/"evidence/security").mkdir(parents=True,exist_ok=True)
(ROOT/"evidence/security/SECURITY-REPORT.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
if findings: print(json.dumps(out,indent=2)); sys.exit(1)
print("SECURITY: PASS (0 high-confidence findings)")
