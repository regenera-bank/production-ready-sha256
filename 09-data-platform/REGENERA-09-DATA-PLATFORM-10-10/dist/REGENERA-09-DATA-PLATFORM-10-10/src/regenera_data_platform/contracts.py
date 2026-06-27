from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re
from typing import Any

_VERSION = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
_TYPES = {"string", "integer", "boolean", "object", "array", "timestamp"}
_CLASSES = {"PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"}


class ContractError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class DataField:
    name: str
    data_type: str
    required: bool
    classification: str

    def __post_init__(self) -> None:
        if not self.name or not self.name.replace("_", "").isalnum():
            raise ContractError("nome de campo inválido")
        if self.data_type not in _TYPES:
            raise ContractError("tipo de campo inválido")
        if self.classification not in _CLASSES:
            raise ContractError("classificação inválida")


@dataclass(frozen=True, slots=True)
class DataContract:
    dataset: str
    version: str
    owner_group: str
    primary_key: tuple[str, ...]
    fields: tuple[DataField, ...]

    def __post_init__(self) -> None:
        if not self.dataset or not self.owner_group:
            raise ContractError("dataset e owner são obrigatórios")
        if not _VERSION.fullmatch(self.version):
            raise ContractError("versão precisa seguir semver")
        names = [field.name for field in self.fields]
        if len(names) != len(set(names)):
            raise ContractError("campo duplicado")
        if not self.primary_key or any(key not in names for key in self.primary_key):
            raise ContractError("chave primária inválida")

    @property
    def fingerprint(self) -> str:
        payload = {
            "dataset": self.dataset,
            "version": self.version,
            "owner_group": self.owner_group,
            "primary_key": list(self.primary_key),
            "fields": [{"name": field.name, "data_type": field.data_type, "required": field.required, "classification": field.classification} for field in self.fields],
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return sha256(encoded).hexdigest()

    def validate_record(self, record: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        declared = {field.name: field for field in self.fields}
        for field in self.fields:
            if field.required and (field.name not in record or record[field.name] is None):
                errors.append(f"required:{field.name}")
                continue
            if field.name in record and record[field.name] is not None:
                value = record[field.name]
                expected = {
                    "string": str, "integer": int, "boolean": bool,
                    "object": dict, "array": list, "timestamp": str,
                }[field.data_type]
                if isinstance(value, bool) and field.data_type == "integer":
                    errors.append(f"type:{field.name}")
                elif not isinstance(value, expected):
                    errors.append(f"type:{field.name}")
        for name in record:
            if name not in declared:
                errors.append(f"unknown:{name}")
        return sorted(errors)

    def required_change_level(self, previous: "DataContract") -> str:
        old = {field.name: field for field in previous.fields}
        new = {field.name: field for field in self.fields}
        if self.dataset != previous.dataset:
            return "MAJOR"
        if any(name not in new for name in old):
            return "MAJOR"
        for name, field in old.items():
            candidate = new[name]
            if candidate.data_type != field.data_type:
                return "MAJOR"
            if not field.required and candidate.required:
                return "MAJOR"
            if candidate.classification != field.classification:
                return "MAJOR"
        if any(name not in old for name in new):
            return "MINOR"
        return "PATCH"


class ContractRegistry:
    def __init__(self) -> None:
        self._contracts: dict[tuple[str, str], DataContract] = {}

    def publish(self, contract: DataContract) -> None:
        key = (contract.dataset, contract.version)
        existing = self._contracts.get(key)
        if existing and existing.fingerprint != contract.fingerprint:
            raise ContractError("versão publicada é imutável")
        versions = [c for (dataset, _), c in self._contracts.items() if dataset == contract.dataset]
        if versions:
            previous = sorted(versions, key=lambda c: tuple(map(int, c.version.split('.'))))[-1]
            required = contract.required_change_level(previous)
            old_v = tuple(map(int, previous.version.split('.')))
            new_v = tuple(map(int, contract.version.split('.')))
            if new_v <= old_v:
                raise ContractError("versão precisa avançar")
            if required == "MAJOR" and new_v[0] <= old_v[0]:
                raise ContractError("mudança incompatível exige major")
            if required == "MINOR" and new_v[:2] <= old_v[:2] and new_v[0] == old_v[0]:
                raise ContractError("campo novo exige minor")
        self._contracts[key] = contract

    def get(self, dataset: str, version: str) -> DataContract:
        try:
            return self._contracts[(dataset, version)]
        except KeyError as exc:
            raise ContractError("contrato não publicado") from exc
