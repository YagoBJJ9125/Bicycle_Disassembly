import { readCatalog,saveCatalog,assets,failure,sameOrigin } from '@/lib/storage';
import { validateBundle } from '@/lib/catalog';
import { validateGlb } from '@/lib/glb';
export async function GET(){try{return Response.json(await readCatalog(),{headers:{'Cache-Control':'no-store'}});}catch(e){return failure(e);}}
// Owner-private Site; access is enforced by the Sites dispatcher, including service callers.
export async function POST(req:Request){if(!sameOrigin(req))return Response.json({error:'Origine non consentita'},{status:403});try{const text=await req.text();if(text.length>6_000_000)return Response.json({error:'Il dossier JSON supera 6 MB'},{status:413});const existing=await readCatalog();let bundle;try{bundle=validateBundle(JSON.parse(text),existing.structures);if(bundle.bikes.some(b=>existing.bikes.some(x=>x.id===b.id)))throw new Error('Una bicicletta con questo ID esiste già.');}catch(e){return Response.json({error:e instanceof Error?e.message:'Dossier non valido'},{status:400});}
 if(bundle.structures.some(s=>s.modelPath))return Response.json({error:'modelPath è riservato agli esempi incorporati. Per importare usa il caricamento GLB e assetId.'},{status:400});
 for(const s of bundle.structures)if(s.assetId){const file=await assets().get(s.assetId);if(!file)return Response.json({error:`Modello GLB assente: ${s.assetId}`},{status:400});const names=validateGlb(await file.arrayBuffer());if(s.parts.some(p=>!names.includes(p.meshName!)))return Response.json({error:'Il GLB non contiene tutti i nodi dichiarati nel dossier.'},{status:400});}
 await saveCatalog(bundle);return Response.json({ok:true,bikes:bundle.bikes.length,structures:bundle.structures.length});}catch(e){return failure(e);}}
