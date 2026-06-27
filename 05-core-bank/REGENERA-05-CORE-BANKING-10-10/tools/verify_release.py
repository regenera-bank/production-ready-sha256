#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import sys

root = Path(__file__).resolve().parents[1]
evidence = root / "evidence"
checksums_path = evidence / "PACKAGE-CHECKSUMS.sha256"
manifest_path = evidence / "MANIFEST.json"
errors: list[str] = []

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

if not checksums_path.is_file() or not manifest_path.is_file():
    print("VERIFY FAIL: manifest or checksums missing")
    sys.exit(1)

listed: dict[str, str] = {}
for line in checksums_path.read_text(encoding="utf-8").splitlines():
    digest, relative = line.split("  ", 1)
    listed[relative] = digest

actual_files = {
    path.relative_to(root).as_posix(): path
    for path in root.rglob("*")
    if path.is_file() and path != checksums_path
}
for relative, path in actual_files.items():
    expected = listed.get(relative)
    if expected is None:
        errors.append(f"unlisted:{relative}")
    elif expected != sha256_file(path):
        errors.append(f"hash-mismatch:{relative}")
for relative in listed:
    if relative not in actual_files:
        errors.append(f"missing:{relative}")

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest_payload = {item["path"]: item for item in manifest["payload"]}
expected_payload = {
    relative: path for relative, path in actual_files.items()
    if relative not in {"evidence/MANIFEST.json"}
}
for relative, path in expected_payload.items():
    item = manifest_payload.get(relative)
    if item is None:
        errors.append(f"manifest-unlisted:{relative}")
    elif item["sha256"] != sha256_file(path) or item["size"] != path.stat().st_size:
        errors.append(f"manifest-mismatch:{relative}")
for relative in manifest_payload:
    if relative not in expected_payload:
        errors.append(f"manifest-orphan:{relative}")

for report_name in ("VALIDATION-REPORT.json", "SECURITY-REPORT.json"):
    report = json.loads((evidence / report_name).read_text(encoding="utf-8"))
    if report.get("status") != "PASS":
        errors.append(f"report-failed:{report_name}")
if "SUMMARY passed=47 failed=0 total=47" not in (evidence / "TEST-RESULTS.txt").read_text(encoding="utf-8"):
    errors.append("tests-not-approved")

print(f"VERIFY {'PASS' if not errors else 'FAIL'} files={len(actual_files)} errors={len(errors)}")
for error in errors:
    print(error)
if errors:
    sys.exit(1)
