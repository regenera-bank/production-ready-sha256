from __future__ import annotations

import hashlib
from xml.etree import ElementTree as ET

from .xml_security import parse_xml_secure


def _normalized(element: ET.Element) -> ET.Element:
    node = ET.Element(element.tag, dict(sorted(element.attrib.items())))
    text = (element.text or "").strip()
    if text:
        node.text = text
    for child in list(element):
        node.append(_normalized(child))
    return node


def canonical_xml(payload: bytes | str) -> bytes:
    root = parse_xml_secure(payload)
    normalized = _normalized(root)
    return ET.tostring(normalized, encoding="utf-8", short_empty_elements=True)


def message_digest(payload: bytes | str) -> str:
    return hashlib.sha256(canonical_xml(payload)).hexdigest()
