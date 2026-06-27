from pathlib import Path
import json, sys

ROOT=Path(__file__).resolve().parents[1]
forbidden_names={'.DS_Store','__MACOSX','__pycache__'}
forbidden_suffixes={'.pyc','.pyo','.zip'}
required=[
 'README.md','Makefile','pyproject.toml','governance/CONTROL-MATRIX.csv',
 'docs/ARCHITECTURE.md','docs/ADR/0001-deterministic-rules.md',
 'policies/KYC-AML-SANCTIONS-POLICY.md','runbooks/RECONCILIATION-BREAK.md',
 'authorship/DECLARACAO-DE-PROCEDENCIA.md',
]
errors=[]
for p in ROOT.rglob('*'):
    rel=p.relative_to(ROOT)
    if any(part in forbidden_names for part in rel.parts): errors.append(f'system-artifact:{rel}')
    if p.is_file() and p.suffix.lower() in forbidden_suffixes: errors.append(f'forbidden-file:{rel}')
for rel in required:
    if not (ROOT/rel).is_file(): errors.append(f'missing:{rel}')
sections=['## Objetivo','## Escopo','## Papéis','## Controles obrigatórios','## Evidências','## Métricas','## Exceções','## Revisão','## Aprovação']
for p in (ROOT/'policies').glob('*.md'):
    text=p.read_text(encoding='utf-8')
    for section in sections:
        if section not in text: errors.append(f'policy-section:{p.relative_to(ROOT)}:{section}')
report={'status':'PASS' if not errors else 'FAIL','errors':errors,'files_scanned':sum(1 for p in ROOT.rglob('*') if p.is_file())}
(ROOT/'evidence').mkdir(exist_ok=True)
(ROOT/'evidence'/'VALIDATION-REPORT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
raise SystemExit(0 if not errors else 1)
