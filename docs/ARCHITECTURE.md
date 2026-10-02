# Mappa del codice

| Area | File | Responsabilità |
|---|---|---|
| Cruscotto e banco | `app/page.tsx` | Selezione bici/pezzo, filtri, schede, WebMCP |
| Libreria e importazione | `components/library.tsx` | Foto, dossier IA, catalogo e caricamento JSON/GLB |
| Visualizzatore | `components/bike-viewer.tsx` | Three.js, GLTFLoader, selezione, isolamento ed esploso |
| Aspetto | `app/globals.css` | Stili dell'applicazione |
| Contratto | `lib/catalog.ts` | Schema Zod, tipi, deduplicazione e grafo di smontaggio |
| Demo | `lib/demo.ts` | Geometrie illustrative e schede didattiche |
| Esempi incorporati | `lib/built-in.ts`, `data/elops-study-v1.json`, `public/models/` | Catalogo iniziale e bici Blender senza upload |
| Avvio Windows | `Avvia-Officina.cmd`, `scripts/start-local.mjs` | Dipendenze, migrazioni, server e browser |
| Dati persistenti | `lib/storage.ts`, `db/schema.ts` | Accesso D1, catalogo e asset R2 |
| Catalogo API | `app/api/catalog/route.ts` | Lettura e importazione atomica metadati |
| Asset API | `app/api/assets/` | Upload e accesso foto/GLB |
| Richieste di ricerca | `app/api/intakes/route.ts` | Dossier con foto e note |
| Validazione 3D | `lib/glb.ts` | GLB incorporato, nodi univoci, restrizioni attuali |
| Database | `drizzle/` | Migrazioni applicate, da non riscrivere |
| Runtime | `vite.config.ts`, `build/`, `scripts/run-framework.mjs` | Vinext, emulazione Cloudflare, autenticazione locale e distribuzione |
| Sorgenti 3D | `models/`, `tools/blender/` | Convenzioni e esportazione Blender |

## Dati e geometrie

Una `Bike` riferisce una `Structure` attraverso `structureId`. Più bici possono riutilizzare la struttura. La struttura contiene pezzi, procedure, standard e limiti di copertura. Non esiste ancora un modello relazionale di sottogruppi condivisi.

Un `Part` riferisce una procedura; `dependsOn` elenca i pezzi da togliere prima. La geometria procedurale è un ripiego didattico. Se la struttura ha `assetId` oppure `modelPath` incorporato, il viewer carica il GLB e collega `meshName` all'oggetto. `lib/glb-nodes.ts` usa le associazioni agli indici originali: GLTFLoader può modificare nomi con punti o collisioni. I nomi Blender devono corrispondere esattamente al dossier; ogni mesh è una foglia e un pezzo fisico. Le posizioni sono in metri, gli spostamenti dell'esploso in metri nel sistema glTF (Y verticale).

Gli oggetti importati conservano la loro trasformazione in scena. Il viewer avvolge ogni mesh in un gruppo e vi applica lo spostamento `explode`; non ricostruisce automaticamente una sequenza meccanica o l'animazione dello svitamento.

## Storage e accesso

D1 contiene `structures`, `bikes`, `intakes`; R2 conserva i file con ID generati dal server. `DB` e `BUCKET` sono i binding. `ASSETS` è riservato ai file statici del runtime. L'accesso online è fornito dal dispatcher del sito privato; le verifiche same-origin proteggono le scritture cross-origin, ma non sono un sistema di autorizzazione multiutente.

`npm run db:init` applica le migrazioni allo stesso storage locale `.wrangler/state` utilizzato dal dev server. È ripetibile e non azzera il database. Un nuovo clone parte con un archivio locale vuoto oltre alla demo incorporata.

Lo sviluppo non richiede il plugin Sites o un connettore IA: gli strumenti necessari sono inclusi e le dipendenze sono bloccate in `package-lock.json`. Per pubblicare sul sito privato esistente serve invece il relativo accesso al provider. Per ospitarlo altrove vanno adattati binding, migrazioni e autenticazione; non basta caricare `dist/client` su GitHub Pages.
