from dataclasses import dataclass
from .canonical import require_identifier,require_minor_units,sha256_hex
from .errors import ConflictError,ValidationError

@dataclass(frozen=True,slots=True)
class RegulatoryReport:
    report_id:str
    obligation_id:str
    period:str
    rows:tuple
    control_count:int
    control_amount_minor:int
    currency:str
    digest:str

class ReportBuilder:
    def __init__(self,report_id,obligation_id,period,currency,allowed_fields,required_fields):
        require_identifier(report_id); require_identifier(obligation_id)
        if len(currency)!=3 or not currency.isalpha() or currency!=currency.upper(): raise ValidationError('moeda inválida')
        self.report_id=report_id; self.obligation_id=obligation_id; self.period=period; self.currency=currency
        self.allowed_fields=frozenset(allowed_fields); self.required_fields=frozenset(required_fields); self._rows=[]; self._references=set(); self._final=None
        if not self.required_fields.issubset(self.allowed_fields): raise ValidationError('campo obrigatório fora da allowlist')
    def add_row(self,row):
        if self._final: raise ConflictError('relatório final é imutável')
        if not isinstance(row,dict): raise ValidationError('linha inválida')
        extra=set(row)-self.allowed_fields; missing=self.required_fields-set(row)
        if extra: raise ValidationError('campo fora da allowlist')
        if missing: raise ValidationError('campo obrigatório ausente')
        if 'amount_minor' in row: require_minor_units(row['amount_minor'])
        reference=row.get('reference')
        if reference is not None:
            if reference in self._references: raise ConflictError('referência duplicada')
            self._references.add(reference)
        self._rows.append(dict(row))
    def finalize(self,expected_count,expected_amount_minor):
        if self._final: return self._final
        require_minor_units(expected_amount_minor)
        actual_count=len(self._rows); actual_amount=sum(r.get('amount_minor',0) for r in self._rows)
        if actual_count!=expected_count: raise ValidationError('contagem não reconciliada')
        if actual_amount!=expected_amount_minor: raise ValidationError('valor não reconciliado')
        body={'report_id':self.report_id,'obligation_id':self.obligation_id,'period':self.period,'rows':self._rows,'control_count':expected_count,'control_amount_minor':expected_amount_minor,'currency':self.currency}
        self._final=RegulatoryReport(**body,digest=sha256_hex(body)); return self._final

@dataclass(frozen=True,slots=True)
class ReconciliationResult:
    state:str
    differences:tuple

def reconcile_report(expected,actual):
    if expected is None or actual is None: return ReconciliationResult('UNKNOWN',('dataset_unavailable',))
    diffs=[]
    for key in ('count','amount_minor','currency','period'):
        if expected.get(key)!=actual.get(key): diffs.append(key)
    return ReconciliationResult('MATCHED' if not diffs else 'MISMATCH',tuple(diffs))
