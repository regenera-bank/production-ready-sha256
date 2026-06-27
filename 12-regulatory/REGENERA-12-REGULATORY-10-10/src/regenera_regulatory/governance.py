from dataclasses import dataclass
from datetime import date
from .canonical import require_identifier,require_sha256
from .errors import AuthorizationError,ValidationError

@dataclass(frozen=True,slots=True)
class Control:
    control_id:str
    owner:str
    evidence_digest:str|None
    review_due:str
    external_dependency:bool=False

    def effective(self,on_date):
        if not self.owner.strip() or not self.evidence_digest: return False
        try: require_sha256(self.evidence_digest)
        except ValidationError: return False
        return on_date<=date.fromisoformat(self.review_due) and not self.external_dependency

@dataclass(frozen=True,slots=True)
class ExceptionRecord:
    exception_id:str
    control_id:str
    requester_id:str
    approver_id:str
    expires_on:str
    reason:str
    compensating_control:str

    def __post_init__(self):
        require_identifier(self.exception_id); require_identifier(self.control_id); require_identifier(self.requester_id); require_identifier(self.approver_id)
        if self.requester_id==self.approver_id: raise AuthorizationError('autoaprovação bloqueada')
        if not self.reason.strip() or not self.compensating_control.strip(): raise ValidationError('exceção incompleta')
    def valid(self,on_date): return on_date<=date.fromisoformat(self.expires_on)

class RegulatoryChange:
    def __init__(self,change_id,source_digest,owner_id):
        require_identifier(change_id); require_sha256(source_digest); require_identifier(owner_id)
        self.change_id=change_id; self.source_digest=source_digest; self.owner_id=owner_id; self.state='RECEIVED'; self.impact=None
    def assess(self,impact,reviewer_id):
        if reviewer_id==self.owner_id: raise AuthorizationError('análise independente obrigatória')
        if impact not in {'NONE','LOW','MEDIUM','HIGH','CRITICAL'}: raise ValidationError('impacto inválido')
        self.impact=impact; self.state='ASSESSED'
    def approve(self,approver_id):
        if self.state!='ASSESSED': raise ValidationError('mudança não avaliada')
        if approver_id==self.owner_id: raise AuthorizationError('autoaprovação bloqueada')
        self.state='APPROVED'
