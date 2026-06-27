import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { loadTokenFiles, flatten, contrastRatio } from '../tools/lib/tokens.mjs';
import { listFiles, sha256 } from '../tools/lib/files.mjs';

const root = resolve(fileURLToPath(new URL('..', import.meta.url)));
const tokens = await loadTokenFiles(root);

test('nomes de token são únicos', () => {
  const names = Object.entries(tokens).flatMap(([group, value]) => flatten(value, [group])).map((entry) => entry.path.join('.'));
  assert.equal(new Set(names).size, names.length);
});

test('contraste principal supera o mínimo', () => {
  const ratio = contrastRatio(tokens.color.text.primary, tokens.color.background.canvas);
  assert.ok(ratio >= tokens.accessibility.minimumTextContrast, String(ratio));
});

test('alvo de toque não cai abaixo de 44', () => {
  assert.ok(tokens.accessibility.minimumTouchTarget >= 44);
});

test('movimento reduzido é obrigatório', () => {
  assert.equal(tokens.accessibility.reducedMotionRequired, true);
  assert.equal(tokens.motion.durationReduced, 0);
});

test('estados financeiros críticos existem', () => {
  const states = tokens.states.transaction;
  for (const state of ['processing', 'settled', 'reconciled', 'reversed', 'failed', 'unknown', 'manual-review']) assert.ok(states.includes(state));
});

test('build é determinístico', async () => {
  const a = await mkdtemp(join(tmpdir(), 'rb-ds-a-'));
  const b = await mkdtemp(join(tmpdir(), 'rb-ds-b-'));
  try {
    for (const dir of [a, b]) {
      const run = spawnSync(process.execPath, ['tools/build.mjs'], { cwd: root, env: { ...process.env, OUT_DIR: dir }, encoding: 'utf8' });
      assert.equal(run.status, 0, run.stderr);
    }
    const filesA = await listFiles(a);
    const filesB = await listFiles(b);
    assert.deepEqual(filesA, filesB);
    for (const file of filesA) assert.equal(await sha256(join(a, file)), await sha256(join(b, file)), file);
  } finally {
    await rm(a, { recursive: true, force: true });
    await rm(b, { recursive: true, force: true });
  }
});

test('quatro plataformas são geradas', async () => {
  const manifest = JSON.parse(await readFile(join(root, 'dist/manifest.json'), 'utf8'));
  assert.deepEqual(manifest.platforms, ['web', 'android', 'ios', 'windows']);
});

test('saída web contém tokens semânticos', async () => {
  const css = await readFile(join(root, 'dist/web/tokens.css'), 'utf8');
  assert.match(css, /--rb-color-text-primary/);
  assert.match(css, /--rb-accessibility-minimum-touch-target/);
});

test('saídas nativas preservam a marca primária', async () => {
  const android = await readFile(join(root, 'dist/android/values/colors.xml'), 'utf8');
  const ios = await readFile(join(root, 'dist/ios/RegeneraDesignTokens.swift'), 'utf8');
  const windows = await readFile(join(root, 'dist/windows/RegeneraDesignTokens.xaml'), 'utf8');
  for (const text of [android, ios, windows]) assert.match(text, /#22D3EE/);
});
