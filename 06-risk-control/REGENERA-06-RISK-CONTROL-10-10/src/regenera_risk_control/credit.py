from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from .money import Money


class CreditAction(str, Enum):
    APPROVE = 'APPROVE'
    REVIEW = 'REVIEW'
    DECLINE = 'DECLINE'


@dataclass(frozen=True, slots=True)
class CreditApplication:
    application_id: str
    requested: Money
    monthly_income: Money
    monthly_debt: Money
    bureau_score: int
    kyc_approved: bool
    aml_clear: bool
    sanctions_hit: bool


@dataclass(frozen=True, slots=True)
class CreditDecision:
    action: CreditAction
    approved_limit: Money
    reasons: tuple[str, ...]


class CreditPolicy:
    def __init__(self, max_dti_bps: int = 4_000, min_score: int = 650) -> None:
        self.max_dti_bps = max_dti_bps
        self.min_score = min_score

    def decide(self, application: CreditApplication) -> CreditDecision:
        if application.requested.currency != application.monthly_income.currency \
                or application.requested.currency != application.monthly_debt.currency:
            raise ValueError('moedas diferentes não entram na decisão')
        reasons: list[str] = []
        if application.sanctions_hit:
            reasons.append('SANCTIONS_HIT')
        if not application.kyc_approved:
            reasons.append('KYC_NOT_APPROVED')
        if not application.aml_clear:
            reasons.append('AML_NOT_CLEAR')
        if application.monthly_income.cents <= 0:
            reasons.append('INCOME_INVALID')
            dti_bps = 10_000
        else:
            dti_bps = application.monthly_debt.cents * 10_000 // application.monthly_income.cents
        if dti_bps > self.max_dti_bps:
            reasons.append('DTI_EXCEEDED')
        if application.bureau_score < self.min_score:
            reasons.append('SCORE_BELOW_POLICY')
        if reasons:
            return CreditDecision(CreditAction.DECLINE, Money(0, application.requested.currency), tuple(reasons))

        affordability = application.monthly_income.cents * 30 // 100
        limit = min(application.requested.cents, affordability * 6)
        if limit < application.requested.cents:
            return CreditDecision(CreditAction.REVIEW, Money(limit, application.requested.currency), ('LIMIT_REDUCED',))
        return CreditDecision(CreditAction.APPROVE, Money(limit, application.requested.currency), ())
