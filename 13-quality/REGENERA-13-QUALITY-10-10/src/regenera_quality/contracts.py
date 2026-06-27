from dataclasses import dataclass
from typing import Mapping, FrozenSet

@dataclass(frozen=True, slots=True)
class Contract:
    name: str
    major: int
    required: FrozenSet[str]
    field_types: Mapping[str, str]

    def __post_init__(self) -> None:
        if not self.name or self.major < 1:
            raise ValueError("invalid_contract_identity")
        if not self.required.issubset(self.field_types.keys()):
            raise ValueError("required_field_without_type")


def compatibility_breaks(old: Contract, new: Contract) -> list[str]:
    breaks: list[str] = []
    removed = set(old.field_types) - set(new.field_types)
    if removed:
        breaks.append("removed_fields:" + ",".join(sorted(removed)))
    newly_required = set(new.required) - set(old.required)
    if newly_required:
        breaks.append("new_required_fields:" + ",".join(sorted(newly_required)))
    for field in sorted(set(old.field_types) & set(new.field_types)):
        if old.field_types[field] != new.field_types[field]:
            breaks.append(f"type_changed:{field}")
    return breaks


def validate_evolution(old: Contract, new: Contract) -> None:
    if old.name != new.name:
        raise ValueError("contract_name_changed")
    breaks = compatibility_breaks(old, new)
    if breaks and new.major <= old.major:
        raise ValueError("breaking_change_requires_major")
    if not breaks and new.major < old.major:
        raise ValueError("contract_major_regression")
