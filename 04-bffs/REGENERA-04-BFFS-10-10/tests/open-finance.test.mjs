import test from 'node:test';
import assert from 'node:assert/strict';
import { assertOpenFinanceClient, assertConsent, buildOpenFinanceResponse } from '../packages/open-finance-api/src/index.mjs';

const validClient = { certificate: { verified: true }, token: { audience: 'regenera-open-finance', scopes: ['accounts.read'] }, requiredScope: 'accounts.read' };

test('open finance exige mTLS', () => assert.throws(() => assertOpenFinanceClient({ ...validClient, certificate: { verified: false } }), /MTLS_REQUIRED/));
test('open finance exige audience correta', () => assert.throws(() => assertOpenFinanceClient({ ...validClient, token: { audience: 'other', scopes: ['accounts.read'] } }), /TOKEN_AUDIENCE_INVALID/));
test('consentimento revogado é bloqueado', () => assert.throws(() => assertConsent({ status: 'REVOKED', expiresAt: '2099-01-01', permissions: ['ACCOUNTS_READ'] }, 'ACCOUNTS_READ'), /CONSENT_NOT_AUTHORISED/));
test('consentimento expirado é bloqueado', () => assert.throws(() => assertConsent({ status: 'AUTHORISED', expiresAt: '2020-01-01', permissions: ['ACCOUNTS_READ'] }, 'ACCOUNTS_READ'), /CONSENT_EXPIRED/));
test('consentimento exige permissão exata', () => assert.throws(() => assertConsent({ status: 'AUTHORISED', expiresAt: '2099-01-01', permissions: ['BALANCES_READ'] }, 'ACCOUNTS_READ'), /CONSENT_PERMISSION_MISSING/));
test('resposta remove campos internos', () => {
  const response = buildOpenFinanceResponse({ interactionId: '123e4567-e89b-42d3-a456-426614174004', consentId: 'c', records: [{ id: 'a', internalRiskScore: 99, operatorNote: 'secret' }] });
  assert.deepEqual(response.data, [{ id: 'a' }]);
});
test('paginação limita cem itens', () => assert.throws(() => buildOpenFinanceResponse({ interactionId: '123e4567-e89b-42d3-a456-426614174004', consentId: 'c', records: [], pageSize: 101 }), /PAGE_SIZE_INVALID/));
