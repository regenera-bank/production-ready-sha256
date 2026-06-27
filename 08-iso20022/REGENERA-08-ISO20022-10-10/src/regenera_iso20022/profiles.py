from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MessageProfile:
    message_id: str
    root_payload: str
    business_name: str
    official_xsd_required: bool = True

    @property
    def namespace(self) -> str:
        return f"urn:iso:std:iso:20022:tech:xsd:{self.message_id}"


PROFILES = {
    "pacs.008.001.08": MessageProfile(
        "pacs.008.001.08", "FIToFICstmrCdtTrf", "Transferência de crédito"
    ),
    "pacs.002.001.10": MessageProfile(
        "pacs.002.001.10", "FIToFIPmtStsRpt", "Status de pagamento"
    ),
    "camt.053.001.08": MessageProfile(
        "camt.053.001.08", "BkToCstmrStmt", "Extrato"
    ),
    "camt.054.001.08": MessageProfile(
        "camt.054.001.08", "BkToCstmrDbtCdtNtfctn", "Notificação de débito e crédito"
    ),
}
