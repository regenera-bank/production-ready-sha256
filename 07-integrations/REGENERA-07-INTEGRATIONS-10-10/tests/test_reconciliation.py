import unittest

from regenera_integrations.errors import ValidationError
from regenera_integrations.kernel import OperationResult, Outcome
from regenera_integrations.reconciliation import Movement, ReconciliationBook, ReconciliationStatus


class ReconciliationTests(unittest.TestCase):
    def test_match(self):
        book = ReconciliationBook()
        items = book.compare([Movement("r1", 100, "BRL")], [Movement("r1", 100, "BRL")])
        self.assertEqual(items[0].status, ReconciliationStatus.MATCHED)

    def test_missing_external(self):
        item = ReconciliationBook().compare([Movement("r1", 100, "BRL")], [])[0]
        self.assertEqual(item.status, ReconciliationStatus.MISSING_EXTERNAL)

    def test_missing_internal(self):
        item = ReconciliationBook().compare([], [Movement("r1", 100, "BRL")])[0]
        self.assertEqual(item.status, ReconciliationStatus.MISSING_INTERNAL)

    def test_amount_mismatch(self):
        item = ReconciliationBook().compare([Movement("r1", 100, "BRL")], [Movement("r1", 101, "BRL")])[0]
        self.assertEqual(item.status, ReconciliationStatus.AMOUNT_MISMATCH)

    def test_currency_mismatch(self):
        item = ReconciliationBook().compare([Movement("r1", 100, "BRL")], [Movement("r1", 100, "USD")])[0]
        self.assertEqual(item.status, ReconciliationStatus.AMOUNT_MISMATCH)

    def test_duplicate_reference_is_rejected(self):
        book = ReconciliationBook()
        with self.assertRaises(ValidationError):
            book.compare([Movement("r1", 100, "BRL"), Movement("r1", 100, "BRL")], [])

    def test_unknown_can_be_resolved(self):
        unknown = OperationResult(Outcome.UNKNOWN, None, {}, 1)
        result = ReconciliationBook.resolve_unknown(unknown, "external-1")
        self.assertEqual(result.outcome, Outcome.SUCCEEDED)
        self.assertEqual(result.provider_reference, "external-1")

    def test_non_unknown_cannot_be_resolved(self):
        with self.assertRaises(ValidationError):
            ReconciliationBook.resolve_unknown(OperationResult(Outcome.REJECTED, None, {}, 1), "x")


if __name__ == "__main__":
    unittest.main()
