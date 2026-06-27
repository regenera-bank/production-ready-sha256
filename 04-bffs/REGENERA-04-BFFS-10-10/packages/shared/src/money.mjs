import { BffError } from './errors.mjs';

const CENTS = /^-?\d{1,19}$/;
const MAX = 9_223_372_036_854_775_807n;
const MIN = -9_223_372_036_854_775_808n;

export function parseCents(value) {
  let cents;
  if (typeof value === 'bigint') cents = value;
  else if (typeof value === 'string' && CENTS.test(value.trim())) cents = BigInt(value.trim());
  else if (typeof value === 'number' && Number.isSafeInteger(value)) cents = BigInt(value);
  else throw new BffError('INVALID_MONEY', 400);

  if (cents > MAX || cents < MIN) throw new BffError('MONEY_OVERFLOW', 400);
  return cents;
}

export function positiveCents(value) {
  const cents = parseCents(value);
  if (cents <= 0n) throw new BffError('AMOUNT_NOT_POSITIVE', 422);
  return cents;
}
