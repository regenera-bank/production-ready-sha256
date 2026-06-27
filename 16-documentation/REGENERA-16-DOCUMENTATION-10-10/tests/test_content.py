import unittest, sys, re, json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import *
class ContentTests(unittest.TestCase):
    def test_no_unverified_production_claim(self):
        rx=re.compile(r'(?i)\b(?:approved for '+r'production|gold '+r'master|100% '+r'compliant|homologado pelo '+r'bacen)\b')
        for p in canonical_docs(): self.assertIsNone(rx.search(p.read_text()))
    def test_unknown_is_documented(self): self.assertIn('UNKNOWN',(DOC_ROOT/'architecture/system-context.md').read_text())
    def test_money_is_integer(self): self.assertIn('unidade mínima inteira',(DOC_ROOT/'architecture/system-context.md').read_text())
    def test_channels_not_authoritative(self): self.assertIn('Canais nunca são fonte autoritativa de saldo',(DOC_ROOT/'architecture/system-context.md').read_text())
    def test_external_dependencies_explicit(self): self.assertIn('aprovação institucional',(ROOT/'governance/EXTERNAL-DEPENDENCIES.md').read_text())
    def test_regulatory_pending(self): self.assertEqual(parse_front_matter(DOC_ROOT/'regulatory/regulatory-matrix.md')[0]['status'],'EXTERNAL_PENDING')
    def test_no_real_secret_examples(self):
        for p in canonical_docs(): self.assertNotRegex(p.read_text(),r'AKIA[0-9A-Z]{16}')
    def test_all_packages_catalogued(self):
        t=(DOC_ROOT/'architecture/domain-map.md').read_text()
        for i in range(17): self.assertRegex(t,rf'\| {i:02d} \|')
    def test_control_count(self): self.assertEqual(len(json.loads((ROOT/'governance/CONTROL-MATRIX.json').read_text())),25)
    def test_external_controls_not_effective(self):
        cs=json.loads((ROOT/'governance/CONTROL-MATRIX.json').read_text())
        for c in cs:
            if c['id'] in {'DOC-020','DOC-021','DOC-022','DOC-023','DOC-024'}: self.assertEqual(c['status'],'EXTERNAL_PENDING')
