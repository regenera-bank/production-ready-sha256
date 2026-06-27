import copy, json, tempfile, unittest
from pathlib import Path
import sys, yaml
from jsonschema import Draft202012Validator, RefResolver
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import ROOT, load, sha256
from compatibility import compare

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.openapi=[load(p) for p in sorted((ROOT/'contracts/openapi').glob('*.yaml'))]
        self.schemas={p.name:load(p) for p in sorted((ROOT/'contracts/json-schema').glob('*.json'))}

    def test_all_yaml_parses(self):
        for p in ROOT.rglob('*.yaml'): self.assertIsNotNone(load(p),p)

    def test_all_json_parses(self):
        for p in ROOT.rglob('*.json'): self.assertIsNotNone(load(p),p)

    def test_openapi_version(self):
        self.assertTrue(all(d['openapi']=='3.1.0' for d in self.openapi))

    def test_openapi_has_real_operations(self):
        self.assertGreaterEqual(sum(len(v) for d in self.openapi for v in d['paths'].values()),6)

    def test_operation_ids_unique(self):
        ids=[]
        for d in self.openapi:
            for item in d['paths'].values():
                for m,op in item.items():
                    if m in {'get','post','put','patch','delete'}: ids.append(op['operationId'])
        self.assertEqual(len(ids),len(set(ids)))

    def test_mutations_require_correlation_and_idempotency(self):
        for d in self.openapi:
            for path,item in d['paths'].items():
                for method,op in item.items():
                    if method not in {'post','put','patch','delete'}: continue
                    refs={x.get('$ref') for x in op.get('parameters',[]) if isinstance(x,dict)}
                    self.assertIn('#/components/parameters/CorrelationId',refs,(path,method))
                    self.assertIn('#/components/parameters/IdempotencyKey',refs,(path,method))

    def test_money_rejects_number(self):
        schema=self.schemas['money.schema.json']
        errs=list(Draft202012Validator(schema).iter_errors(load(ROOT/'fixtures/invalid/money-number.json')))
        self.assertTrue(errs)

    def test_money_accepts_integer_string(self):
        schema=self.schemas['money.schema.json']
        self.assertFalse(list(Draft202012Validator(schema).iter_errors(load(ROOT/'fixtures/valid/money.json'))))

    def test_money_rejects_leading_zero(self):
        schema=self.schemas['money.schema.json']
        self.assertTrue(list(Draft202012Validator(schema).iter_errors({'currency':'BRL','amountCents':'01'})))

    def test_money_rejects_float_string(self):
        schema=self.schemas['money.schema.json']
        self.assertTrue(list(Draft202012Validator(schema).iter_errors({'currency':'BRL','amountCents':'1.50'})))

    def test_idempotency_has_unknown(self):
        self.assertIn('UNKNOWN',self.schemas['idempotency-record.schema.json']['properties']['status']['enum'])

    def test_transaction_has_reconciliation_required(self):
        enum=self.schemas['transaction.schema.json']['properties']['status']['enum']
        self.assertIn('UNKNOWN',enum); self.assertIn('RECONCILIATION_REQUIRED',enum)

    def test_pix_has_unknown(self):
        enum=self.schemas['pix-payment.schema.json']['properties']['status']['enum']
        self.assertIn('UNKNOWN',enum)

    def test_pix_rejects_fake_success_state(self):
        schema=self.schemas['pix-payment.schema.json']
        resolver=RefResolver.from_schema(schema,store={'money.schema.json':self.schemas['money.schema.json']})
        errs=list(Draft202012Validator(schema,resolver=resolver).iter_errors(load(ROOT/'fixtures/invalid/pix-success.json')))
        self.assertTrue(errs)

    def test_asyncapi_has_operations(self):
        d=load(ROOT/'contracts/asyncapi/financial-events-v1.yaml')
        self.assertEqual(d['asyncapi'],'3.0.0'); self.assertGreaterEqual(len(d['operations']),3)

    def test_event_envelope_requires_correlation(self):
        d=load(ROOT/'contracts/asyncapi/financial-events-v1.yaml')
        req=d['components']['schemas']['EventEnvelope']['required']
        self.assertIn('correlationId',req); self.assertIn('eventVersion',req)

    def test_error_codes_unique_and_shaped(self):
        d=load(ROOT/'contracts/error-catalog/error-catalog.yaml')
        codes=list(d['errors'])
        self.assertEqual(len(codes),len(set(codes)))
        self.assertTrue(all(c.startswith('RG-') for c in codes))

    def test_error_remediation_exists(self):
        catalog=load(ROOT/'contracts/error-catalog/error-catalog.yaml')['errors']
        actions=load(ROOT/'contracts/error-catalog/remediation.yaml')['actions']
        self.assertTrue(all(v['remediation'] in actions for v in catalog.values()))

    def test_unknown_error_is_not_retryable(self):
        e=load(ROOT/'contracts/error-catalog/error-catalog.yaml')['errors']['RG-TRANSACTION-UNKNOWN']
        self.assertFalse(e['retryable']); self.assertEqual(e['remediation'],'RECONCILE')

    def test_breaking_path_removal_detected(self):
        old={'paths':{'/x':{'get':{'operationId':'x'}}}}; new={'paths':{}}
        self.assertTrue(compare(old,new))

    def test_breaking_required_field_detected(self):
        old={'type':'object','required':['a'],'properties':{'a':{'type':'string'},'b':{'type':'string'}}}
        new=copy.deepcopy(old); new['required'].append('b')
        self.assertTrue(compare(old,new))

    def test_breaking_type_change_detected(self):
        old={'type':'object','properties':{'a':{'type':'string'}}}
        new={'type':'object','properties':{'a':{'type':'integer'}}}
        self.assertTrue(compare(old,new))

    def test_optional_field_is_compatible(self):
        old={'type':'object','properties':{'a':{'type':'string'}}}
        new={'type':'object','properties':{'a':{'type':'string'},'b':{'type':'integer'}}}
        self.assertFalse(compare(old,new))

    def test_no_system_artifacts(self):
        bad=[]
        for p in ROOT.rglob('*'):
            if p.name in {'.DS_Store','__MACOSX','__pycache__'} or p.suffix=='.pyc' or p.name.startswith('._'): bad.append(p)
        self.assertEqual([],bad)

    def test_no_real_domains_in_contracts(self):
        for p in (ROOT/'contracts').rglob('*'):
            if p.is_file(): self.assertNotIn('.world',p.read_text(encoding='utf-8',errors='ignore'))

    def test_no_private_keys(self):
        for p in ROOT.rglob('*'):
            if p.is_file(): marker='BEGIN PRIVATE' + ' KEY'; self.assertNotIn(marker,p.read_text(encoding='utf-8',errors='ignore'))

    def test_owner_declared_and_reviewer_pending(self):
        d=load(ROOT/'governance/OWNERS.yaml')
        self.assertEqual(d['owner']['name'],'Don Paulo Ricardo')
        self.assertEqual(d['independentReviewer']['approvalStatus'],'PENDING')

    def test_author_cannot_self_approve(self):
        d=load(ROOT/'governance/OWNERS.yaml')
        self.assertNotEqual(d['owner']['name'],d['independentReviewer']['name'])

    def test_no_active_exceptions(self):
        self.assertEqual(load(ROOT/'governance/EXCEPTIONS.yaml')['exceptions'],[])

    def test_sign_script_does_not_contain_private_key(self):
        text=(ROOT/'tools/sign_release.sh').read_text()
        self.assertIn('gpg --list-secret-keys',text); self.assertNotIn('PRIVATE KEY',text)

    def test_no_destructive_global_clean(self):
        for p in ROOT.rglob('*'):
            if p.is_file() and p.suffix in {'.sh','.py'}:
                marker='rm ' + '-rf'; self.assertNotIn(marker,p.read_text(encoding='utf-8',errors='ignore'),p)

    def test_evidence_hashes_close(self):
        checks=ROOT/'release/EVIDENCE-CHECKSUMS.sha256'
        if not checks.exists(): self.skipTest('evidence checks generated after test execution')
        for line in checks.read_text().splitlines():
            if not line: continue
            expected,rel=line.split('  ',1); self.assertEqual(expected,sha256(ROOT/rel),rel)

    def test_release_payload_hashes_close(self):
        for line in (ROOT/'release/PAYLOAD-CHECKSUMS.sha256').read_text().splitlines():
            if not line: continue
            expected,rel=line.split('  ',1); self.assertEqual(expected,sha256(ROOT/rel),rel)

if __name__=='__main__': unittest.main()
