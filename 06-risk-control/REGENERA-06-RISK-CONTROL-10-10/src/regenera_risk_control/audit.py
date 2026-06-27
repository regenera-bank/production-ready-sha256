from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any


@dataclass(frozen=True, slots=True)
class AuditEvent:
    sequence: int
    event_type: str
    actor: str
    subject: str
    payload: dict[str, Any]
    previous_hash: str
    event_hash: str


class AuditChain:
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    @staticmethod
    def _digest(sequence: int, event_type: str, actor: str, subject: str,
                payload: dict[str, Any], previous_hash: str) -> str:
        body = json.dumps({
            'sequence': sequence,
            'event_type': event_type,
            'actor': actor,
            'subject': subject,
            'payload': payload,
            'previous_hash': previous_hash,
        }, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        return sha256(body.encode('utf-8')).hexdigest()

    def append(self, event_type: str, actor: str, subject: str,
               payload: dict[str, Any]) -> AuditEvent:
        if not event_type or not actor or not subject:
            raise ValueError('evento, ator e objeto são obrigatórios')
        previous = self._events[-1].event_hash if self._events else '0' * 64
        sequence = len(self._events) + 1
        digest = self._digest(sequence, event_type, actor, subject, payload, previous)
        event = AuditEvent(sequence, event_type, actor, subject, dict(payload), previous, digest)
        self._events.append(event)
        return event

    def events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)

    def verify(self) -> bool:
        previous = '0' * 64
        for expected, event in enumerate(self._events, start=1):
            if event.sequence != expected or event.previous_hash != previous:
                return False
            digest = self._digest(event.sequence, event.event_type, event.actor,
                                  event.subject, event.payload, event.previous_hash)
            if digest != event.event_hash:
                return False
            previous = event.event_hash
        return True
