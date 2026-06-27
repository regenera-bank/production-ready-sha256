import { attrs, escapeHtml } from '../core.mjs';

export function renderMoneyInput({ id, label, value = '', error, disabled = false, currency = 'BRL' }) {
  if (!id) throw new TypeError('id obrigatório');
  if (!String(label ?? '').trim()) throw new TypeError('label obrigatório');

  const helpId = `${id}-help`;
  const inputAttrs = attrs({
    id,
    name: id,
    class: 'rb-input rb-money-input',
    inputmode: 'decimal',
    autocomplete: 'off',
    value,
    disabled,
    'aria-invalid': error ? 'true' : 'false',
    'aria-describedby': helpId,
  });

  const message = error ? escapeHtml(error) : `Valor em ${escapeHtml(currency)}. Digite centavos com separador decimal.`;
  return `<label class="rb-field" for="${escapeHtml(id)}"><span class="rb-field__label">${escapeHtml(label)}</span><input ${inputAttrs}><span id="${escapeHtml(helpId)}" class="rb-field__help">${message}</span></label>`;
}
