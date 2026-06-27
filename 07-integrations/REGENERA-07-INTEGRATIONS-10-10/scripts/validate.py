#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {"dist", ".build-tmp", ".git"}
FORBIDDEN_NAMES = {".DS_Store", "__MACOSX", "__pycache__"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".zip", ".rar", ".7z"}
REQUIRED = [
    "README.md",
    "Makefile",
    "pyproject.toml",
    "governance/CONTROL-MATRIX.json",
    "governance/INTEGRATION-REGISTRY.json",
    "governance/OWNERSHIP.json",
    "governance/APPROVAL-RECORD.json",
    "governance/SOURCE-INVENTORY.json",
    "docs/architecture/INTEGRATION-ARCHITECTURE.md",
    "docs/policies/TRANSPORT-AND-SECURITY-POLICY.md",
    "docs/policies/RETRY-IDEMPOTENCY-UNKNOWN-POLICY.md",
    "docs/policies/THIRD-PARTY-LIFECYCLE-POLICY.md",
    "docs/runbooks/UNKNOWN-OUTCOME.md",
    "docs/runbooks/PROVIDER-OUTAGE.md",
]
POLICY_SECTIONS = {
    "## Objetivo",
    "## Escopo",
    "## Responsabilidades",
    "## Controles obrigatórios",
    "## Evidências",
    "## Exceções",
    "## Revisão",
}

errors: list[str] = []
for item in REQUIRED:
    if not (ROOT / item).is_file():
        errors.append(f"missing:{item}")

for path in ROOT.rglob("*"):
    rel = path.relative_to(ROOT)
    if set(rel.parts) & EXCLUDED:
        continue
    if path.is_symlink():
        errors.append(f"symlink:{rel}")
    if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
        errors.append(f"system-or-archive:{rel}")
    if path.is_file() and path.stat().st_size == 0:
        errors.append(f"empty-file:{rel}")

for path in (ROOT / "src").rglob("*.py"):
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        errors.append(f"syntax:{path.relative_to(ROOT)}:{exc.lineno}")

for path in (ROOT / "docs" / "policies").glob("*.md"):
    text = path.read_text(encoding="utf-8")
    missing = sorted(POLICY_SECTIONS - set(line.strip() for line in text.splitlines()))
    if missing:
        errors.append(f"policy-sections:{path.relative_to(ROOT)}:{'|'.join(missing)}")

try:
    registry = json.loads((ROOT / "governance/INTEGRATION-REGISTRY.json").read_text(encoding="utf-8"))
    if len(registry["integrations"]) != 14:
        errors.append("integration-registry-count")
    codes = [item["code"] for item in registry["integrations"]]
    if len(codes) != len(set(codes)):
        errors.append("integration-registry-duplicate")
    for item in registry["integrations"]:
        if not item.get("external_evidence_required"):
            errors.append(f"integration-evidence:{item.get('code')}")
        if item.get("status") == "PRODUCTION_ACTIVE":
            errors.append(f"unsupported-production-claim:{item.get('code')}")
except Exception as exc:
    errors.append(f"integration-registry-invalid:{exc}")

try:
    controls = json.loads((ROOT / "governance/CONTROL-MATRIX.json").read_text(encoding="utf-8"))
    if len(controls["controls"]) < 20:
        errors.append("control-matrix-too-small")
    for control in controls["controls"]:
        for field in ("control_id", "owner", "evidence", "frequency", "blocking", "test_reference"):
            if not control.get(field):
                errors.append(f"control-field:{control.get('control_id')}:{field}")
except Exception as exc:
    errors.append(f"control-matrix-invalid:{exc}")

approval = json.loads((ROOT / "governance/APPROVAL-RECORD.json").read_text(encoding="utf-8"))
if approval.get("author") == approval.get("independent_approver") and approval.get("independent_approver"):
    errors.append("self-approval")
if approval.get("release_authorized") is True and not approval.get("signature_reference"):
    errors.append("unsigned-approval")

report = {"schema": "regenera.validation.v1", "passed": not errors, "errors": sorted(errors)}
(ROOT / ".build-tmp").mkdir(exist_ok=True)
(ROOT / ".build-tmp" / "validation.json").write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(report, sort_keys=True, ensure_ascii=False))
raise SystemExit(0 if not errors else 1)
