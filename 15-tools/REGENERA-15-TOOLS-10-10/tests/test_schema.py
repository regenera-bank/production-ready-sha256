import unittest
from regenera_tools.schema import parse_json_strict,validate
from regenera_tools.errors import ValidationError
class SchemaTest(unittest.TestCase):
 def test_parse(self): self.assertEqual(parse_json_strict('{"a":1}'),{"a":1})
 def test_duplicate(self): self.assertRaises(ValidationError,parse_json_strict,'{"a":1,"a":2}')
 def test_invalid(self): self.assertRaises(ValidationError,parse_json_strict,'{')
 def test_object(self): self.assertEqual(validate({"a":"x"},{"type":"object","required":["a"]}),[])
 def test_required(self): self.assertTrue(validate({}, {"type":"object","required":["a"]}))
 def test_additional(self): self.assertTrue(validate({"x":1},{"type":"object","properties":{},"additionalProperties":False}))
 def test_integer_bool_rejected(self): self.assertTrue(validate(True,{"type":"integer"}))
 def test_minimum(self): self.assertTrue(validate(1,{"type":"integer","minimum":2}))
 def test_maximum(self): self.assertTrue(validate(3,{"type":"integer","maximum":2}))
 def test_pattern(self): self.assertTrue(validate("abc",{"type":"string","pattern":"[0-9]+"}))
 def test_min_length(self): self.assertTrue(validate("a",{"type":"string","minLength":2}))
 def test_max_length(self): self.assertTrue(validate("abc",{"type":"string","maxLength":2}))
 def test_enum(self): self.assertTrue(validate("X",{"type":"string","enum":["A"]}))
 def test_array(self): self.assertTrue(validate([1,"x"],{"type":"array","items":{"type":"integer"}}))
 def test_nested(self): self.assertEqual(validate({"a":{"b":1}},{"type":"object","properties":{"a":{"type":"object","properties":{"b":{"type":"integer"}}}}}),[])
