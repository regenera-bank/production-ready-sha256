from dataclasses import dataclass,asdict
from .canonical import require_identifier,require_sha256,sha256_hex
from .errors import ConflictError,ExternalDependencyError,ValidationError,StateTransitionError

@dataclass(frozen=True,slots=True)
class SubmissionRequest:
    submission_id:str
    obligation_id:str
    report_digest:str
    evidence_digest:str
    approval_payload_digest:str
    idempotency_key:str
    channel:str

    def __post_init__(self):
        require_identifier(self.submission_id); require_identifier(self.obligation_id); require_identifier(self.idempotency_key); require_identifier(self.channel)
        require_sha256(self.report_digest); require_sha256(self.evidence_digest); require_sha256(self.approval_payload_digest)
        expected=sha256_hex({'report_digest':self.report_digest,'evidence_digest':self.evidence_digest,'obligation_id':self.obligation_id})
        if self.approval_payload_digest!=expected: raise ValidationError('aprovação não cobre relatório e evidência')

@dataclass(frozen=True,slots=True)
class SubmissionResult:
    state:str
    protocol:str|None
    reason:str|None
    request_digest:str

class SubmissionGateway:
    def __init__(self,channels):
        self.channels=dict(channels); self._registry={}
    def submit(self,request,transport):
        if self.channels.get(request.channel)!='ACTIVE_HOMOLOGATED': raise ExternalDependencyError('canal não homologado')
        digest=sha256_hex(asdict(request)); prior=self._registry.get(request.idempotency_key)
        if prior:
            prior_digest,prior_result=prior
            if prior_digest!=digest: raise ConflictError('idempotency key reutilizada com outro payload')
            return prior_result
        response=transport(request)
        status=response.get('status') if isinstance(response,dict) else None
        if status=='ACKNOWLEDGED':
            protocol=response.get('protocol')
            if not protocol or protocol.startswith(('LOCAL-','TEST-','SIM-')): raise ValidationError('protocolo externo inválido')
            result=SubmissionResult('SUBMITTED',protocol,None,digest)
        elif status=='REJECTED':
            reason=response.get('reason','').strip()
            if not reason: raise ValidationError('rejeição sem motivo')
            result=SubmissionResult('REJECTED',response.get('protocol'),reason,digest)
        elif status in {'TIMEOUT','AMBIGUOUS','UNAVAILABLE'} or status is None:
            result=SubmissionResult('UNKNOWN',None,'resultado externo ambíguo',digest)
        else:
            raise ValidationError('status externo inválido')
        self._registry[request.idempotency_key]=(digest,result); return result
    def reconcile(self,idempotency_key,lookup):
        if idempotency_key not in self._registry: raise ValidationError('submissão desconhecida')
        digest,current=self._registry[idempotency_key]
        if current.state!='UNKNOWN': return current
        response=lookup(idempotency_key)
        if response.get('status')=='ACKNOWLEDGED' and response.get('protocol') and not response['protocol'].startswith(('LOCAL-','TEST-','SIM-')):
            result=SubmissionResult('SUBMITTED',response['protocol'],None,digest)
        elif response.get('status')=='REJECTED' and response.get('reason'):
            result=SubmissionResult('REJECTED',response.get('protocol'),response['reason'],digest)
        else:
            return current
        self._registry[idempotency_key]=(digest,result); return result
