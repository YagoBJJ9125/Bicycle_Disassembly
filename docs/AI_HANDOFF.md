# Riprendere il progetto con qualsiasi IA

Questo repository contiene il codice dell'applicazione, il contratto JSON, le migrazioni, la demo e gli strumenti di sviluppo. Non richiede un particolare assistente per essere modificato. Le funzioni online dipendono dal runtime Cloudflare e dall'accesso privato del sito; il riconoscimento IA è ancora un flusso esterno, non un servizio integrato.

## Primo messaggio da usare in una nuova conversazione

> Lavora nel repository Bicycle_Disassembly. Prima leggi AGENTS.md, progetto.md, README.md, docs/ARCHITECTURE.md e lib/catalog.ts. Il progetto è una piattaforma italiana di restauro bici con libreria e modelli scomponibili fino alla minuteria. Non considerare la demo procedurale un modello reale verificato. Per i modelli segui docs/BLENDER_WORKFLOW.md. Consulta il catalogo aggiornato prima di creare nuove strutture. Distingui i dati verificati dalle ipotesi, conserva ID e migrazioni, evita credenziali nel client. Verifica catalogo, TypeScript e build; aggiorna la documentazione in base a ciò che hai effettivamente realizzato.

Aggiungere poi la modifica desiderata e le foto/manuali pertinenti. Per un'IA priva di accesso ai file, allegare almeno questi documenti e i file interessati; il solo link a un repository privato non concede accesso.

## Avvio e orientamento

Node.js 22.13 o superiore nella famiglia 22, npm e Git. `npm ci`, `npm run db:init`, `npm run dev`. Aprire http://127.0.0.1:5173/. L'emulazione D1/R2 è locale e non richiede credenziali Cloudflare. In questo PC le dipendenze sono già installate.

`npm run check:catalog`, `npm run check:types`, `npm run build` sono le verifiche di consegna. `npm run check:model -- modello.glb dossier.json structure-id` controlla i modelli esterni. `scripts/check-api.mjs` è un test manuale con server avviato e scritture nel database locale: non eseguirlo contro l'archivio reale.

## Stato da conservare

- La demo è ancora procedurale e schematica: 656 elementi, interni parziali, quantità illustrative.
- Non esistono ancora sorgenti `.blend` di biciclette reali verificate. Il flusso è collaudato con Blender portabile 4.5.14 LTS su `models/fastener-example-v1`: tre pezzi illustrativi, filetto esterno geometrico e foro del dado liscio. Sono inclusi sorgente, GLB, dossier, report e anteprima; non attribuirli a un ricambio OEM. Il pacchetto Blender è locale in `.tools` e non viene versionato; si recupera con `tools/blender/get-portable.ps1`.
- L'IA non deve inventare particolari nascosti, standard, utensili, misure o coppie di serraggio.
- `dependsOn` descrive le rimozioni precedenti. Un telaio saldato resta un componente unico.
- `.openai/hosting.json` conserva l'identità del sito esistente; non ricrearla per sviluppare localmente.
- Un commit/push non distribuisce automaticamente l'applicazione online. Il workflow GitHub verifica il codice e non pubblica il sito.
- Il repository GitHub confermato è `YagoBJJ9125/Bicycle_Disassembly`, pubblico come creato dal proprietario. Il remote `origin` punta a GitHub; `sites` resta il provider del sito privato.
- Il catalogo online, gli asset R2 e i dossier caricati sono dati esterni al repository. Richiedere l'esportazione aggiornata per lavorare su una bici reale.

## Priorità consigliata

Scegliere una prima bici reale e documentarne un sottogruppo, per esempio mozzo anteriore o serie sterzo. Ricostruire geometrie con quote e distinta dei pezzi, importare il GLB e verificare selezione, esploso e utensili. Dopo la verifica, estendere il metodo agli altri gruppi. Una bici interamente credibile nasce dall'inventario e dalle fonti, non da una sola foto o dal numero di poligoni.
