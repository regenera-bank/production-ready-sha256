#!/usr/bin/env python3
import json, pathlib, sys, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
count=suite.countTestCases()
result=unittest.TextTestRunner(verbosity=2).run(suite)
summary={"suite":"regenera-quality","passed":count-len(result.failures)-len(result.errors),"failed":len(result.failures),"errors":len(result.errors),"status":"PASS" if result.wasSuccessful() else "FAIL"}
out=ROOT/'evidence/results/TEST-RESULTS.json'; out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
raise SystemExit(0 if result.wasSuccessful() else 1)
