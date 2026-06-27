import { mkdir, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { loadTokenFiles, flatten, cssName, resourceName, pascal } from './lib/tokens.mjs';

const root = resolve(fileURLToPath(new URL('..', import.meta.url)));
const out = resolve(process.env.OUT_DIR || join(root, 'dist'));
const tokens = await loadTokenFiles(root);
const entries = Object.entries(tokens).flatMap(([group, value]) => flatten(value, [group])).sort((a, b) => a.path.join('.').localeCompare(b.path.join('.')));

const hash = createHash('sha256').update(JSON.stringify(tokens)).digest('hex');
await mkdir(join(out, 'web'), { recursive: true });
await mkdir(join(out, 'android', 'values'), { recursive: true });
await mkdir(join(out, 'ios'), { recursive: true });
await mkdir(join(out, 'windows'), { recursive: true });

const css = [':root {', ...entries.filter((entry) => !Array.isArray(entry.value)).map((entry) => `  ${cssName(entry.path)}: ${typeof entry.value === 'number' ? entry.value : entry.value};`), '}', ''].join('\n');
await writeFile(join(out, 'web', 'tokens.css'), css);
await writeFile(join(out, 'web', 'tokens.json'), `${JSON.stringify(tokens, null, 2)}\n`);

const colors = entries.filter((entry) => typeof entry.value === 'string' && /^#[0-9A-F]{6}$/i.test(entry.value));
const dimensions = entries.filter((entry) => typeof entry.value === 'number' && ['spacing', 'radius', 'typography', 'accessibility'].includes(entry.path[0]));
const androidColors = ['<?xml version="1.0" encoding="utf-8"?>', '<resources>', ...colors.map((entry) => `  <color name="${resourceName(entry.path)}">${entry.value}</color>`), '</resources>', ''].join('\n');
const androidDimens = ['<?xml version="1.0" encoding="utf-8"?>', '<resources>', ...dimensions.map((entry) => `  <dimen name="${resourceName(entry.path)}">${entry.value}dp</dimen>`), '</resources>', ''].join('\n');
await writeFile(join(out, 'android', 'values', 'colors.xml'), androidColors);
await writeFile(join(out, 'android', 'values', 'dimens.xml'), androidDimens);

const swift = ['import Foundation', '', 'public enum RegeneraDesignTokens {', ...entries.filter((entry) => !Array.isArray(entry.value)).map((entry) => `  public static let ${pascal(entry.path)} = ${typeof entry.value === 'number' ? entry.value : JSON.stringify(entry.value)}`), '}', ''].join('\n');
await writeFile(join(out, 'ios', 'RegeneraDesignTokens.swift'), swift);

const xamlValues = entries.filter((entry) => !Array.isArray(entry.value)).map((entry) => {
  const key = `Rb${pascal(entry.path)}`;
  if (typeof entry.value === 'string' && /^#[0-9A-F]{6}$/i.test(entry.value)) return `  <Color x:Key="${key}">${entry.value}</Color>`;
  if (typeof entry.value === 'number') return `  <x:Double x:Key="${key}">${entry.value}</x:Double>`;
  return `  <x:String x:Key="${key}">${String(entry.value).replaceAll('&', '&amp;')}</x:String>`;
});
const xaml = ['<?xml version="1.0" encoding="utf-8"?>', '<ResourceDictionary xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">', ...xamlValues, '</ResourceDictionary>', ''].join('\n');
await writeFile(join(out, 'windows', 'RegeneraDesignTokens.xaml'), xaml);

const manifest = { schema_version: 1, release: '1.0.0', source_hash: hash, platforms: ['web', 'android', 'ios', 'windows'], token_count: entries.length };
await writeFile(join(out, 'manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`);
console.log(`build: ${entries.length} tokens; source=${hash}`);
