#!/usr/bin/env python3
import hashlib, json, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'evidence/PAYLOAD-MANIFEST.json').read_text())['files']
for item in manifest:
    p=ROOT/item['path']
    if not p.is_file(): raise SystemExit('missing:'+item['path'])
    if p.stat().st_size!=item['size']: raise SystemExit('size_mismatch:'+item['path'])
    if hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']: raise SystemExit('hash_mismatch:'+item['path'])
listed={x['path'] for x in manifest}
excluded={'evidence/PAYLOAD-MANIFEST.json','evidence/PAYLOAD-CHECKSUMS.sha256'}
actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.relative_to(ROOT).as_posix() not in excluded}
if listed!=actual: raise SystemExit('manifest_coverage_mismatch')
print('VERIFY-RELEASE: PASS',len(manifest))
