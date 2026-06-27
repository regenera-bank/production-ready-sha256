import unittest

from regenera_integrations.adapters import ADAPTERS, validate_adapter_request
from regenera_integrations.errors import ValidationError


class AdapterTests(unittest.TestCase):
    def test_registry_has_fourteen_adapters(self):
        self.assertEqual(len(ADAPTERS), 14)

    def test_all_adapters_declare_external_evidence(self):
        self.assertTrue(all(spec.external_evidence for spec in ADAPTERS.values()))

    def test_spi_requires_valid_ispb(self):
        with self.assertRaises(ValidationError):
            validate_adapter_request("spi", {"ispb": "123", "amount_minor": 1, "currency": "BRL", "idempotency_key": "k"})

    def test_spi_financial_fields_are_required(self):
        with self.assertRaises(ValidationError):
            validate_adapter_request("spi", {"ispb": "12345678"})

    def test_spi_valid_payload(self):
        validate_adapter_request("spi", {"ispb": "12345678", "amount_minor": 100, "currency": "BRL", "idempotency_key": "k"})

    def test_financial_float_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_adapter_request("b3", {"amount_minor": 1.5, "currency": "BRL", "idempotency_key": "k"})

    def test_financial_boolean_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_adapter_request("swift", {"amount_minor": True, "currency": "USD", "idempotency_key": "k"})

    def test_invalid_currency_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_adapter_request("custody", {"amount_minor": 10, "currency": "XYZ", "idempotency_key": "k"})

    def test_open_finance_requires_authorised_consent(self):
        with self.assertRaises(ValidationError):
            validate_adapter_request("open-finance", {"consent_status": "REVOKED", "scope": "ACCOUNTS_READ"})

    def test_open_finance_requires_scope(self):
        with self.assertRaises(ValidationError):
            validate_adapter_request("open-finance", {"consent_status": "AUTHORISED"})

    def test_notifications_block_sensitive_fields(self):
        with self.assertRaises(ValidationError):
            validate_adapter_request("notifications", {"message": "ok", "token": "x"})

    def test_notifications_accept_safe_payload(self):
        validate_adapter_request("notifications", {"message": "ok", "correlation_id": "c"})

    def test_unknown_adapter_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_adapter_request("unknown", {"x": 1})

    def test_empty_payload_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_adapter_request("notifications", {})


if __name__ == "__main__":
    unittest.main()
