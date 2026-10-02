import { z } from 'zod';

const vector = z.tuple([z.number().finite().min(-100).max(100), z.number().finite().min(-100).max(100), z.number().finite().min(-100).max(100)]);
export const geometrySchema = z.object({ kind: z.enum(['tube','ring','box','ball','cylinder']), position: vector, size: vector, end: vector.optional(), rotation: vector.optional(), color: z.string().regex(/^#[0-9a-fA-F]{6}$/) });
const toolSchema = z.object({ name: z.string().min(1).max(200), size: z.string().min(1).max(150), certainty: z.enum(['verified','indicative','unknown']) });
const sourceSchema = z.object({ title: z.string().min(1).max(200), url: z.string().url().refine(v => v.startsWith('https://')), scope: z.string().min(1).max(400) });
const procedureSchema = z.object({ id: z.string().min(1).max(100), title: z.string().min(1).max(200), steps: z.array(z.string().min(1).max(1200)).min(1).max(30), tools: z.array(toolSchema).max(20), warnings: z.array(z.string().max(1000)).max(10), sources: z.array(sourceSchema).max(20) });
const partSchema = z.object({ id: z.string().min(1).max(100), name: z.string().min(1).max(200), group: z.string().min(1).max(100), description: z.string().min(1).max(2000), procedureId: z.string(), dependsOn: z.array(z.string()).max(100), evidence: z.enum(['verified','indicative','unknown']), geometry: geometrySchema, explode: vector, meshName: z.string().max(150).optional(), serviceability: z.enum(['serviceable','specialist','inseparable']) });
export const structureSchema = z.object({ id: z.string().min(1).max(100), name: z.string().min(1).max(200), version: z.number().int().min(1), kind: z.enum(['didactic','reference','verified']), standards: z.record(z.string().max(200)).refine(v => Object.keys(v).length >= 5, 'Inserire almeno cinque standard meccanici'), coverage: z.string().min(1).max(2000), parts: z.array(partSchema).min(1).max(3000), procedures: z.array(procedureSchema).min(1).max(300), assetId: z.string().regex(/^[a-f0-9-]+\.glb$/).optional() });
export const bikeSchema = z.object({ id: z.string().min(1).max(100), name: z.string().min(1).max(200), brand: z.string().min(1).max(100), category: z.enum(['Città','Corsa','MTB','Gravel','BMX','Altre']), subtype: z.string().max(150), year: z.string().max(50), structureId: z.string(), status: z.enum(['didactic','reference','verified']), notes: z.string().max(3000), color: z.string().regex(/^#[0-9a-fA-F]{6}$/) });
export const bundleSchema = z.object({ schemaVersion: z.literal(1), structures: z.array(structureSchema).max(30), bikes: z.array(bikeSchema).max(100) });
export type Part = z.infer<typeof partSchema>;
export type Structure = z.infer<typeof structureSchema>;
export type Bike = z.infer<typeof bikeSchema>;
export type Bundle = z.infer<typeof bundleSchema>;
export type Procedure = z.infer<typeof procedureSchema>;
export const labels = { verified: 'Verificato', indicative: 'Indicativo', unknown: 'Da identificare', didactic: 'Didattico', reference: 'Riferimento' };

export function signature(standards: Record<string,string>) {
  return Object.keys(standards).sort().map(k => `${k.toLowerCase().trim()}:${standards[k].toLowerCase().trim()}`).join('|');
}
export function matchStructures(standards: Record<string,string>, structures: Structure[]) {
  const known = Object.entries(standards).filter(([,v]) => v.trim() && !/^(unknown|sconosciuto|da verificare|\?)$/i.test(v.trim()));
  return structures.map(s => {
    const entries = Object.entries(s.standards);
    const conflicts = known.filter(([k,v]) => s.standards[k] && s.standards[k].toLowerCase().trim() !== v.toLowerCase().trim()).map(([k])=>k);
    const matches = known.filter(([k,v]) => s.standards[k]?.toLowerCase().trim() === v.toLowerCase().trim()).length;
    const exact = s.kind !== 'didactic' && known.length === entries.length && Object.keys(standards).length === entries.length && matches === entries.length && conflicts.length === 0 && entries.every(([,v])=>! /^(unknown|sconosciuto|da verificare|\?)$/i.test(v.trim()));
    return { structureId: s.id, name: s.name, exact, score: entries.length ? matches / entries.length : 0, conflicts, missing: entries.filter(([k])=>!known.some(([key])=>key===k)).map(([k])=>k) };
  }).sort((a,b)=>Number(b.exact)-Number(a.exact)||b.score-a.score);
}
export function validateBundle(input: unknown, existing: Structure[] = []): Bundle {
  const b = bundleSchema.parse(input);
  const structures = new Map(existing.map(s=>[s.id,s]));
  const unique = (ids: string[], what: string) => { if(new Set(ids).size!==ids.length) throw new Error(`ID duplicati: ${what}`); };
  unique(b.structures.map(s=>s.id),'strutture'); unique(b.bikes.map(s=>s.id),'biciclette');
  for (const s of b.structures) {
    if (structures.has(s.id)) throw new Error(`La struttura ${s.id} esiste già: usa il suo ID oppure crea una nuova versione con un nuovo ID.`);
    unique(s.parts.map(p=>p.id),'pezzi'); unique(s.procedures.map(p=>p.id),'procedure');
    const parts = new Map(s.parts.map(p=>[p.id,p]));
    const visiting = new Set<string>(), visited = new Set<string>();
    function visit(id:string) { if(visiting.has(id))throw new Error(`Dipendenze circolari: ${id}`); if(visited.has(id))return; const p=parts.get(id);if(!p)throw new Error(`Dipendenza assente: ${id}`); visiting.add(id); p.dependsOn.forEach(visit);visiting.delete(id);visited.add(id); }
    for(const p of s.parts){ if(!s.procedures.some(r=>r.id===p.procedureId))throw new Error(`Procedura assente per ${p.name}`); if(s.assetId&&!p.meshName)throw new Error(`Nodo GLB assente per ${p.name}`);if(p.geometry.kind==='tube'&&!p.geometry.end)throw new Error(`Estremo geometrico assente per ${p.name}`);visit(p.id); }
    if(s.kind==='verified'&&(s.parts.some(p=>p.evidence!=='verified')||s.procedures.some(p=>!p.sources.length)))throw new Error('Una struttura verificata richiede evidenze per ogni pezzo e fonti per ogni procedura.');
    if(s.kind!=='didactic'&&existing.concat(b.structures.filter(x=>x!==s)).some(x=>x.kind!=='didactic'&&signature(x.standards)===signature(s.standards)))throw new Error(`Struttura meccanica già presente: riutilizza l’ID esistente.`);
    structures.set(s.id,s);
  }
  for(const bike of b.bikes){ const s=structures.get(bike.structureId);if(!s)throw new Error(`Struttura assente per ${bike.name}`);if(bike.status==='verified'&&s.kind!=='verified')throw new Error('Una bici verificata richiede una struttura verificata.');if(s.kind==='didactic'&&bike.status!=='didactic')throw new Error('Una struttura didattica non può essere attribuita come riferimento a una bici reale.'); }
  return b;
}
export function removalPlan(partId:string,s:Structure):Part[]{const out:Part[]=[], seen=new Set<string>();function visit(id:string){if(seen.has(id))return;seen.add(id);const p=s.parts.find(p=>p.id===id);if(!p)return;p.dependsOn.forEach(visit);out.push(p);}visit(partId);return out;}
