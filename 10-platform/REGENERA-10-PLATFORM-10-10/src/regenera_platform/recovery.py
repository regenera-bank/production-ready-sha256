from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from .errors import PlatformControlError


def file_hash(data: bytes) -> str:
    return sha256(data).hexdigest()


@dataclass(frozen=True, slots=True)
class BackupRecord:
    backup_id: str
    created_at: datetime
    payload_sha256: str
    encrypted: bool
    immutable: bool
    cross_region: bool

    def validate(self) -> None:
        if len(self.payload_sha256) != 64:
            raise PlatformControlError("BACKUP_HASH_INVALID")
        if not self.encrypted or not self.immutable:
            raise PlatformControlError("BACKUP_PROTECTION_REQUIRED")


@dataclass(frozen=True, slots=True)
class RestoreExercise:
    backup: BackupRecord
    restored_sha256: str
    started_at: datetime
    completed_at: datetime
    data_loss_minutes: float
    financial_breaks: int

    def validate(self, rto_minutes: int, rpo_minutes: int) -> None:
        self.backup.validate()
        if self.restored_sha256 != self.backup.payload_sha256:
            raise PlatformControlError("RESTORE_HASH_MISMATCH")
        elapsed=(self.completed_at-self.started_at).total_seconds()/60
        if elapsed < 0 or elapsed > rto_minutes:
            raise PlatformControlError("RTO_BREACHED")
        if self.data_loss_minutes < 0 or self.data_loss_minutes > rpo_minutes:
            raise PlatformControlError("RPO_BREACHED")
        if self.financial_breaks != 0:
            raise PlatformControlError("RESTORE_FINANCIAL_BREAK")


@dataclass(frozen=True, slots=True)
class FailoverDecision:
    primary_state: str
    replica_lag_seconds: float
    target_region_ready: bool
    reconciliation_complete: bool

    def decide(self, max_lag_seconds: float) -> str:
        if self.primary_state not in {"CONFIRMED_DOWN","CONFIRMED_HEALTHY","UNKNOWN"}:
            raise PlatformControlError("PRIMARY_STATE_INVALID")
        if self.primary_state == "UNKNOWN":
            return "BLOCKED_UNKNOWN"
        if self.primary_state == "CONFIRMED_HEALTHY":
            return "NO_FAILOVER"
        if not self.target_region_ready or self.replica_lag_seconds > max_lag_seconds or not self.reconciliation_complete:
            return "BLOCKED_NOT_READY"
        return "FAILOVER_AUTHORIZED"


@dataclass(frozen=True, slots=True)
class SLOWindow:
    target_percent: float
    observed_percent: float
    window_minutes: int

    def status(self) -> str:
        if not (0 < self.target_percent <= 100 and 0 <= self.observed_percent <= 100 and self.window_minutes > 0):
            raise PlatformControlError("SLO_INPUT_INVALID")
        return "BREACHED" if self.observed_percent < self.target_percent else "HEALTHY"
