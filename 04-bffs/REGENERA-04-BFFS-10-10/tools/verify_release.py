#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
checks = DIST / 'release/PACKAGE-CHECKSUMS.sha256'
problems = []
listed = set()
if not checks.is_file():
    problems.append('missing-checksums')
else:
    for line in checks.read_text().splitlines():
        if not line.strip(): continue
        expected, rel = line.split('  ', 1)
        listed.add(rel)
        path = DIST / rel
        if not path.is_file(): problems.append(f'missing:{rel}'); continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected: problems.append(f'hash:{rel}')
actual_files = {p.relative_to(DIST).as_posix() for p in DIST.rglob('*') if p.is_file() and p.name != 'PACKAGE-CHECKSUMS.sha256'}
for rel in sorted(actual_files - listed): problems.append(f'unlisted:{rel}')
for rel in sorted(listed - actual_files): problems.append(f'orphan:{rel}')
for forbidden in ('.DS_Store', '__MACOSX', '__pycache__'):
    if any(forbidden in p.parts or p.name == forbidden for p in DIST.rglob('*')):
        problems.append(f'forbidden:{forbidden}')
report = {'status': 'PASS' if not problems else 'FAIL', 'problems': problems, 'covered_files': len(listed)}
(ROOT / 'evidence/RELEASE-VERIFICATION.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
sys.exit(0 if not problems else 1)
