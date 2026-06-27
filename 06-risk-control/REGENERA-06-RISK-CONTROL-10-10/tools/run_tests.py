from pathlib import Path
import json, os, sys, unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
result=unittest.TestResult(); suite.run(result)
report={
  'status':'PASS' if result.wasSuccessful() else 'FAIL',
  'tests_run':result.testsRun,
  'failures':[str(test) for test,_ in result.failures],
  'errors':[str(test) for test,_ in result.errors],
  'skipped':len(result.skipped),
}
(ROOT/'evidence').mkdir(exist_ok=True)
(ROOT/'evidence'/'TEST-RESULTS.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
raise SystemExit(0 if result.wasSuccessful() else 1)
