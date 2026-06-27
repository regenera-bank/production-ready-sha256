from dataclasses import dataclass
from datetime import date,datetime
from .canonical import require_identifier,sha256_hex
from .errors import AuthorizationError,ConflictError,StateTransitionError,ValidationError

@dataclass(frozen=True,slots=True)
class AccessGrant:
    grant_id:str
    subject_id:str
    purpose:str
    max_classification:str
    expires_at:str
    approver_id:str
    requester_id:str
    def __post_init__(self):
        require_identifier(self.grant_id); require_identifier(self.subject_id); require_identifier(self.approver_id); require_identifier(self.requester_id)
        if self.approver_id==self.requester_id: raise AuthorizationError('autoaprovação bloqueada')
        if not self.purpose.strip(): raise ValidationError('finalidade obrigatória')
        stamp=datetime.fromisoformat(self.expires_at.replace('Z','+00:00'))
        if stamp.tzinfo is None: raise ValidationError('expiração precisa de timezone')
    def allows(self,purpose,classification,at):
        levels={'PUBLIC':0,'INTERNAL':1,'CONFIDENTIAL':2,'RESTRICTED':3}
        if purpose!=self.purpose: return False
        if classification not in levels or self.max_classification not in levels: return False
        return levels[classification]<=levels[self.max_classification] and datetime.fromisoformat(at.replace('Z','+00:00'))<=datetime.fromisoformat(self.expires_at.replace('Z','+00:00'))

@dataclass(frozen=True,slots=True)
class RetentionRecord:
    record_id:str
    retain_until:str
    legal_hold:bool=False

    def __post_init__(self):
        require_identifier(self.record_id); date.fromisoformat(self.retain_until)

    def can_dispose(self,on_date):
        return not self.legal_hold and on_date>=date.fromisoformat(self.retain_until)

class DataSubjectRequest:
    def __init__(self,request_id,subject_id,request_type,due_date):
        require_identifier(request_id); require_identifier(subject_id)
        if request_type not in {'ACCESS','CORRECTION','DELETION','PORTABILITY','REVOCATION'}: raise ValidationError('tipo inválido')
        self.request_id=request_id; self.subject_id=subject_id; self.request_type=request_type; self.due_date=due_date
        self.state='RECEIVED'; self.identity_verified=False; self.completion_digest=None
    def verify_identity(self):
        if self.state!='RECEIVED': raise StateTransitionError('estado inválido')
        self.identity_verified=True; self.state='IN_PROGRESS'
    def complete(self,evidence,reviewer_id,operator_id):
        if self.state!='IN_PROGRESS' or not self.identity_verified: raise StateTransitionError('identidade não verificada')
        if reviewer_id==operator_id: raise AuthorizationError('revisão independente obrigatória')
        if not evidence: raise ValidationError('evidência obrigatória')
        self.completion_digest=sha256_hex({'request_id':self.request_id,'evidence':evidence,'reviewer_id':reviewer_id}); self.state='FULFILLED'; return self.completion_digest
