// A plain Node entrypoint so a Windows double-click needs no script-policy changes.
import {existsSync} from 'node:fs';
import {spawn,spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {setTimeout as pause} from 'node:timers/promises';

const root=fileURLToPath(new URL('../',import.meta.url));process.chdir(root);
const url='http://127.0.0.1:5173/';const noBrowser=process.argv.includes('--no-browser');
const [major,minor]=process.versions.node.split('.').map(Number);
if(major<22||(major===22&&minor<13))throw new Error('Installa Node.js 22.13 o successivo, poi riapri Avvia-Officina.cmd.');
async function isOfficina(){
 try{const response=await fetch(url+'api/catalog',{signal:AbortSignal.timeout(1500)});
  if(!response.ok)return false;const data=await response.json();
  return data.schemaVersion===1&&data.bikes?.some(b=>b.id==='elops-study-bike');
 }catch{return false;}
}
function browser(){
 if(noBrowser)return;
 const command=process.platform==='win32'?['cmd.exe',['/d','/c','start','',url]]:
   process.platform==='darwin'?['open',[url]]:['xdg-open',[url]];
 const result=spawn(command[0],command[1],{stdio:'ignore',windowsHide:true});
 result.on('error',()=>console.log('Apri nel browser: '+url));result.unref();
}
if(await isOfficina()){
 console.log('Officina è già avviata: '+url);browser();
}else{
if(!existsSync('node_modules/vinext/dist/cli.js')){
 console.log('Prima configurazione: download delle dipendenze con npm ci.');
 const install=process.platform==='win32'?spawnSync('cmd.exe',['/d','/c','npm ci'],{stdio:'inherit',windowsHide:true}):spawnSync('npm',['ci'],{stdio:'inherit'});
 if(install.error||install.status!==0)throw new Error('Installazione non riuscita. Verifica Node/npm e la connessione Internet, poi riprova.');
}
const init=spawnSync(process.execPath,['scripts/db-init.mjs'],{stdio:'inherit'});
if(init.error||init.status!==0)throw new Error('Database locale non inizializzato. Leggi il messaggio di errore.');
console.log('Avvio Officina. Tieni aperta questa finestra; Ctrl+C arresta il programma.');
const child=spawn(process.execPath,['scripts/run-framework.mjs','dev'],{stdio:'inherit',windowsHide:true});
let finished=false;
child.on('error',e=>{finished=true;console.error(e.message);process.exitCode=1;});
child.on('exit',code=>{finished=true;process.exitCode=code??1;});
process.on('SIGINT',()=>{child.kill('SIGINT');});
process.on('SIGTERM',()=>{child.kill('SIGTERM');});
for(let attempt=0;attempt<60&&!finished;attempt++){
 if(await isOfficina()){console.log('Pronto: '+url+' — esempio 3D già caricato.');browser();break;}
 await pause(1000);
 if(attempt===59)console.log('Il server impiega più tempo del previsto. Controlla i messaggi e apri '+url+' quando è pronto.');
}
}
