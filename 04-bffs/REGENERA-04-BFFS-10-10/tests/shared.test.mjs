import test from 'node:test';
import assert from 'node:assert/strict';
import { parseCents, positiveCents } from '../packages/shared/src/money.mjs';
import { IdempotencyStore } from '../packages/shared/src/idempotency.mjs';
import { CircuitBreaker } from '../packages/shared/src/resilience.mjs';
import { AuditChain } from '../packages/shared/src/audit-chain.mjs';
import { safeTelemetry } from '../packages/shared/src/telemetry.mjs';

const key = '123e4567-e89b-42d3-a456-426614174000';

test('dinheiro aceita centavos inteiros', () => assert.equal(parseCents('1200'), 1200n));
test('dinheiro recusa float', () => assert.throws(() => parseCents(10.5), /INVALID_MONEY/));
test('valor financeiro precisa ser positivo', () => assert.throws(() => positiveCents('0'), /AMOUNT_NOT_POSITIVE/));
test('idempotência devolve o resultado original', () => {
  const store = new IdempotencyStore();
  assert.deepEqual(store.begin('pix', key, { amount: '100' }), { kind: 'NEW' });
  store.complete('pix', key, { id: 'p1', status: 'DEBITED' });
  assert.deepEqual(store.begin('pix', key, { amount: '100' }), { kind: 'REPLAY', response: { id: 'p1', status: 'DEBITED' } });
});
test('idempotência recusa payload diferente', () => {
  const store = new IdempotencyStore();
  store.begin('pix', key, { amount: '100' });
  assert.throws(() => store.begin('pix', key, { amount: '101' }), /IDEMPOTENCY_CONFLICT/);
});
test('estado desconhecido bloqueia repetição', () => {
  const store = new IdempotencyStore();
  store.begin('pix', key, { amount: '100' });
  store.markUnknown('pix', key);
  assert.throws(() => store.begin('pix', key, { amount: '100' }), /EXECUTION_STATE_UNKNOWN/);
});
test('reconciliação fecha estado desconhecido', () => {
  const store = new IdempotencyStore();
  store.begin('pix', key, { amount: '100' });
  store.markUnknown('pix', key);
  store.reconcile('pix', key, { status: 'SETTLED' });
  assert.equal(store.begin('pix', key, { amount: '100' }).response.status, 'SETTLED');
});
test('circuit breaker abre após falhas', async () => {
  let now = 0;
  const breaker = new CircuitBreaker({ failureThreshold: 2, resetAfterMs: 1000, now: () => now });
  await assert.rejects(() => breaker.execute(async () => { throw new Error('down'); }));
  await assert.rejects(() => breaker.execute(async () => { throw new Error('down'); }));
  await assert.rejects(() => breaker.execute(async () => 'ok'), /CIRCUIT_OPEN/);
  now = 1001;
  assert.equal(await breaker.execute(async () => 'ok'), 'ok');
});
test('trilha encadeada detecta adulteração', () => {
  const chain = new AuditChain();
  chain.append({ action: 'OPEN' });
  chain.append({ action: 'APPROVE' });
  const entries = chain.entries();
  assert.equal(AuditChain.verify(entries), true);
  entries[0].event.action = 'DELETE';
  assert.equal(AuditChain.verify(entries), false);
});
test('telemetria remove campos sensíveis', () => {
  assert.deepEqual(safeTelemetry({ correlationId: 'c', route: '/x', token: 'secret', document: 'cpf' }), { correlationId: 'c', route: '/x' });
});
