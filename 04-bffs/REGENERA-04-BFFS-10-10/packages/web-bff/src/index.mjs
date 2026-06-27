import { BffError, assert } from '../../shared/src/errors.mjs';
import { correlationId } from '../../shared/src/correlation.mjs';
import { positiveCents } from '../../shared/src/money.mjs';

export function assertBrowserRequest({ origin, allowedOrigins, csrfCookie, csrfHeader }) {
  assert(allowedOrigins.includes(origin), 'ORIGIN_NOT_ALLOWED', 403);
  assert(typeof csrfCookie === 'string' && csrfCookie.length >= 32, 'CSRF_COOKIE_INVALID', 403);
  assert(csrfHeader === csrfCookie, 'CSRF_MISMATCH', 403);
}

export function composeHome({ accounts, recentTransactions, correlation }) {
  for (const account of accounts) {
    assert(account.source === 'CORE_BANKING', 'NON_AUTHORITATIVE_ACCOUNT_SOURCE', 500);
    assert(typeof account.availableBalanceCents === 'string', 'INVALID_ACCOUNT_BALANCE', 500);
  }

  return {
    correlationId: correlationId(correlation),
    cacheControl: 'no-store',
    accounts: structuredClone(accounts),
    recentTransactions: structuredClone(recentTransactions)
  };
}

export async function createPixIntent({ input, idempotency, gateway }) {
  positiveCents(input.amountCents);
  const payload = {
    accountId: input.accountId,
    destination: input.destination,
    amountCents: input.amountCents
  };
  const started = idempotency.begin('web:pix', input.idempotencyKey, payload);
  if (started.kind === 'REPLAY') return started.response;

  try {
    const response = await gateway(payload, correlationId(input.correlationId));
    if (response.status === 'UNKNOWN') {
      idempotency.markUnknown('web:pix', input.idempotencyKey);
      throw new BffError('EXECUTION_STATE_UNKNOWN', 409);
    }
    idempotency.complete('web:pix', input.idempotencyKey, response);
    return response;
  } catch (error) {
    if (error.code !== 'EXECUTION_STATE_UNKNOWN') idempotency.markUnknown('web:pix', input.idempotencyKey);
    throw error;
  }
}
