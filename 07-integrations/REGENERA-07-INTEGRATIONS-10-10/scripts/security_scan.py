#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {"dist", ".build-tmp", ".git"}
TEXT_SUFFIXES = {".py", ".md", ".json", ".toml", ".yaml", ".yml", ".sh", ""}

# Os padrões são montados em partes. O scanner não pode acusar a própria regra.
patterns = {
    "private-key": re.compile("BEGIN " + "PRIVATE KEY"),
    "aws-access-key": re.compile("AKIA" + r"[0-9A-Z]{16}"),
    "github-token": re.compile("gh" + "p_" + r"[A-Za-z0-9]{30,}"),
    "generic-secret-assignment": re.compile(r"(?i)(password|client_secret|api_key)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
}
findings: list[dict[str, object]] = []
for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT)
    if set(rel.parts) & EXCLUDED_PARTS:
        continue
    if path.name == Path(__file__).name:
        continue
    if path.suffix.lower() not in TEXT_SUFFIXES:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for name, pattern in patterns.items():
        for match in pattern.finditer(text):
            findings.append({"rule": name, "file": str(rel), "line": text.count("\n", 0, match.start()) + 1})

report = {"schema": "regenera.security-scan.v1", "passed": not findings, "high_confidence_findings": findings}
(ROOT / ".build-tmp").mkdir(exist_ok=True)
(ROOT / ".build-tmp" / "security.json").write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(report, sort_keys=True, ensure_ascii=False))
raise SystemExit(0 if not findings else 1)
