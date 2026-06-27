#!/usr/bin/env python3
from pathlib import Path
import shutil, json, hashlib
from common import ROOT, load, sha256
DIST=ROOT/'dist'; TMP=ROOT/'dist.tmp'
if TMP.exists(): shutil.rmtree(TMP)
TMP.mkdir()
for section in ('openapi','asyncapi','json-schema','error-catalog'):
    src=ROOT/'contracts'/section
    dst=TMP/section
    shutil.copytree(src,dst)
manifest=[]
for p in sorted(TMP.rglob('*')):
    if p.is_file(): manifest.append({'path':str(p.relative_to(TMP)),'sha256':sha256(p),'size':p.stat().st_size})
(TMP/'manifest.json').write_text(json.dumps({'version':(ROOT/'VERSION').read_text().strip(),'files':manifest},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
if DIST.exists(): shutil.rmtree(DIST)
TMP.replace(DIST)
print(f'build: PASS ({len(manifest)} contract files)')
