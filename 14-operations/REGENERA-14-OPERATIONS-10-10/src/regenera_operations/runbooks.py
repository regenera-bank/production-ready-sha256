from __future__ import annotations
from dataclasses import dataclass
import re
from .errors import ConflictError, ValidationError, AuthorizationError
from .utils import digest, require_sha256

_VERSION=re.compile(r"^[1-9]\d*\.[0-9]+\.[0-9]+$")

@dataclass(frozen=True, slots=True)
class Runbook:
    runbook_id: str
    version: str
    owner_id: str
    steps: tuple[str, ...]
    rollback_steps: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.runbook_id.strip() or not self.owner_id.strip() or not _VERSION.fullmatch(self.version):
            raise ValidationError("runbook inválido")
        if not self.steps or any(not step.strip() for step in self.steps):
            raise ValidationError("runbook sem passos")
        if not self.rollback_steps:
            raise ValidationError("runbook sem rollback")

    @property
    def content_digest(self) -> str:
        return digest({"id":self.runbook_id,"version":self.version,"owner":self.owner_id,"steps":self.steps,"rollback":self.rollback_steps})

class RunbookRegistry:
    def __init__(self) -> None:
        self._versions: dict[tuple[str,str],Runbook]={}
        self._active: dict[str,Runbook]={}

    def publish(self, runbook: Runbook) -> Runbook:
        key=(runbook.runbook_id,runbook.version)
        current=self._versions.get(key)
        if current and current.content_digest != runbook.content_digest:
            raise ConflictError("versão publicada é imutável")
        self._versions[key]=current or runbook
        return self._versions[key]

    def activate(self, runbook_id: str, version: str, approval_digest: str, approver_id: str) -> Runbook:
        runbook=self._versions.get((runbook_id,version))
        if not runbook:
            raise ValidationError("runbook ausente")
        require_sha256(approval_digest, "approval_digest")
        if approval_digest != runbook.content_digest:
            raise AuthorizationError("aprovação vinculada a outro runbook")
        if approver_id == runbook.owner_id:
            raise AuthorizationError("owner não ativa o próprio runbook")
        self._active[runbook_id]=runbook
        return runbook
