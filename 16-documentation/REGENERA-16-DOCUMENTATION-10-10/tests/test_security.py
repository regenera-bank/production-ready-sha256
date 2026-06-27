import unittest, re, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import *
class SecurityTests(unittest.TestCase):
    def test_private_key_fixture(self): self.assertRegex('-----BEGIN PRIVATE KEY-----',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
    def test_aws_fixture(self): self.assertRegex('AKIA1234567890ABCDEF',r'AKIA[0-9A-Z]{16}')
    def test_no_binary_payload(self):
        for p in payload_files():
            with self.subTest(p=p): p.read_text(encoding='utf-8')
    def test_no_large_payload(self):
        for p in payload_files(): self.assertLess(p.stat().st_size,2_000_000)
    def test_no_macos_residue(self):
        for p in ROOT.rglob('*'): self.assertNotIn(p.name,{'.DS_Store','__MACOSX'})
    def test_no_nested_zip(self):
        for p in ROOT.rglob('*.zip'): self.fail(f'ZIP interno: {p}')
