#!/usr/bin/env python3
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
RELEASE_NAME = "REGENERA-07-INTEGRATIONS-10-10"
DIST = ROOT / "dist" / RELEASE_NAME
SOURCE_ITEMS = [
    "src", "tests", "scripts", "docs", "governance",
    "README.md", "README-APLICACAO.md", "CHANGELOG.md", "Makefile", "pyproject.toml",
    "DECLARACAO-PROCEDENCIA.md", "HISTORICO-INCREMENTAL.md",
    "ATA-REVISAO-TECNICA.md", "ASSINATURA-EXTERNA-REQUERIDA.md",
]

for required in ("validation.json", "test-results.json", "security.json"):
    if not (ROOT / ".build-tmp" / required).is_file():
        raise SystemExit(f"evidência ausente: {required}")

shutil.rmtree(DIST, ignore_errors=True)
DIST.mkdir(parents=True)
for item in SOURCE_ITEMS:
    source = ROOT / item
    target = DIST / item
    if source.is_dir():
        shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

(DIST / "evidence").mkdir()
for name in ("validation.json", "test-results.json", "security.json"):
    shutil.copy2(ROOT / ".build-tmp" / name, DIST / "evidence" / name)

files = sorted(path for path in DIST.rglob("*") if path.is_file())
manifest = {
    "schema": "regenera.release-manifest.v1",
    "release": RELEASE_NAME,
    "release_date": "2026-06-26",
    "payload_file_count_before_evidence": len(files),
    "activation_status": "BLOCKED_EXTERNAL_APPROVAL",
    "author": "Don Paulo Ricardo",
    "independent_approval": "PENDING",
    "signature": "PENDING_EXTERNAL_GPG",
}
(DIST / "RELEASE-MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

sbom = {
    "bomFormat": "CycloneDX",
    "specVersion": "1.5",
    "version": 1,
    "metadata": {"component": {"type": "application", "name": "regenera-integrations", "version": "1.0.0"}},
    "components": [],
    "properties": [{"name": "regenera.runtime_dependencies", "value": "python-standard-library-only"}],
}
(DIST / "SBOM.cdx.json").write_text(json.dumps(sbom, indent=2, sort_keys=True) + "\n", encoding="utf-8")

source_inventory = json.loads((ROOT / "governance" / "SOURCE-INVENTORY.json").read_text(encoding="utf-8"))
provenance = {
    "schema": "regenera.build-provenance.v1",
    "builder": "scripts/build_release.py",
    "source_archive_sha256": source_inventory["source_sha256"],
    "build_inputs": SOURCE_ITEMS,
    "network_used": False,
    "external_dependencies_installed": False,
    "generated_at": "2026-06-26T00:00:00-03:00",
}
(DIST / "BUILD-PROVENANCE.json").write_text(json.dumps(provenance, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

checksum_file = DIST / "PAYLOAD-CHECKSUMS.sha256"
covered = sorted(path for path in DIST.rglob("*") if path.is_file() and path != checksum_file)
with checksum_file.open("w", encoding="utf-8", newline="\n") as stream:
    for path in covered:
        stream.write(f"{sha256(path.read_bytes()).hexdigest()}  {path.relative_to(DIST).as_posix()}\n")
print(json.dumps({"release": RELEASE_NAME, "covered_files": len(covered)}, sort_keys=True))
