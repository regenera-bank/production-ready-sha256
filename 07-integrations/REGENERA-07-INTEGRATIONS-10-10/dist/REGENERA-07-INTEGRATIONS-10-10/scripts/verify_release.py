#!/usr/bin/env python3
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "REGENERA-07-INTEGRATIONS-10-10"
checksum_file = DIST / "PAYLOAD-CHECKSUMS.sha256"
errors: list[str] = []
listed: set[str] = set()
if not checksum_file.is_file():
    errors.append("missing-checksum-file")
else:
    for raw in checksum_file.read_text(encoding="utf-8").splitlines():
        expected, relative = raw.split("  ", 1)
        listed.add(relative)
        path = DIST / relative
        if not path.is_file():
            errors.append(f"missing:{relative}")
        elif sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(f"mismatch:{relative}")
actual = {
    path.relative_to(DIST).as_posix()
    for path in DIST.rglob("*")
    if path.is_file() and path != checksum_file
}
for extra in sorted(actual - listed):
    errors.append(f"uncovered:{extra}")
for stale in sorted(listed - actual):
    errors.append(f"stale:{stale}")
report = {"schema": "regenera.release-verification.v1", "passed": not errors, "covered_files": len(listed), "errors": errors}
print(json.dumps(report, sort_keys=True, ensure_ascii=False))
raise SystemExit(0 if not errors else 1)
