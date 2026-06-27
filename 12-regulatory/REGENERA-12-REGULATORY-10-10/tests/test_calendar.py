import unittest
from datetime import date
from regenera_regulatory.calendar import BusinessCalendar,obligation_status
from regenera_regulatory.errors import ValidationError

class CalendarTests(unittest.TestCase):
    def setUp(self): self.cal=BusinessCalendar({date(2026,1,1)})
    def test_weekday_is_business_day(self): self.assertTrue(self.cal.is_business_day(date(2026,1,2)))
    def test_weekend_is_not_business_day(self): self.assertFalse(self.cal.is_business_day(date(2026,1,3)))
    def test_holiday_is_not_business_day(self): self.assertFalse(self.cal.is_business_day(date(2026,1,1)))
    def test_next_business_day_skips_weekend(self): self.assertEqual(self.cal.next_business_day(date(2026,1,3)),date(2026,1,5))
    def test_previous_business_day_skips_weekend(self): self.assertEqual(self.cal.previous_business_day(date(2026,1,4)),date(2026,1,2))
    def test_add_positive_business_days(self): self.assertEqual(self.cal.add_business_days(date(2026,1,2),1),date(2026,1,5))
    def test_add_negative_business_days(self): self.assertEqual(self.cal.add_business_days(date(2026,1,5),-1),date(2026,1,2))
    def test_invalid_count_is_blocked(self):
        with self.assertRaises(ValidationError): self.cal.add_business_days(date(2026,1,1),1.5)
    def test_completed_status(self): self.assertEqual(obligation_status(date(2026,1,1),date(2026,1,2),True).state,'COMPLETE')
    def test_unknown_date_status(self): self.assertEqual(obligation_status(date(2026,1,1),date(2026,1,2),False,False).state,'UNKNOWN')
    def test_overdue_status(self): self.assertEqual(obligation_status(date(2026,1,1),date(2026,1,2)).state,'OVERDUE')
    def test_due_today_status(self): self.assertEqual(obligation_status(date(2026,1,2),date(2026,1,2)).state,'DUE_TODAY')
    def test_due_soon_status(self): self.assertEqual(obligation_status(date(2026,1,5),date(2026,1,2)).state,'DUE_SOON')
    def test_upcoming_status(self): self.assertEqual(obligation_status(date(2026,2,1),date(2026,1,2)).state,'UPCOMING')
