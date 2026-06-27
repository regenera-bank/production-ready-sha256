const currencyPattern = /^[A-Z]{3}$/;

export function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

export function formatMoney(amountCents, currency = 'BRL', locale = 'pt-BR') {
  if (typeof amountCents !== 'bigint') throw new TypeError('amountCents precisa ser bigint');
  if (!currencyPattern.test(currency)) throw new TypeError('currency inválida');

  const negative = amountCents < 0n;
  const abs = negative ? -amountCents : amountCents;
  const integer = abs / 100n;
  const fraction = String(abs % 100n).padStart(2, '0');
  const grouped = new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }).format(integer);
  const symbol = currency === 'BRL' ? 'R$' : currency;
  return `${negative ? '-' : ''}${symbol} ${grouped},${fraction}`;
}

export function attrs(values) {
  return Object.entries(values)
    .filter(([, value]) => value !== undefined && value !== null && value !== false)
    .map(([key, value]) => value === true ? key : `${key}="${escapeHtml(value)}"`)
    .join(' ');
}

export function assertEnum(value, allowed, name) {
  if (!allowed.includes(value)) throw new TypeError(`${name} inválido`);
  return value;
}
