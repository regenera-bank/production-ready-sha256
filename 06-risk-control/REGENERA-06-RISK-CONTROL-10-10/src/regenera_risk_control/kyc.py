from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from enum import Enum


class KycDecision(str, Enum):
    APPROVED = 'APPROVED'
    REVIEW = 'REVIEW'
    REJECTED = 'REJECTED'


@dataclass(frozen=True, slots=True)
class KycProfile:
    customer_id: str
    full_name: str
    birth_date: date
    document_hash: str
    document_expires_at: date
    address_verified: bool
    biometric_verified: bool
    pep: bool = False
    sanctions_hit: bool = False


@dataclass(frozen=True, slots=True)
class KycResult:
    decision: KycDecision
    reasons: tuple[str, ...]


class KycEngine:
    def evaluate(self, profile: KycProfile, today: date) -> KycResult:
        reasons: list[str] = []
        if not profile.customer_id or not profile.full_name.strip():
            reasons.append('IDENTITY_REQUIRED')
        if len(profile.document_hash) != 64:
            reasons.append('DOCUMENT_EVIDENCE_INVALID')
        if profile.document_expires_at < today:
            reasons.append('DOCUMENT_EXPIRED')
        if not profile.address_verified:
            reasons.append('ADDRESS_NOT_VERIFIED')
        if not profile.biometric_verified:
            reasons.append('BIOMETRIC_NOT_VERIFIED')
        if profile.sanctions_hit:
            return KycResult(KycDecision.REJECTED, tuple(reasons + ['SANCTIONS_HIT']))
        if profile.pep:
            reasons.append('PEP_ENHANCED_DUE_DILIGENCE')
        if reasons:
            return KycResult(KycDecision.REVIEW, tuple(reasons))
        return KycResult(KycDecision.APPROVED, ())
