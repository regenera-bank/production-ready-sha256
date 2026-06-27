import unittest
from pathlib import Path

from regenera_iso20022.errors import IdempotencyConflict, ValidationError
from regenera_iso20022.registry import MessageRegistry, MessageState


XML = (Path(__file__).parent / 'fixtures' / 'valid' / 'pacs.008.001.08.xml').read_text(encoding='utf-8')


class RegistryTests(unittest.TestCase):
    def test_same_message_replays(self):
        registry = MessageRegistry()
        first, replay1 = registry.register('MSG-1', XML)
        second, replay2 = registry.register('MSG-1', XML)
        self.assertFalse(replay1)
        self.assertTrue(replay2)
        self.assertIs(first, second)

    def test_same_id_different_payload_conflicts(self):
        registry = MessageRegistry()
        registry.register('MSG-1', XML)
        with self.assertRaises(IdempotencyConflict):
            registry.register('MSG-1', XML.replace('125.40', '125.41'))

    def test_unknown_blocks_resend(self):
        registry = MessageRegistry()
        registry.register('MSG-1', XML)
        registry.transition('MSG-1', MessageState.VALIDATED)
        registry.transition('MSG-1', MessageState.SENT)
        registry.transition('MSG-1', MessageState.UNKNOWN)
        with self.assertRaises(ValidationError):
            registry.assert_resend_allowed('MSG-1')

    def test_unknown_can_reconcile(self):
        registry = MessageRegistry()
        registry.register('MSG-1', XML)
        registry.transition('MSG-1', MessageState.VALIDATED)
        registry.transition('MSG-1', MessageState.SENT)
        registry.transition('MSG-1', MessageState.UNKNOWN)
        record = registry.transition('MSG-1', MessageState.RECONCILIATION_REQUIRED)
        self.assertEqual(record.state, MessageState.RECONCILIATION_REQUIRED)

    def test_invalid_transition_fails(self):
        registry = MessageRegistry()
        registry.register('MSG-1', XML)
        with self.assertRaises(ValidationError):
            registry.transition('MSG-1', MessageState.ACKNOWLEDGED)
