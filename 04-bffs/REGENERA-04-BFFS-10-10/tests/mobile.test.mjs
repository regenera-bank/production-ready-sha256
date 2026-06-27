import test from 'node:test';
import assert from 'node:assert/strict';
import { NonceStore, authorizeMobileRequest, confirmMobilePix } from '../packages/mobile-bff/src/index.mjs';

const verifier = async token => ({ valid: token === 'valid', deviceId: 'device-1', platform: 'IOS' });

test('mobile recusa attestation inválida', async () => {
  await assert.rejects(() => authorizeMobileRequest({ attestation: { token: 'bad', nonce: 'n'.repeat(24) }, expectedDeviceId: 'device-1', verifier, nonceStore: new NonceStore() }), /ATTESTATION_INVALID/);
});
test('mobile recusa dispositivo diferente', async () => {
  await assert.rejects(() => authorizeMobileRequest({ attestation: { token: 'valid', nonce: 'n'.repeat(24) }, expectedDeviceId: 'device-2', verifier, nonceStore: new NonceStore() }), /DEVICE_BINDING_MISMATCH/);
});
test('mobile bloqueia replay de nonce', async () => {
  const store = new NonceStore();
  const attestation = { token: 'valid', nonce: 'n'.repeat(24) };
  await authorizeMobileRequest({ attestation, expectedDeviceId: 'device-1', verifier, nonceStore: store });
  await assert.rejects(() => authorizeMobileRequest({ attestation, expectedDeviceId: 'device-1', verifier, nonceStore: store }), /NONCE_REPLAY/);
});
test('mobile exige confirmação biométrica', async () => {
  await assert.rejects(() => confirmMobilePix({ request: { deviceId: 'device-1', biometricConfirmed: false, amountCents: '100' }, authorization: { deviceId: 'device-1' }, gateway: async () => ({ status: 'DEBITED' }) }), /BIOMETRIC_CONFIRMATION_REQUIRED/);
});
test('mobile bloqueia resultado desconhecido', async () => {
  await assert.rejects(() => confirmMobilePix({ request: { deviceId: 'device-1', biometricConfirmed: true, amountCents: '100' }, authorization: { deviceId: 'device-1' }, gateway: async () => ({ status: 'UNKNOWN' }) }), /EXECUTION_STATE_UNKNOWN/);
});
