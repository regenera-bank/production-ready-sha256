#!/usr/bin/env python3
import pathlib, shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
for p in list(ROOT.rglob('__pycache__')):
    if p.is_dir(): shutil.rmtree(p)
for p in ROOT.rglob('*.pyc'): p.unlink(missing_ok=True)
for name in ['TEST-RESULTS.json','SECURITY-REPORT.json','RELEASE-GATE.json','BUILD-SUMMARY.json']:
    (ROOT/'evidence/results'/name).unlink(missing_ok=True)
for name in ['PAYLOAD-MANIFEST.json','PAYLOAD-CHECKSUMS.sha256','SBOM.cdx.json']:
    (ROOT/'evidence'/name).unlink(missing_ok=True)
print('CLEAN: PASS')
