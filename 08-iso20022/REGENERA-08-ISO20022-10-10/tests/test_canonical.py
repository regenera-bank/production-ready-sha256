import unittest
from regenera_iso20022.canonical import canonical_xml, message_digest


class CanonicalTests(unittest.TestCase):
    def test_whitespace_does_not_change_digest(self):
        a = '<a x="1"><b>valor</b></a>'
        b = '<a x="1">\n  <b> valor </b>\n</a>'
        self.assertEqual(message_digest(a), message_digest(b))

    def test_content_changes_digest(self):
        self.assertNotEqual(message_digest('<a>1</a>'), message_digest('<a>2</a>'))

    def test_attributes_are_sorted(self):
        self.assertEqual(canonical_xml('<a z="2" a="1"/>'), canonical_xml('<a a="1" z="2"/>'))
