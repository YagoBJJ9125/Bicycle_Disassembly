import type {Object3D} from 'three';
import type {GLTF} from 'three/addons/loaders/GLTFLoader.js';

/** Resolve catalog names before GLTFLoader sanitization and deduplication. */
export function catalogNodes(gltf:GLTF):Map<string,Object3D>{
  const nodes=new Map<string,Object3D>();
  gltf.scene.traverse(object=>{
    const index=gltf.parser.associations.get(object)?.nodes;
    if(index!==undefined){
      const name=gltf.parser.json.nodes[index]?.name;
      if(name)nodes.set(name,object);
    }
  });
  return nodes;
}
