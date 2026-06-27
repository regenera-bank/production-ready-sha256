from dataclasses import dataclass
import re

@dataclass(frozen=True, slots=True)
class Finding:
    rule: str
    severity: str

_SECRET_RULES = (
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private_key"),
    (re.compile(r"(?i)aws_secret_access_key\s*[:=]"), "cloud_secret"),
    (re.compile(r"(?i)password\s*[:=]\s*['\"][^'\"]{8,}"), "embedded_password"),
)


def scan_text(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for regex, rule in _SECRET_RULES:
        if regex.search(text):
            findings.append(Finding(rule, "CRITICAL"))
    if re.search(r"(?i)\b(latest)\b", text) and "image:" in text:
        findings.append(Finding("unpinned_container", "HIGH"))
    if "pull_request_target" in text:
        findings.append(Finding("unsafe_workflow_trigger", "HIGH"))
    return findings


def validate_workflow_permissions(workflow: str) -> None:
    if "permissions:" not in workflow or "contents: read" not in workflow:
        raise ValueError("workflow_permissions_not_restricted")
    if "@main" in workflow or "@master" in workflow:
        raise ValueError("workflow_action_not_pinned")
