import unittest, sys, json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import *
class RegistryTests(unittest.TestCase):
    def test_registry_exists(self): self.assertTrue((ROOT/'registry/documents.json').exists())
    def test_registry_matches_count(self): self.assertEqual(len(json.loads((ROOT/'registry/documents.json').read_text())),len(canonical_docs()))
    def test_registry_sorted(self):
        r=json.loads((ROOT/'registry/documents.json').read_text()); self.assertEqual([x['id'] for x in r],sorted(x['id'] for x in r))
    def test_registry_hashes(self):
        for r in json.loads((ROOT/'registry/documents.json').read_text()): self.assertEqual(r['sha256'],sha256(ROOT/r['path']))
    def test_source_inventory_sha(self): self.assertEqual(json.loads((ROOT/'evidence/source/SOURCE-INVENTORY.json').read_text())['source_sha256'],'b7427ff675069b155890df1d912d35312c101b0c98a6a49ddfd25f927e9023f0')
