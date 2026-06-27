import unittest
from concurrent.futures import ThreadPoolExecutor
from regenera_quality.financial import Posting, JournalRegistry, validate_journal
from regenera_quality.money import Money

class FinancialTests(unittest.TestCase):
    def postings(self, amount=100):
        return (Posting("a","DEBIT",Money(amount)), Posting("b","CREDIT",Money(amount)))
    def test_balanced(self): validate_journal(self.postings())
    def test_two_postings_required(self): self.assertRaises(ValueError, validate_journal, self.postings()[:1])
    def test_side_validated(self): self.assertRaises(ValueError, validate_journal, (Posting("a","X",Money(1)),Posting("b","CREDIT",Money(1))))
    def test_balance_validated(self): self.assertRaises(ValueError, validate_journal, (Posting("a","DEBIT",Money(2)),Posting("b","CREDIT",Money(1))))
    def test_currency_validated(self): self.assertRaises(ValueError, validate_journal, (Posting("a","DEBIT",Money(1)),Posting("b","CREDIT",Money(1,"USD"))))
    def test_positive_required(self): self.assertRaises(ValueError, validate_journal, self.postings(0))
    def test_first_post(self): self.assertEqual(JournalRegistry().post("k","j",self.postings()).journal_id,"j")
    def test_replay_returns_original(self):
        r=JournalRegistry(); first=r.post("k","j1",self.postings()); second=r.post("k","j2",self.postings()); self.assertIs(first,second)
    def test_conflicting_replay(self):
        r=JournalRegistry(); r.post("k","j",self.postings()); self.assertRaises(ValueError,r.post,"k","j2",self.postings(200))
    def test_concurrent_single_effect(self):
        r=JournalRegistry()
        with ThreadPoolExecutor(max_workers=8) as pool:
            items=list(pool.map(lambda _: r.post("k","j",self.postings()), range(32)))
        self.assertEqual(len({id(x) for x in items}),1)
