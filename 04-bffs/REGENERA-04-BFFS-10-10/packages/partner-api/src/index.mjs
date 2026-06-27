import { createHmac, timingSafeEqual } from 'node:crypto';
import { assert, BffError } from '../../shared/src/errors.mjs';
import { positiveCents } from '../../shared/src/money.mjs';

export function authenticatePartner({ certificate, allowedFingerprints, token, requiredScope }) {
  assert(certificate?.verified === true, 'MTLS_REQUIRED', 401);
  assert(allowedFingerprints.includes(certificate.fingerprint256), 'MTLS_CERTIFICATE_REJECTED', 403);
  assert(Array.isArray(token?.scopes) && token.scopes.includes(requiredScope), 'SCOPE_REQUIRED', 403);
  return { clientId: token.clientId };
}

export class SlidingQuota {
  constructor(limit) {
    this.limit = limit;
    this.usage = new Map();
  }
  consume(clientId) {
    const used = this.usage.get(clientId) ?? 0;
    if (used >= this.limit) throw new BffError('QUOTA_EXCEEDED', 429);
    this.usage.set(clientId, used + 1);
    return this.limit - used - 1;
  }
}

export function createPartnerPixRequest(input) {
  positiveCents(input.amountCents);
  assert(typeof input.idempotencyKey === 'string', 'IDEMPOTENCY_KEY_REQUIRED', 400);
  return {
    accountId: input.accountId,
    destinationKeyHash: input.destinationKeyHash,
    amountCents: String(input.amountCents),
    idempotencyKey: input.idempotencyKey
  };
}

export function signWebhook(secret, timestamp, body) {
  return createHmac('sha256', secret).update(String(timestamp)).update('.').update(body).digest('base64url');
}

export function verifyWebhook({ secret, timestamp, body, signature, now = Date.now(), toleranceMs = 300_000 }) {
  if (!Number.isInteger(timestamp)) return false;
  if (Math.abs(now - timestamp * 1000) > toleranceMs) return false;
  const expected = Buffer.from(signWebhook(secret, timestamp, body));
  const received = Buffer.from(signature);
  return expected.length === received.length && timingSafeEqual(expected, received);
}
