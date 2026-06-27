import unittest
from regenera_data_platform.contracts import DataContract, DataField
from regenera_data_platform.ingestion import IngestionRegistry, IngestionStatus, IngestionError
from regenera_data_platform.quality import DataQualityGate, not_null, unique, accepted_values, freshness


def contract(): return DataContract("events","1.0.0","data-platform",("id",),(DataField("id","string",True,"INTERNAL"),DataField("state","string",True,"INTERNAL")))


class IngestionTests(unittest.TestCase):
    def test_valid_enters_processing(self): self.assertEqual(IngestionRegistry().begin("s","e",{"id":"1","state":"OK"},contract()).status, IngestionStatus.PROCESSING)
    def test_invalid_enters_quarantine(self): self.assertEqual(IngestionRegistry().begin("s","e",{"id":"1"},contract()).status, IngestionStatus.QUARANTINED)
    def test_commit(self):
        r=IngestionRegistry(); r.begin("s","e",{"id":"1","state":"OK"},contract()); self.assertEqual(r.commit("s","e",{"rows":1}).status,IngestionStatus.COMMITTED)
    def test_replay_returns_original(self):
        r=IngestionRegistry(); a=r.begin("s","e",{"id":"1","state":"OK"},contract()); b=r.begin("s","e",{"id":"1","state":"OK"},contract()); self.assertIs(a,b)
    def test_payload_mismatch_rejected(self):
        r=IngestionRegistry(); r.begin("s","e",{"id":"1","state":"OK"},contract())
        with self.assertRaises(IngestionError): r.begin("s","e",{"id":"1","state":"NO"},contract())
    def test_unknown_blocks_retry(self):
        r=IngestionRegistry(); r.begin("s","e",{"id":"1","state":"OK"},contract()); r.mark_unknown("s","e")
        with self.assertRaises(IngestionError): r.begin("s","e",{"id":"1","state":"OK"},contract())
    def test_reconcile_unknown(self):
        r=IngestionRegistry(); r.begin("s","e",{"id":"1","state":"OK"},contract()); r.mark_unknown("s","e"); r.reconcile("s","e",True,{"rows":1}); self.assertEqual(r.begin("s","e",{"id":"1","state":"OK"},contract()).status,IngestionStatus.COMMITTED)


class QualityTests(unittest.TestCase):
    def test_not_null(self): self.assertEqual(len(DataQualityGate([not_null("Q1","id")]).evaluate([{"id":None}])),1)
    def test_unique(self): self.assertEqual(len(DataQualityGate([unique("Q1","id")]).evaluate([{"id":1},{"id":1}])),1)
    def test_accepted(self): self.assertEqual(len(DataQualityGate([accepted_values("Q1","state",{"OK"})]).evaluate([{"state":"NO"}])),1)
    def test_freshness(self): self.assertEqual(len(DataQualityGate([freshness("Q1","ts",100)]).evaluate([{"ts":99}])),1)
    def test_blocking_fails(self):
        with self.assertRaises(ValueError): DataQualityGate([not_null("Q1","id")]).assert_publishable([{}])
    def test_clean_passes(self): DataQualityGate([not_null("Q1","id"),unique("Q2","id")]).assert_publishable([{"id":1},{"id":2}])
    def test_duplicate_rule_rejected(self):
        with self.assertRaises(ValueError): DataQualityGate([not_null("Q1","id"),unique("Q1","id")])

if __name__ == '__main__': unittest.main()
