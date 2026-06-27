import unittest
from regenera_quality.accessibility import audit_html

class AccessibilityTests(unittest.TestCase):
    def test_clean_html(self): self.assertEqual(audit_html('<img alt="saldo"><input aria-label="valor"><button>Pagar</button>'),{"images_without_alt":0,"inputs_without_name":0,"unnamed_buttons":0})
    def test_image_without_alt(self): self.assertEqual(audit_html('<img src="x">')["images_without_alt"],1)
    def test_empty_alt_flagged(self): self.assertEqual(audit_html('<img alt="">')["images_without_alt"],1)
    def test_input_without_name(self): self.assertEqual(audit_html('<input>')["inputs_without_name"],1)
    def test_input_id_allowed(self): self.assertEqual(audit_html('<input id="amount">')["inputs_without_name"],0)
    def test_button_without_name(self): self.assertEqual(audit_html('<button></button>')["unnamed_buttons"],1)
    def test_button_aria_allowed(self): self.assertEqual(audit_html('<button aria-label="Fechar"></button>')["unnamed_buttons"],0)
