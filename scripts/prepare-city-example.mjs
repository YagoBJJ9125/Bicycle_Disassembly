import {readFileSync,writeFileSync,mkdirSync,copyFileSync} from 'node:fs';
const bundle=JSON.parse(readFileSync('models/elops-study-v1/catalog.json','utf8'));
mkdirSync('public/models',{recursive:true});
copyFileSync('models/elops-study-v1/web/assembly.glb','public/models/elops-study-v1.glb');
writeFileSync('data/elops-study-v1.json',JSON.stringify(bundle,null,2)+'\n');
console.log(`Esempio incorporato: ${bundle.structures[0].parts.length} pezzi, nessuna importazione manuale necessaria.`);
