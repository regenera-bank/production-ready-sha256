from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import re
import unicodedata


def _normalize(value: str) -> str:
    folded = unicodedata.normalize('NFKD', value)
    ascii_only = ''.join(ch for ch in folded if not unicodedata.combining(ch))
    return re.sub(r'[^A-Z0-9 ]+', ' ', ascii_only.upper()).strip()


@dataclass(frozen=True, slots=True)
class SanctionsEntry:
    list_id: str
    primary_name: str
    aliases: tuple[str, ...] = ()
    document_hashes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SanctionsResult:
    matched: bool
    list_ids: tuple[str, ...]
    match_basis: tuple[str, ...]


class SanctionsIndex:
    def __init__(self, entries: tuple[SanctionsEntry, ...]) -> None:
        self._entries = entries

    @staticmethod
    def hash_document(document: str) -> str:
        return sha256(document.strip().encode('utf-8')).hexdigest()

    def screen(self, name: str, document: str | None = None) -> SanctionsResult:
        name_key = _normalize(name)
        document_hash = self.hash_document(document) if document else None
        ids: list[str] = []
        basis: list[str] = []
        for entry in self._entries:
            names = {_normalize(entry.primary_name), *(_normalize(a) for a in entry.aliases)}
            matched_name = name_key in names
            matched_document = bool(document_hash and document_hash in entry.document_hashes)
            if matched_name or matched_document:
                ids.append(entry.list_id)
                basis.append('DOCUMENT' if matched_document else 'NAME_EXACT_NORMALIZED')
        return SanctionsResult(bool(ids), tuple(ids), tuple(basis))
