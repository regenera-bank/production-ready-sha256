#!/usr/bin/env python3
from pathlib import Path
import json, re, sys
from common import ROOT
required=["README.md","config/platform-baseline.json","config/platform-registry.json","policies/platform-security.md","runbooks/region-loss.md","controls/CONTROL-MATRIX.csv"]
errors=[]
for rel in required:
    if not (ROOT/rel).is_file(): errors.append(f"missing:{rel}")
for p in ROOT.rglob("*"):
    if not p.is_file(): continue
    rel=p.relative_to(ROOT).as_posix()
    if any(x in p.parts for x in [".git","release"]): continue
    if p.name in {".DS_Store"} or "__MACOSX" in p.parts or "__pycache__" in p.parts or p.suffix==".pyc": errors.append(f"system-file:{rel}")
    if p.suffix.lower() in {".zip",".tar",".gz"}: errors.append(f"nested-archive:{rel}")
    if p.stat().st_size==0: errors.append(f"empty-file:{rel}")
base=json.loads((ROOT/"config/platform-baseline.json").read_text())
if base["status"]!="PENDING_INSTITUTIONAL_APPROVAL": errors.append("baseline-status-invalid")
registry=json.loads((ROOT/"config/platform-registry.json").read_text())
for item in registry["modules"]:
    if item["state"]=="BLOCKED_EXTERNAL_EVIDENCE" and not item["evidence_required"]: errors.append(f"external-evidence-not-required:{item['name']}")
if errors:
    print("VALIDATION: FAIL"); print("\n".join(errors)); sys.exit(1)
print(f"VALIDATION: PASS ({sum(1 for p in ROOT.rglob('*') if p.is_file())} files)")
