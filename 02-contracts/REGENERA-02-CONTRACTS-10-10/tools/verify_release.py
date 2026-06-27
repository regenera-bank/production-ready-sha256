#!/usr/bin/env python3
from pathlib import Path
import sys
from common import ROOT, sha256

def verify(checks):
    errors=[]
    for line in checks.read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        expected,rel=line.split('  ',1)
        p=ROOT/rel
        if not p.exists(): errors.append(f'missing:{rel}')
        elif sha256(p)!=expected: errors.append(f'hash:{rel}')
    return errors

errors=verify(ROOT/'release'/'PAYLOAD-CHECKSUMS.sha256')
evidence=ROOT/'release'/'EVIDENCE-CHECKSUMS.sha256'
if evidence.exists(): errors.extend(verify(evidence))
if errors:
    print('\n'.join(errors),file=sys.stderr); raise SystemExit(1)
print('verify-release: PASS')
