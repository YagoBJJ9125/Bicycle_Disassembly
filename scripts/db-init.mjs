// Initialize the same local D1 storage used by Vite, without an online account.
import './sites-env.mjs';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const hosting = JSON.parse(readFileSync(new URL('../.openai/hosting.json', import.meta.url), 'utf8'));
if (!hosting.d1) throw new Error('Il progetto non ha un binding D1 configurato.');
mkdirSync('.sites-runtime', { recursive: true });
const configPath = '.sites-runtime/wrangler-local.json';
writeFileSync(configPath, JSON.stringify({
  name: 'officina-local',
  compatibility_date: '2026-05-15',
  d1_databases: [{
    binding: hosting.d1,
    database_name: 'site-creator-d1',
    database_id: '00000000-0000-4000-8000-000000000000',
    migrations_dir: '../drizzle',
  }],
}, null, 2));
const result = spawnSync(process.execPath, [
  fileURLToPath(new URL('../node_modules/wrangler/bin/wrangler.js', import.meta.url)),
  'd1', 'migrations', 'apply', 'site-creator-d1', '--local',
  '--persist-to', '.wrangler/state', '--config', configPath,
], { stdio: 'inherit', env: process.env });
if (result.error) throw result.error;
process.exit(result.status ?? 1);
