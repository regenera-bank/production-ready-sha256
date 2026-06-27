from pathlib import Path
import json, sys
from common import ROOT, EVIDENCE, FIXED_ISO, write_json

PROHIBITED_NAMES = {".DS_Store", "__MACOSX", "__pycache__"}
PROHIBITED_SUFFIXES = {".pyc", ".pyo", ".zip"}
REQUIRED = [
    "README.md", "Makefile", "pyproject.toml", "governance/CONTROL-MATRIX.json",
    "governance/MODULE-REGISTRY.json", "governance/SOURCE-INVENTORY.json",
    "docs/architecture/DATA-PLATFORM-ARCHITECTURE.md",
]
POLICY_SECTIONS = ["## Objetivo", "## Escopo", "## Controles obrigatórios", "## Evidências", "## Exceções", "## Violações"]

errors=[]
for rel in REQUIRED:
    if not (ROOT/rel).is_file(): errors.append(f"missing:{rel}")
for path in ROOT.rglob('*'):
    if 'dist' in path.parts: continue
    if path.name in PROHIBITED_NAMES: errors.append(f"system-artifact:{path.relative_to(ROOT)}")
    if path.is_file() and path.suffix in PROHIBITED_SUFFIXES: errors.append(f"prohibited-file:{path.relative_to(ROOT)}")
    if path.is_symlink(): errors.append(f"symlink:{path.relative_to(ROOT)}")
for path in (ROOT/'docs/policies').glob('*.md'):
    text=path.read_text(encoding='utf-8')
    for section in POLICY_SECTIONS:
        if section not in text: errors.append(f"policy-section:{path.name}:{section}")
for path in list((ROOT/'governance').glob('*.json')):
    try: json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc: errors.append(f"json:{path.name}:{exc}")
# A validação procura assinaturas sintéticas sem guardar as expressões completas em linha única.
for path in ROOT.rglob('*'):
    if not path.is_file() or 'dist' in path.parts or path.suffix not in {'.md','.py','.json','.yml','.yaml'}: continue
    if path.name == 'validate.py': continue
    text=path.read_text(encoding='utf-8', errors='ignore').lower()
    forbidden=["generated"+" by ai", "as an"+" ai", "lifecycle:"+" experimental", "m"+"vp"]
    for token in forbidden:
        if token in text: errors.append(f"prohibited-content:{path.relative_to(ROOT)}:{token}")
status='PASS' if not errors else 'FAIL'
write_json(EVIDENCE/'validation-report.json', {"generated_at":FIXED_ISO,"status":status,"errors":errors})
print(f"validation: {status} ({len(errors)} erros)")
if errors:
    for error in errors: print(error)
    sys.exit(1)
