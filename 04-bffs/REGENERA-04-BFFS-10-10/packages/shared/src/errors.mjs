export class BffError extends Error {
  constructor(code, status, detail = undefined) {
    super(code);
    this.name = 'BffError';
    this.code = code;
    this.status = status;
    this.detail = detail;
  }
}

export function assert(condition, code, status = 400, detail = undefined) {
  if (!condition) throw new BffError(code, status, detail);
}
