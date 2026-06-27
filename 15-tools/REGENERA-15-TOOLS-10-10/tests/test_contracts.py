import unittest
from regenera_tools.contracts import lint_openapi,lint_asyncapi
class ContractsTest(unittest.TestCase):
 def api(self): return {"openapi":"3.1.0","info":{"title":"x","version":"1"},"paths":{"/x":{"get":{"operationId":"getX","responses":{"200":{}}}}}}
 def test_openapi_ok(self): self.assertEqual(lint_openapi(self.api()),[])
 def test_openapi_version(self): d=self.api();d["openapi"]="3.0.0";self.assertTrue(lint_openapi(d))
 def test_info(self): d=self.api();d["info"]={};self.assertTrue(lint_openapi(d))
 def test_paths(self): d=self.api();d["paths"]={};self.assertTrue(lint_openapi(d))
 def test_path_slash(self): d=self.api();d["paths"]={"x":d["paths"]["/x"]};self.assertTrue(lint_openapi(d))
 def test_operation_id(self): d=self.api();del d["paths"]["/x"]["get"]["operationId"];self.assertTrue(lint_openapi(d))
 def test_duplicate_id(self): d=self.api();d["paths"]["/y"]={"get":{"operationId":"getX","responses":{"200":{}}}};self.assertTrue(lint_openapi(d))
 def test_responses(self): d=self.api();d["paths"]["/x"]["get"]["responses"]={};self.assertTrue(lint_openapi(d))
 def test_mutating_requires_idempotency(self): d=self.api();d["paths"]["/x"]={"post":{"operationId":"postX","responses":{"409":{}}}};self.assertTrue(lint_openapi(d))
 def test_mutating_ok(self): d=self.api();d["paths"]["/x"]={"post":{"operationId":"postX","parameters":[{"in":"header","name":"Idempotency-Key","required":True}],"responses":{"201":{},"409":{}}}};self.assertEqual(lint_openapi(d),[])
 def test_async_ok(self): self.assertEqual(lint_asyncapi({"asyncapi":"3.0.0","channels":{"x":{"address":"x.v1","messages":{"event":{}}}}}),[])
 def test_async_version(self): self.assertTrue(lint_asyncapi({"asyncapi":"2.6.0","channels":{"x":{"address":"x","messages":{"e":{}}}}}))
 def test_async_channels(self): self.assertTrue(lint_asyncapi({"asyncapi":"3.0.0","channels":{}}))
 def test_async_address(self): self.assertTrue(lint_asyncapi({"asyncapi":"3.0.0","channels":{"x":{"messages":{"e":{}}}}}))
 def test_async_duplicate(self): self.assertTrue(lint_asyncapi({"asyncapi":"3.0.0","channels":{"x":{"address":"a","messages":{"e":{}}},"y":{"address":"a","messages":{"e":{}}}}}))
 def test_async_messages(self): self.assertTrue(lint_asyncapi({"asyncapi":"3.0.0","channels":{"x":{"address":"a","messages":{}}}}))
