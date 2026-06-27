from pathlib import Path
import json
import re

ROOT = Path(__file__).parents[1]
findings = []
patterns = {
    'private-key': re.compile('-----BEGIN ' + 'PRIVATE KEY-----'),
    'aws-access-key': re.compile('AKIA' + r'[A-Z0-9]{16}'),
    'github-token': re.compile('gh' + r'[pousr]_[A-Za-z0-9]{30,}'),
    'generic-secret-assignment': re.compile(r'(?i)(password|secret|token)\s*[=:]\s*["\'][^"\']{12,}["\']'),
}
text_ext = {'.py', '.md', '.json', '.toml', '.xml', '.csv', '.yml', '.yaml', '.sh', '.txt'}
for path in ROOT.rglob('*'):
    if not path.is_file() or path.suffix not in text_ext:
        continue
    if any(part in {'build', '__pycache__'} for part in path.parts):
        continue
    if path == Path(__file__) or 'tests/fixtures/invalid' in path.as_posix():
        continue
    text = path.read_text(encoding='utf-8', errors='ignore')
    for name, pattern in patterns.items():
        if pattern.search(text):
            findings.append({'type': name, 'file': path.relative_to(ROOT).as_posix()})
output = ROOT / 'evidence' / 'generated'
output.mkdir(parents=True, exist_ok=True)
report = {'status': 'PASS' if not findings else 'FAIL', 'findings': findings, 'exit_code': 0 if not findings else 1}
(output / 'SECURITY-RESULTS.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(report['exit_code'])
