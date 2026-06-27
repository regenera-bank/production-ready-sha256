import unittest
from regenera_tools.secrets import scan_text,validate_exclusions
from regenera_tools.comments import lint_comments
class SecretsCommentsTest(unittest.TestCase):
 def test_clean(self): self.assertEqual(scan_text("hello"),[])
 def test_private_key(self): self.assertEqual(scan_text("-----BEGIN "+"PRIVATE KEY-----")[0].rule,"private_key")
 def test_cloud_key(self): self.assertEqual(scan_text("AKIA"+"A"*16)[0].rule,"cloud_access_key")
 def test_github(self): self.assertEqual(scan_text("gh"+"p_"+"a"*36)[0].rule,"github_token")
 def test_password(self): self.assertEqual(scan_text("password='abcdefgh'")[0].rule,"password_assignment")
 def test_bearer(self): self.assertEqual(scan_text("Bearer "+"a"*30)[0].rule,"bearer_token")
 def test_redacted(self): self.assertEqual(scan_text("password='abcdefgh'")[0].excerpt,"[REDACTED]")
 def test_exclusion_ok(self): self.assertEqual(validate_exclusions({"tests/x.py":"fixture isolado para validar a regra de segurança"}),[])
 def test_exclusion_path(self): self.assertTrue(validate_exclusions({"../x":"justificativa suficientemente longa para teste"}))
 def test_exclusion_reason(self): self.assertTrue(validate_exclusions({"x":"curta"}))
 def test_comment_ok(self): self.assertEqual(lint_comments("# falha fechada evita estado ambíguo"),[])
 def test_comment_long(self): self.assertTrue(lint_comments("# "+"x"*161))
 def test_comment_banner(self): self.assertTrue(lint_comments("# ========= seção"))
 def test_comment_pending(self): self.assertTrue(lint_comments("# TO"+"DO corrigir"))
 def test_comment_generic(self): self.assertTrue(lint_comments("# helper function"))
