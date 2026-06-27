from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json

from .errors import SecurityControlError


_ALLOWED_PAYLOAD_FIELDS = frozenset({"action", "resource", "result", "source", "reason", "artifact_digest", "ip_class"})


@dataclass(frozen=True, slots=True)
class SecurityEvent:
    event_id: str
    event_type: str
    principal_id: str
    occurred_at: datetime
    payload: dict


@dataclass(frozen=True, slots=True)
class DetectionRule:
    rule_id: str
    event_type: str
    severity: str
    threshold: int
    window_minutes: int = 5


@dataclass(frozen=True, slots=True)
class Alert:
    alert_id: str
    rule_id: str
    principal_id: str
    severity: str
    first_seen_at: datetime
    last_seen_at: datetime
    count: int
    state: str


class DetectionEngine:
    def __init__(self, rules: tuple[DetectionRule, ...]) -> None:
        self._rules = rules
        self._events: list[SecurityEvent] = []
        self._event_fingerprints: dict[str, str] = {}
        self._alerts: dict[str, Alert] = {}
        self.telemetry_state = "AVAILABLE"

    def set_telemetry_state(self, state: str) -> None:
        if state not in {"AVAILABLE", "DEGRADED", "UNAVAILABLE"}:
            raise SecurityControlError("estado de telemetria inválido")
        self.telemetry_state = state

    @staticmethod
    def sanitized_payload(payload: dict) -> dict:
        return {key: value for key, value in payload.items() if key in _ALLOWED_PAYLOAD_FIELDS}

    def ingest(self, event: SecurityEvent, now: datetime | None = None) -> tuple[Alert, ...]:
        current = now or datetime.now(timezone.utc)
        if self.telemetry_state == "UNAVAILABLE":
            raise SecurityControlError("UNKNOWN: telemetria indisponível")
        if event.occurred_at.tzinfo is None:
            raise SecurityControlError("evento sem timezone")
        if event.occurred_at > current + timedelta(minutes=1):
            raise SecurityControlError("evento no futuro")
        if not event.event_id.strip() or not event.event_type.strip() or not event.principal_id.strip():
            raise SecurityControlError("evento incompleto")
        clean = SecurityEvent(event.event_id, event.event_type, event.principal_id, event.occurred_at, self.sanitized_payload(event.payload))
        material = json.dumps({
            "event_type": clean.event_type,
            "principal_id": clean.principal_id,
            "occurred_at": clean.occurred_at.astimezone(timezone.utc).isoformat(),
            "payload": clean.payload,
        }, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        fingerprint = hashlib.sha256(material.encode("utf-8")).hexdigest()
        previous = self._event_fingerprints.get(clean.event_id)
        if previous is not None:
            if previous != fingerprint:
                raise SecurityControlError("event_id reutilizado com conteúdo diferente")
            return ()
        self._event_fingerprints[clean.event_id] = fingerprint
        self._events.append(clean)
        raised=[]
        for rule in self._rules:
            if rule.event_type != clean.event_type:
                continue
            start=current-timedelta(minutes=rule.window_minutes)
            count=sum(1 for item in self._events if item.event_type==rule.event_type and item.principal_id==clean.principal_id and start <= item.occurred_at <= current)
            if count < rule.threshold:
                continue
            dedupe=f"{rule.rule_id}|{clean.principal_id}"
            alert_id=hashlib.sha256(dedupe.encode()).hexdigest()[:24]
            old=self._alerts.get(dedupe)
            alert=Alert(alert_id,rule.rule_id,clean.principal_id,rule.severity,old.first_seen_at if old else current,current,count,"OPEN")
            self._alerts[dedupe]=alert
            raised.append(alert)
        return tuple(raised)

    @property
    def alerts(self) -> tuple[Alert, ...]:
        return tuple(self._alerts.values())
