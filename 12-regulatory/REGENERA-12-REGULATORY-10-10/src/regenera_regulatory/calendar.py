from dataclasses import dataclass
from datetime import date,timedelta
from .errors import ValidationError

class BusinessCalendar:
    def __init__(self,holidays=()): self.holidays=frozenset(holidays)
    def is_business_day(self,day:date): return day.weekday()<5 and day not in self.holidays
    def next_business_day(self,day:date):
        while not self.is_business_day(day): day+=timedelta(days=1)
        return day
    def previous_business_day(self,day:date):
        while not self.is_business_day(day): day-=timedelta(days=1)
        return day
    def add_business_days(self,start:date,count:int):
        if isinstance(count,bool) or not isinstance(count,int): raise ValidationError('count inválido')
        if count==0: return self.next_business_day(start)
        step=1 if count>0 else -1; current=start; remaining=abs(count)
        while remaining:
            current+=timedelta(days=step)
            if self.is_business_day(current): remaining-=1
        return current

@dataclass(frozen=True,slots=True)
class CalendarStatus:
    state:str
    days_remaining:int
    escalation_required:bool


def obligation_status(due_date:date,today:date,completed=False,external_date_confirmed=True):
    if completed: return CalendarStatus('COMPLETE',(due_date-today).days,False)
    if not external_date_confirmed: return CalendarStatus('UNKNOWN',0,True)
    delta=(due_date-today).days
    if delta<0: return CalendarStatus('OVERDUE',delta,True)
    if delta==0: return CalendarStatus('DUE_TODAY',0,True)
    if delta<=5: return CalendarStatus('DUE_SOON',delta,True)
    return CalendarStatus('UPCOMING',delta,False)
