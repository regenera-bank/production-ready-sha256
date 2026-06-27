#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from regenera_iso20022.errors import Iso20022Error
from regenera_iso20022.validator import Iso20022Validator

parser = argparse.ArgumentParser(description='Valida mensagem no perfil interno ISO 20022')
parser.add_argument('xml')
args = parser.parse_args()
try:
    report = Iso20022Validator().validate(Path(args.xml).read_bytes())
    print(json.dumps(report.__dict__, ensure_ascii=False, indent=2))
except Iso20022Error as exc:
    print(json.dumps({'status': 'FAIL', 'code': exc.code, 'message': exc.message}, ensure_ascii=False, indent=2))
    raise SystemExit(1)
