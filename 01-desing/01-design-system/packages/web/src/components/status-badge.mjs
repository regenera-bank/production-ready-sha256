import { assertEnum, escapeHtml } from '../core.mjs';

const statuses = ['processing', 'settled', 'reconciled', 'reversed', 'failed', 'unknown', 'manual-review'];
const labels = {
  processing: 'Em processamento',
  settled: 'Liquidada',
  reconciled: 'Conciliada',
  reversed: 'Estornada',
  failed: 'Falhou',
  unknown: 'Confirmação pendente',
  'manual-review': 'Em análise',
};

export function renderStatusBadge(status) {
  assertEnum(status, statuses, 'status');
  return `<span class="rb-status rb-status--${status}" role="status">${escapeHtml(labels[status])}</span>`;
}
