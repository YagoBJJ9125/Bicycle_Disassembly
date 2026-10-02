import {readFileSync,writeFileSync} from 'node:fs';
const path='app/page.tsx';let s=readFileSync(path,'utf8');
const start=s.indexOf("{view==='library'?<div className=\"library-layout\">");
const end=s.indexOf(':<><div className="breadcrumb">',start);
if(start<0||end<0)throw new Error('Expected library slice missing');
s=s.slice(0,start)+"{archiveError&&<div className=\"archive-error\" role=\"alert\">{archiveError}<button onClick={()=>void refresh()}>Riprova</button></div>}{view==='library'?<LibraryView bundle={bundle} intakes={intakes} onOpen={openBike} onRefresh={refresh} dialogOpen={dialogOpen} onDialogChange={setDialogOpen}/>"+s.slice(end);
s=s.replace('<span>Città</span>','<span>{bike.category}</span>').replace('<span className="pill">DIDATTICA</span>','<span className="pill">{labels[bike.status]}</span>').replace('Questo è un esempio generico. Misure e componenti interni vanno verificati sulla tua bici.','{structure.kind===\'didactic\'?\'Questo è un esempio generico. Misure e componenti interni vanno verificati sulla tua bici.\':bike.notes}').replace('<dd>Schematica</dd>','<dd>{structure.assetId?\'Modello GLB\':\'Schematica\'}</dd>').replace('Modello schematico</span>','{structure.assetId?\'Modello GLB\':\'Modello schematico\'}</span>').replace('/ modello didattico</span>','/ {labels[structure.kind].toLowerCase()}</span>');
writeFileSync(path,s);
