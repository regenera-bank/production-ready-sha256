import { escapeHtml, assertEnum } from '../core.mjs';
import { renderStatusBadge } from './status-badge.mjs';

const states = ['processing', 'settled', 'reconciled', 'reversed', 'failed', 'unknown', 'manual-review'];

export function renderTransactionState({ state, title, detail, correlationId }) {
  assertEnum(state, states, 'state');
  if (!title) throw new TypeError('title obrigatório');

  const safeCorrelation = correlationId ? `<code class="rb-correlation">${escapeHtml(correlationId)}</code>` : '';
  const retryWarning = state === 'unknown'
    ? '<p class="rb-state__warning">Não repita a operação. Consulte o resultado antes de criar nova intenção.</p>'
    : '';

  return `<section class="rb-state rb-state--${state}" aria-labelledby="transaction-state-title">${renderStatusBadge(state)}<h2 id="transaction-state-title">${escapeHtml(title)}</h2><p>${escapeHtml(detail ?? '')}</p>${retryWarning}${safeCorrelation}</section>`;
}
