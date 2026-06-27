import unittest
from regenera_quality.security import scan_text, validate_workflow_permissions

class SecurityTests(unittest.TestCase):
    def test_clean_text(self): self.assertEqual(scan_text("safe"),[])
    def test_private_key(self): self.assertEqual(scan_text("-----BEGIN PRIVATE KEY-----")[0].severity,"CRITICAL")
    def test_cloud_secret(self): self.assertTrue(scan_text("aws_secret_access_key=abc"))
    def test_embedded_password(self): self.assertTrue(scan_text("password='12345678'"))
    def test_latest_image(self): self.assertTrue(scan_text("image: bank:latest"))
    def test_unsafe_trigger(self): self.assertTrue(scan_text("pull_request_target:"))
    def test_workflow_permissions(self): validate_workflow_permissions("permissions:\n  contents: read\nuses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683")
    def test_missing_permissions(self): self.assertRaises(ValueError,validate_workflow_permissions,"uses: actions/checkout@abc")
    def test_unpinned_action(self): self.assertRaises(ValueError,validate_workflow_permissions,"permissions:\n  contents: read\nuses: x@y@main")
