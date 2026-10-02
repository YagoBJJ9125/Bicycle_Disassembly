import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import ts from 'typescript';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
mkdirSync('.sites-runtime/city-check',{recursive:true});
for(const name of ['catalog','glb-nodes'])writeFileSync(`.sites-runtime/city-check/${name}.mjs`,ts.transpileModule(readFileSync(`lib/${name}.ts`,'utf8'),{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext}}).outputText);
const {validateBundle,matchStructures}=await import('../.sites-runtime/city-check/catalog.mjs');
const {catalogNodes}=await import('../.sites-runtime/city-check/glb-nodes.mjs');
const bundle=JSON.parse(readFileSync('data/elops-study-v1.json','utf8'));
assert(JSON.stringify(bundle)===JSON.stringify(JSON.parse(readFileSync('models/elops-study-v1/catalog.json','utf8'))),'Bundled catalog must match editable source');
validateBundle(bundle);
const structure=bundle.structures[0];
assert.equal(structure.parts.length,704);
assert.equal(matchStructures(structure.standards,[structure])[0].exact,false,'Unknown internals must prevent confirmed reuse');
const bytes=readFileSync('public/models/elops-study-v1.glb');
assert(bytes.equals(readFileSync('models/elops-study-v1/web/assembly.glb')),'Bundled GLB must match exported source');
const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
gltf.scene.updateMatrixWorld(true);
const nodes=catalogNodes(gltf);
for(const part of structure.parts){
  const node=nodes.get(part.meshName);
  assert(node,`Viewer cannot resolve ${part.meshName}`);
  assert(node.matrixWorld.elements.every(Number.isFinite));
}
// This real source node has a period: lookup by Three.js object.name fails.
assert(nodes.has('saddle-rail--0.021'));
assert.equal(gltf.scene.getObjectByName('saddle-rail--0.021'),undefined);
console.log('City example verified: catalog, bundled files, 704 viewer bindings and original glTF names.');
