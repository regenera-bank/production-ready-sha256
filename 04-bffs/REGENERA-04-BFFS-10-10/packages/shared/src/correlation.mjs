import { randomUUID } from 'node:crypto';

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export function correlationId(value) {
  if (value === undefined || value === null || value === '') return randomUUID();
  if (!UUID.test(String(value))) throw new Error('INVALID_CORRELATION_ID');
  return String(value);
}
