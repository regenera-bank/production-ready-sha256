from dataclasses import dataclass,asdict
from datetime import datetime,date
from .canonical import require_identifier,require_sha256,sha256_hex
from .errors import ConflictError,EvidenceError,AuthorizationError,ValidationError

@dataclass(frozen=True,slots=True)
class EvidenceArtifact:
    evidence_id:str
    evidence_type:str
    sha256:str
    source:str
    collected_at:str
    classification:str
    retention_until:str

    def __post_init__(self):
        require_identifier(self.evidence_id); require_identifier(self.evidence_type); require_sha256(self.sha256)
        if not self.source.strip(): raise ValidationError('origem obrigatória')
        if self.classification not in {'PUBLIC','INTERNAL','CONFIDENTIAL','RESTRICTED'}: raise ValidationError('classificação inválida')
        stamp=datetime.fromisoformat(self.collected_at.replace('Z','+00:00'))
        if stamp.tzinfo is None: raise ValidationError('coleta precisa de timezone')
        date.fromisoformat(self.retention_until)

class EvidenceBundle:
    def __init__(self,bundle_id,owner_id,required_types):
        require_identifier(bundle_id); require_identifier(owner_id)
        self.bundle_id=bundle_id; self.owner_id=owner_id; self.required_types=frozenset(required_types)
        if not self.required_types: raise ValidationError('tipos de evidência obrigatórios')
        self._items={}; self._frozen=False; self._digest=None; self.approver_id=None
    @property
    def items(self): return tuple(self._items.values())
    @property
    def frozen(self): return self._frozen
    @property
    def complete(self): return self.required_types.issubset({x.evidence_type for x in self._items.values()})
    @property
    def digest(self): return self._digest
    def add(self,artifact):
        if self._frozen: raise ConflictError('bundle aprovado é imutável')
        if artifact.evidence_id in self._items:
            if self._items[artifact.evidence_id]!=artifact: raise ConflictError('evidence_id reutilizado')
            return self._items[artifact.evidence_id]
        self._items[artifact.evidence_id]=artifact; return artifact
    def freeze(self,approver_id,mfa_verified,approved_at):
        require_identifier(approver_id)
        if approver_id==self.owner_id: raise AuthorizationError('autoaprovação bloqueada')
        if not mfa_verified: raise AuthorizationError('MFA obrigatório')
        if not self.complete: raise EvidenceError('evidência incompleta')
        self._digest=sha256_hex({'bundle_id':self.bundle_id,'items':[asdict(x) for x in sorted(self._items.values(),key=lambda x:x.evidence_id)],'approved_at':approved_at,'approver_id':approver_id})
        self.approver_id=approver_id; self._frozen=True; return self._digest
