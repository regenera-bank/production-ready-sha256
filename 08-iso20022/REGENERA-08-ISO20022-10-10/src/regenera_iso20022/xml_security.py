from __future__ import annotations

from dataclasses import dataclass
from xml.etree import ElementTree as ET

from .errors import SecurityError, ValidationError


@dataclass(frozen=True)
class XmlLimits:
    max_bytes: int = 1_048_576
    max_elements: int = 20_000
    max_depth: int = 64
    max_text_bytes: int = 262_144


_FORBIDDEN = (b"<!doctype", b"<!entity", b"system ", b"public ")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def namespace_of(tag: str) -> str:
    if tag.startswith("{") and "}" in tag:
        return tag[1:].split("}", 1)[0]
    return ""


def parse_xml_secure(payload: bytes | str, limits: XmlLimits | None = None) -> ET.Element:
    limits = limits or XmlLimits()
    raw = payload.encode("utf-8") if isinstance(payload, str) else payload

    if len(raw) > limits.max_bytes:
        raise SecurityError("XML_TOO_LARGE", "Mensagem excede o limite de bytes")

    lowered = raw.lower()
    if any(token in lowered for token in _FORBIDDEN):
        raise SecurityError("XML_DTD_FORBIDDEN", "DTD e entidades externas são proibidas")

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValidationError("XML_MALFORMED", "XML malformado") from exc

    count = 0
    text_bytes = 0
    stack: list[tuple[ET.Element, int]] = [(root, 1)]

    while stack:
        node, depth = stack.pop()
        count += 1
        if count > limits.max_elements:
            raise SecurityError("XML_ELEMENT_LIMIT", "Quantidade de elementos excedida")
        if depth > limits.max_depth:
            raise SecurityError("XML_DEPTH_LIMIT", "Profundidade XML excedida")
        if node.text:
            text_bytes += len(node.text.encode("utf-8"))
        if node.tail:
            text_bytes += len(node.tail.encode("utf-8"))
        if text_bytes > limits.max_text_bytes:
            raise SecurityError("XML_TEXT_LIMIT", "Conteúdo textual excede o limite")
        for child in reversed(list(node)):
            stack.append((child, depth + 1))

    return root
