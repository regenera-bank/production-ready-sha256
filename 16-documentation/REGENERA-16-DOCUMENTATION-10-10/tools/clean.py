from pathlib import Path
import os, shutil
ROOT=Path(__file__).resolve().parents[1]
for current, dirs, files in os.walk(ROOT, topdown=False):
    current=Path(current)
    for name in files:
        if name.endswith('.pyc'):
            (current/name).unlink(missing_ok=True)
    for name in dirs:
        if name=='__pycache__':
            shutil.rmtree(current/name, ignore_errors=False)
