import { readFile, stat } from 'node:fs/promises';
import { join, resolve, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { listFiles } from './lib/files.mjs';
import { loadTokenFiles, flatten, contrastRatio } from './lib/tokens.mjs';
import { validateApproval } from './lib/governance.mjs';

const root = resolve(fileURLToPath(new URL('..', import.meta.url)));
const files = await listFiles(root, { exclude: ['node_modules', 'dist', 'evidence', '.git'] });
const failures = [];
const forbiddenNames = ['.DS_Store', '__MACOSX', '__pycache__'];
for (const file of files) {
  const parts = file.split('/');
  if (parts.some((part) => forbiddenNames.includes(part)) || file.endsWith('.pyc')) failures.push(`system-file:${file}`);
  if ((await stat(join(root, file))).size === 0) failures.push(`empty-file:${file}`);
  if (['.json'].includes(extname(file))) {
    try { JSON.parse(await readFile(join(root, file), 'utf8')); } catch { failures.push(`invalid-json:${file}`); }
  }
}

const tokens = await loadTokenFiles(root);
const entries = Object.entries(tokens).flatMap(([group, value]) => flatten(value, [group]));
const names = entries.map((entry) => entry.path.join('.'));
if (new Set(names).size !== names.length) failures.push('duplicate-token-name');
if (tokens.accessibility.minimumTouchTarget < 44) failures.push('touch-target-below-44');
if (!tokens.accessibility.reducedMotionRequired) failures.push('reduced-motion-not-required');
const ratio = contrastRatio(tokens.color.text.primary, tokens.color.background.canvas);
if (ratio < tokens.accessibility.minimumTextContrast) failures.push(`contrast:${ratio.toFixed(2)}`);

const approval = JSON.parse(await readFile(join(root, 'governance/release-approval.json'), 'utf8'));
const approvalFailures = validateApproval(approval);
if (approval.institutional_approval === 'APPROVED') failures.push(...approvalFailures.map((item) => `approval:${item}`));

const required = ['README.md', 'governance/owners.json', 'governance/controls.json', 'docs/00-GOVERNANCA.md', 'docs/02-ACESSIBILIDADE.md', 'docs/05-POLITICA-DE-RELEASE.md'];
for (const file of required) if (!files.includes(file)) failures.push(`required-missing:${file}`);

const externalPattern = /(?:src|href)=[\"']https?:\/\/|\bfetch\s*\(\s*[\"']https?:\/\/|\bimport\s+[^;]*[\"']https?:\/\//i;
for (const file of files.filter((item) => item.startsWith('packages/') || item.startsWith('assets/'))) {
  const text = await readFile(join(root, file), 'utf8').catch(() => '');
  if (externalPattern.test(text)) failures.push(`runtime-external-url:${file}`);
}

if (failures.length) {
  console.error(failures.join('\n'));
  process.exit(1);
}
console.log(`validate: ok; files=${files.length}; tokens=${entries.length}; contrast=${ratio.toFixed(2)}`);
