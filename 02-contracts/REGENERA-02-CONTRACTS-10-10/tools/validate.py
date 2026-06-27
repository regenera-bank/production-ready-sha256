#!/usr/bin/env python3
from pathlib import Path
import json, re, sys, yaml
from jsonschema.validators import validator_for
from common import ROOT, load

errors=[]
operation_ids=set()

for p in sorted((ROOT/'contracts').rglob('*')):
    if not p.is_file() or p.suffix not in {'.yaml','.yml','.json'}: continue
    try: data=load(p)
    except Exception as exc:
        errors.append(f'parse:{p.relative_to(ROOT)}:{exc}')
        continue
    if p.suffix=='.json' and isinstance(data,dict) and '$schema' in data:
        try:
            cls=validator_for(data); cls.check_schema(data)
        except Exception as exc: errors.append(f'json-schema:{p.relative_to(ROOT)}:{exc}')
    if isinstance(data,dict) and 'openapi' in data:
        if data['openapi']!='3.1.0': errors.append(f'openapi-version:{p.relative_to(ROOT)}')
        if not data.get('paths'): errors.append(f'openapi-no-paths:{p.relative_to(ROOT)}')
        for path,item in data.get('paths',{}).items():
            for method,op in item.items():
                if method.lower() not in {'get','post','put','patch','delete'}: continue
                oid=op.get('operationId')
                if not oid: errors.append(f'operation-id-missing:{p.relative_to(ROOT)}:{path}:{method}')
                elif oid in operation_ids: errors.append(f'operation-id-duplicate:{oid}')
                else: operation_ids.add(oid)
                if method.lower() in {'post','put','patch','delete'}:
                    refs=[x.get('$ref','') for x in op.get('parameters',[]) if isinstance(x,dict)]
                    if '#/components/parameters/CorrelationId' not in refs: errors.append(f'correlation-id-missing:{oid}')
                    if '#/components/parameters/IdempotencyKey' not in refs: errors.append(f'idempotency-key-missing:{oid}')
    if isinstance(data,dict) and 'asyncapi' in data:
        if data['asyncapi']!='3.0.0': errors.append(f'asyncapi-version:{p.relative_to(ROOT)}')
        if not data.get('operations'): errors.append(f'asyncapi-no-operations:{p.relative_to(ROOT)}')

for p in sorted(ROOT.rglob('*')):
    if p.is_dir():
        if p.name in {'__MACOSX','__pycache__'}: errors.append(f'system-dir:{p.relative_to(ROOT)}')
    else:
        if p.name=='.DS_Store' or p.suffix=='.pyc' or p.name.startswith('._'): errors.append(f'system-file:{p.relative_to(ROOT)}')

if errors:
    print('\n'.join(errors), file=sys.stderr); raise SystemExit(1)
print(f'validate: PASS ({len(operation_ids)} operations)')
