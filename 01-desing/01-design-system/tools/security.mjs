import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { listFiles } from './lib/files.mjs';

const root = resolve(fileURLToPath(new URL('..', import.meta.url)));
const files = await listFiles(root, { exclude: ['node_modules', 'dist', 'evidence', '.git'] });
const findings = [];
const rules = [
  ['private-key', /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/],
  ['aws-access-key', /AKIA[0-9A-Z]{16}/],
  ['generic-secret', /(?:password|secret|token)\s*[:=]\s*["'][^"']{16,}["']/i],
  ['dynamic-code', /\beval\s*\(|new Function\s*\(/],
  ['unsafe-dom', /\.innerHTML\s*=/],
];
for (const file of files) {
  const text = await readFile(join(root, file), 'utf8').catch(() => null);
  if (text === null) continue;
  for (const [rule, pattern] of rules) if (pattern.test(text)) findings.push({ file, rule });
}
await mkdir(join(root, 'evidence'), { recursive: true });
const report = { schema_version: 1, scanned_files: files.length, findings, status: findings.length ? 'FAILED' : 'PASSED' };
await writeFile(join(root, 'evidence', 'SECURITY-REPORT.json'), `${JSON.stringify(report, null, 2)}\n`);
if (findings.length) {
  console.error(JSON.stringify(findings, null, 2));
  process.exit(1);
}
console.log(`security: ok; scanned=${files.length}`);
