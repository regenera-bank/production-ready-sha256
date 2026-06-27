from __future__ import annotations
from dataclasses import dataclass, replace
from hashlib import sha256
import json


@dataclass(frozen=True, slots=True)
class RegulatoryReport:
    report_id: str
    report_type: str
    period: str
    prepared_by: str
    payload_hash: str
    evidence_hashes: tuple[str, ...]
    approved_by: str | None = None
    submitted: bool = False


class RegulatoryReportService:
    def prepare(self, report_id: str, report_type: str, period: str,
                prepared_by: str, payload: dict,
                evidence_hashes: tuple[str, ...]) -> RegulatoryReport:
        if not evidence_hashes or any(len(item) != 64 for item in evidence_hashes):
            raise ValueError('relatório exige evidência íntegra')
        body = json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        digest = sha256(body.encode('utf-8')).hexdigest()
        return RegulatoryReport(report_id, report_type, period, prepared_by,
                                digest, evidence_hashes)

    def approve(self, report: RegulatoryReport, approver: str) -> RegulatoryReport:
        if approver == report.prepared_by:
            raise PermissionError('preparador não aprova o próprio relatório')
        return replace(report, approved_by=approver)

    def submit(self, report: RegulatoryReport, payload: dict) -> RegulatoryReport:
        if report.approved_by is None:
            raise PermissionError('relatório sem aprovação não é submetido')
        body = json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        if sha256(body.encode('utf-8')).hexdigest() != report.payload_hash:
            raise ValueError('payload mudou depois da aprovação')
        return replace(report, submitted=True)
