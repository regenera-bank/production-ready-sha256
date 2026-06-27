import unittest
from regenera_iso20022.errors import ValidationError
from regenera_iso20022.reconciliation import reconcile_payment_status


class ReconciliationTests(unittest.TestCase):
    def test_settled_closes_payment(self):
        result = reconcile_payment_status(
            {'message_id': 'MSG-1', 'transaction_ids': ['TX-1']},
            {'message_id': 'STS-1', 'original_message_id': 'MSG-1', 'transaction_ids': ['TX-1'], 'status': 'ACSC'},
        )
        self.assertEqual(result.action, 'CLOSE_AS_SETTLED')

    def test_wrong_original_is_rejected(self):
        with self.assertRaises(ValidationError):
            reconcile_payment_status({'message_id': 'MSG-1'}, {'original_message_id': 'MSG-2', 'status': 'ACSC'})

    def test_unknown_transaction_is_rejected(self):
        with self.assertRaises(ValidationError):
            reconcile_payment_status(
                {'message_id': 'MSG-1', 'transaction_ids': ['TX-1']},
                {'message_id': 'STS-1', 'original_message_id': 'MSG-1', 'transaction_ids': ['TX-2'], 'status': 'ACSC'},
            )

    def test_pending_stays_pending(self):
        result = reconcile_payment_status(
            {'message_id': 'MSG-1', 'transaction_ids': []},
            {'message_id': 'STS-1', 'original_message_id': 'MSG-1', 'transaction_ids': [], 'status': 'PDNG'},
        )
        self.assertEqual(result.action, 'KEEP_PENDING')
