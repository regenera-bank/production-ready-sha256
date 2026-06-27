from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json


@dataclass(frozen=True, slots=True)
class LineageEntry:
    sequence: int
    dataset: str
    operation: str
    input_hashes: tuple[str, ...]
    output_hash: str
    previous_hash: str
    entry_hash: str


class LineageChain:
    def __init__(self) -> None:
        self._entries: list[LineageEntry] = []

    @property
    def entries(self) -> tuple[LineageEntry, ...]:
        return tuple(self._entries)

    def append(self, dataset: str, operation: str, input_hashes: tuple[str, ...], output_hash: str) -> LineageEntry:
        if not dataset or not operation or not output_hash:
            raise ValueError("lineage incompleto")
        previous = self._entries[-1].entry_hash if self._entries else "0" * 64
        body = {
            "sequence": len(self._entries) + 1,
            "dataset": dataset,
            "operation": operation,
            "input_hashes": list(input_hashes),
            "output_hash": output_hash,
            "previous_hash": previous,
        }
        digest = sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        entry = LineageEntry(entry_hash=digest, **body)
        self._entries.append(entry)
        return entry

    def verify(self) -> bool:
        previous = "0" * 64
        for position, entry in enumerate(self._entries, start=1):
            body = {
                "sequence": entry.sequence,
                "dataset": entry.dataset,
                "operation": entry.operation,
                "input_hashes": list(entry.input_hashes),
                "output_hash": entry.output_hash,
                "previous_hash": entry.previous_hash,
            }
            digest = sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if entry.sequence != position or entry.previous_hash != previous or entry.entry_hash != digest:
                return False
            previous = entry.entry_hash
        return True

    def tamper_for_test(self, index: int, output_hash: str) -> None:
        self._entries[index] = replace(self._entries[index], output_hash=output_hash)
