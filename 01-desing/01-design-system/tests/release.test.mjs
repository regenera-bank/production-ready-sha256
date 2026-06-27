import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { listFiles } from '../tools/lib/files.mjs';

const root = resolve(fileURLToPath(new URL('..', import.meta.url)));

test('árvore não contém resíduos locais', async () => {
  const files = await listFiles(root, { exclude: ['node_modules', '.git'] });
  for (const file of files) {
    assert.doesNotMatch(file, /(^|\/)(\.DS_Store|__MACOSX|__pycache__)(\/|$)/);
    assert.doesNotMatch(file, /\.pyc$/);
  }
});

test('workflow possui permissão somente leitura', async () => {
  const workflow = await readFile(join(root, '.github/workflows/ci.yml'), 'utf8');
  assert.match(workflow, /permissions:\n  contents: read/);
  assert.doesNotMatch(workflow, /id-token: write|packages: write|contents: write/);
});

test('workflow fixa checkout por hash', async () => {
  const workflow = await readFile(join(root, '.github/workflows/ci.yml'), 'utf8');
  assert.match(workflow, /actions\/checkout@[0-9a-f]{40}/);
});

test('runtime não contém URL externa', async () => {
  const files = await listFiles(join(root, 'packages'));
  for (const file of files) {
    const text = await readFile(join(root, 'packages', file), 'utf8');
    assert.doesNotMatch(text, /https?:\/\//i, file);
  }
});

test('manifesto do build fecha quatro plataformas', async () => {
  const manifest = JSON.parse(await readFile(join(root, 'dist/manifest.json'), 'utf8'));
  assert.equal(manifest.platforms.length, 4);
  assert.ok(manifest.source_hash.length === 64);
});

test('licença proprietária está presente', async () => {
  const license = await readFile(join(root, 'LICENSE'), 'utf8');
  assert.match(license, /Regenera Corporate Ltda/);
  assert.match(license, /All rights reserved/);
});
