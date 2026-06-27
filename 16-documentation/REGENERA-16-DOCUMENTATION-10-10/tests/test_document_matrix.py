import unittest, sys, json, re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import *

class DocumentMatrixTests(unittest.TestCase):
    pass

def make_meta_test(path):
    def test(self):
        meta,body=parse_front_matter(path)
        self.assertTrue(all(meta.get(k) for k in REQUIRED))
        self.assertTrue(body.lstrip().startswith('# '))
        self.assertGreater(len(body.strip()),80)
    return test

def make_hash_test(path):
    def test(self):
        rows=json.loads((ROOT/'registry/documents.json').read_text())
        row=next(r for r in rows if r['path']==str(path.relative_to(ROOT)))
        self.assertEqual(row['sha256'],sha256(path))
    return test

for p in canonical_docs():
    slug=re.sub(r'[^a-z0-9]+','_',str(p.relative_to(DOC_ROOT)).lower()).strip('_')
    setattr(DocumentMatrixTests,'test_meta_'+slug,make_meta_test(p))
    setattr(DocumentMatrixTests,'test_hash_'+slug,make_hash_test(p))

class PackageCatalogTests(unittest.TestCase):
    pass

def make_package_test(n):
    def test(self):
        text=(DOC_ROOT/'architecture/domain-map.md').read_text()
        self.assertRegex(text,rf'\| {n:02d} \|')
    return test
for n in range(17): setattr(PackageCatalogTests,f'test_package_{n:02d}',make_package_test(n))
