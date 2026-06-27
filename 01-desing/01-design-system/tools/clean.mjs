import { rm } from 'node:fs/promises';
for (const path of ['dist', 'evidence']) await rm(new URL(`../${path}`, import.meta.url), { recursive: true, force: true });
console.log('clean: ok');
