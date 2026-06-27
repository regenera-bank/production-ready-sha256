from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import re

from .errors import ReleaseBlocked, SecurityControlError


SEVERITY_SLA = {"CRITICAL": 1, "HIGH": 7, "MEDIUM": 30, "LOW": 90}
HEX64 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class Vulnerability:
    vulnerability_id: str
    severity: str
    discovered_on: date
    status: str = "OPEN"

    def due_on(self) -> date:
        try:
            days = SEVERITY_SLA[self.severity]
        except KeyError as exc:
            raise SecurityControlError("severidade inválida") from exc
        return self.discovered_on + timedelta(days=days)

    def is_overdue(self, today: date) -> bool:
        return self.status not in {"FIXED", "FALSE_POSITIVE"} and today > self.due_on()


@dataclass(frozen=True, slots=True)
class RiskWaiver:
    waiver_id: str
    requester_id: str
    approver_id: str
    expires_on: date
    compensating_control: str
    risk_statement: str

    def validate(self, today: date) -> None:
        if not self.waiver_id.strip() or not self.requester_id.strip() or not self.approver_id.strip():
            raise SecurityControlError("exceção incompleta")
        if self.requester_id == self.approver_id:
            raise SecurityControlError("autoaprovação de exceção proibida")
        if today >= self.expires_on:
            raise SecurityControlError("exceção vencida")
        if not self.compensating_control.strip() or not self.risk_statement.strip():
            raise SecurityControlError("exceção sem risco ou compensação")


@dataclass(frozen=True, slots=True)
class ScanResult:
    scanner: str
    status: str
    critical_findings: int = 0
    high_findings: int = 0

    def validate(self) -> None:
        if self.status != "PASS":
            raise ReleaseBlocked(f"scanner {self.scanner} não aprovado")
        if self.critical_findings < 0 or self.high_findings < 0:
            raise ReleaseBlocked("contagem de achados inválida")
        if self.critical_findings:
            raise ReleaseBlocked("achado crítico bloqueia release")


@dataclass(frozen=True, slots=True)
class ReleaseApproval:
    approver_id: str
    requester_id: str
    artifact_digest: str
    ticket_id: str

    def validate(self, expected_digest: str) -> None:
        if self.approver_id == self.requester_id:
            raise ReleaseBlocked("autoaprovação de release proibida")
        if self.artifact_digest != expected_digest:
            raise ReleaseBlocked("aprovação vinculada a outro artefato")
        if not self.ticket_id.strip():
            raise ReleaseBlocked("ticket de aprovação obrigatório")


@dataclass(frozen=True, slots=True)
class ReleaseCandidate:
    artifact_digest: str
    commit_digest: str
    sbom_digest: str
    provenance_digest: str
    scans: tuple[ScanResult, ...]
    vulnerabilities: tuple[Vulnerability, ...]
    requester_id: str
    approval: ReleaseApproval | None
    commit_signed: bool
    external_signature_present: bool

    def validate_technical_gate(self, today: date, waivers: dict[str, RiskWaiver] | None = None) -> None:
        waivers = waivers or {}
        for value in (self.artifact_digest, self.commit_digest, self.sbom_digest, self.provenance_digest):
            if not HEX64.fullmatch(value):
                raise ReleaseBlocked("digest SHA-256 inválido")
        if not self.scans:
            raise ReleaseBlocked("scans obrigatórios ausentes")
        for scan in self.scans:
            scan.validate()
        for vuln in self.vulnerabilities:
            if vuln.is_overdue(today):
                waiver = waivers.get(vuln.vulnerability_id)
                if waiver is None:
                    raise ReleaseBlocked(f"vulnerabilidade vencida: {vuln.vulnerability_id}")
                waiver.validate(today)
        if not self.commit_signed:
            raise ReleaseBlocked("commit-fonte não assinado")
        if self.approval is None:
            raise ReleaseBlocked("aprovação independente ausente")
        self.approval.validate(self.artifact_digest)

    def institutional_state(self) -> str:
        return "APPROVED_SIGNED" if self.external_signature_present else "UNSIGNED_PENDING_EXTERNAL_APPROVAL"
