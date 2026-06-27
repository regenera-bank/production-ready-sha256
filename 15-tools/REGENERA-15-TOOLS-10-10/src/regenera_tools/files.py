from __future__ import annotations
import os, tempfile
from pathlib import Path
from .errors import SecurityError
from .paths import resolve_within

def atomic_write(root: Path, relative: str, data: bytes, *, overwrite: bool=False) -> Path:
    target=resolve_within(root, relative)
    if target.exists() and target.is_symlink():
        raise SecurityError("destino não pode ser symlink")
    if target.exists() and not overwrite:
        raise FileExistsError(relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=".regenera-",dir=target.parent)
    try:
        with os.fdopen(fd,"wb") as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp,target)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    return target

def safe_remove(root: Path, relative: str, *, approved: bool=False, dry_run: bool=True) -> bool:
    target=resolve_within(root,relative)
    if not approved:
        raise PermissionError("remoção exige aprovação explícita")
    if dry_run:
        return target.exists()
    if target.is_dir():
        if any(target.iterdir()): raise OSError("diretório não está vazio")
        target.rmdir(); return True
    if target.exists(): target.unlink(); return True
    return False
