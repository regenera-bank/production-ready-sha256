export function validateApproval(record) {
  const failures = [];
  if (!record.author) failures.push('author ausente');
  if (record.institutional_approval === 'APPROVED' && !record.independent_reviewer) failures.push('revisor independente ausente');
  if (record.institutional_approval === 'APPROVED' && record.independent_reviewer === record.author) failures.push('autoaprovação bloqueada');
  if (record.institutional_approval === 'APPROVED' && record.cryptographic_signature !== 'VERIFIED') failures.push('assinatura não verificada');
  return failures;
}

export function evaluateControl(control, evidencePresent, now = new Date()) {
  if (!control.owner) return 'INEFFECTIVE_OWNER_MISSING';
  if (!evidencePresent) return 'INEFFECTIVE_EVIDENCE_MISSING';
  if (control.exception?.expires_at && new Date(control.exception.expires_at) <= now) return 'BLOCKED_EXCEPTION_EXPIRED';
  return 'EFFECTIVE';
}
