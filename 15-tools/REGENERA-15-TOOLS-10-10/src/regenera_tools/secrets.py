from __future__ import annotations
from dataclasses import dataclass
import re

@dataclass(frozen=True, slots=True)
class Finding:
    rule: str
    line: int
    excerpt: str

def _patterns() -> dict[str, re.Pattern[str]]:
    return {
        "private_key": re.compile("BEGIN" + r"\s+(?:RSA\s+|EC\s+|OPENSSH\s+)?PRIVATE\s+KEY"),
        "cloud_access_key": re.compile("AKIA" + r"[0-9A-Z]{16}"),
        "github_token": re.compile("gh" + "p_" + r"[A-Za-z0-9]{36,}"),
        "password_assignment": re.compile(r'''(?i)(?:password|passwd)\s*[:=]\s*['"][^'"]{8,}['"]'''),
        "bearer_token": re.compile(r"(?i)bearer\s+[a-z0-9._-]{24,}"),
    }

def scan_text(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for number, line in enumerate(text.splitlines(), 1):
        for name, pattern in _patterns().items():
            if pattern.search(line):
                findings.append(Finding(name, number, "[REDACTED]"))
    return findings

def validate_exclusions(exclusions: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for path, reason in exclusions.items():
        if not path or path.startswith("/") or ".." in path.split("/"):
            errors.append(f"exclusão inválida:{path}")
        if len(reason.strip()) < 20:
            errors.append(f"justificativa insuficiente:{path}")
    return errors
