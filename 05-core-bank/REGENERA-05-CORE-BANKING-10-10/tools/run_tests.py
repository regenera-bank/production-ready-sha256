#!/usr/bin/env python3
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
evidence = root / "evidence"
evidence.mkdir(parents=True, exist_ok=True)

if shutil.which("kotlinc") is None:
    print("TEST FAIL: kotlinc not found")
    sys.exit(1)
if shutil.which("java") is None:
    print("TEST FAIL: java not found")
    sys.exit(1)

with tempfile.TemporaryDirectory(prefix="regenera-core-tests-") as temp:
    jar = Path(temp) / "core-banking-tests.jar"
    compile_cmd = [
        "kotlinc",
        str(root / "src/main/kotlin"),
        str(root / "src/test/kotlin"),
        "-include-runtime",
        "-d",
        str(jar),
    ]
    compiled = subprocess.run(compile_cmd, cwd=root, text=True, capture_output=True)
    if compiled.returncode != 0:
        print(compiled.stdout, end="")
        print(compiled.stderr, end="")
        sys.exit(compiled.returncode)
    executed = subprocess.run(["java", "-jar", str(jar)], cwd=root, text=True, capture_output=True)

output = executed.stdout.replace("\r\n", "\n")
if executed.stderr:
    output += executed.stderr.replace("\r\n", "\n")
(evidence / "TEST-RESULTS.txt").write_text(output, encoding="utf-8")
print(output, end="")

summary = re.search(r"SUMMARY passed=(\d+) failed=(\d+) total=(\d+)", output)
if executed.returncode != 0 or summary is None:
    sys.exit(executed.returncode or 1)
passed, failed, total = map(int, summary.groups())
if failed != 0 or passed != total or total < 45:
    print(f"TEST FAIL: passed={passed} failed={failed} total={total}")
    sys.exit(1)
