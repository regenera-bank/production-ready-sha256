from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
manifest_path=ROOT/"evidence/integrity/PAYLOAD-MANIFEST.json"
checks_path=ROOT/"evidence/integrity/PAYLOAD-CHECKSUMS.sha256"
errors=[]
if not manifest_path.is_file() or not checks_path.is_file():
    errors.append("arquivos de integridade ausentes")
else:
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    excluded=set(manifest["exclusions"])
    actual=sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and str(p.relative_to(ROOT)) not in excluded and '__pycache__' not in p.parts and p.suffix!='.pyc')
    expected=sorted(r["path"] for r in manifest["files"])
    if actual!=expected:
        errors.append("conjunto de arquivos divergente")
    for r in manifest["files"]:
        p=ROOT/r["path"]
        if not p.is_file(): errors.append(f"ausente:{r['path']}"); continue
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        if digest!=r["sha256"] or p.stat().st_size!=r["size"]: errors.append(f"hash divergente:{r['path']}")
    check_lines=checks_path.read_text(encoding="utf-8").splitlines()
    expected_lines=[f"{r['sha256']}  {r['path']}" for r in manifest["files"]]
    if check_lines!=expected_lines: errors.append("arquivo de checksums divergente")
for p in ROOT.rglob('*'):
    if any(part in {'__MACOSX','__pycache__','node_modules'} for part in p.parts) or p.name=='.DS_Store' or p.suffix=='.pyc': errors.append(f"resíduo:{p.relative_to(ROOT)}")
    if p.is_file() and p.suffix.lower()=='.zip': errors.append(f"zip interno:{p.relative_to(ROOT)}")
print("VERIFY:","FAIL" if errors else "PASS")
if errors:
    print("\n".join(errors)); sys.exit(1)
