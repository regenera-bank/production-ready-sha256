import { readFile, readdir } from 'node:fs/promises';
import { join, basename } from 'node:path';

export async function loadTokenFiles(root) {
  const dir = join(root, 'tokens');
  const result = {};
  for (const name of (await readdir(dir)).filter((item) => item.endsWith('.json')).sort()) {
    result[basename(name, '.json')] = JSON.parse(await readFile(join(dir, name), 'utf8'));
  }
  return result;
}

export function flatten(value, prefix = []) {
  const out = [];
  for (const [key, item] of Object.entries(value)) {
    const path = [...prefix, key];
    if (item && typeof item === 'object' && !Array.isArray(item)) out.push(...flatten(item, path));
    else out.push({ path, value: item });
  }
  return out;
}

export function cssName(path) {
  return `--rb-${path.join('-').replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`)}`;
}

export function resourceName(path) {
  return `rb_${path.join('_').replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`)}`;
}

export function pascal(path) {
  return path.join('_').split(/[_-]/).map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join('');
}

export function contrastRatio(a, b) {
  const luminance = (hex) => {
    const channels = hex.replace('#', '').match(/.{2}/g).map((part) => parseInt(part, 16) / 255).map((c) => c <= .03928 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4);
    return .2126 * channels[0] + .7152 * channels[1] + .0722 * channels[2];
  };
  const l1 = luminance(a);
  const l2 = luminance(b);
  return (Math.max(l1, l2) + .05) / (Math.min(l1, l2) + .05);
}
