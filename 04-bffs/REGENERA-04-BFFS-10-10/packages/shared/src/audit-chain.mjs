import { createHash } from 'node:crypto';
import { canonicalJson } from './canonical-json.mjs';

function hash(value) {
  return createHash('sha256').update(value).digest('hex');
}

export class AuditChain {
  #events = [];

  append(event) {
    const previousHash = this.#events.at(-1)?.hash ?? '0'.repeat(64);
    const payload = { sequence: this.#events.length + 1, previousHash, event: structuredClone(event) };
    const entry = { ...payload, hash: hash(canonicalJson(payload)) };
    this.#events.push(entry);
    return structuredClone(entry);
  }

  entries() {
    return structuredClone(this.#events);
  }

  static verify(entries) {
    let previousHash = '0'.repeat(64);
    for (let index = 0; index < entries.length; index += 1) {
      const entry = entries[index];
      const payload = { sequence: index + 1, previousHash, event: entry.event };
      if (entry.sequence !== index + 1) return false;
      if (entry.previousHash !== previousHash) return false;
      if (entry.hash !== hash(canonicalJson(payload))) return false;
      previousHash = entry.hash;
    }
    return true;
  }
}
