import { env } from 'cloudflare:workers';
import { builtInBundle as demoBundle } from './built-in';
import { bundleSchema, signature, type Bundle, type Structure, type Bike } from './catalog';
export function database(){const db=(env as unknown as {DB?:D1Database}).DB;if(!db)throw new Error('Archivio non disponibile. Riprova più tardi.');return db;}
export function assets(){const bucket=(env as unknown as {BUCKET?:R2Bucket}).BUCKET;if(!bucket)throw new Error('Archivio file non disponibile. Riprova più tardi.');return bucket;}
export async function readCatalog():Promise<Bundle>{const db=database();const [s,b]=await Promise.all([db.prepare('SELECT data FROM structures ORDER BY created_at DESC').all<{data:string}>(),db.prepare('SELECT data FROM bikes ORDER BY created_at DESC').all<{data:string}>()]);return bundleSchema.parse({schemaVersion:1,structures:[...demoBundle.structures,...s.results.map(r=>JSON.parse(r.data)).filter(r=>!demoBundle.structures.some(s=>s.id===r.id))],bikes:[...demoBundle.bikes,...b.results.map(r=>JSON.parse(r.data))]});}
export async function saveCatalog(bundle:Bundle){const db=database(),now=Date.now();const statements=[];const stored=await db.prepare('SELECT id FROM structures').all<{id:string}>();const ids=new Set(stored.results.map(r=>r.id));
 for(const s of bundle.structures)statements.push(db.prepare('INSERT INTO structures (id,signature,data,created_at) VALUES (?,?,?,?)').bind(s.id,s.kind==='didactic'?`didactic:${s.id}`:signature(s.standards),JSON.stringify(s),now));
 // The shipped demo remains immutable in source, but a bike may reference it after an explicit didactic import.
 for(const b of bundle.bikes)if(!ids.has(b.structureId)&&!bundle.structures.some(s=>s.id===b.structureId)){const s=demoBundle.structures.find(s=>s.id===b.structureId);if(s&&!ids.has(s.id)){statements.push(db.prepare('INSERT OR IGNORE INTO structures (id,signature,data,created_at) VALUES (?,?,?,?)').bind(s.id,`didactic:${s.id}`,JSON.stringify(s),now));ids.add(s.id);}}
 for(const b of bundle.bikes)statements.push(db.prepare('INSERT INTO bikes (id,structure_id,data,created_at) VALUES (?,?,?,?)').bind(b.id,b.structureId,JSON.stringify(b),now));if(statements.length)await db.batch(statements);
}
export function failure(e:unknown){console.error('Officina storage:',e instanceof Error?e.message:'unknown');return Response.json({error:'Operazione non completata. I dati inseriti sono conservati nel modulo: riprova.'},{status:503});}
export function sameOrigin(req:Request){const origin=req.headers.get('origin');const expected=new URL(req.url).origin;return !origin||origin===expected;}
