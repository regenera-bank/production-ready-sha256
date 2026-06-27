from pathlib import Path
import ast
import json
import sys

ROOT = Path(__file__).parents[1]
failures = []
for path in ROOT.rglob('*'):
    rel = path.relative_to(ROOT).as_posix()
    if any(part in {'build', '__pycache__'} for part in path.parts):
        continue
    if path.is_file():
        if path.name == '.DS_Store' or path.suffix == '.pyc' or '__MACOSX' in path.parts:
            failures.append(f'system-artifact:{rel}')
        if path.suffix == '.zip':
            failures.append(f'nested-zip:{rel}')
        if path.stat().st_size == 0:
            failures.append(f'empty-file:{rel}')
        if path.suffix == '.py':
            try:
                ast.parse(path.read_text(encoding='utf-8'))
            except SyntaxError as exc:
                failures.append(f'python-syntax:{rel}:{exc.lineno}')
required = [
    'README.md', 'Makefile', 'profiles/message-profiles.json',
    'governance/controls.csv', 'governance/APPROVAL-RECORD.json',
    'docs/ARCHITECTURE.md', 'docs/policies/MESSAGE-GOVERNANCE.md',
    'docs/runbooks/UNKNOWN-DELIVERY.md',
]
for rel in required:
    if not (ROOT / rel).is_file():
        failures.append(f'missing:{rel}')
profile = json.loads((ROOT / 'profiles/message-profiles.json').read_text(encoding='utf-8'))
if profile.get('external_activation') != 'BLOCKED_UNTIL_OFFICIAL_XSD_AND_INSTITUTIONAL_APPROVAL':
    failures.append('external-activation-not-blocked')
output = ROOT / 'evidence' / 'generated'
output.mkdir(parents=True, exist_ok=True)
report = {'status': 'PASS' if not failures else 'FAIL', 'failures': failures, 'exit_code': 0 if not failures else 1}
(output / 'VALIDATION-RESULTS.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(report['exit_code'])
