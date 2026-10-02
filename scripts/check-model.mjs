// Check an exported GLB against the platform contract before uploading it.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import ts from 'typescript';

process.chdir(fileURLToPath(new URL('../', import.meta.url)));
const [modelPath, catalogPath, structureId] = process.argv.slice(2);
if (!modelPath || !catalogPath || !structureId) {
  console.error('Uso: npm run check:model -- modello.glb dossier.json structure-id');
  process.exit(1);
}
mkdirSync('.sites-runtime/model-check', { recursive: true });
for (const name of ['catalog', 'glb']) {
  writeFileSync(`.sites-runtime/model-check/${name}.mjs`, ts.transpileModule(
    readFileSync(`lib/${name}.ts`, 'utf8'),
    { compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ESNext } },
  ).outputText);
}
const { validateGlb } = await import('../.sites-runtime/model-check/glb.mjs');
const { validateBundle } = await import('../.sites-runtime/model-check/catalog.mjs');
const bytes = readFileSync(modelPath);
if (bytes.length > 25_000_000) throw new Error('Il GLB supera il limite attuale di 25 MB.');
const names = validateGlb(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength));
const bundle = validateBundle(JSON.parse(readFileSync(catalogPath, 'utf8')));
const structure = bundle.structures.find(s => s.id === structureId);
if (!structure) throw new Error(`Struttura assente: ${structureId}`);
const expected = structure.parts.map(p => p.meshName);
if (expected.some(name => !name)) throw new Error('Ogni pezzo deve avere meshName nel dossier.');
if (new Set(expected).size !== expected.length) throw new Error('Due pezzi condividono meshName.');
const missing = expected.filter(name => !names.includes(name));
const extra = names.filter(name => !expected.includes(name));
if (missing.length || extra.length) {
  throw new Error(`Nodi mancanti: ${missing.join(', ') || 'nessuno'}; non assegnati: ${extra.join(', ') || 'nessuno'}`);
}
const jsonLength = bytes.readUInt32LE(12);
const gltf = JSON.parse(bytes.subarray(20, 20 + jsonLength).toString('utf8'));
for (const node of gltf.nodes ?? []) {
  if (node.mesh !== undefined && node.children?.length) {
    throw new Error(`Il nodo mesh ${node.name} ha figli: rendere ciascun pezzo una mesh foglia per il viewer attuale.`);
  }
}
let triangles = 0;
for (const node of gltf.nodes ?? []) {
  if (node.mesh === undefined) continue;
  for (const primitive of gltf.meshes[node.mesh].primitives) {
    if ((primitive.mode ?? 4) !== 4) throw new Error('Esportare soltanto triangoli.');
    const accessor = gltf.accessors[primitive.indices ?? primitive.attributes.POSITION];
    if (!accessor || accessor.count % 3) throw new Error('Conteggio triangoli non valido.');
    triangles += accessor.count / 3;
  }
}
console.log(`GLB conforme: ${names.length} pezzi, ${triangles.toLocaleString('it-IT')} triangoli, ${(bytes.length / 1_000_000).toFixed(2)} MB.`);
console.log('Controllare inoltre quote, interni, selezione ed esploso nel banco 3D: la conformità non certifica la meccanica.');
