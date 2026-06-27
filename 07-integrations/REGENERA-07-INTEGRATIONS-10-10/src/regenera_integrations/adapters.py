from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from .errors import ValidationError


@dataclass(frozen=True)
class AdapterSpec:
    code: str
    responsibility: str
    financial_effect: bool
    activation_status: str
    external_evidence: tuple[str, ...]


ADAPTERS: dict[str, AdapterSpec] = {
    "spi": AdapterSpec("spi", "liquidação Pix", True, "BLOCKED_EXTERNAL", ("homologação SPI", "certificado ICP-Brasil", "conectividade RSFN")),
    "dict": AdapterSpec("dict", "diretório de identificadores Pix", False, "BLOCKED_EXTERNAL", ("homologação DICT", "certificado mTLS")),
    "open-finance": AdapterSpec("open-finance", "consentimento e compartilhamento de dados", False, "BLOCKED_EXTERNAL", ("registro de participante", "certificados de transporte e assinatura")),
    "bacen": AdapterSpec("bacen", "remessas e protocolos regulatórios", False, "BLOCKED_EXTERNAL", ("credenciamento do canal", "layout vigente aprovado")),
    "b3": AdapterSpec("b3", "custódia e eventos de mercado", True, "BLOCKED_EXTERNAL", ("contrato B3", "homologação de mensageria")),
    "susep": AdapterSpec("susep", "reportes e consultas securitárias", False, "BLOCKED_EXTERNAL", ("credenciamento SUSEP", "layout vigente aprovado")),
    "swift": AdapterSpec("swift", "mensageria financeira internacional", True, "BLOCKED_EXTERNAL", ("BIC ativo", "HSM", "homologação SWIFT")),
    "card-networks": AdapterSpec("card-networks", "mensagens de bandeira", True, "BLOCKED_EXTERNAL", ("certificação de bandeira", "chaves de rede")),
    "card-processor": AdapterSpec("card-processor", "autorização e liquidação de cartões", True, "BLOCKED_EXTERNAL", ("contrato de processamento", "homologação financeira")),
    "custody": AdapterSpec("custody", "posição e movimentação de ativos", True, "BLOCKED_EXTERNAL", ("contrato de custódia", "contas homologadas")),
    "bureaus": AdapterSpec("bureaus", "consulta de crédito", False, "BLOCKED_EXTERNAL", ("contrato de bureau", "base legal e consentimento")),
    "correspondents": AdapterSpec("correspondents", "operações de correspondentes", True, "BLOCKED_EXTERNAL", ("credenciamento", "limites operacionais")),
    "kyc-providers": AdapterSpec("kyc-providers", "validação cadastral e biométrica", False, "BLOCKED_EXTERNAL", ("contrato de tratamento", "homologação antifraude")),
    "notifications": AdapterSpec("notifications", "entrega de notificações", False, "READY_REFERENCE", ("provedor aprovado", "domínios e remetentes validados")),
}


ISPB = re.compile(r"^\d{8}$")
E2E = re.compile(r"^E\d{8}\d{8}[A-Za-z0-9]{15}$")
UUID = re.compile(r"^[0-9a-fA-F-]{36}$")


def validate_adapter_request(code: str, payload: dict[str, Any]) -> None:
    if code not in ADAPTERS:
        raise ValidationError("adaptador desconhecido")
    if not isinstance(payload, dict) or not payload:
        raise ValidationError("payload obrigatório")

    if code in {"spi", "dict"}:
        ispb = str(payload.get("ispb", ""))
        if not ISPB.fullmatch(ispb):
            raise ValidationError("ISPB inválido")

    if code == "spi" and "end_to_end_id" in payload:
        if not E2E.fullmatch(str(payload["end_to_end_id"])):
            raise ValidationError("EndToEndId inválido")

    if ADAPTERS[code].financial_effect:
        amount = payload.get("amount_minor")
        currency = payload.get("currency")
        if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
            raise ValidationError("valor financeiro deve usar unidade mínima inteira positiva")
        if currency not in {"BRL", "USD", "EUR"}:
            raise ValidationError("moeda inválida")
        if not payload.get("idempotency_key"):
            raise ValidationError("idempotency_key obrigatória")

    if code == "open-finance":
        if payload.get("consent_status") != "AUTHORISED":
            raise ValidationError("consentimento não autorizado")
        if not payload.get("scope"):
            raise ValidationError("scope obrigatório")

    if code == "notifications":
        forbidden = {"password", "token", "full_card_number", "pix_key"}
        if forbidden & set(payload):
            raise ValidationError("notificação contém dado proibido")
