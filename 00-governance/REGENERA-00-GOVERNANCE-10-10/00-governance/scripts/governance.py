#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json, os, re, shutil, subprocess, sys, tempfile, time, zipfile
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {'.git','dist','__pycache__','.pytest_cache','.mypy_cache'}
SYSTEM_NAMES = {'.DS_Store','Thumbs.db','.Spotlight-V100'}
FORBIDDEN_DIRS = {'__MACOSX'}
FORBIDDEN_SUFFIXES = {'.pyc','.pyo'}
SECRET_PATTERNS = {
    'private-key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'aws-access-key': re.compile(r'AKIA[0-9A-Z]{16}'),
    'github-token': re.compile(r'gh[pousr]_[A-Za-z0-9_]{20,}'),
    'credential-url': re.compile(r'https?://[^\s/:]+:[^\s/@]+@'),
}
REQUIRED_POLICY_SECTIONS = {'Objetivo','Escopo','Responsabilidades','Evidências','Métricas'}


def iter_files(root: Path = ROOT, include_evidence: bool = True):
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts):
            continue
        rel = path.relative_to(root).as_posix()
        if not include_evidence and rel.startswith('evidence/release/'):
            continue
        yield path


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def read_text(path: Path):
    try: return path.read_text(encoding='utf-8')
    except UnicodeDecodeError: return None


def parse_metadata(body: str):
    def grab(label):
        m=re.search(rf'^\*\*{re.escape(label)}:\*\*\s*(.+?)\s*$', body, re.M)
        return m.group(1).strip() if m else None
    return {
        'document_id': grab('Documento'), 'state': grab('Estado'),
        'author': grab('Autor responsável'), 'owner': grab('Owner operacional'),
        'effective': grab('Vigência'), 'next_review': grab('Próxima revisão'),
    }


def headings(body: str):
    return {m.group(1).strip() for m in re.finditer(r'^##\s+(.+?)\s*$', body, re.M)}


def validate_root(root: Path = ROOT):
    errors=[]; docs={}
    required=['README.md','GOVERNANCE-MANIFEST.yaml','OWNERS.yaml','RACI.csv','CONTROL-MATRIX.csv','REGULATORY-TRACEABILITY.csv','scripts/governance.py','tests/test_governance.py']
    for rel in required:
        if not (root/rel).is_file(): errors.append(f'missing:{rel}')
    for path in iter_files(root):
        relative=path.relative_to(root)
        if path.name in SYSTEM_NAMES or any(part in FORBIDDEN_DIRS for part in relative.parts) or path.suffix in FORBIDDEN_SUFFIXES:
            errors.append(f'system-artifact:{relative.as_posix()}')
        body=read_text(path)
        if body is None: continue
        if not relative.as_posix().startswith(('scripts/','tests/')) and re.search(r'\b(' + '|'.join(('TO'+'DO','FIX'+'ME','T'+'BD')) + r')\b', body): errors.append(f'unresolved-marker:{relative.as_posix()}')
        if path.suffix=='.md' and not relative.as_posix().startswith('authorship/drafts/'):
            md=parse_metadata(body)
            if md['document_id']:
                if md['document_id'] in docs: errors.append(f'duplicate-document-id:{md["document_id"]}')
                docs[md['document_id']]=relative.as_posix()
                for field in ('state','author','owner','effective','next_review'):
                    if not md[field]: errors.append(f'missing-metadata:{relative.as_posix()}:{field}')
                if md['author'] != 'Don Paulo Ricardo': errors.append(f'author-mismatch:{relative.as_posix()}')
                try:
                    if date.fromisoformat(md['next_review']) < date(2026,6,26): errors.append(f'expired-document:{relative.as_posix()}')
                except Exception: errors.append(f'invalid-review-date:{relative.as_posix()}')
        if relative.as_posix().startswith('policies/') and path.suffix=='.md':
            missing=REQUIRED_POLICY_SECTIONS-headings(body)
            if missing: errors.append(f'policy-sections:{relative.as_posix()}:{"|".join(sorted(missing))}')
    owners=(root/'OWNERS.yaml').read_text(encoding='utf-8') if (root/'OWNERS.yaml').exists() else ''
    owner_ids=set(re.findall(r'^\s*- owner_id:\s*(\S+)', owners, re.M))
    if len(owner_ids)<5: errors.append('owner-registry-too-small')
    try:
        with (root/'CONTROL-MATRIX.csv').open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
        required_cols={'control_id','control','domain','document_id','expected_evidence','frequency','criticality','owner_id','control_type','effectiveness_rule'}
        if not rows or not required_cols.issubset(rows[0].keys()): errors.append('invalid-control-matrix')
        ids=[r['control_id'] for r in rows]
        if len(ids)!=len(set(ids)): errors.append('duplicate-control-id')
        if len(rows)<30: errors.append('insufficient-control-coverage')
        for row in rows:
            if row['owner_id'] not in owner_ids: errors.append(f'unknown-owner:{row["control_id"]}:{row["owner_id"]}')
            if not row['expected_evidence'].strip(): errors.append(f'missing-control-evidence:{row["control_id"]}')
    except Exception as e: errors.append(f'control-matrix-error:{e}')
    manifest=(root/'GOVERNANCE-MANIFEST.yaml').read_text(encoding='utf-8') if (root/'GOVERNANCE-MANIFEST.yaml').exists() else ''
    if 'status: pending-external-signature' not in manifest: errors.append('independent-approval-not-pending')
    if 'author-cannot-approve-own-release' not in manifest: errors.append('self-approval-rule-missing')
    wf=(root/'.github/workflows/governance.yml').read_text(encoding='utf-8') if (root/'.github/workflows/governance.yml').exists() else ''
    if 'permissions:\n  contents: read' not in wf: errors.append('workflow-not-readonly')
    if 'actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683' not in wf: errors.append('checkout-not-pinned')
    return errors, docs


