// Portable source snapshot + Git history. No installed dependencies or live data.
import { mkdirSync, writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
function git(args) {
  const result = spawnSync('git', args, { cwd: root, encoding: 'utf8' });
  if (result.status !== 0 || result.error) throw new Error(result.error?.message || result.stderr);
  return result.stdout.trim();
}
if (git(['status', '--porcelain']).length) {
  throw new Error('Prima del backup registra le modifiche con git commit: il backup contiene soltanto HEAD.');
}
const commit = git(['rev-parse', 'HEAD']);
mkdirSync(new URL('../outputs/', import.meta.url), { recursive: true });
git(['archive', '--format=zip', '--prefix=Bicycle_Disassembly/', '--output=outputs/officina-source.zip', 'HEAD']);
git(['bundle', 'create', 'outputs/officina-history.bundle', '--all']);
git(['bundle', 'verify', 'outputs/officina-history.bundle']);
writeFileSync(new URL('../outputs/README.txt', import.meta.url),
  `Officina — sorgente portabile\nCommit: ${commit}\n\n` +
  'officina-source.zip: estrarre, leggere README.md, poi npm ci, npm run db:init, npm run dev.\n' +
  'officina-history.bundle: clone offline con git clone officina-history.bundle Bicycle_Disassembly.\n' +
  'Non contiene node_modules, credenziali, cache, database o fotografie/GLB caricati nel sito.\n' +
  'Questi file si scaricano e si conservano separatamente. Leggere docs/PORTABILITA.md.\n');
console.log(`Backup del commit ${commit}: outputs/officina-source.zip e outputs/officina-history.bundle`);
