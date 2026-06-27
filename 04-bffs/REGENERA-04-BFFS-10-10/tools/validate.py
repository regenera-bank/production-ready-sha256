#!/usr/bin/env python3
from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[1]
problems = []

required = [
    'README.md', 'Makefile', 'config/services.json', 'contracts/bff-boundaries.json',
    'governance/CONTROL-MATRIX.json', 'packages/shared/src/idempotency.mjs',
    'packages/web-bff/src/index.mjs', 'packages/mobile-bff/src/index.mjs',
    'packages/operations-bff/src/index.mjs', 'packages/partner-api/src/index.mjs',
    'packages/open-finance-api/src/index.mjs'
]
for rel in required:
    if not (ROOT / rel).is_file(): problems.append(f'missing:{rel}')

for path in ROOT.rglob('*'):
    rel = path.relative_to(ROOT).as_posix()
    if any(part in {'.git', 'dist'} for part in path.parts): continue
    if path.is_dir() and path.name in {'__MACOSX', '__pycache__', '.regenera-' + 'agent', 'source' + '-material'}:
        problems.append(f'forbidden-dir:{rel}')
    if path.is_file():
        if path.name == '.DS_Store' or path.suffix in {'.pyc', '.zip'}:
            problems.append(f'forbidden-file:{rel}')
        if path.suffix == '.json':
            try: json.loads(path.read_text(encoding='utf-8'))
            except Exception as exc: problems.append(f'invalid-json:{rel}:{exc}')

services = json.loads((ROOT / 'config/services.json').read_text())['services']
if len(services) != 5: problems.append('services-count')
if any(item.get('authoritative_financial_source') is not False for item in services):
    problems.append('authoritative-bff')

active = [ROOT / 'packages', ROOT / 'docs', ROOT / 'governance', ROOT / 'contracts', ROOT / 'config']
for base in active:
    for path in base.rglob('*'):
        if not path.is_file() or path.suffix not in {'.mjs', '.md', '.json'}: continue
        text = path.read_text(encoding='utf-8', errors='replace').lower()
        banned = ['generated' + ' by', 'as an ' + 'ai', 'enterprise system', 'ultra-optimized', 'hyper-secure']
        for term in banned:
            if term in text: problems.append(f'prohibited-text:{path.relative_to(ROOT)}:{term}')

report = {'status': 'PASS' if not problems else 'FAIL', 'problems': sorted(problems)}
(ROOT / 'evidence').mkdir(exist_ok=True)
(ROOT / 'evidence/VALIDATION-REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
sys.exit(0 if not problems else 1)
