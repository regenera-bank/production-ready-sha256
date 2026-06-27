#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import os
from pathlib import Path
import sys
import unittest
import shutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True

suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
buffer = io.StringIO()
result = unittest.TextTestRunner(stream=buffer, verbosity=2).run(suite)

build_tmp = ROOT / ".build-tmp"
build_tmp.mkdir(exist_ok=True)
report = {
    "schema": "regenera.test-results.v1",
    "tests_run": result.testsRun,
    "failures": len(result.failures),
    "errors": len(result.errors),
    "skipped": len(result.skipped),
    "successful": result.wasSuccessful(),
}
(build_tmp / "test-results.json").write_text(
    json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
print(buffer.getvalue(), end="")
print(json.dumps(report, sort_keys=True, ensure_ascii=False))
for cache in ROOT.rglob("__pycache__"):
    shutil.rmtree(cache, ignore_errors=True)
for bytecode in ROOT.rglob("*.pyc"):
    bytecode.unlink(missing_ok=True)
raise SystemExit(0 if result.wasSuccessful() else 1)
