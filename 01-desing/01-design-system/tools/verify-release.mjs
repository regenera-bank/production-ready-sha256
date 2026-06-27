import { readFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { sha256 } from './lib/files.mjs';

const root = resolve(fileURLToPath(new URL('..', import.meta.url)));
const manifest = JSON.parse(await readFile(join(root, 'evidence/FILE-MANIFEST.json'), 'utf8'));
const failures = [];
for (const item of manifest.files) {
  const actual = await sha256(join(root, item.path)).catch(() => null);
  if (actual !== item.sha256) failures.push(item.path);
}
const checksumLines = (await readFile(join(root, 'evidence/PACKAGE-CHECKSUMS.sha256'), 'utf8')).trim().split('\n');
if (checksumLines.length !== manifest.files.length) failures.push('checksum-count');
for (const forbidden of ['.DS_Store', '__MACOSX', '__pycache__', '.pyc']) {
  if (manifest.files.some((item) => item.path.includes(forbidden))) failures.push(`forbidden:${forbidden}`);
}
if (failures.length) {
  console.error(failures.join('\n'));
  process.exit(1);
}
console.log(`verify-release: ok; files=${manifest.files.length}`);
