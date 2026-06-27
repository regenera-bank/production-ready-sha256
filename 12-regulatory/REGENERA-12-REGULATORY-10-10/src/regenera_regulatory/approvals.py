from dataclasses import dataclass
from datetime import datetime,timezone
from .canonical import require_identifier,require_sha256,sha256_hex
from .errors import AuthorizationError,ConflictError,StateTransitionError,ValidationError

@dataclass(frozen=True,slots=True)
class ApprovalDecision:
    request_id:str
    payload_digest:str
    maker_id:str
    checker_id:str
    decided_at:str
    signature_fingerprint:str
    decision_digest:str

class ApprovalRequest:
    def __init__(self,request_id,payload_digest,maker_id,expires_at):
        require_identifier(request_id); require_sha256(payload_digest); require_identifier(maker_id)
        self.request_id=request_id; self.payload_digest=payload_digest; self.maker_id=maker_id
        self.expires_at=datetime.fromisoformat(expires_at.replace('Z','+00:00'))
        if self.expires_at.tzinfo is None: raise ValidationError('expiração precisa de timezone')
        self.state='PENDING'; self.decision=None
    def approve(self,checker_id,mfa_verified,signature_fingerprint,decided_at):
        require_identifier(checker_id)
        now=datetime.fromisoformat(decided_at.replace('Z','+00:00'))
        if self.state!='PENDING': raise StateTransitionError('aprovação já decidida')
        if checker_id==self.maker_id: raise AuthorizationError('autoaprovação bloqueada')
        if not mfa_verified: raise AuthorizationError('MFA obrigatório')
        if now>self.expires_at: self.state='EXPIRED'; raise StateTransitionError('aprovação expirada')
        if not signature_fingerprint or len(signature_fingerprint)<16: raise ValidationError('fingerprint institucional inválido')
        body={'request_id':self.request_id,'payload_digest':self.payload_digest,'maker_id':self.maker_id,'checker_id':checker_id,'decided_at':decided_at,'signature_fingerprint':signature_fingerprint}
        self.decision=ApprovalDecision(**body,decision_digest=sha256_hex(body)); self.state='APPROVED'; return self.decision
    def reject(self,checker_id,reason):
        if self.state!='PENDING': raise StateTransitionError('aprovação já decidida')
        if checker_id==self.maker_id: raise AuthorizationError('autoaprovação bloqueada')
        if not reason.strip(): raise ValidationError('motivo obrigatório')
        self.state='REJECTED'
