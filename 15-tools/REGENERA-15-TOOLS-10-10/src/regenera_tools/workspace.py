from __future__ import annotations
from pathlib import Path
import re
from .paths import has_residue

PIN=re.compile(r"uses:\s*[^@\s]+@[0-9a-f]{40}\s*$")
def validate_workspace(root: Path, required: list[str]) -> list[str]:
    errors=[]
    for rel in required:
        if not (root/rel).is_file(): errors.append(f"arquivo ausente:{rel}")
    for p in root.rglob("*"):
        rel=p.relative_to(root)
        if has_residue(rel): errors.append(f"resíduo:{rel}")
        if p.is_symlink(): errors.append(f"symlink:{rel}")
        if p.is_file() and p.suffix.lower()==".zip": errors.append(f"zip interno:{rel}")
    return errors

def lint_workflow(text: str)->list[str]:
    errors=[]
    if "permissions:" not in text or "contents: read" not in text: errors.append("permissions mínimas ausentes")
    for line in text.splitlines():
        if "uses:" in line and not PIN.search(line.strip()): errors.append("action sem pin de commit")
    return errors
