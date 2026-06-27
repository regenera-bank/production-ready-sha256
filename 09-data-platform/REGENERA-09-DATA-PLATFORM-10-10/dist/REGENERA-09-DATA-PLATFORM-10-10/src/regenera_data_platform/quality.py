from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable


@dataclass(frozen=True, slots=True)
class QualityFinding:
    rule_id: str
    severity: str
    row_index: int | None
    detail: str


@dataclass(frozen=True, slots=True)
class QualityRule:
    rule_id: str
    severity: str
    evaluator: Callable[[list[dict[str, Any]]], list[QualityFinding]]


class DataQualityGate:
    def __init__(self, rules: Iterable[QualityRule]) -> None:
        self.rules = tuple(rules)
        if not self.rules:
            raise ValueError("gate sem regra não controla nada")
        ids = [rule.rule_id for rule in self.rules]
        if len(ids) != len(set(ids)):
            raise ValueError("rule_id duplicado")

    def evaluate(self, rows: list[dict[str, Any]]) -> list[QualityFinding]:
        findings: list[QualityFinding] = []
        for rule in self.rules:
            findings.extend(rule.evaluator(rows))
        return findings

    def assert_publishable(self, rows: list[dict[str, Any]]) -> None:
        blocking = [f for f in self.evaluate(rows) if f.severity == "BLOCKING"]
        if blocking:
            raise ValueError("dataset bloqueado por qualidade")


def not_null(rule_id: str, field: str, severity: str = "BLOCKING") -> QualityRule:
    def evaluate(rows: list[dict[str, Any]]) -> list[QualityFinding]:
        return [QualityFinding(rule_id, severity, i, f"{field} ausente")
                for i, row in enumerate(rows) if row.get(field) is None]
    return QualityRule(rule_id, severity, evaluate)


def unique(rule_id: str, field: str, severity: str = "BLOCKING") -> QualityRule:
    def evaluate(rows: list[dict[str, Any]]) -> list[QualityFinding]:
        seen: dict[Any, int] = {}
        findings: list[QualityFinding] = []
        for i, row in enumerate(rows):
            value = row.get(field)
            if value in seen:
                findings.append(QualityFinding(rule_id, severity, i, f"{field} duplicado"))
            else:
                seen[value] = i
        return findings
    return QualityRule(rule_id, severity, evaluate)


def accepted_values(rule_id: str, field: str, values: set[Any], severity: str = "BLOCKING") -> QualityRule:
    def evaluate(rows: list[dict[str, Any]]) -> list[QualityFinding]:
        return [QualityFinding(rule_id, severity, i, f"{field} fora do domínio")
                for i, row in enumerate(rows) if row.get(field) not in values]
    return QualityRule(rule_id, severity, evaluate)


def freshness(rule_id: str, field: str, minimum_epoch: int, severity: str = "BLOCKING") -> QualityRule:
    def evaluate(rows: list[dict[str, Any]]) -> list[QualityFinding]:
        findings = []
        for i, row in enumerate(rows):
            value = row.get(field)
            if not isinstance(value, int) or value < minimum_epoch:
                findings.append(QualityFinding(rule_id, severity, i, f"{field} fora da janela"))
        return findings
    return QualityRule(rule_id, severity, evaluate)
