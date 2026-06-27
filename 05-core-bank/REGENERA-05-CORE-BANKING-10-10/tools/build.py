#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile

root = Path(__file__).resolve().parents[1]
build = root / "build"
evidence = root / "evidence"
build.mkdir(parents=True, exist_ok=True)
evidence.mkdir(parents=True, exist_ok=True)

required_reports = [
    evidence / "VALIDATION-REPORT.json",
    evidence / "SECURITY-REPORT.json",
    evidence / "TEST-RESULTS.txt",
]
missing = [str(path.relative_to(root)) for path in required_reports if not path.is_file()]
if missing:
    print("BUILD FAIL: missing evidence: " + ", ".join(missing))
    sys.exit(1)
if "SUMMARY passed=47 failed=0 total=47" not in (evidence / "TEST-RESULTS.txt").read_text(encoding="utf-8"):
    print("BUILD FAIL: tests are not approved")
    sys.exit(1)

if shutil.which("kotlinc") is None:
    print("BUILD FAIL: kotlinc not found")
    sys.exit(1)

with tempfile.TemporaryDirectory(prefix="regenera-core-build-") as temp:
    raw = Path(temp) / "core-banking-domain.raw.jar"
    result = subprocess.run(
        ["kotlinc", str(root / "src/main/kotlin"), "-d", str(raw)],
        cwd=root,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, end="")
        sys.exit(result.returncode)

    target = build / "core-banking-domain.jar"
    with zipfile.ZipFile(raw, "r") as source, zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for name in sorted(source.namelist()):
            data = source.read(name)
            info = zipfile.ZipInfo(name, date_time=(2026, 6, 26, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            output.writestr(info, data)

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def source_files() -> list[Path]:
    selected: list[Path] = []
    for base in (root / "src", root / "db", root / "docs", root / "governance"):
        for path in base.rglob("*"):
            if path.is_file():
                selected.append(path)
    return sorted(selected)

source_components = [
    {
        "path": path.relative_to(root).as_posix(),
        "sha256": sha256_file(path),
        "size": path.stat().st_size,
    }
    for path in source_files()
]
source_tree_hash = hashlib.sha256(
    "\n".join(f"{item['sha256']}  {item['path']}" for item in source_components).encode("utf-8"),
).hexdigest()

sbom = {
    "bomFormat": "CycloneDX",
    "specVersion": "1.5",
    "version": 1,
    "metadata": {
        "component": {
            "type": "application",
            "name": "regenera-core-banking",
            "version": "1.0.0",
        }
    },
    "components": [
        {"type": "framework", "name": "Kotlin Standard Library", "scope": "required"},
        {"type": "platform", "name": "Java Runtime", "scope": "required"},
        {"type": "database", "name": "PostgreSQL", "scope": "optional"},
    ],
    "properties": [
        {"name": "regenera:external-runtime-dependencies", "value": "0"},
        {"name": "regenera:source-files", "value": str(len(source_components))},
    ],
}
(evidence / "SBOM.cdx.json").write_text(
    json.dumps(sbom, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

provenance = {
    "artifact": "build/core-banking-domain.jar",
    "artifact_sha256": sha256_file(build / "core-banking-domain.jar"),
    "artifact_size": (build / "core-banking-domain.jar").stat().st_size,
    "build_command": "kotlinc src/main/kotlin -d core-banking-domain.jar; normalized zip entries",
    "release_version": "1.0.0",
    "release_date": "2026-06-26",
    "source_tree_sha256": source_tree_hash,
    "source_components": source_components,
    "network_access": "not_required",
}
(evidence / "BUILD-PROVENANCE.json").write_text(
    json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(f"BUILD PASS artifact_sha256={provenance['artifact_sha256']}")
