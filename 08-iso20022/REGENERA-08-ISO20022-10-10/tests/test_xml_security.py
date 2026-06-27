import unittest

from regenera_iso20022.errors import SecurityError, ValidationError
from regenera_iso20022.xml_security import XmlLimits, parse_xml_secure


class XmlSecurityTests(unittest.TestCase):
    def test_rejects_dtd_and_entity(self):
        with self.assertRaises(SecurityError):
            parse_xml_secure('<!DOCTYPE a [<!ENTITY x SYSTEM "file:///etc/passwd">]><a>&x;</a>')

    def test_rejects_malformed_xml(self):
        with self.assertRaises(ValidationError):
            parse_xml_secure('<Document>')

    def test_rejects_large_payload(self):
        with self.assertRaises(SecurityError):
            parse_xml_secure('<a>' + ('x' * 200) + '</a>', XmlLimits(max_bytes=100))

    def test_rejects_excessive_depth(self):
        xml = '<a>' * 10 + '</a>' * 10
        with self.assertRaises(SecurityError):
            parse_xml_secure(xml, XmlLimits(max_depth=5))

    def test_rejects_element_flood(self):
        xml = '<a>' + '<b/>' * 20 + '</a>'
        with self.assertRaises(SecurityError):
            parse_xml_secure(xml, XmlLimits(max_elements=10))

    def test_accepts_small_safe_xml(self):
        root = parse_xml_secure('<a><b>ok</b></a>')
        self.assertEqual(root.tag, 'a')
