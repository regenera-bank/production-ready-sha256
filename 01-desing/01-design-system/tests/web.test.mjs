import test from 'node:test';
import assert from 'node:assert/strict';
import { escapeHtml, formatMoney, renderButton, renderMoneyInput, renderStatusBadge, renderTransactionState, renderConsent, renderReceipt } from '../packages/web/src/index.mjs';

test('escape bloqueia marcação executável', () => {
  assert.equal(escapeHtml('<script>alert(1)</script>'), '&lt;script&gt;alert(1)&lt;/script&gt;');
});

test('dinheiro usa bigint e mantém centavos', () => {
  assert.equal(formatMoney(123456n), 'R$ 1.234,56');
  assert.equal(formatMoney(-1n), '-R$ 0,01');
});

test('dinheiro recusa number', () => {
  assert.throws(() => formatMoney(100), /bigint/);
});

test('botão possui tipo explícito e estado acessível', () => {
  const html = renderButton({ label: 'Confirmar', loading: true });
  assert.match(html, /type="button"/);
  assert.match(html, /aria-busy="true"/);
  assert.match(html, /disabled/);
});

test('botão recusa variante desconhecida', () => {
  assert.throws(() => renderButton({ label: 'X', variant: 'neon' }), /variant inválido/);
});

test('campo monetário relaciona erro ao input', () => {
  const html = renderMoneyInput({ id: 'amount', label: 'Valor', error: 'Valor inválido' });
  assert.match(html, /aria-invalid="true"/);
  assert.match(html, /aria-describedby="amount-help"/);
  assert.match(html, /Valor inválido/);
});

test('status desconhecido não aceita valor arbitrário', () => {
  assert.throws(() => renderStatusBadge('approved'), /status inválido/);
});

test('estado unknown proíbe repetição cega', () => {
  const html = renderTransactionState({ state: 'unknown', title: 'Confirmação pendente', detail: 'A rede ainda não confirmou.', correlationId: 'abc-123' });
  assert.match(html, /Não repita a operação/);
  assert.doesNotMatch(html, />Tentar novamente</);
});

test('consentimento usa fieldset e required real', () => {
  const html = renderConsent({ id: 'terms', title: 'Consentimento', purpose: 'Autorizar compartilhamento', required: true });
  assert.match(html, /<fieldset/);
  assert.match(html, /required/);
});

test('comprovante escapa linhas adicionais', () => {
  const html = renderReceipt({ title: 'Comprovante', amountCents: 100n, dateTime: '2026-06-26T10:00:00-03:00', transactionId: 'tx-1', rows: [{ label: 'Recebedor', value: '<b>Nome</b>' }] });
  assert.match(html, /&lt;b&gt;Nome&lt;\/b&gt;/);
  assert.match(html, /R\$ 1,00/);
});
