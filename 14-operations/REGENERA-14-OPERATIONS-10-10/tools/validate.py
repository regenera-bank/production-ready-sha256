from pathlib import Path
import ast,json,sys
ROOT=Path(__file__).resolve().parents[1]
required=["README.md","Makefile","release.json","governance/CONTROL-MATRIX.json","governance/DOMAIN-REGISTRY.json","src/regenera_operations/incident.py","src/regenera_operations/change.py","src/regenera_operations/reconciliation.py","tests/test_incident.py","tools/verify_release.py"]
errors=[]
for rel in required:
    if not (ROOT/rel).is_file(): errors.append(f"arquivo ausente:{rel}")
for p in ROOT.rglob("*.py"):
    try: ast.parse(p.read_text(encoding="utf-8"),filename=str(p))
    except SyntaxError as exc: errors.append(f"python inválido:{p.relative_to(ROOT)}:{exc.lineno}")
for p in ROOT.rglob("*.json"):
    try: json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc: errors.append(f"json inválido:{p.relative_to(ROOT)}:{exc}")
for p in ROOT.rglob("*"):
    rel=str(p.relative_to(ROOT))
    if any(part in {"__MACOSX","__pycache__","node_modules"} for part in p.parts) or p.name==".DS_Store" or p.suffix==".pyc": errors.append(f"resíduo:{rel}")
    if p.is_file() and p.suffix.lower()==".zip": errors.append(f"zip interno:{rel}")
out=ROOT/"evidence/validation"; out.mkdir(parents=True,exist_ok=True)
report={"status":"FAILED" if errors else "PASSED","errors":errors,"required_files":len(required),"python_files":sum(1 for p in ROOT.rglob("*.py") if "evidence" not in p.parts),"json_files":sum(1 for p in ROOT.rglob("*.json") if "evidence" not in p.parts)}
(out/"VALIDATION-RESULTS.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("VALIDATION:",report["status"])
if errors:
    print("\n".join(errors)); sys.exit(1)
