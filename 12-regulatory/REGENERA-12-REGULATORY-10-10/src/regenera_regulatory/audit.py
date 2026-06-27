from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from .canonical import sha256_hex, require_identifier
from .errors import ConflictError, ValidationError

@dataclass(frozen=True,slots=True)
class AuditRecord:
    event_id:str
    occurred_at:str
    actor_id:str
    action:str
    object_id:str
    payload_digest:str
    previous_hash:str
    record_hash:str

class AuditChain:
    def __init__(self):
        self._records=[]
        self._event_ids=set()

    @property
    def records(self): return tuple(self._records)

    def append(self,event_id,actor_id,action,object_id,payload,occurred_at=None):
        require_identifier(event_id); require_identifier(actor_id); require_identifier(action); require_identifier(object_id)
        if event_id in self._event_ids: raise ConflictError("event_id já registrado")
        occurred_at=occurred_at or datetime.now(timezone.utc).isoformat()
        if not occurred_at.endswith(('+00:00','Z')): raise ValidationError("timestamp precisa estar em UTC")
        previous=self._records[-1].record_hash if self._records else '0'*64
        payload_digest=sha256_hex(payload)
        body={'event_id':event_id,'occurred_at':occurred_at,'actor_id':actor_id,'action':action,'object_id':object_id,'payload_digest':payload_digest,'previous_hash':previous}
        record=AuditRecord(**body,record_hash=sha256_hex(body))
        self._records.append(record); self._event_ids.add(event_id)
        return record

    def verify(self):
        previous='0'*64
        seen=set()
        for record in self._records:
            if record.event_id in seen: return False
            body={k:v for k,v in asdict(record).items() if k!='record_hash'}
            if record.previous_hash!=previous or sha256_hex(body)!=record.record_hash: return False
            previous=record.record_hash; seen.add(record.event_id)
        return True
