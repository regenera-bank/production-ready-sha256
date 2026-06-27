#!/usr/bin/env python3
from pathlib import Path
import csv
import json
import re
import stat
import sys

root = Path(__file__).resolve().parents[1]
evidence = root / "evidence"
evidence.mkdir(parents=True, exist_ok=True)

errors: list[str] = []
checks: list[dict[str, object]] = []

def record(name: str, passed: bool, detail: str) -> None:
    checks.append({"check": name, "status": "PASS" if passed else "FAIL", "detail": detail})
    if not passed:
        errors.append(f"{name}: {detail}")

forbidden_names = {".DS_Store", "Thumbs.db"}
forbidden_dirs = {"__MACOSX", "__pycache__", ".regenera-agent", "node_modules"}
forbidden_suffixes = {".pyc", ".pyo", ".swp", ".tmp", ".zip"}

bad_paths: list[str] = []
empty_files: list[str] = []
world_writable: list[str] = []
for path in root.rglob("*"):
    rel = path.relative_to(root).as_posix()
    if any(part in forbidden_dirs for part in path.parts):
        bad_paths.append(rel)
    if path.is_file():
        if path.name in forbidden_names or path.suffix.lower() in forbidden_suffixes:
            bad_paths.append(rel)
        if path.stat().st_size == 0:
            empty_files.append(rel)
        if path.stat().st_mode & stat.S_IWOTH:
            world_writable.append(rel)

record("no_forbidden_artifacts", not bad_paths, ", ".join(sorted(set(bad_paths))) or "clean")
record("no_empty_files", not empty_files, ", ".join(empty_files) or "clean")
record("no_world_writable_files", not world_writable, ", ".join(world_writable) or "clean")

required = [
    "README.md",
    "RELEASE.json",
    "Makefile",
    "src/main/kotlin/com/regenera/core/Money.kt",
    "src/main/kotlin/com/regenera/core/Ledger.kt",
    "src/main/kotlin/com/regenera/core/Payments.kt",
    "src/test/kotlin/com/regenera/core/CoreBankingTestMain.kt",
    "db/migrations/V001__core_banking_foundation.sql",
    "governance/controls/CONTROL-MATRIX.csv",
    "governance/OWNERS.json",
]
missing = [name for name in required if not (root / name).is_file()]
record("required_files", not missing, ", ".join(missing) or "present")

content_roots = [root / "src", root / "db", root / "docs", root / "governance"]
forbidden_fragments = [
    "Generated" + " by",
    "As an" + " AI",
    "REGENERA " + "ENTERPRISE SYSTEM",
    "Ultra-" + "Optimized",
    "Hyper-" + "secure",
    "lifecycle:" + " experimental",
    "TODO" + ": implement",
    "FIX" + "ME",
]
content_hits: list[str] = []
for base in content_roots:
    for path in base.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".kt", ".sql", ".md", ".json", ".csv"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for fragment in forbidden_fragments:
            if fragment.lower() in text.lower():
                content_hits.append(f"{path.relative_to(root)}:{fragment}")
record("no_synthetic_signatures", not content_hits, ", ".join(content_hits) or "clean")

sql = (root / "db/migrations/V001__core_banking_foundation.sql").read_text(encoding="utf-8")
sql_requirements = [
    "CREATE TABLE journal_entries",
    "CREATE TABLE ledger_postings",
    "CREATE TABLE idempotency_records",
    "CREATE TABLE payments",
    "CREATE TABLE outbox_events",
    "CREATE TABLE reconciliation_cases",
    "CREATE TABLE audit_events",
    "LEDGER_UNBALANCED",
    "trg_postings_immutable",
    "trg_audit_events_immutable",
]
missing_sql = [item for item in sql_requirements if item not in sql]
record("sql_controls_present", not missing_sql, ", ".join(missing_sql) or "present")

with (root / "governance/controls/CONTROL-MATRIX.csv").open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
required_columns = {
    "control_id", "domain", "control", "owner", "executor", "frequency",
    "blocking", "evidence", "test_reference", "status",
}
columns = set(rows[0].keys()) if rows else set()
record("control_matrix_columns", required_columns.issubset(columns), str(sorted(columns)))
record("control_matrix_depth", len(rows) >= 20, f"controls={len(rows)}")
record(
    "control_matrix_no_unowned",
    all(row.get("owner", "").strip() for row in rows),
    "all controls have owner" if rows and all(row.get("owner", "").strip() for row in rows) else "owner missing",
)
allowed_status = {"TESTED", "SPECIFIED", "PENDING_EXTERNAL"}
invalid_status = [row["control_id"] for row in rows if row.get("status") not in allowed_status]
record("control_matrix_status", not invalid_status, ", ".join(invalid_status) or "valid")

owners = json.loads((root / "governance/OWNERS.json").read_text(encoding="utf-8"))
owner_name = owners.get("document_owner", {}).get("name", "").strip()
record("nominal_owner", owner_name == "Don Paulo Ricardo", owner_name or "missing")
record(
    "independent_review_block",
    owners.get("production_activation") == "BLOCKED_UNTIL_INDEPENDENT_APPROVAL",
    str(owners.get("production_activation")),
)

release = json.loads((root / "RELEASE.json").read_text(encoding="utf-8"))
record("release_signature_pending", release.get("signature_status") == "EXTERNAL_SIGNATURE_REQUIRED", str(release.get("signature_status")))
record("production_not_self_approved", release.get("production_activation") == "BLOCKED_PENDING_EXTERNAL_EVIDENCE", str(release.get("production_activation")))

report = {
    "status": "PASS" if not errors else "FAIL",
    "checks": checks,
    "errors": errors,
}
(evidence / "VALIDATION-REPORT.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(f"VALIDATION {report['status']} checks={len(checks)} errors={len(errors)}")
if errors:
    for error in errors:
        print(error)
    sys.exit(1)
