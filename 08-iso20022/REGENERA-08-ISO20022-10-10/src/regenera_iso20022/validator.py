from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from xml.etree import ElementTree as ET

from .errors import ValidationError
from .model import Money, parse_signed_amount, validate_bic, validate_identifier
from .profiles import PROFILES, MessageProfile
from .xml_security import local_name, namespace_of, parse_xml_secure


@dataclass
class ValidationReport:
    message_type: str
    message_id: str
    transaction_count: int
    total_amount: str | None
    currency: str | None
    warnings: list[str] = field(default_factory=list)


def _child(parent: ET.Element, name: str, required: bool = True) -> ET.Element | None:
    for item in list(parent):
        if local_name(item.tag) == name:
            return item
    if required:
        raise ValidationError("ELEMENT_REQUIRED", f"Elemento obrigatório ausente: {name}")
    return None


def _children(parent: ET.Element, name: str) -> list[ET.Element]:
    return [item for item in list(parent) if local_name(item.tag) == name]


def _path(parent: ET.Element, names: list[str], required: bool = True) -> ET.Element | None:
    current: ET.Element | None = parent
    for name in names:
        if current is None:
            return None
        current = _child(current, name, required=required)
    return current


def _text(node: ET.Element | None, code: str) -> str:
    value = (node.text or "").strip() if node is not None else ""
    if not value:
        raise ValidationError(code, "Conteúdo obrigatório ausente")
    return value


def _parse_datetime(value: str) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError("DATETIME_INVALID", "Data e hora inválidas") from exc


def _parse_date(value: str) -> None:
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError("DATE_INVALID", "Data inválida") from exc


