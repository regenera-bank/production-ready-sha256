#!/usr/bin/env python3
import json
import os
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
os.environ["PYTHONDONTWRITEBYTECODE"]="1"
suite=unittest.defaultTestLoader.discover(str(ROOT/"tests"),pattern="test_*.py")
count=suite.countTestCases()
result=unittest.TextTestRunner(verbosity=2).run(suite)
out={
    "tests":count,
    "passed":count-len(result.failures)-len(result.errors)-len(result.skipped),
    "failures":len(result.failures),
    "errors":len(result.errors),
    "skipped":len(result.skipped),
    "status":"PASS" if result.wasSuccessful() else "FAIL",
}
path=ROOT/"evidence/test/TEST-RESULTS.json"
path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
if not result.wasSuccessful(): sys.exit(1)
print(f"TESTS: PASS ({count}/{count})")
