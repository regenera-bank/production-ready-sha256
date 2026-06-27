import { createHash } from 'node:crypto';
import { readFile, readdir, stat } from 'node:fs/promises';
import { join, relative } from 'node:path';

export async function listFiles(root, { exclude = [] } = {}) {
  const files = [];
  async function walk(dir) {
    for (const name of (await readdir(dir)).sort()) {
      const full = join(dir, name);
      const rel = relative(root, full).replaceAll('\\', '/');
      if (exclude.some((rule) => rel === rule || rel.startsWith(`${rule}/`))) continue;
      const info = await stat(full);
      if (info.isDirectory()) await walk(full);
      else if (info.isFile()) files.push(rel);
    }
  }
  await walk(root);
  return files.sort();
}

export async function sha256(path) {
  const data = await readFile(path);
  return createHash('sha256').update(data).digest('hex');
}

export function stableJson(value) {
  return `${JSON.stringify(value, Object.keys(value).sort(), 2)}\n`;
}
