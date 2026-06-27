#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

root = Path(__file__).resolve().parents[1]
evidence = root / "evidence"
evidence.mkdir(parents=True, exist_ok=True)

patterns = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "jwt_literal": re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    "password_assignment": re.compile(r"(?i)\b(?:password|passwd)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
}

findings: list[dict[str, object]] = []
scan_suffixes = {".kt", ".sql", ".md", ".json", ".csv", ".py", ".yml", ".yaml"}
for path in root.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in scan_suffixes:
        continue
    rel = path.relative_to(root).as_posix()
    if rel.startswith("build/") or rel.startswith("evidence/") or rel == "tools/security_scan.py":
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    for name, pattern in patterns.items():
        for match in pattern.finditer(text):
            findings.append({
                "rule": name,
                "file": rel,
                "offset": match.start(),
                "value": "REDACTED",
            })

report = {
    "status": "PASS" if not findings else "FAIL",
    "files_scanned": sum(
        1 for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in scan_suffixes
    ),
    "findings": findings,
}
(evidence / "SECURITY-REPORT.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(f"SECURITY {report['status']} findings={len(findings)}")
if findings:
    sys.exit(1)
