import test from 'node:test';
import assert from 'node:assert/strict';
import { authenticatePartner, SlidingQuota, createPartnerPixRequest, signWebhook, verifyWebhook } from '../packages/partner-api/src/index.mjs';

test('parceiro exige mTLS', () => assert.throws(() => authenticatePartner({ certificate: { verified: false }, allowedFingerprints: [], token: { scopes: ['pix.write'] }, requiredScope: 'pix.write' }), /MTLS_REQUIRED/));
test('parceiro exige fingerprint aprovado', () => assert.throws(() => authenticatePartner({ certificate: { verified: true, fingerprint256: 'bad' }, allowedFingerprints: ['good'], token: { scopes: ['pix.write'] }, requiredScope: 'pix.write' }), /MTLS_CERTIFICATE_REJECTED/));
test('parceiro exige escopo', () => assert.throws(() => authenticatePartner({ certificate: { verified: true, fingerprint256: 'good' }, allowedFingerprints: ['good'], token: { scopes: ['accounts.read'] }, requiredScope: 'pix.write' }), /SCOPE_REQUIRED/));
test('quota bloqueia excesso', () => {
  const quota = new SlidingQuota(2);
  quota.consume('c'); quota.consume('c');
  assert.throws(() => quota.consume('c'), /QUOTA_EXCEEDED/);
});
test('requisição pix não transporta chave crua', () => {
  const request = createPartnerPixRequest({ accountId: 'a', destinationKeyHash: 'hash', amountCents: '100', idempotencyKey: 'k' });
  assert.equal('destinationKey' in request, false);
  assert.equal(request.destinationKeyHash, 'hash');
});
test('webhook válido passa', () => {
  const secret = Buffer.from('s'.repeat(32));
  const body = Buffer.from('{"id":"1"}');
  const timestamp = 1_700_000_000;
  const signature = signWebhook(secret, timestamp, body);
  assert.equal(verifyWebhook({ secret, timestamp, body, signature, now: timestamp * 1000 }), true);
});
test('webhook adulterado falha', () => {
  const secret = Buffer.from('s'.repeat(32));
  const timestamp = 1_700_000_000;
  const signature = signWebhook(secret, timestamp, Buffer.from('a'));
  assert.equal(verifyWebhook({ secret, timestamp, body: Buffer.from('b'), signature, now: timestamp * 1000 }), false);
});
test('webhook vencido falha', () => {
  const secret = Buffer.from('s'.repeat(32));
  const body = Buffer.from('a');
  const timestamp = 1_700_000_000;
  const signature = signWebhook(secret, timestamp, body);
  assert.equal(verifyWebhook({ secret, timestamp, body, signature, now: timestamp * 1000 + 300_001 }), false);
});
