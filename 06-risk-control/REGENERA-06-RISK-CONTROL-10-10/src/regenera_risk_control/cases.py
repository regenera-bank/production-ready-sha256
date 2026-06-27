from __future__ import annotations
from dataclasses import dataclass, replace
from enum import Enum


class CaseStatus(str, Enum):
    OPEN = 'OPEN'
    INVESTIGATING = 'INVESTIGATING'
    PENDING_APPROVAL = 'PENDING_APPROVAL'
    CLOSED = 'CLOSED'


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    case_type: str
    opened_by: str
    assigned_to: str
    status: CaseStatus = CaseStatus.OPEN
    evidence: tuple[str, ...] = ()
    proposed_disposition: str | None = None
    approved_by: str | None = None


class CaseManager:
    def __init__(self) -> None:
        self._cases: dict[str, Case] = {}

    def open(self, case: Case) -> Case:
        if case.case_id in self._cases:
            raise ValueError('caso duplicado')
        if not case.case_type or not case.opened_by or not case.assigned_to:
            raise ValueError('caso incompleto')
        self._cases[case.case_id] = case
        return case

    def add_evidence(self, case_id: str, evidence_hash: str) -> Case:
        if len(evidence_hash) != 64:
            raise ValueError('evidência precisa de SHA-256')
        case = self._cases[case_id]
        updated = replace(case, evidence=case.evidence + (evidence_hash,),
                          status=CaseStatus.INVESTIGATING)
        self._cases[case_id] = updated
        return updated

    def propose_close(self, case_id: str, actor: str, disposition: str) -> Case:
        case = self._cases[case_id]
        if actor != case.assigned_to:
            raise PermissionError('somente responsável propõe encerramento')
        if not case.evidence:
            raise ValueError('caso sem evidência não fecha')
        updated = replace(case, proposed_disposition=disposition,
                          status=CaseStatus.PENDING_APPROVAL)
        self._cases[case_id] = updated
        return updated

    def approve_close(self, case_id: str, approver: str) -> Case:
        case = self._cases[case_id]
        if case.status != CaseStatus.PENDING_APPROVAL:
            raise ValueError('caso não aguarda aprovação')
        if approver in {case.opened_by, case.assigned_to}:
            raise PermissionError('autoaprovação é proibida')
        updated = replace(case, approved_by=approver, status=CaseStatus.CLOSED)
        self._cases[case_id] = updated
        return updated
