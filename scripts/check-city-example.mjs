import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import ts from 'typescript';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {Box3,Vector3} from 'three';
mkdirSync('.sites-runtime/city-check',{recursive:true});
for(const name of ['catalog','glb-nodes'])writeFileSync(`.sites-runtime/city-check/${name}.mjs`,ts.transpileModule(readFileSync(`lib/${name}.ts`,'utf8'),{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext}}).outputText);
const {validateBundle,matchStructures}=await import('../.sites-runtime/city-check/catalog.mjs');
const {catalogNodes}=await import('../.sites-runtime/city-check/glb-nodes.mjs');
const id='elops-study-v2';
const bundle=JSON.parse(readFileSync(`data/${id}.json`,'utf8'));
assert(JSON.stringify(bundle)===JSON.stringify(JSON.parse(readFileSync(`models/${id}/catalog.json`,'utf8'))),'Bundled catalog must match editable source');
validateBundle(bundle);
const structure=bundle.structures[0];
assert.equal(structure.parts.length,718);
assert.equal(matchStructures(structure.standards,[structure])[0].exact,false,'Unknown internals must prevent confirmed reuse');
const bytes=readFileSync(`public/models/${id}.glb`);
assert(bytes.equals(readFileSync(`models/${id}/web/assembly.glb`)),'Bundled GLB must match exported source');
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
const c=JSON.parse(readFileSync(`models/${id}/assembly-constraints.json`,'utf8'));
for(let i=0;i<c.chainPins.length;i++){
  const p=new Vector3(...c.chainPins[i]),q=new Vector3(...c.chainPins[(i+1)%c.chainPins.length]);
  assert(Math.abs(p.distanceTo(q)-.0127)<1e-7,'Chain pitch differs from 12.7 mm');
  const box=new Box3().setFromObject(nodes.get(`chain-pin-${i}`));
  assert(box.getCenter(new Vector3()).distanceTo(p)<1e-6,'Pin geometry differs from assembly constraint');
  assert(box.getSize(new Vector3()).z>.008,'Pin axis or end heads lost during instancing');
}
const plateBox=new Box3().setFromObject(nodes.get('chainring'));
assert(plateBox.getSize(new Vector3()).z<.003,'Chainring must remain a thin metal plate');
for(let i=0;i<3;i++)assert(nodes.has(`rear-housing-clip-${i}`));
for(const tag of ['front','rear'])assert(nodes.has(`brake-adjuster-${tag}`));
assert(nodes.has('head-spacer'));
console.log('City revision 2 verified: 718 viewer bindings, exact-pitch chain pins, thin chainring, housing clips, adjusters and steering spacer.');
