import { escapeHtml, formatMoney } from '../core.mjs';

export function renderReceipt({ title, amountCents, currency = 'BRL', dateTime, transactionId, rows = [] }) {
  if (!title || !transactionId) throw new TypeError('title e transactionId são obrigatórios');
  if (typeof amountCents !== 'bigint') throw new TypeError('amountCents precisa ser bigint');

  const extra = rows.map(({ label, value }) => `<dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd>`).join('');
  return `<article class="rb-receipt" aria-labelledby="receipt-title"><h2 id="receipt-title">${escapeHtml(title)}</h2><strong class="rb-receipt__amount">${escapeHtml(formatMoney(amountCents, currency))}</strong><dl><dt>Data</dt><dd>${escapeHtml(dateTime)}</dd><dt>Identificador</dt><dd>${escapeHtml(transactionId)}</dd>${extra}</dl></article>`;
}
