import { spawnSync } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(fileURLToPath(new URL('..', import.meta.url)));
const steps = [
  ['clean', ['tools/clean.mjs']],
  ['validate', ['tools/validate.mjs']],
  ['build', ['tools/build.mjs']],
  ['test', ['--test', '--test-reporter=tap', 'tests/governance.test.mjs', 'tests/release.test.mjs', 'tests/tokens.test.mjs', 'tests/web.test.mjs']],
  ['security', ['tools/security.mjs']],
  ['evidence', ['tools/evidence.mjs']],
  ['verify-release', ['tools/verify-release.mjs']],
];
const normalize = (value) => String(value || '')
  .replace(/duration_ms: [0-9.]+/g, 'duration_ms: <measured>')
  .replace(/# duration_ms [0-9.]+/g, '# duration_ms <measured>');

const results = [];
for (const [name, args] of steps) {
  const run = spawnSync(process.execPath, args, { cwd: root, encoding: 'utf8' });
  process.stdout.write(run.stdout || '');
  process.stderr.write(run.stderr || '');
  const stdout = normalize(run.stdout);
  const stderr = normalize(run.stderr);
  results.push({ name, command: ['node', ...args].join(' '), exit_code: run.status, stdout, stderr });
  if (run.status !== 0) process.exit(run.status ?? 1);
}
await mkdir(join(root, 'evidence/logs'), { recursive: true });
for (const result of results) await writeFile(join(root, 'evidence/logs', `${result.name}.log`), `${result.stdout}${result.stderr}`);
await writeFile(join(root, 'evidence/EXECUTION-RESULTS.json'), `${JSON.stringify({ schema_version: 1, source_date_epoch: '2026-06-26T00:00:00Z', results: results.map(({ stdout, stderr, ...rest }) => ({ ...rest, stdout_bytes: Buffer.byteLength(stdout), stderr_bytes: Buffer.byteLength(stderr) })) }, null, 2)}\n`);

// logs e resultado passam a fazer parte da evidência. fecha os hashes de novo.
const final = spawnSync(process.execPath, ['tools/evidence.mjs'], { cwd: root, encoding: 'utf8' });
process.stdout.write(final.stdout || '');
process.stderr.write(final.stderr || '');
if (final.status !== 0) process.exit(final.status ?? 1);
const verify = spawnSync(process.execPath, ['tools/verify-release.mjs'], { cwd: root, encoding: 'utf8' });
process.stdout.write(verify.stdout || '');
process.stderr.write(verify.stderr || '');
process.exit(verify.status ?? 1);
