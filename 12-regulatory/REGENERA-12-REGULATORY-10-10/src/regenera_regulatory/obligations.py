from dataclasses import dataclass
from datetime import date
from .canonical import require_identifier, require_sha256, sha256_hex
from .errors import StateTransitionError, ValidationError, ExternalDependencyError

@dataclass(frozen=True,slots=True)
class ObligationDefinition:
    obligation_id:str
    domain:str
    owner_id:str
    legal_source_digest:str|None
    due_date_confirmed:bool
    layout_approved:bool
    channel_homologated:bool
    independent_approval_required:bool=True

    def __post_init__(self):
        require_identifier(self.obligation_id); require_identifier(self.domain); require_identifier(self.owner_id)
        if self.legal_source_digest is not None: require_sha256(self.legal_source_digest)

    @property
    def activation_ready(self):
        return bool(self.legal_source_digest and self.due_date_confirmed and self.layout_approved and self.channel_homologated)

class ObligationInstance:
    _allowed={
        'DRAFT':{'READY','OVERDUE'},
        'READY':{'APPROVED','OVERDUE'},
        'APPROVED':{'SUBMITTED','UNKNOWN','REJECTED','OVERDUE'},
        'SUBMITTED':{'ACCEPTED','REJECTED','UNKNOWN'},
        'UNKNOWN':{'SUBMITTED','ACCEPTED','REJECTED'},
        'REJECTED':{'DRAFT'},
        'ACCEPTED':set(),
        'OVERDUE':{'READY','APPROVED','SUBMITTED','UNKNOWN','REJECTED'},
    }
    def __init__(self,instance_id,definition,period,due_date):
        require_identifier(instance_id)
        if not isinstance(definition,ObligationDefinition): raise ValidationError('definição inválida')
        if not period.strip(): raise ValidationError('período obrigatório')
        if not isinstance(due_date,date): raise ValidationError('prazo inválido')
        self.instance_id=instance_id; self.definition=definition; self.period=period; self.due_date=due_date
        self.state='DRAFT'; self.report_digest=None; self.evidence_digest=None; self.approval_digest=None; self.protocol=None

    def bind_payload(self,report_digest,evidence_digest):
        if self.state not in {'DRAFT','REJECTED'}: raise StateTransitionError('payload não pode ser alterado neste estado')
        require_sha256(report_digest); require_sha256(evidence_digest)
        self.report_digest=report_digest; self.evidence_digest=evidence_digest
        if self.state=='REJECTED': self.state='DRAFT'
        return self.payload_digest

    @property
    def payload_digest(self):
        if not self.report_digest or not self.evidence_digest: return None
        return sha256_hex({'obligation_id':self.definition.obligation_id,'instance_id':self.instance_id,'period':self.period,'report_digest':self.report_digest,'evidence_digest':self.evidence_digest})

    def mark_ready(self):
        if not self.definition.activation_ready: raise ExternalDependencyError('obrigação sem configuração externa aprovada')
        if not self.payload_digest: raise ValidationError('relatório e evidência obrigatórios')
        self._transition('READY')

    def approve(self,approval_digest):
        require_sha256(approval_digest)
        if approval_digest!=self.payload_digest: raise ValidationError('aprovação não cobre o payload atual')
        self.approval_digest=approval_digest; self._transition('APPROVED')

    def record_submission(self,state,protocol=None):
        if state not in {'SUBMITTED','UNKNOWN','REJECTED'}: raise ValidationError('resultado de submissão inválido')
        if state=='SUBMITTED' and not protocol: raise ValidationError('protocolo externo obrigatório')
        if protocol and protocol.startswith(('LOCAL-','TEST-','SIM-')): raise ValidationError('protocolo externo inválido')
        self.protocol=protocol; self._transition(state)

    def reconcile(self,state,protocol=None):
        if self.state!='UNKNOWN': raise StateTransitionError('reconciliação exige estado UNKNOWN')
        if state not in {'SUBMITTED','ACCEPTED','REJECTED'}: raise ValidationError('resultado de reconciliação inválido')
        if state in {'SUBMITTED','ACCEPTED'} and not protocol: raise ValidationError('protocolo externo obrigatório')
        self.protocol=protocol; self._transition(state)

    def mark_accepted(self):
        if not self.protocol: raise ValidationError('aceite sem protocolo')
        self._transition('ACCEPTED')

    def evaluate_deadline(self,today):
        if today>self.due_date and self.state not in {'ACCEPTED','REJECTED'}:
            self._transition('OVERDUE')
        return self.state

    def _transition(self,target):
        if target not in self._allowed.get(self.state,set()): raise StateTransitionError(f'transição inválida: {self.state}->{target}')
        self.state=target
