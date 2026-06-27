from dataclasses import dataclass
from hashlib import sha256
import json

@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    sequence: int
    event: str
    payload_digest: str
    previous_digest: str
    digest: str

class EvidenceChain:
    def __init__(self) -> None:
        self.records: list[EvidenceRecord] = []

    def append(self, event: str, payload: dict) -> EvidenceRecord:
        if not event:
            raise ValueError("event_required")
        payload_digest = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        previous = self.records[-1].digest if self.records else "0" * 64
        sequence = len(self.records) + 1
        digest = sha256(f"{sequence}|{event}|{payload_digest}|{previous}".encode()).hexdigest()
        record = EvidenceRecord(sequence, event, payload_digest, previous, digest)
        self.records.append(record)
        return record

    def verify(self) -> bool:
        previous = "0" * 64
        for expected_sequence, record in enumerate(self.records, start=1):
            digest = sha256(
                f"{record.sequence}|{record.event}|{record.payload_digest}|{record.previous_digest}".encode()
            ).hexdigest()
            if record.sequence != expected_sequence or record.previous_digest != previous or record.digest != digest:
                return False
            previous = record.digest
        return True
