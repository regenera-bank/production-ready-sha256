import test from 'node:test';
import assert from 'node:assert/strict';
import { assertBrowserRequest, composeHome, createPixIntent } from '../packages/web-bff/src/index.mjs';
import { IdempotencyStore } from '../packages/shared/src/idempotency.mjs';

const key = '123e4567-e89b-42d3-a456-426614174001';
const correlationId = '123e4567-e89b-42d3-a456-426614174002';

test('web exige origem permitida', () => assert.throws(() => assertBrowserRequest({ origin: 'https://evil', allowedOrigins: ['https://bank'], csrfCookie: 'x'.repeat(32), csrfHeader: 'x'.repeat(32) }), /ORIGIN_NOT_ALLOWED/));
test('web exige csrf casado', () => assert.throws(() => assertBrowserRequest({ origin: 'https://bank', allowedOrigins: ['https://bank'], csrfCookie: 'x'.repeat(32), csrfHeader: 'y'.repeat(32) }), /CSRF_MISMATCH/));
test('home aceita somente saldo da fonte autoritativa', () => assert.throws(() => composeHome({ accounts: [{ source: 'CLIENT', availableBalanceCents: '100' }], recentTransactions: [] }), /NON_AUTHORITATIVE/));
test('home preserva saldo sem recalcular', () => {
  const response = composeHome({ accounts: [{ source: 'CORE_BANKING', availableBalanceCents: '101' }], recentTransactions: [], correlation: correlationId });
  assert.equal(response.accounts[0].availableBalanceCents, '101');
  assert.equal(response.cacheControl, 'no-store');
});
test('pix web devolve replay idempotente', async () => {
  const store = new IdempotencyStore();
  let calls = 0;
  const input = { accountId: 'a', destination: 'b', amountCents: '100', idempotencyKey: key, correlationId };
  const gateway = async () => { calls += 1; return { paymentId: 'p1', status: 'DEBITED' }; };
  assert.equal((await createPixIntent({ input, idempotency: store, gateway })).paymentId, 'p1');
  assert.equal((await createPixIntent({ input, idempotency: store, gateway })).paymentId, 'p1');
  assert.equal(calls, 1);
});
test('pix web bloqueia unknown', async () => {
  const store = new IdempotencyStore();
  const input = { accountId: 'a', destination: 'b', amountCents: '100', idempotencyKey: key, correlationId };
  await assert.rejects(() => createPixIntent({ input, idempotency: store, gateway: async () => ({ status: 'UNKNOWN' }) }), /EXECUTION_STATE_UNKNOWN/);
  await assert.rejects(() => createPixIntent({ input, idempotency: store, gateway: async () => ({ status: 'DEBITED' }) }), /EXECUTION_STATE_UNKNOWN/);
});
