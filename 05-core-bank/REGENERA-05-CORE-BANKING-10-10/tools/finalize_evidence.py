#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
evidence = root / "evidence"
manifest_path = evidence / "MANIFEST.json"
checksums_path = evidence / "PACKAGE-CHECKSUMS.sha256"
for path in (manifest_path, checksums_path):
    if path.exists():
        path.unlink()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

payload = []
for path in sorted(root.rglob("*")):
    if not path.is_file():
        continue
    if path in {manifest_path, checksums_path}:
        continue
    payload.append({
        "path": path.relative_to(root).as_posix(),
        "sha256": sha256_file(path),
        "size": path.stat().st_size,
    })
manifest = {
    "artifact": "REGENERA-05-CORE-BANKING-10-10",
    "version": "1.0.0",
    "release_date": "2026-06-26",
    "payload_count": len(payload),
    "payload": payload,
}
manifest_path.write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

checksum_files = [path for path in sorted(root.rglob("*")) if path.is_file() and path != checksums_path]
checksums_path.write_text(
    "".join(f"{sha256_file(path)}  {path.relative_to(root).as_posix()}\n" for path in checksum_files),
    encoding="utf-8",
)
print(f"EVIDENCE PASS payload={len(payload)} checksums={len(checksum_files)}")
