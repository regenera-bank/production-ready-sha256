import unittest, sys, json, re
from pathlib import Path
from urllib.parse import urldefrag
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import *
class BuildTests(unittest.TestCase):
    def test_generated_site_exists(self): self.assertTrue((GENERATED/'site/index.html').exists())
    def test_css_exists(self): self.assertTrue((GENERATED/'site/assets/site.css').exists())
    def test_root_css_link(self): self.assertIn('href="assets/site.css"',(GENERATED/'site/index.html').read_text())
    def test_nested_css_links(self):
        for p in (GENERATED/'site').rglob('*.html'):
            rel=p.relative_to(GENERATED/'site')
            prefix='../'*(len(rel.parts)-1)
            self.assertIn(f'href="{prefix}assets/site.css"',p.read_text())
    def test_no_remote_assets(self):
        for p in (GENERATED/'site').rglob('*.html'):
            t=p.read_text(); self.assertNotIn('https://',t); self.assertNotIn('http://',t)
    def test_search_index_sorted(self):
        r=json.loads((GENERATED/'search-index.json').read_text()); self.assertEqual([x['id'] for x in r],sorted(x['id'] for x in r))
    def test_html_escapes_source(self):
        for p in (GENERATED/'site').rglob('*.html'): self.assertNotIn('<script>',p.read_text().lower())
    def test_generated_links_resolve(self):
        rx=re.compile(r'href="([^"]+)"')
        for p in (GENERATED/'site').rglob('*.html'):
            for href in rx.findall(p.read_text()):
                if href.startswith(('http://','https://','mailto:')): continue
                target,_=urldefrag(href)
                dest=(p.parent/target).resolve()
                with self.subTest(page=p,href=href): self.assertTrue(dest.exists())
    def test_registry_copy_exists(self): self.assertTrue((GENERATED/'site/data/documents.json').exists())
    def test_registry_copy_matches(self):
        self.assertEqual((GENERATED/'site/data/documents.json').read_text(),(ROOT/'registry/documents.json').read_text())
