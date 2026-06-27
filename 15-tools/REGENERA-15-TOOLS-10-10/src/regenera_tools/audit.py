from __future__ import annotations
from dataclasses import dataclass
from .canonical import canonical_json,sha256_bytes

@dataclass(frozen=True, slots=True)
class AuditEntry:
    sequence:int; payload:dict; previous_hash:str; hash:str
class AuditChain:
    def __init__(self): self.entries=[]
    def append(self,payload:dict)->AuditEntry:
        previous=self.entries[-1].hash if self.entries else "0"*64
        sequence=len(self.entries)+1
        digest=sha256_bytes(canonical_json({"sequence":sequence,"payload":payload,"previous_hash":previous}))
        entry=AuditEntry(sequence,payload,previous,digest); self.entries.append(entry); return entry
    def verify(self)->bool:
        previous="0"*64
        for i,entry in enumerate(self.entries,1):
            expected=sha256_bytes(canonical_json({"sequence":i,"payload":entry.payload,"previous_hash":previous}))
            if entry.sequence!=i or entry.previous_hash!=previous or entry.hash!=expected: return False
            previous=entry.hash
        return True
