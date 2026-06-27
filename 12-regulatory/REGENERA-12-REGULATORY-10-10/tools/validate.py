#!/usr/bin/env python3
import csv,json,sys
from common import ROOT
required=['README.md','README-APLICACAO.md','config/regulatory-baseline.json','config/regulatory-registry.json','config/obligation-catalog.json','controls/CONTROL-MATRIX.csv','policies/obligation-management.md','policies/submission-management.md','runbooks/unknown-submission.md','evidence/source/SOURCE-INVENTORY.json','src/regenera_regulatory/obligations.py','docs/STATE-MACHINE.md','schemas/obligation.schema.json','schemas/evidence.schema.json','schemas/regulatory-report.schema.json','schemas/submission-receipt.schema.json','config/retention-classes.json','pyproject.toml']
errors=[]
for rel in required:
    if not (ROOT/rel).is_file(): errors.append(f'missing:{rel}')
for path in ROOT.rglob('*'):
    if not path.is_file() or 'release' in path.parts: continue
    rel=path.relative_to(ROOT).as_posix()
    if path.name=='.DS_Store' or '__MACOSX' in path.parts or '__pycache__' in path.parts or path.suffix=='.pyc': errors.append(f'system-file:{rel}')
    if path.suffix.lower() in {'.zip','.tar','.gz','.tgz'}: errors.append(f'nested-archive:{rel}')
    if path.stat().st_size==0: errors.append(f'empty-file:{rel}')
baseline=json.loads((ROOT/'config/regulatory-baseline.json').read_text())
if baseline.get('status')!='PENDING_INSTITUTIONAL_APPROVAL': errors.append('baseline-status-invalid')
if baseline.get('fail_closed') is not True: errors.append('fail-closed-disabled')
registry=json.loads((ROOT/'config/regulatory-registry.json').read_text())
if len(registry.get('domains',[]))!=14: errors.append('domain-count-invalid')
for domain in registry.get('domains',[]):
    if not domain.get('evidence_required'): errors.append(f'evidence-not-required:{domain.get("code")}')
    if domain.get('legal_mapping')!='PENDING_INDEPENDENT_LEGAL_REVIEW': errors.append(f'legal-mapping-state:{domain.get("code")}')
for schema in (ROOT/'schemas').glob('*.json'):
    json.loads(schema.read_text())
retention=json.loads((ROOT/'config/retention-classes.json').read_text())
if retention.get('state')!='PENDING_LEGAL_CONFIGURATION': errors.append('retention-state-invalid')
if any(item.get('retention_days') is not None for item in retention.get('classes',[])): errors.append('retention-period-invented')
catalog=json.loads((ROOT/'config/obligation-catalog.json').read_text())
for item in catalog.get('obligations',[]):
    if item.get('activation_state')!='BLOCKED_EXTERNAL_EVIDENCE': errors.append(f'obligation-activated:{item.get("obligation_id")}')
with (ROOT/'controls/CONTROL-MATRIX.csv').open(encoding='utf-8') as h: rows=list(csv.DictReader(h))
if len(rows)!=25: errors.append(f'control-count:{len(rows)}')
for row in rows:
    if not row['owner'].strip() or not row['evidence'].strip(): errors.append(f'control-incomplete:{row["control_id"]}')
    if not (ROOT/f'evidence/control/{row["control_id"]}.json').is_file(): errors.append(f'control-evidence-missing:{row["control_id"]}')
forbidden=('Gener'+'ated by','As an'+' AI','Enterprise'+' System','M'+'VP','TO'+'DO implement','place'+'holder implementation','regenera-'+'ag'+'ent','ag'+'ent CLI','simulated'+' protocol','fake'+' approval')
for path in ROOT.rglob('*'):
    if not path.is_file() or any(part in {'release','.git'} for part in path.parts) or path.name=='validate.py': continue
    try: text=path.read_text(encoding='utf-8')
    except UnicodeDecodeError: continue
    for token in forbidden:
        if token.lower() in text.lower(): errors.append(f'forbidden-content:{path.relative_to(ROOT)}:{token}')
if errors:
    print('VALIDATION: FAIL'); print('\n'.join(errors)); sys.exit(1)
print(f"VALIDATION: PASS ({sum(1 for p in ROOT.rglob('*') if p.is_file())} files)")
