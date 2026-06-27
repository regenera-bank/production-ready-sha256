from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import ipaddress
import re
from .errors import PlatformControlError
from .integrity import digest

HEX64 = re.compile(r"^[0-9a-f]{64}$")


def utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise PlatformControlError("TIMEZONE_REQUIRED")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class WorkloadIdentity:
    subject: str
    audience: str
    issuer: str
    expires_at: datetime
    static_secret: str | None = None

    def validate(self, now: datetime) -> None:
        if not self.subject or not self.audience or not self.issuer.startswith("https://"):
            raise PlatformControlError("WORKLOAD_IDENTITY_INVALID")
        if self.static_secret:
            raise PlatformControlError("STATIC_CREDENTIAL_FORBIDDEN")
        if utc(self.expires_at) <= utc(now):
            raise PlatformControlError("WORKLOAD_IDENTITY_EXPIRED")


@dataclass(frozen=True, slots=True)
class SecretLease:
    secret_id: str
    issued_at: datetime
    expires_at: datetime
    rotation_evidence: str
    plaintext: str | None = None

    def validate(self, now: datetime, max_age_days: int = 90) -> None:
        if self.plaintext is not None:
            raise PlatformControlError("PLAINTEXT_SECRET_FORBIDDEN")
        if not self.rotation_evidence:
            raise PlatformControlError("SECRET_ROTATION_EVIDENCE_REQUIRED")
        age=(utc(now)-utc(self.issued_at)).total_seconds()/86400
        if age < 0 or age > max_age_days or utc(self.expires_at) <= utc(now):
            raise PlatformControlError("SECRET_LEASE_INVALID")


@dataclass(frozen=True, slots=True)
class ReleaseApproval:
    approver: str
    artifact_sha256: str
    signed: bool
    approved_at: datetime


@dataclass(frozen=True, slots=True)
class ReleaseCandidate:
    artifact_sha256: str
    image_reference: str
    source_commit: str
    author: str
    approvals: tuple[ReleaseApproval, ...]
    sbom_sha256: str
    provenance_sha256: str

    def validate(self) -> None:
        for value, code in [(self.artifact_sha256,"ARTIFACT_HASH_INVALID"),(self.sbom_sha256,"SBOM_HASH_INVALID"),(self.provenance_sha256,"PROVENANCE_HASH_INVALID")]:
            if not HEX64.fullmatch(value):
                raise PlatformControlError(code)
        if "@sha256:" not in self.image_reference or self.image_reference.endswith(":latest"):
            raise PlatformControlError("IMAGE_DIGEST_REQUIRED")
        valid=[a for a in self.approvals if a.signed and a.artifact_sha256 == self.artifact_sha256 and a.approver != self.author]
        if not valid:
            raise PlatformControlError("INDEPENDENT_SIGNED_APPROVAL_REQUIRED")


@dataclass(frozen=True, slots=True)
class ExceptionGrant:
    exception_id: str
    owner: str
    approver: str
    expires_at: datetime
    evidence_hash: str

    def validate(self, now: datetime) -> None:
        if not self.owner or not self.approver:
            raise PlatformControlError("EXCEPTION_OWNER_REQUIRED")
        if self.owner == self.approver:
            raise PlatformControlError("SELF_APPROVAL_FORBIDDEN")
        if utc(self.expires_at) <= utc(now):
            raise PlatformControlError("EXCEPTION_EXPIRED")
        if not HEX64.fullmatch(self.evidence_hash):
            raise PlatformControlError("EXCEPTION_EVIDENCE_REQUIRED")


@dataclass(frozen=True, slots=True)
class NetworkRule:
    source_cidr: str
    destination: str
    port: int
    protocol: str = "TCP"
    mtls_required: bool = True
    approved_public_edge: bool = False

    def validate(self) -> None:
        network=ipaddress.ip_network(self.source_cidr, strict=False)
        if self.port < 1 or self.port > 65535:
            raise PlatformControlError("NETWORK_PORT_INVALID")
        if str(network) in {"0.0.0.0/0","::/0"} and not self.approved_public_edge:
            raise PlatformControlError("PUBLIC_NETWORK_RULE_FORBIDDEN")
        if not self.mtls_required:
            raise PlatformControlError("MTLS_REQUIRED")


@dataclass(frozen=True, slots=True)
class KubernetesBaseline:
    image: str
    run_as_non_root: bool
    read_only_root_filesystem: bool
    seccomp_profile: str
    dropped_capabilities: tuple[str, ...]
    automount_service_account_token: bool
    cpu_request: str
    memory_request: str
    liveness_probe: bool
    readiness_probe: bool

    def validate(self) -> None:
        if "@sha256:" not in self.image or self.image.endswith(":latest"):
            raise PlatformControlError("K8S_IMAGE_DIGEST_REQUIRED")
        if not self.run_as_non_root or not self.read_only_root_filesystem:
            raise PlatformControlError("K8S_HARDENING_REQUIRED")
        if self.seccomp_profile != "RuntimeDefault" or "ALL" not in self.dropped_capabilities:
            raise PlatformControlError("K8S_KERNEL_HARDENING_REQUIRED")
        if self.automount_service_account_token:
            raise PlatformControlError("K8S_TOKEN_AUTOMOUNT_FORBIDDEN")
        if not all([self.cpu_request,self.memory_request,self.liveness_probe,self.readiness_probe]):
            raise PlatformControlError("K8S_OPERABILITY_REQUIRED")


@dataclass(frozen=True, slots=True)
class ControlEvidence:
    control_id: str
    owner: str
    approver: str
    evidence_hash: str
    reviewed_at: datetime
    review_due_at: datetime

    def effective(self, now: datetime) -> bool:
        return bool(self.control_id and self.owner and self.approver and self.owner != self.approver and HEX64.fullmatch(self.evidence_hash) and utc(self.reviewed_at) <= utc(now) < utc(self.review_due_at))


@dataclass(slots=True)
class IdempotencyRegistry:
    _entries: dict[str, tuple[str, object]] = field(default_factory=dict)

    def execute(self, key: str, request: object, operation) -> object:
        request_hash=digest(request)
        if key in self._entries:
            previous_hash, result=self._entries[key]
            if previous_hash != request_hash:
                raise PlatformControlError("IDEMPOTENCY_CONFLICT")
            return result
        result=operation()
        self._entries[key]=(request_hash,result)
        return result
