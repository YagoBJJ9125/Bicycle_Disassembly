'use client';
import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import type { Part, Structure } from '@/lib/catalog';
type Props={structure:Structure; selected:string|null; explode:number; isolate:boolean; group:string; reset:number; onSelect:(id:string)=>void};
export default function BikeViewer(props:Props){
 const mount=useRef<HTMLDivElement>(null),current=useRef(props);current.current=props;
 const [error,setError]=useState(''),[loading,setLoading]=useState(true);
 useEffect(()=>{
  const host=mount.current;if(!host)return;let stopped=false,frame=0;setLoading(true);setError('');
  const scene=new THREE.Scene();scene.background=new THREE.Color('#edf1ee');
  const camera=new THREE.PerspectiveCamera(35,1,.001,150);camera.position.set(2.8,2.25,3.9);
  let renderer:THREE.WebGLRenderer;
  try{renderer=new THREE.WebGLRenderer({antialias:true});}catch{setError('3D non disponibile in questo browser. Puoi comunque consultare le schede dei pezzi.');setLoading(false);return;}
  renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;host.appendChild(renderer.domElement);
  const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,.85,0);controls.enableDamping=true;controls.minDistance=.025;controls.maxDistance=16;
  scene.add(new THREE.HemisphereLight('#ffffff','#66726d',3));const sun=new THREE.DirectionalLight('#ffffff',4);sun.position.set(2,4,5);scene.add(sun);const fill=new THREE.DirectionalLight('#ffffff',1.8);fill.position.set(-3,1,-4);scene.add(fill);
  const grid=new THREE.GridHelper(10,50,'#c6d3ca','#dce4dd');grid.position.y=.08;scene.add(grid);
  const nodes=new Map<string,THREE.Group>(),origins=new Map<string,THREE.Vector3>(),resources=new Set<THREE.BufferGeometry|THREE.Material>();resources.add(grid.geometry);(Array.isArray(grid.material)?grid.material:[grid.material]).forEach(m=>resources.add(m));
  function track(object:THREE.Object3D){object.traverse(o=>{if(o instanceof THREE.Mesh){resources.add(o.geometry);(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>resources.add(m));}});}
  function shape(p:Part){const g=p.geometry;let geo:THREE.BufferGeometry;
   if(g.kind==='tube'){const start=new THREE.Vector3(...g.position),delta=new THREE.Vector3(...g.end!).sub(start);geo=new THREE.CylinderGeometry(g.size[0],g.size[0],delta.length(),12);const mesh=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color:g.color,metalness:.65,roughness:.3}));mesh.position.copy(delta).multiplyScalar(.5);mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),delta.normalize());return mesh;}
   if(g.kind==='ring')geo=new THREE.TorusGeometry(g.size[0],Math.max(g.size[1],.001),8,56);else if(g.kind==='box')geo=new THREE.BoxGeometry(...g.size);else if(g.kind==='ball')geo=new THREE.SphereGeometry(g.size[0],10,8);else geo=new THREE.CylinderGeometry(g.size[0],g.size[0],Math.max(g.size[1],.001),12);
   const mesh=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color:g.color,metalness:.6,roughness:.4}));if(g.rotation)mesh.rotation.set(...g.rotation);return mesh;
  }
  function build(){for(const p of props.structure.parts){const node=new THREE.Group();node.userData.partId=p.id;node.position.set(...p.geometry.position);node.add(shape(p));nodes.set(p.id,node);origins.set(p.id,node.position.clone());scene.add(node);track(node);}
   if(props.structure.id==='classic-city-demo-v1'){
    const welded=nodes.get('frame')!,base=new THREE.Vector3(-.28,.34,0);const tubes=[[[ -.47,1.29,0],[.66,1.30,0]], [[-.28,.34,0],[.66,1.30,0]], [[-.28,.34,-.035],[-.93,.57,-.035]], [[-.28,.34,.035],[-.93,.57,.035]], [[-.47,1.29,-.035],[-.93,.57,-.035]], [[-.47,1.29,.035],[-.93,.57,.035]],[[.66,1.40,0],[.70,1.13,0]]];
    tubes.forEach(([a,b],i)=>{const p={...props.structure.parts[0],geometry:{kind:'tube' as const,position:a as [number,number,number],end:b as [number,number,number],size:[i<2?.026:.014,0,0] as [number,number,number],color:'#77b9ad'}};const mesh=shape(p);mesh.position.add(new THREE.Vector3(...a).sub(base));welded.add(mesh);track(mesh);});
   }
  }
  function fit(target?:THREE.Object3D){const box=new THREE.Box3();if(target)box.setFromObject(target);else nodes.forEach(n=>{if(n.visible)box.union(new THREE.Box3().setFromObject(n));});if(box.isEmpty())return;const center=box.getCenter(new THREE.Vector3()),length=Math.max(box.getSize(new THREE.Vector3()).length(),.05);controls.target.copy(center);camera.position.copy(center).add(new THREE.Vector3(.45,.27,1).normalize().multiplyScalar(length*1.55));controls.update();}
  async function init(){try{if(props.structure.assetId){const gltf=await new GLTFLoader().loadAsync(`/api/assets/${props.structure.assetId}`);if(stopped){track(gltf.scene);resources.forEach(r=>r.dispose());return;}gltf.scene.updateMatrixWorld(true);for(const p of props.structure.parts){const original=gltf.scene.getObjectByName(p.meshName!);if(!original)throw new Error(`Nodo mancante: ${p.meshName}`);const node=new THREE.Group();node.userData.partId=p.id;const copy=original.clone(true);copy.applyMatrix4(original.parent?.matrixWorld||new THREE.Matrix4());copy.traverse(o=>{if(o instanceof THREE.Mesh)o.material=Array.isArray(o.material)?o.material.map(m=>m.clone()):o.material.clone();});node.add(copy);nodes.set(p.id,node);origins.set(p.id,new THREE.Vector3());scene.add(node);track(node);}}else build();if(!stopped){fit();setLoading(false);}}catch(e){if(!stopped){setError(e instanceof Error?e.message:'Errore 3D');setLoading(false);}}}
  let lastReset=props.reset,lastIsolate=props.isolate,lastSelected=props.selected,lastGroup=props.group;
  const animate=()=>{if(stopped)return;frame=requestAnimationFrame(animate);const state=current.current;
   for(const p of props.structure.parts){const node=nodes.get(p.id);if(!node)continue;const chosen=state.selected===p.id;node.visible=state.isolate?chosen:(state.group==='Tutti'||state.group===p.group);node.position.copy(origins.get(p.id)!).addScaledVector(new THREE.Vector3(...p.explode),state.explode/100);node.traverse(o=>{if(o instanceof THREE.Mesh)for(const mat of Array.isArray(o.material)?o.material:[o.material])if(mat instanceof THREE.MeshStandardMaterial){mat.emissive.set(chosen?'#da6637':'#000000');mat.emissiveIntensity=chosen?.55:0;}});}
   if(lastReset!==state.reset||lastIsolate!==state.isolate||(state.isolate&&lastSelected!==state.selected)||lastGroup!==state.group){fit(state.isolate&&state.selected?nodes.get(state.selected):undefined);lastReset=state.reset;lastIsolate=state.isolate;lastSelected=state.selected;lastGroup=state.group;}controls.update();renderer.render(scene,camera);
  };animate();void init();
  const observer=new ResizeObserver(()=>{const w=host.clientWidth,h=host.clientHeight;if(w&&h){renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();}});observer.observe(host);
  let down=[0,0];const onDown=(e:PointerEvent)=>{down=[e.clientX,e.clientY];};const onUp=(e:PointerEvent)=>{if(Math.hypot(e.clientX-down[0],e.clientY-down[1])>5)return;const rect=renderer.domElement.getBoundingClientRect(),ray=new THREE.Raycaster();ray.setFromCamera(new THREE.Vector2((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1),camera);const hit=ray.intersectObjects([...nodes.values()].filter(x=>x.visible),true)[0];if(hit){let o:THREE.Object3D|null=hit.object;while(o&&!o.userData.partId)o=o.parent;if(o?.userData.partId)current.current.onSelect(o.userData.partId);}};
  renderer.domElement.addEventListener('pointerdown',onDown);renderer.domElement.addEventListener('pointerup',onUp);
  return()=>{stopped=true;cancelAnimationFrame(frame);observer.disconnect();controls.dispose();renderer.domElement.removeEventListener('pointerdown',onDown);renderer.domElement.removeEventListener('pointerup',onUp);resources.forEach(r=>r.dispose());renderer.dispose();renderer.domElement.remove();};
 },[props.structure]);
 return <div className="three-host" ref={mount} role="img" aria-label="Bicicletta 3D: trascina per ruotare, scorri per zoomare. Puoi selezionare i pezzi anche dall’elenco.">{loading&&!error&&<div className="viewer-message">Preparazione del banco 3D…</div>}{error&&<div className="viewer-message error">{error}</div>}</div>;
}
