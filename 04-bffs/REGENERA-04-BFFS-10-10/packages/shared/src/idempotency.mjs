import { createHash } from 'node:crypto';
import { canonicalJson } from './canonical-json.mjs';
import { BffError } from './errors.mjs';

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function digest(value) {
  return createHash('sha256').update(canonicalJson(value)).digest('hex');
}

export class IdempotencyStore {
  #records = new Map();

  begin(scope, key, payload) {
    if (!UUID.test(key)) throw new BffError('INVALID_IDEMPOTENCY_KEY', 400);
    const recordKey = `${scope}:${key}`;
    const hash = digest(payload);
    const existing = this.#records.get(recordKey);

    if (!existing) {
      this.#records.set(recordKey, { hash, state: 'PROCESSING' });
      return { kind: 'NEW' };
    }

    if (existing.hash !== hash) throw new BffError('IDEMPOTENCY_CONFLICT', 409);
    if (existing.state === 'DONE') return { kind: 'REPLAY', response: structuredClone(existing.response) };
    if (existing.state === 'UNKNOWN') throw new BffError('EXECUTION_STATE_UNKNOWN', 409);
    throw new BffError('REQUEST_IN_PROGRESS', 409);
  }

  complete(scope, key, response) {
    const recordKey = `${scope}:${key}`;
    const existing = this.#records.get(recordKey);
    if (!existing || existing.state !== 'PROCESSING') throw new BffError('IDEMPOTENCY_STATE_INVALID', 409);
    this.#records.set(recordKey, { ...existing, state: 'DONE', response: structuredClone(response) });
  }

  markUnknown(scope, key) {
    const recordKey = `${scope}:${key}`;
    const existing = this.#records.get(recordKey);
    if (!existing) throw new BffError('IDEMPOTENCY_RECORD_NOT_FOUND', 404);
    this.#records.set(recordKey, { ...existing, state: 'UNKNOWN' });
  }

  reconcile(scope, key, response) {
    const recordKey = `${scope}:${key}`;
    const existing = this.#records.get(recordKey);
    if (!existing || existing.state !== 'UNKNOWN') throw new BffError('IDEMPOTENCY_NOT_UNKNOWN', 409);
    this.#records.set(recordKey, { ...existing, state: 'DONE', response: structuredClone(response) });
  }
}
