from __future__ import annotations
from datetime import datetime,timezone

def effective(control: dict, now: datetime|None=None)->bool:
    now=now or datetime.now(timezone.utc)
    if not control.get("owner") or not control.get("evidence") or control.get("status")!="IMPLEMENTED": return False
    review=control.get("reviewed_at")
    if not review: return False
    parsed=datetime.fromisoformat(review.replace("Z","+00:00"))
    return parsed.tzinfo is not None and parsed<=now
