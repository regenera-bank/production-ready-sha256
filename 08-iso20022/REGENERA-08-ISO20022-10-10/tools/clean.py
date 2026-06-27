from pathlib import Path
import shutil

ROOT = Path(__file__).parents[1]
for rel in ('build', 'evidence/generated'):
    target = ROOT / rel
    if target.exists():
        shutil.rmtree(target)
for path in ROOT.rglob('__pycache__'):
    shutil.rmtree(path)
for path in ROOT.rglob('*.pyc'):
    path.unlink()
