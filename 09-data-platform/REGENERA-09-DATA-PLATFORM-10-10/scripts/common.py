from pathlib import Path
import hashlib, json, os

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
FIXED_EPOCH = int(os.environ.get("SOURCE_DATE_EPOCH", "1782432000"))
FIXED_ISO = "2026-06-26T00:00:00Z"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
