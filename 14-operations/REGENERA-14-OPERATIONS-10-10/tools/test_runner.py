from pathlib import Path
import json, os, sys, unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src")); sys.path.insert(0,str(ROOT/"tests"))
suite=unittest.defaultTestLoader.discover(str(ROOT/"tests"),pattern="test_*.py")
count=suite.countTestCases()
result=unittest.TextTestRunner(verbosity=1).run(suite)
out=ROOT/"evidence/test"; out.mkdir(parents=True,exist_ok=True)
report={"suite":"operations","status":"PASSED" if result.wasSuccessful() else "FAILED","tests_run":result.testsRun,"expected":count,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}
(out/"TEST-RESULTS.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print(f"TESTS: {result.testsRun}/{count} {'PASS' if result.wasSuccessful() else 'FAIL'}")
sys.exit(0 if result.wasSuccessful() and result.testsRun==count else 1)
