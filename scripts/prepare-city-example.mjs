import {readFileSync,writeFileSync,mkdirSync,copyFileSync} from 'node:fs';
const id='elops-study-v2';
const bundle=JSON.parse(readFileSync(`models/${id}/catalog.json`,'utf8'));
mkdirSync('public/models',{recursive:true});
copyFileSync(`models/${id}/web/assembly.glb`,`public/models/${id}.glb`);
writeFileSync(`data/${id}.json`,JSON.stringify(bundle,null,2)+'\n');
console.log(`Esempio incorporato: ${bundle.structures[0].parts.length} pezzi, nessuna importazione manuale necessaria.`);