class Iso20022Validator:
    def detect_profile(self, root: ET.Element) -> MessageProfile:
        namespace = namespace_of(root.tag)
        for profile in PROFILES.values():
            if namespace == profile.namespace:
                return profile
        raise ValidationError("NAMESPACE_UNSUPPORTED", "Namespace fora dos perfis aprovados")

    def validate(self, payload: bytes | str) -> ValidationReport:
        root = parse_xml_secure(payload)
        if local_name(root.tag) != "Document":
            raise ValidationError("DOCUMENT_ROOT_INVALID", "Raiz deve ser Document")
        profile = self.detect_profile(root)
        body = _child(root, profile.root_payload)
        if profile.message_id == "pacs.008.001.08":
            return self._validate_pacs008(body, profile)
        if profile.message_id == "pacs.002.001.10":
            return self._validate_pacs002(body, profile)
        if profile.message_id == "camt.053.001.08":
            return self._validate_camt053(body, profile)
        if profile.message_id == "camt.054.001.08":
            return self._validate_camt054(body, profile)
        raise ValidationError("PROFILE_NOT_IMPLEMENTED", "Perfil sem validador")

    def _validate_group_header(self, body: ET.Element) -> tuple[str, int, Decimal | None]:
        header = _child(body, "GrpHdr")
        msg_id = validate_identifier(_text(_child(header, "MsgId"), "MSG_ID_REQUIRED"), "MSG_ID_INVALID")
        created = _text(_child(header, "CreDtTm"), "CREATED_AT_REQUIRED")
        _parse_datetime(created)
        count_text = _text(_child(header, "NbOfTxs"), "TRANSACTION_COUNT_REQUIRED")
        try:
            count = int(count_text)
        except ValueError as exc:
            raise ValidationError("TRANSACTION_COUNT_INVALID", "Quantidade de transações inválida") from exc
        if count <= 0:
            raise ValidationError("TRANSACTION_COUNT_INVALID", "Quantidade deve ser positiva")
        control = _child(header, "CtrlSum", required=False)
        control_sum = Decimal(_text(control, "CONTROL_SUM_INVALID")) if control is not None else None
        return msg_id, count, control_sum

    def _validate_pacs008(self, body: ET.Element, profile: MessageProfile) -> ValidationReport:
        msg_id, declared_count, control_sum = self._validate_group_header(body)
        transactions = _children(body, "CdtTrfTxInf")
        if declared_count != len(transactions):
            raise ValidationError("TRANSACTION_COUNT_MISMATCH", "NbOfTxs diverge do conteúdo")
        seen_instr: set[str] = set()
        seen_tx: set[str] = set()
        total = Decimal("0")
        currency: str | None = None
        for tx in transactions:
            payment_id = _child(tx, "PmtId")
            instr = validate_identifier(_text(_child(payment_id, "InstrId"), "INSTR_ID_REQUIRED"), "INSTR_ID_INVALID")
            validate_identifier(_text(_child(payment_id, "EndToEndId"), "E2E_ID_REQUIRED"), "E2E_ID_INVALID")
            tx_id = validate_identifier(_text(_child(payment_id, "TxId"), "TX_ID_REQUIRED"), "TX_ID_INVALID")
            if instr in seen_instr or tx_id in seen_tx:
                raise ValidationError("DUPLICATE_TRANSACTION_ID", "Identificador duplicado na mensagem")
            seen_instr.add(instr)
            seen_tx.add(tx_id)
            amount_node = _child(tx, "IntrBkSttlmAmt")
            tx_currency = amount_node.attrib.get("Ccy", "")
            money = Money.parse(_text(amount_node, "AMOUNT_REQUIRED"), tx_currency)
            if currency is None:
                currency = tx_currency
            elif currency != tx_currency:
                raise ValidationError("MIXED_CURRENCY", "Uma mensagem não pode misturar moedas")
            total += money.amount
            _parse_date(_text(_child(tx, "IntrBkSttlmDt"), "SETTLEMENT_DATE_REQUIRED"))
            for side in ("DbtrAgt", "CdtrAgt"):
                bic = _path(tx, [side, "FinInstnId", "BICFI"])
                validate_bic(_text(bic, "BIC_REQUIRED"))
            for side in ("Dbtr", "Cdtr"):
                _text(_path(tx, [side, "Nm"]), "PARTY_NAME_REQUIRED")
            for side in ("DbtrAcct", "CdtrAcct"):
                validate_identifier(_text(_path(tx, [side, "Id", "Othr", "Id"]), "ACCOUNT_ID_REQUIRED"), "ACCOUNT_ID_INVALID")
        if control_sum is not None and control_sum != total:
            raise ValidationError("CONTROL_SUM_MISMATCH", "CtrlSum diverge da soma das transações")
        return ValidationReport(profile.message_id, msg_id, len(transactions), str(total), currency,
                                ["XSD oficial pendente de incorporação"])

    def _validate_pacs002(self, body: ET.Element, profile: MessageProfile) -> ValidationReport:
        header = _child(body, "GrpHdr")
        msg_id = validate_identifier(_text(_child(header, "MsgId"), "MSG_ID_REQUIRED"), "MSG_ID_INVALID")
        _parse_datetime(_text(_child(header, "CreDtTm"), "CREATED_AT_REQUIRED"))
        original = _child(body, "OrgnlGrpInfAndSts")
        validate_identifier(_text(_child(original, "OrgnlMsgId"), "ORIGINAL_MSG_ID_REQUIRED"), "ORIGINAL_MSG_ID_INVALID")
        status = _text(_child(original, "GrpSts"), "GROUP_STATUS_REQUIRED")
        if status not in {"ACCP", "ACSC", "PDNG", "RJCT"}:
            raise ValidationError("STATUS_INVALID", "Status fora do perfil")
        reasons = _children(original, "StsRsnInf")
        if status == "RJCT" and not reasons:
            raise ValidationError("REJECTION_REASON_REQUIRED", "Rejeição exige motivo")
        for reason in reasons:
            code = _path(reason, ["Rsn", "Cd"])
            validate_identifier(_text(code, "REASON_CODE_REQUIRED"), "REASON_CODE_INVALID")
        tx_status = _children(body, "TxInfAndSts")
        for item in tx_status:
            validate_identifier(_text(_child(item, "OrgnlTxId"), "ORIGINAL_TX_ID_REQUIRED"), "ORIGINAL_TX_ID_INVALID")
            current = _text(_child(item, "TxSts"), "TRANSACTION_STATUS_REQUIRED")
            if current not in {"ACCP", "ACSC", "PDNG", "RJCT"}:
                raise ValidationError("TRANSACTION_STATUS_INVALID", "Status de transação inválido")
        return ValidationReport(profile.message_id, msg_id, len(tx_status), None, None,
                                ["XSD oficial pendente de incorporação"])

    def _validate_camt053(self, body: ET.Element, profile: MessageProfile) -> ValidationReport:
        group = _child(body, "GrpHdr")
        msg_id = validate_identifier(_text(_child(group, "MsgId"), "MSG_ID_REQUIRED"), "MSG_ID_INVALID")
        _parse_datetime(_text(_child(group, "CreDtTm"), "CREATED_AT_REQUIRED"))
        statements = _children(body, "Stmt")
        if not statements:
            raise ValidationError("STATEMENT_REQUIRED", "Extrato sem statement")
        total_entries = 0
        for statement in statements:
            validate_identifier(_text(_child(statement, "Id"), "STATEMENT_ID_REQUIRED"), "STATEMENT_ID_INVALID")
            balances = _children(statement, "Bal")
            if len(balances) < 2:
                raise ValidationError("BALANCE_PAIR_REQUIRED", "Extrato exige saldos de abertura e fechamento")
            balance_values: dict[str, tuple[Decimal, str]] = {}
            for balance in balances:
                code = _text(_path(balance, ["Tp", "CdOrPrtry", "Cd"]), "BALANCE_TYPE_REQUIRED")
                amount_node = _child(balance, "Amt")
                balance_currency = amount_node.attrib.get("Ccy", "")
                balance_values[code] = (parse_signed_amount(_text(amount_node, "BALANCE_AMOUNT_REQUIRED"), balance_currency), balance_currency)
            if "OPBD" not in balance_values or "CLBD" not in balance_values:
                raise ValidationError("OPEN_CLOSE_BALANCE_REQUIRED", "Saldos OPBD e CLBD são obrigatórios")
            entries = _children(statement, "Ntry")
            total_entries += len(entries)
            delta = Decimal("0")
            currency = balance_values["OPBD"][1]
            if balance_values["CLBD"][1] != currency:
                raise ValidationError("MIXED_CURRENCY", "Saldos de abertura e fechamento usam moedas diferentes")
            for entry in entries:
                amount_node = _child(entry, "Amt")
                money = Money.parse(_text(amount_node, "ENTRY_AMOUNT_REQUIRED"), amount_node.attrib.get("Ccy", ""))
                if money.currency != currency:
                    raise ValidationError("MIXED_CURRENCY", "Extrato mistura moedas")
                indicator = _text(_child(entry, "CdtDbtInd"), "CREDIT_DEBIT_REQUIRED")
                if indicator == "CRDT":
                    delta += money.amount
                elif indicator == "DBIT":
                    delta -= money.amount
                else:
                    raise ValidationError("CREDIT_DEBIT_INVALID", "Indicador de crédito ou débito inválido")
            if balance_values["OPBD"][0] + delta != balance_values["CLBD"][0]:
                raise ValidationError("BALANCE_RECONCILIATION_FAILED", "Saldos não reconciliam com os lançamentos")
        return ValidationReport(profile.message_id, msg_id, total_entries, None, None,
                                ["XSD oficial pendente de incorporação"])

    def _validate_camt054(self, body: ET.Element, profile: MessageProfile) -> ValidationReport:
        group = _child(body, "GrpHdr")
        msg_id = validate_identifier(_text(_child(group, "MsgId"), "MSG_ID_REQUIRED"), "MSG_ID_INVALID")
        _parse_datetime(_text(_child(group, "CreDtTm"), "CREATED_AT_REQUIRED"))
        notifications = _children(body, "Ntfctn")
        if not notifications:
            raise ValidationError("NOTIFICATION_REQUIRED", "Notificação ausente")
        count = 0
        currencies: set[str] = set()
        total = Decimal("0")
        for notification in notifications:
            validate_identifier(_text(_child(notification, "Id"), "NOTIFICATION_ID_REQUIRED"), "NOTIFICATION_ID_INVALID")
            for entry in _children(notification, "Ntry"):
                count += 1
                amount_node = _child(entry, "Amt")
                money = Money.parse(_text(amount_node, "ENTRY_AMOUNT_REQUIRED"), amount_node.attrib.get("Ccy", ""))
                currencies.add(money.currency)
                total += money.amount
                indicator = _text(_child(entry, "CdtDbtInd"), "CREDIT_DEBIT_REQUIRED")
                if indicator not in {"CRDT", "DBIT"}:
                    raise ValidationError("CREDIT_DEBIT_INVALID", "Indicador inválido")
                reference = _path(entry, ["NtryDtls", "TxDtls", "Refs", "TxId"])
                validate_identifier(_text(reference, "TX_ID_REQUIRED"), "TX_ID_INVALID")
        if len(currencies) > 1:
            raise ValidationError("MIXED_CURRENCY", "Notificação mistura moedas")
        currency = next(iter(currencies)) if currencies else None
        return ValidationReport(profile.message_id, msg_id, count, str(total), currency,
                                ["XSD oficial pendente de incorporação"])
