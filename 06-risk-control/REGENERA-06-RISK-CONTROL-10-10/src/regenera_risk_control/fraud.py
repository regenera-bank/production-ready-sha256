from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from .money import Money


class FraudAction(str, Enum):
    APPROVE = 'APPROVE'
    CHALLENGE = 'CHALLENGE'
    BLOCK = 'BLOCK'
    UNKNOWN = 'UNKNOWN'


@dataclass(frozen=True, slots=True)
class FraudRequest:
    transaction_id: str
    amount: Money
    trusted_device: bool
    beneficiary_age_days: int
    attempts_10m: int
    geo_anomaly: bool
    credential_reset_24h: bool
    signals_available: bool = True


@dataclass(frozen=True, slots=True)
class FraudDecision:
    action: FraudAction
    score: int
    reasons: tuple[str, ...]


class FraudEngine:
    def assess(self, request: FraudRequest) -> FraudDecision:
        if not request.signals_available:
            return FraudDecision(FraudAction.UNKNOWN, 0, ('SIGNALS_UNAVAILABLE',))
        if not request.amount.positive():
            raise ValueError('fraude precisa de valor positivo')

        score = 0
        reasons: list[str] = []
        if not request.trusted_device:
            score += 30; reasons.append('UNTRUSTED_DEVICE')
        if request.beneficiary_age_days < 1:
            score += 20; reasons.append('NEW_BENEFICIARY')
        if request.attempts_10m >= 5:
            score += 30; reasons.append('VELOCITY')
        if request.geo_anomaly:
            score += 25; reasons.append('GEO_ANOMALY')
        if request.credential_reset_24h:
            score += 35; reasons.append('RECENT_CREDENTIAL_RESET')
        if request.amount.cents >= 2_000_000:
            score += 20; reasons.append('HIGH_VALUE')

        if score >= 70:
            return FraudDecision(FraudAction.BLOCK, score, tuple(reasons))
        if score >= 30:
            return FraudDecision(FraudAction.CHALLENGE, score, tuple(reasons))
        return FraudDecision(FraudAction.APPROVE, score, tuple(reasons))
