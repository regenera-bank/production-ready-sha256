#!/usr/bin/env python3
import importlib.util, sys
missing=[m for m in ('yaml','jsonschema') if importlib.util.find_spec(m) is None]
if missing:
    print('Dependências ausentes:', ', '.join(missing), file=sys.stderr)
    raise SystemExit(2)
print('doctor: PASS')
