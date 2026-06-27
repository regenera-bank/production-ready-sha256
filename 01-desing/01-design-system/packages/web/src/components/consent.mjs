import { escapeHtml, attrs } from '../core.mjs';

export function renderConsent({ id, title, purpose, required = false, checked = false }) {
  if (!id || !title || !purpose) throw new TypeError('id, title e purpose são obrigatórios');
  const input = attrs({ id, type: 'checkbox', name: id, required, checked });
  return `<fieldset class="rb-consent"><legend>${escapeHtml(title)}</legend><label for="${escapeHtml(id)}"><input ${input}><span>${escapeHtml(purpose)}</span></label></fieldset>`;
}
