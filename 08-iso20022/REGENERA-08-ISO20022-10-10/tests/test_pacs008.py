import unittest
from pathlib import Path
from datetime import date, datetime, timezone

from regenera_iso20022.builders import CreditTransfer, build_pacs008
from regenera_iso20022.errors import ValidationError
from regenera_iso20022.validator import Iso20022Validator


FIXTURE = Path(__file__).parent / 'fixtures' / 'valid' / 'pacs.008.001.08.xml'


class Pacs008Tests(unittest.TestCase):
    def setUp(self):
        self.validator = Iso20022Validator()
        self.xml = FIXTURE.read_text(encoding='utf-8')

    def test_valid_message(self):
        report = self.validator.validate(self.xml)
        self.assertEqual(report.message_type, 'pacs.008.001.08')
        self.assertEqual(report.transaction_count, 1)
        self.assertEqual(report.total_amount, '125.40')
        self.assertEqual(report.currency, 'BRL')

    def test_rejects_wrong_namespace(self):
        with self.assertRaises(ValidationError):
            self.validator.validate(self.xml.replace('pacs.008.001.08', 'pacs.008.001.99'))

    def test_rejects_wrong_count(self):
        with self.assertRaises(ValidationError):
            self.validator.validate(self.xml.replace('<NbOfTxs>1</NbOfTxs>', '<NbOfTxs>2</NbOfTxs>'))

    def test_rejects_control_sum_mismatch(self):
        with self.assertRaises(ValidationError):
            self.validator.validate(self.xml.replace('<CtrlSum>125.40</CtrlSum>', '<CtrlSum>125.41</CtrlSum>'))

    def test_rejects_invalid_bic(self):
        with self.assertRaises(ValidationError):
            self.validator.validate(self.xml.replace('AAAABRSP', 'BAD'))

    def test_rejects_excessive_decimal_scale(self):
        with self.assertRaises(ValidationError):
            self.validator.validate(self.xml.replace('125.40</IntrBkSttlmAmt>', '125.401</IntrBkSttlmAmt>'))

    def test_builder_round_trip(self):
        payload = build_pacs008('MSG-BUILD-1', [CreditTransfer(
            instruction_id='INS-BUILD-1', end_to_end_id='E2E-BUILD-1', transaction_id='TX-BUILD-1',
            amount='10.50', currency='BRL', settlement_date=date(2026, 6, 26),
            debtor_bic='AAAABRSP', creditor_bic='BBBBBRSP', debtor_name='Devedor', creditor_name='Credor',
            debtor_account='ACC-1', creditor_account='ACC-2')],
            created_at=datetime(2026, 6, 26, 12, 0, tzinfo=timezone.utc))
        report = self.validator.validate(payload)
        self.assertEqual(report.total_amount, '10.50')
