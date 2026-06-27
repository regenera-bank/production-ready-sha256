import { assert } from '../../shared/src/errors.mjs';
import { correlationId } from '../../shared/src/correlation.mjs';

export function assertOpenFinanceClient({ certificate, token, requiredScope }) {
  assert(certificate?.verified === true, 'MTLS_REQUIRED', 401);
  assert(token?.audience === 'regenera-open-finance', 'TOKEN_AUDIENCE_INVALID', 401);
  assert(Array.isArray(token.scopes) && token.scopes.includes(requiredScope), 'SCOPE_REQUIRED', 403);
}

export function assertConsent(consent, permission, now = Date.now()) {
  assert(consent?.status === 'AUTHORISED', 'CONSENT_NOT_AUTHORISED', 403);
  assert(new Date(consent.expiresAt).getTime() > now, 'CONSENT_EXPIRED', 403);
  assert(Array.isArray(consent.permissions) && consent.permissions.includes(permission), 'CONSENT_PERMISSION_MISSING', 403);
}

export function buildOpenFinanceResponse({ interactionId, consentId, records, page = 1, pageSize = 25 }) {
  assert(Number.isInteger(page) && page >= 1, 'PAGE_INVALID', 400);
  assert(Number.isInteger(pageSize) && pageSize >= 1 && pageSize <= 100, 'PAGE_SIZE_INVALID', 400);
  return {
    meta: { interactionId: correlationId(interactionId), consentId, page, pageSize },
    data: records.map(({ internalRiskScore, operatorNote, ...publicRecord }) => publicRecord)
  };
}
