import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const approval = JSON.parse(readFileSync('governance/RELEASE-APPROVAL.json', 'utf8'));
const matrix = JSON.parse(readFileSync('governance/CONTROL-MATRIX.json', 'utf8'));
const exceptions = JSON.parse(readFileSync('governance/EXCEPTIONS.json', 'utf8'));

test('ativação produtiva permanece bloqueada sem aprovação externa', () => {
  assert.equal(approval.production_activation, 'BLOCKED_UNTIL_EXTERNAL_APPROVAL');
  assert.equal(approval.cryptographic_signature, 'PENDING_EXTERNAL_SIGNATURE');
});

test('controles possuem owner, teste e evidência', () => {
  for (const control of matrix.controls) {
    assert.ok(control.owner);
    assert.ok(control.test);
    assert.ok(control.evidence);
    assert.equal(control.blocking, true);
  }
});

test('exceção proíbe autoaprovação e exige retrospectiva', () => {
  assert.equal(exceptions.self_approval_forbidden, true);
  assert.equal(exceptions.retrospective_required, true);
  assert.ok(exceptions.maximum_validity_hours <= 24);
});

test('código dos BFFs não contém SQL nem cliente de banco', () => {
  const roots = ['packages/web-bff', 'packages/mobile-bff', 'packages/operations-bff', 'packages/partner-api', 'packages/open-finance-api'];
  const files = [];
  const walk = dir => {
    for (const name of readdirSync(dir)) {
      const path = join(dir, name);
      if (statSync(path).isDirectory()) walk(path);
      else files.push(path);
    }
  };
  roots.forEach(walk);
  const prohibited = /\b(?:INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM|SELECT\s+.+\s+FROM|typeorm|prisma|sequelize|pg\.Pool)\b/i;
  for (const file of files) assert.equal(prohibited.test(readFileSync(file, 'utf8')), false, file);
});

test('políticas possuem escopo, controles, evidência e exceção', () => {
  const text = readFileSync('docs/POLICY-BFF-BOUNDARY.md', 'utf8');
  for (const section of ['## Escopo', '## Controles obrigatórios', '## Evidência', '## Exceção', '## Violação']) {
    assert.ok(text.includes(section), section);
  }
});
