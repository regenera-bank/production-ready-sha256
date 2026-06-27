import hashlib
import hmac
import unittest

from regenera_integrations.errors import AuthenticationError, ValidationError
from regenera_integrations.security import EndpointPolicy, redact_payload, validate_mtls_peer, verify_webhook_hmac


class SecurityTests(unittest.TestCase):
    def test_https_and_allowlist_are_required(self):
        policy = EndpointPolicy(frozenset({"api.partner.example"}))
        policy.validate("https://api.partner.example/v1")
        with self.assertRaises(ValidationError):
            policy.validate("http://api.partner.example/v1")
        with self.assertRaises(ValidationError):
            policy.validate("https://evil.example/v1")

    def test_credentials_in_url_are_rejected(self):
        policy = EndpointPolicy(frozenset({"api.partner.example"}))
        with self.assertRaises(ValidationError):
            policy.validate("https://user:pass@api.partner.example/v1")

    def test_mtls_fingerprint_is_validated(self):
        fp = "ab" * 32
        validate_mtls_peer(fingerprint=fp, allowed_fingerprints={fp})
        with self.assertRaises(AuthenticationError):
            validate_mtls_peer(fingerprint="cd" * 32, allowed_fingerprints={fp})

    def test_mtls_format_is_rejected(self):
        with self.assertRaises(AuthenticationError):
            validate_mtls_peer(fingerprint="short", allowed_fingerprints=set())

    def test_webhook_signature_passes(self):
        body = b'{"event":"done"}'
        secret = b"local-test-secret-not-for-production"
        timestamp = 1000
        signature = hmac.new(secret, b"1000." + body, hashlib.sha256).hexdigest()
        verify_webhook_hmac(body=body, timestamp=timestamp, signature_hex=signature, secret=secret, now=1000)

    def test_webhook_tamper_is_detected(self):
        with self.assertRaises(AuthenticationError):
            verify_webhook_hmac(body=b"x", timestamp=1000, signature_hex="00" * 32, secret=b"secret", now=1000)

    def test_webhook_replay_window_is_enforced(self):
        with self.assertRaises(AuthenticationError):
            verify_webhook_hmac(body=b"x", timestamp=1000, signature_hex="00" * 32, secret=b"secret", now=2000)

    def test_redaction_uses_allowlist(self):
        payload = {"correlation_id": "c", "token": "secret", "status": "ok"}
        self.assertEqual(redact_payload(payload, {"correlation_id", "status"}), {"correlation_id": "c", "status": "ok"})


if __name__ == "__main__":
    unittest.main()
