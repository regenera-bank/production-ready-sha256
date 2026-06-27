from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date, timezone
from decimal import Decimal
from xml.etree import ElementTree as ET

from .model import Money, validate_bic, validate_identifier
from .profiles import PROFILES


@dataclass(frozen=True)
class CreditTransfer:
    instruction_id: str
    end_to_end_id: str
    transaction_id: str
    amount: str
    currency: str
    settlement_date: date
    debtor_bic: str
    creditor_bic: str
    debtor_name: str
    creditor_name: str
    debtor_account: str
    creditor_account: str


def _sub(parent: ET.Element, tag: str, text: str | None = None, **attrs: str) -> ET.Element:
    node = ET.SubElement(parent, tag, attrs)
    if text is not None:
        node.text = text
    return node


def build_pacs008(message_id: str, transfers: list[CreditTransfer], created_at: datetime | None = None) -> bytes:
    profile = PROFILES["pacs.008.001.08"]
    validate_identifier(message_id, "MSG_ID_INVALID")
    if not transfers:
        raise ValueError("ao menos uma transferência é obrigatória")
    created_at = created_at or datetime.now(timezone.utc)
    ET.register_namespace("", profile.namespace)
    document = ET.Element(f"{{{profile.namespace}}}Document")
    body = _sub(document, f"{{{profile.namespace}}}{profile.root_payload}")
    header = _sub(body, f"{{{profile.namespace}}}GrpHdr")
    _sub(header, f"{{{profile.namespace}}}MsgId", message_id)
    _sub(header, f"{{{profile.namespace}}}CreDtTm", created_at.isoformat().replace("+00:00", "Z"))
    _sub(header, f"{{{profile.namespace}}}NbOfTxs", str(len(transfers)))
    total = Decimal("0")
    for item in transfers:
        money = Money.parse(item.amount, item.currency)
        total += money.amount
    _sub(header, f"{{{profile.namespace}}}CtrlSum", format(total, "f"))
    settlement = _sub(header, f"{{{profile.namespace}}}SttlmInf")
    _sub(settlement, f"{{{profile.namespace}}}SttlmMtd", "CLRG")
    for item in transfers:
        validate_bic(item.debtor_bic)
        validate_bic(item.creditor_bic)
        tx = _sub(body, f"{{{profile.namespace}}}CdtTrfTxInf")
        pmt = _sub(tx, f"{{{profile.namespace}}}PmtId")
        _sub(pmt, f"{{{profile.namespace}}}InstrId", validate_identifier(item.instruction_id))
        _sub(pmt, f"{{{profile.namespace}}}EndToEndId", validate_identifier(item.end_to_end_id))
        _sub(pmt, f"{{{profile.namespace}}}TxId", validate_identifier(item.transaction_id))
        _sub(tx, f"{{{profile.namespace}}}IntrBkSttlmAmt", item.amount, Ccy=item.currency)
        _sub(tx, f"{{{profile.namespace}}}IntrBkSttlmDt", item.settlement_date.isoformat())
        for side, bic in (("DbtrAgt", item.debtor_bic), ("CdtrAgt", item.creditor_bic)):
            agent = _sub(tx, f"{{{profile.namespace}}}{side}")
            fin = _sub(agent, f"{{{profile.namespace}}}FinInstnId")
            _sub(fin, f"{{{profile.namespace}}}BICFI", bic)
        for side, name in (("Dbtr", item.debtor_name), ("Cdtr", item.creditor_name)):
            party = _sub(tx, f"{{{profile.namespace}}}{side}")
            _sub(party, f"{{{profile.namespace}}}Nm", name)
        for side, account in (("DbtrAcct", item.debtor_account), ("CdtrAcct", item.creditor_account)):
            acct = _sub(tx, f"{{{profile.namespace}}}{side}")
            ident = _sub(acct, f"{{{profile.namespace}}}Id")
            other = _sub(ident, f"{{{profile.namespace}}}Othr")
            _sub(other, f"{{{profile.namespace}}}Id", validate_identifier(account))
    return ET.tostring(document, encoding="utf-8", xml_declaration=True, short_empty_elements=True)
