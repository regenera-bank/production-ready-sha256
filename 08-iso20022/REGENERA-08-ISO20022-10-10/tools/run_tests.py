from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).parents[1]
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))

suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_*.py')
result = unittest.TextTestRunner(verbosity=2).run(suite)
output = ROOT / 'evidence' / 'generated'
output.mkdir(parents=True, exist_ok=True)
report = {
    'command': 'python tools/run_tests.py',
    'tests_run': result.testsRun,
    'failures': len(result.failures),
    'errors': len(result.errors),
    'skipped': len(result.skipped),
    'status': 'PASS' if result.wasSuccessful() else 'FAIL',
    'exit_code': 0 if result.wasSuccessful() else 1,
}
(output / 'TEST-RESULTS.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
raise SystemExit(report['exit_code'])
