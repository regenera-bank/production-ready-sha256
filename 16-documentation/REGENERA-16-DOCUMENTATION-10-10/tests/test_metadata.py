import unittest, sys, re
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import *
class MetadataTests(unittest.TestCase):
    def test_documents_exist(self): self.assertGreaterEqual(len(canonical_docs()),25)
    def test_front_matter(self):
        for p in canonical_docs():
            with self.subTest(p=p):
                m,b=parse_front_matter(p); self.assertTrue(all(m.get(k) for k in REQUIRED))
    def test_unique_ids(self):
        ids=[parse_front_matter(p)[0]['id'] for p in canonical_docs()]; self.assertEqual(len(ids),len(set(ids)))
    def test_versions(self):
        for p in canonical_docs(): self.assertRegex(parse_front_matter(p)[0]['version'],r'^\d+\.\d+\.\d+$')
    def test_status(self):
        for p in canonical_docs(): self.assertIn(parse_front_matter(p)[0]['status'],ALLOWED_STATUSES)
    def test_classification(self):
        for p in canonical_docs(): self.assertIn(parse_front_matter(p)[0]['classification'],ALLOWED_CLASSIFICATIONS)
    def test_active_not_stale(self):
        today=date(2026,6,26)
        for p in canonical_docs():
            m,_=parse_front_matter(p)
            if m['status']=='ACTIVE': self.assertGreaterEqual(date.fromisoformat(m['next_review_due']),today)
    def test_review_not_future(self):
        today=date(2026,6,26)
        for p in canonical_docs(): self.assertLessEqual(date.fromisoformat(parse_front_matter(p)[0]['last_reviewed']),today)
    def test_h1(self):
        for p in canonical_docs(): self.assertTrue(parse_front_matter(p)[1].lstrip().startswith('# '))
    def test_owner_not_reviewer_only(self):
        for p in canonical_docs():
            m,_=parse_front_matter(p); self.assertNotEqual(m['owner'].strip(),m['reviewers'].strip())
