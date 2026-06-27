from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
scan_ext={".py",".json",".md",".yml",".yaml",".toml",".sh",".txt"}
excluded={"tools/security_scan.py"}
patterns={
 "private_key":re.compile("BEGIN"+r"\s+(?:RSA\s+|EC\s+|OPENSSH\s+)?PRIVATE\s+KEY"),
 "cloud_access_key":re.compile("AKIA"+r"[0-9A-Z]{16}"),
 "hardcoded_password":re.compile(r"(?i)(password|passwd)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
 "bearer_token":re.compile(r"(?i)bearer\s+[a-z0-9._-]{24,}"),
}
findings=[]
for p in ROOT.rglob("*"):
    if not p.is_file() or p.suffix.lower() not in scan_ext: continue
    rel=str(p.relative_to(ROOT))
    if rel in excluded or rel.startswith("evidence/"): continue
    text=p.read_text(encoding="utf-8",errors="ignore")
    for name,pattern in patterns.items():
        if pattern.search(text): findings.append({"file":rel,"rule":name})
terms=["".join(x) for x in [("A","s an ","AI"),("M","VP"),("place","holder"),("Generated ","by")]]
for p in ROOT.rglob("*"):
    if not p.is_file() or p.suffix.lower() not in scan_ext: continue
    rel=str(p.relative_to(ROOT))
    if rel in excluded or rel.startswith("evidence/"): continue
    text=p.read_text(encoding="utf-8",errors="ignore")
    for term in terms:
        if term.lower() in text.lower(): findings.append({"file":rel,"rule":"forbidden_release_term"})
out=ROOT/"evidence/security"; out.mkdir(parents=True,exist_ok=True)
report={"status":"FAILED" if findings else "PASSED","findings":findings,"excluded":sorted(excluded),"files_scanned":sum(1 for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in scan_ext and str(p.relative_to(ROOT)) not in excluded and "evidence" not in p.parts)}
(out/"SECURITY-SCAN.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("SECURITY:",report["status"])
if findings:
    print(json.dumps(findings,indent=2)); sys.exit(1)
