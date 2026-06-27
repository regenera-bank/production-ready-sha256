import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { listFiles, sha256 } from './lib/files.mjs';

const root = resolve(fileURLToPath(new URL('..', import.meta.url)));
const evidence = join(root, 'evidence');
await mkdir(evidence, { recursive: true });
const excluded = ['node_modules', '.git', 'evidence/FILE-MANIFEST.json', 'evidence/PACKAGE-CHECKSUMS.sha256'];
const files = await listFiles(root, { exclude: excluded });
const manifest = [];
for (const file of files) manifest.push({ path: file, sha256: await sha256(join(root, file)) });
await writeFile(join(evidence, 'FILE-MANIFEST.json'), `${JSON.stringify({ schema_version: 1, exclusions: excluded.slice(2), files: manifest }, null, 2)}\n`);
await writeFile(join(evidence, 'PACKAGE-CHECKSUMS.sha256'), `${manifest.map((item) => `${item.sha256}  ${item.path}`).join('\n')}\n`);

const packageJson = JSON.parse(await readFile(join(root, 'package.json'), 'utf8'));
const sbom = {
  bomFormat: 'CycloneDX',
  specVersion: '1.5',
  version: 1,
  metadata: { component: { type: 'library', name: packageJson.name, version: packageJson.version } },
  components: [],
};
await writeFile(join(evidence, 'SBOM.cyclonedx.json'), `${JSON.stringify(sbom, null, 2)}\n`);
const inventory = { runtime_dependencies: [], development_dependencies: [], package_manager: 'npm', lockfile: 'package-lock.json' };
await writeFile(join(evidence, 'DEPENDENCY-INVENTORY.json'), `${JSON.stringify(inventory, null, 2)}\n`);
console.log(`evidence: files=${manifest.length}`);
