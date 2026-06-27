import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { validateApproval, evaluateControl } from '../tools/lib/governance.mjs';

const owners = JSON.parse(await readFile(new URL('../governance/owners.json', import.meta.url), 'utf8'));
const controls = JSON.parse(await readFile(new URL('../governance/controls.json', import.meta.url), 'utf8'));

test('owner nominal existe', () => {
  assert.equal(owners.primary.name, 'Don Paulo Ricardo');
  assert.ok(owners.primary.role);
});

test('autoaprovação é bloqueada', () => {
  const failures = validateApproval({ author: 'Don Paulo Ricardo', independent_reviewer: 'Don Paulo Ricardo', institutional_approval: 'APPROVED', cryptographic_signature: 'VERIFIED' });
  assert.ok(failures.includes('autoaprovação bloqueada'));
});

test('aprovação sem assinatura é bloqueada', () => {
  const failures = validateApproval({ author: 'A', independent_reviewer: 'B', institutional_approval: 'APPROVED', cryptographic_signature: 'PENDING' });
  assert.ok(failures.includes('assinatura não verificada'));
});

test('owner ausente torna controle ineficaz', () => {
  assert.equal(evaluateControl({ id: 'X' }, true), 'INEFFECTIVE_OWNER_MISSING');
});

test('evidência ausente torna controle ineficaz', () => {
  assert.equal(evaluateControl({ id: 'X', owner: 'A' }, false), 'INEFFECTIVE_EVIDENCE_MISSING');
});

test('exceção vencida bloqueia controle', () => {
  const control = { id: 'X', owner: 'A', exception: { expires_at: '2026-01-01T00:00:00Z' } };
  assert.equal(evaluateControl(control, true, new Date('2026-06-26T00:00:00Z')), 'BLOCKED_EXCEPTION_EXPIRED');
});

test('controles bloqueantes possuem evidência e métrica', () => {
  for (const control of controls.controls.filter((item) => item.blocking)) {
    assert.ok(control.owner, control.id);
    assert.ok(control.evidence.length > 0, control.id);
    assert.equal(typeof control.threshold, 'number', control.id);
  }
});

test('revisão independente é exigida', () => {
  assert.equal(owners.self_approval_allowed, false);
  assert.ok(owners.independent_reviews.every((item) => item.status.includes('REQUIRED')));
});
