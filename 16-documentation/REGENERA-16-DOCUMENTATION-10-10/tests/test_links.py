import unittest, sys, re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import *
class LinkTests(unittest.TestCase):
    def test_local_links_exist(self):
        rx=re.compile(r'\[[^]]+\]\(([^)]+)\)')
        for p in canonical_docs():
            _,body=parse_front_matter(p)
            for target in rx.findall(body):
                if target.startswith(('http://','https://','mailto:')): continue
                filepart=target.split('#',1)[0]; dest=(p.parent/filepart).resolve() if filepart else p.resolve()
                with self.subTest(source=p,target=target): self.assertTrue(dest.exists())
    def test_no_absolute_local_paths(self):
        for p in canonical_docs(): self.assertNotRegex(p.read_text(),r'\]\(/(?:Users|Volumes|mnt|home)/')
    def test_index_has_major_sections(self):
        t=(DOC_ROOT/'index.md').read_text();
        for section in ['Arquitetura','Catálogos','Governança','Decisões e resposta']: self.assertIn(section,t)
