import { BffError } from './errors.mjs';

export class CircuitBreaker {
  constructor({ failureThreshold = 3, resetAfterMs = 30_000, now = () => Date.now() } = {}) {
    this.failureThreshold = failureThreshold;
    this.resetAfterMs = resetAfterMs;
    this.now = now;
    this.failures = 0;
    this.openedAt = null;
  }

  canCall() {
    if (this.openedAt === null) return true;
    return this.now() - this.openedAt >= this.resetAfterMs;
  }

  success() {
    this.failures = 0;
    this.openedAt = null;
  }

  failure() {
    this.failures += 1;
    if (this.failures >= this.failureThreshold) this.openedAt = this.now();
  }

  async execute(fn) {
    if (!this.canCall()) throw new BffError('CIRCUIT_OPEN', 503);
    try {
      const result = await fn();
      this.success();
      return result;
    } catch (error) {
      this.failure();
      throw error;
    }
  }
}

export async function withTimeout(promise, timeoutMs) {
  let timer;
  try {
    return await Promise.race([
      promise,
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(new BffError('DOWNSTREAM_TIMEOUT', 504)), timeoutMs);
      })
    ]);
  } finally {
    clearTimeout(timer);
  }
}
