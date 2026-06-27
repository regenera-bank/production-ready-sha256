from __future__ import annotations
from pathlib import Path
import json
from .canonical import sha256_file
from .errors import IntegrityError
from .paths import has_residue

def payload_files(root: Path, exclusions: set[str]) -> list[Path]:
    files=[]
    for p in root.rglob("*"):
        rel=str(p.relative_to(root))
        if rel in exclusions: continue
        if p.is_symlink(): raise IntegrityError(f"symlink:{rel}")
        if not p.is_file(): continue
        if has_residue(p.relative_to(root)): raise IntegrityError(f"resíduo:{rel}")
        if p.suffix.lower()==".zip": raise IntegrityError(f"zip interno:{rel}")
        files.append(p)
    return sorted(files)

def create_manifest(root: Path, exclusions: set[str]) -> dict:
    records=[{"path":str(p.relative_to(root)),"sha256":sha256_file(p),"size":p.stat().st_size} for p in payload_files(root,exclusions)]
    return {"algorithm":"SHA-256","exclusions":sorted(exclusions),"file_count":len(records),"files":records}

def verify_manifest(root: Path, manifest: dict) -> list[str]:
    errors=[]; exclusions=set(manifest.get("exclusions",[]))
    try: actual=[str(p.relative_to(root)) for p in payload_files(root,exclusions)]
    except IntegrityError as exc: return [str(exc)]
    expected=[r["path"] for r in manifest.get("files",[])]
    if actual!=expected: errors.append("conjunto de arquivos divergente")
    for record in manifest.get("files",[]):
        p=root/record["path"]
        if not p.is_file(): errors.append(f"ausente:{record['path']}"); continue
        if sha256_file(p)!=record["sha256"] or p.stat().st_size!=record["size"]: errors.append(f"hash divergente:{record['path']}")
    return errors
