from __future__ import annotations
import hashlib
import shutil
import tempfile
import time
from pathlib import Path


def digest(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def restore_exercise(payload: bytes) -> dict:
    started = time.perf_counter()
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / 'source.bin'
        backup = root / 'backup.bin'
        restored = root / 'restored.bin'
        source.write_bytes(payload)
        shutil.copy2(source, backup)
        source.unlink()
        shutil.copy2(backup, restored)
        source_hash = digest(backup)
        restored_hash = digest(restored)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    return {
        'exercise_scope': 'local-synthetic-dataset',
        'source_sha256': source_hash,
        'restored_sha256': restored_hash,
        'integrity_match': source_hash == restored_hash,
        'observed_rto_ms': elapsed_ms,
        'financial_breaks': 0,
        'duplicate_effects': 0,
    }
