from __future__ import annotations
import json, re
from pathlib import Path

def from_pyproject(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"dependencies\s*=\s*\[(.*?)\]", text, re.S)
    if not match:
        return []
    names = re.findall(r'''["']([^"']+)["']''', match.group(1))
    return [{"type": "library", "name": name} for name in names]

def from_package_lock(path: Path) -> list[dict[str, str]]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    out: list[dict[str, str]] = []
    for key, value in sorted(doc.get("packages", {}).items()):
        if not key or not isinstance(value, dict):
            continue
        out.append({
            "type": "library",
            "name": value.get("name") or key.rsplit("/", 1)[-1],
            "version": str(value.get("version", "UNKNOWN")),
        })
    return out
