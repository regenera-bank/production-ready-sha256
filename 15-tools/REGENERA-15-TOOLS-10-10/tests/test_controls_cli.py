import json,unittest,io
from datetime import datetime,timezone,timedelta
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stdout, redirect_stderr
from common import TempCase
from regenera_tools.controls import effective
from regenera_tools.cli import main,parser
class ControlsCliTest(TempCase):
 def control(self): return {"owner":"x","evidence":"e","status":"IMPLEMENTED","reviewed_at":"2026-01-01T00:00:00Z"}
 def test_effective(self): self.assertTrue(effective(self.control(),datetime(2026,6,26,tzinfo=timezone.utc)))
 def test_no_owner(self): c=self.control();c["owner"]="";self.assertFalse(effective(c))
 def test_no_evidence(self): c=self.control();c["evidence"]="";self.assertFalse(effective(c))
 def test_status(self): c=self.control();c["status"]="BLOCKED";self.assertFalse(effective(c))
 def test_no_review(self): c=self.control();del c["reviewed_at"];self.assertFalse(effective(c))
 def test_future_review(self): c=self.control();c["reviewed_at"]="2030-01-01T00:00:00Z";self.assertFalse(effective(c,datetime(2026,6,26,tzinfo=timezone.utc)))
 def test_parser(self): self.assertEqual(parser().parse_args(["scan-secrets","x"]).command,"scan-secrets")
 def call(self,args):
  with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()): return main(args)
 def test_cli_scan_clean(self): p=self.root/"x";p.write_text("ok");self.assertEqual(self.call(["scan-secrets",str(p)]),0)
 def test_cli_scan_bad(self): p=self.root/"x";p.write_text("AKIA"+"A"*16);self.assertEqual(self.call(["scan-secrets",str(p)]),1)
 def test_cli_openapi(self): p=self.root/"x";p.write_text(json.dumps({"openapi":"3.1.0","info":{"title":"x","version":"1"},"paths":{"/x":{"get":{"operationId":"x","responses":{"200":{}}}}}}));self.assertEqual(self.call(["lint-openapi",str(p)]),0)
 def test_cli_migrations(self): d=self.root/"m";d.mkdir();(d/"0001_a.sql").write_text("SELECT 1;");self.assertEqual(self.call(["validate-migrations",str(d)]),0)
 def test_cli_workspace(self): (self.root/"x").write_text("x");self.assertEqual(self.call(["validate-workspace",str(self.root),"--require","x"]),0)
