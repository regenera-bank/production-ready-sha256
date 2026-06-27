from __future__ import annotations
from pathlib import Path, PurePosixPath
from .errors import SecurityError

RESIDUES={".DS_Store","__MACOSX","__pycache__","node_modules"}

def normalized_relative(raw: str) -> Path:
    if not raw or "\x00" in raw:
        raise SecurityError("caminho vazio ou inválido")
    posix=PurePosixPath(raw.replace("\\","/"))
    if posix.is_absolute() or any(part in {"", ".", ".."} for part in posix.parts):
        raise SecurityError("caminho precisa ser relativo e normalizado")
    return Path(*posix.parts)

def resolve_within(root: Path, raw: str) -> Path:
    root=root.resolve()
    rel=normalized_relative(raw)
    candidate=root/rel
    current=root
    for part in rel.parts:
        current=current/part
        if current.exists() and current.is_symlink():
            raise SecurityError("symlink não é aceito")
    resolved=candidate.resolve(strict=False)
    if resolved != root and root not in resolved.parents:
        raise SecurityError("caminho escapou do workspace")
    return resolved

def has_residue(path: Path) -> bool:
    return any(part in RESIDUES for part in path.parts) or path.suffix==".pyc"
