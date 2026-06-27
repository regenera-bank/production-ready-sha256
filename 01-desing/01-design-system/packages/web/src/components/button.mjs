import { attrs, escapeHtml, assertEnum } from '../core.mjs';

const variants = ['primary', 'secondary', 'danger', 'ghost'];

export function renderButton({ label, variant = 'primary', disabled = false, loading = false, type = 'button', id }) {
  assertEnum(variant, variants, 'variant');
  assertEnum(type, ['button', 'submit', 'reset'], 'type');
  if (!String(label ?? '').trim()) throw new TypeError('label obrigatório');

  const blocked = disabled || loading;
  const text = loading ? 'Processando' : label;
  const htmlAttrs = attrs({
    id,
    type,
    class: `rb-button rb-button--${variant}`,
    disabled: blocked,
    'aria-disabled': blocked ? 'true' : undefined,
    'aria-busy': loading ? 'true' : undefined,
  });

  return `<button ${htmlAttrs}><span>${escapeHtml(text)}</span></button>`;
}
