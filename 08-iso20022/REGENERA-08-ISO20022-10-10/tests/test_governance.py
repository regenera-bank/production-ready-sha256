import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class GovernanceTests(unittest.TestCase):
    def test_controls_have_owner_and_evidence(self):
        rows = list(csv.DictReader((ROOT / 'governance' / 'controls.csv').open(encoding='utf-8')))
        self.assertGreaterEqual(len(rows), 25)
        for row in rows:
            self.assertTrue(row['owner'])
            self.assertTrue(row['evidence'])
            self.assertIn(row['blocking'], {'true', 'false'})

    def test_external_activation_is_blocked(self):
        data = json.loads((ROOT / 'profiles' / 'message-profiles.json').read_text(encoding='utf-8'))
        self.assertEqual(data['external_activation'], 'BLOCKED_UNTIL_OFFICIAL_XSD_AND_INSTITUTIONAL_APPROVAL')

    def test_approval_is_not_fabricated(self):
        data = json.loads((ROOT / 'governance' / 'APPROVAL-RECORD.json').read_text(encoding='utf-8'))
        self.assertEqual(data['status'], 'PENDING_INDEPENDENT_REVIEW_AND_SIGNATURE')
        self.assertFalse(data['cryptographic_signature_present'])

    def test_no_nested_zip(self):
        self.assertEqual(list(ROOT.rglob('*.zip')), [])