def validate():
    errors,docs=validate_root(ROOT)
    result={'status':'PASS' if not errors else 'FAIL','errors':errors,'documents':len(docs),'files':len(list(iter_files(ROOT)))}
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if not errors else 1


def security():
    findings=[]
    for path in iter_files(ROOT):
        body=read_text(path)
        if body is None: continue
        rel=path.relative_to(ROOT).as_posix()
        for rule,pat in SECRET_PATTERNS.items():
            if pat.search(body): findings.append({'rule':rule,'path':rel})
        if path.suffix in {'.sh','.command'} and re.search(r'\b(rm\s+-rf|git\s+reset\s+--hard|git\s+clean\s+-fdx|rsync\s+--delete)\b',body):
            findings.append({'rule':'destructive-command','path':rel})
    result={'status':'PASS' if not findings else 'FAIL','findings':findings}
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if not findings else 1


def payload_files():
    for p in iter_files(ROOT, include_evidence=False):
        rel=p.relative_to(ROOT).as_posix()
        if rel.startswith('dist/'): continue
        yield p


def write_evidence(output: Path, tests_summary: dict, continuity: dict):
    output.mkdir(parents=True,exist_ok=True)
    errors,docs=validate_root(ROOT)
    (output/'VALIDATION.json').write_text(json.dumps({'status':'PASS' if not errors else 'FAIL','errors':errors,'documents':len(docs)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (output/'TESTS.json').write_text(json.dumps(tests_summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (output/'CONTINUITY-EXERCISE.json').write_text(json.dumps(continuity,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    sec=[]
    for p in iter_files(ROOT):
        body=read_text(p)
        if body:
            for rule,pat in SECRET_PATTERNS.items():
                if pat.search(body): sec.append({'rule':rule,'path':p.relative_to(ROOT).as_posix()})
    (output/'SECURITY.json').write_text(json.dumps({'status':'PASS' if not sec else 'FAIL','findings':sec},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def build(out: Path):
    out.mkdir(parents=True,exist_ok=True)
    items=[]
    for p in payload_files(): items.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha256(p),'size':p.stat().st_size})
    with (out/'PAYLOAD-MANIFEST.csv').open('w',encoding='utf-8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=['path','sha256','size']); wr.writeheader(); wr.writerows(items)
    (out/'PAYLOAD-CHECKSUMS.sha256').write_text(''.join(f"{x['sha256']}  {x['path']}\n" for x in items),encoding='utf-8')
    sbom={'bomFormat':'CycloneDX','specVersion':'1.5','version':1,'metadata':{'component':{'type':'data','name':'regenera-governance','version':'10.0.0'}},'components':[{'type':'file','name':x['path'],'hashes':[{'alg':'SHA-256','content':x['sha256']}]} for x in items]}
    (out/'SBOM.cyclonedx.json').write_text(json.dumps(sbom,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    archive=out/'regenera-governance-payload.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in payload_files():
            rel=p.relative_to(ROOT).as_posix(); info=zipfile.ZipInfo(f'00-governance/{rel}',date_time=(2026,6,26,12,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=((0o755 if rel=='scripts/governance.py' else 0o644)&0xFFFF)<<16
            z.writestr(info,p.read_bytes())
    result={'archive':archive.name,'files':len(items),'sha256':sha256(archive)}
    (out/'BUILD-PROVENANCE.json').write_text(json.dumps({'builder':'scripts/governance.py','offline':True,'deterministic_timestamp':'2026-06-26T12:00:00-03:00',**result},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0


def verify_release(out: Path):
    archive=out/'regenera-governance-payload.zip'; checks=out/'PAYLOAD-CHECKSUMS.sha256'
    errors=[]
    if not archive.is_file(): errors.append('missing-archive')
    if not checks.is_file(): errors.append('missing-checksums')
    if errors: print(json.dumps({'status':'FAIL','errors':errors},indent=2)); return 1
    expected={}
    for line in checks.read_text(encoding='utf-8').splitlines():
        h,rel=line.split('  ',1); expected[rel]=h
    with tempfile.TemporaryDirectory() as td:
        with zipfile.ZipFile(archive) as z: z.extractall(td)
        root=Path(td)/'00-governance'
        for rel,h in expected.items():
            p=root/rel
            if not p.is_file(): errors.append(f'missing:{rel}')
            elif sha256(p)!=h: errors.append(f'hash-mismatch:{rel}')
        found={p.relative_to(root).as_posix() for p in iter_files(root,include_evidence=False)}
        extra=found-set(expected)
        if extra: errors.extend(f'unexpected:{x}' for x in sorted(extra))
        val_errors,_=validate_root(root); errors.extend(f'extracted:{e}' for e in val_errors)
    result={'status':'PASS' if not errors else 'FAIL','errors':errors,'verified_files':len(expected)}
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if not errors else 1


def clean(out: Path):
    if out.exists(): shutil.rmtree(out)
    for p in ROOT.rglob('__pycache__'):
        if p.is_dir(): shutil.rmtree(p)
    for p in ROOT.rglob('*.py[co]'):
        if p.is_file(): p.unlink()
    return 0


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('command',choices=['validate','security','build','verify-release','clean']); ap.add_argument('--out',default=str(ROOT/'dist')); a=ap.parse_args()
    if a.command=='validate': raise SystemExit(validate())
    if a.command=='security': raise SystemExit(security())
    if a.command=='build': raise SystemExit(build(Path(a.out)))
    if a.command=='verify-release': raise SystemExit(verify_release(Path(a.out)))
    raise SystemExit(clean(Path(a.out)))
if __name__=='__main__': main()
