import { createHash } from 'node:crypto';
import { assert, BffError } from '../../shared/src/errors.mjs';
import { positiveCents } from '../../shared/src/money.mjs';

export class NonceStore {
  #used = new Set();
  consume(nonce) {
    assert(typeof nonce === 'string' && nonce.length >= 24, 'NONCE_INVALID', 400);
    const digest = createHash('sha256').update(nonce).digest('hex');
    if (this.#used.has(digest)) throw new BffError('NONCE_REPLAY', 409);
    this.#used.add(digest);
  }
}

export async function authorizeMobileRequest({ attestation, expectedDeviceId, verifier, nonceStore }) {
  const claim = await verifier(attestation.token);
  assert(claim.valid === true, 'ATTESTATION_INVALID', 403);
  assert(claim.deviceId === expectedDeviceId, 'DEVICE_BINDING_MISMATCH', 403);
  nonceStore.consume(attestation.nonce);
  return { deviceId: claim.deviceId, platform: claim.platform };
}

export async function confirmMobilePix({ request, authorization, gateway }) {
  assert(authorization.deviceId === request.deviceId, 'DEVICE_BINDING_MISMATCH', 403);
  assert(request.biometricConfirmed === true, 'BIOMETRIC_CONFIRMATION_REQUIRED', 403);
  positiveCents(request.amountCents);
  const outcome = await gateway(request);
  if (outcome.status === 'UNKNOWN') throw new BffError('EXECUTION_STATE_UNKNOWN', 409);
  return outcome;
}
