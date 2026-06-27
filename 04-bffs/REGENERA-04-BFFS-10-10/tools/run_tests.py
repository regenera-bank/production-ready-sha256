#!/usr/bin/env python3
from pathlib import Path
import json, re, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
files = [str(path.relative_to(ROOT)) for path in sorted((ROOT / 'tests').glob('*.test.mjs'))]
cmd = ['node', '--test', '--test-reporter=tap', *files]
proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
raw = proc.stdout + proc.stderr
summary = {}
for key in ('tests', 'pass', 'fail', 'cancelled', 'skipped', 'todo'):
    match = re.search(rf'^# {key} (\d+)$', raw, re.MULTILINE)
    summary[key] = int(match.group(1)) if match else None
summary['exit_code'] = proc.returncode
summary['status'] = 'PASS' if proc.returncode == 0 and summary.get('fail') == 0 else 'FAIL'
normalized = re.sub(r'^# duration_ms .*$', '# duration_ms NORMALIZED', raw, flags=re.MULTILINE)
normalized = re.sub(r'duration_ms: [0-9.]+', 'duration_ms: NORMALIZED', normalized)
(ROOT / 'evidence').mkdir(exist_ok=True)
(ROOT / 'evidence/TEST-RESULTS.log').write_text(normalized)
(ROOT / 'evidence/TEST-RESULTS.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, ensure_ascii=False))
sys.exit(proc.returncode)
