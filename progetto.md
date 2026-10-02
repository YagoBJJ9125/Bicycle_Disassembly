# Officina — atlante della bicicletta

## Scopo e utente
Il proprietario sta avviando un’attività di restauro e parte senza conoscenze di biciclette. Deve vedere in anticipo cosa troverà durante lo smontaggio, comprendere la funzione di ogni componente e conoscere procedura, prerequisiti e utensili necessari, comprese le misure. La lingua del prodotto è italiano.

La piattaforma deve diventare una libreria di biciclette, organizzata per categoria, marca e sottotipo, con un banco 3D navigabile. Il traguardo è la scomposizione completa delle bici documentate fino a viti, rondelle, molle, sfere e componenti minimi effettivamente separabili. Non significa tagliare saldature o aprire cartucce non revisionabili.

## Stato reale della prima versione
- Libreria filtrabile per categoria e marca, ricerca per nome, marca, anno e sottotipo.
- Banco 3D Three.js, rotazione, zoom, selezione di ciascun pezzo, isolamento, filtro per gruppo e cursore esploso.
- Bici intera Elops Speed 500 di riferimento, ricostruita in Blender: 704 elementi, sorgente modificabile, GLB incorporato da circa 3,4 MB. Allestimento da fonti Decathlon; geometria e interni non documentati restano approssimati. Ruota libera, cartuccia, interni leve ed elettronica non sono completamente scomposti. Non è una distinta OEM verificata.
- Avvio Windows con doppio clic su `Avvia-Officina.cmd`: installazione dipendenze se mancanti, migrazioni ripetibili, browser e riuso dell'istanza locale. Guida `docs/AVVIO.md`.
- Demo procedurale monovelocità: 656 elementi singolarmente selezionabili. È schematica, con quantità illustrative. Nessun marchio o modello commerciale viene simulato come identificato.
- Descrizione, procedura di gruppo, utensili e misure con attendibilità, dipendenze, avvertenze e fonti per i gruppi documentati.
- Archivio persistente D1 per strutture, biciclette e dossier; R2 per fotografie e GLB. Il Site è privato del proprietario.
- Foto → dossier persistente → istruzioni scaricabili per un’IA nella conversazione → confronto della libreria → importazione JSON e opzionale GLB.
- Controllo strutturale all’importazione: ID univoci, riferimenti validi, dipendenze senza cicli, corrispondenza nodi GLB, firma meccanica senza duplicati.
- Esportazione JSON del catalogo. Le fotografie e i GLB restano file separati: questa esportazione non è un backup completo dei file.

Non sono implementati: servizio IA autonomo nel sito, ricerca web automatica nel sito, generazione CAD automatica, inventario verificato di un modello reale, checklist persistente di un restauro, editor manuale del catalogo, riutilizzo automatico dei singoli sottogruppi. Il protocollo per l’IA consente di lavorare nel progetto adesso; non sostituisce un collegamento a un servizio IA.

## Procedura per una nuova bici
1. Raccogli almeno entrambi i lati, marchi sul telaio, sigle del cambio/freni, mozzi, pedivelle e zona movimento centrale. Conserva foto e note. Non dedurre componenti nascosti dalla forma del telaio.
2. Leggi il catalogo aggiornato tramite l’esportazione UI o `GET /api/catalog` nel contesto autorizzato. Se il sito privato non è accessibile all’IA, il proprietario allega foto e catalogo alla conversazione.
3. Identifica candidati marca/modello/anno e ogni gruppo installato. Specifica i livelli di confidenza e le foto o misure mancanti. Il componente effettivamente montato prevale sull’allestimento storico.
4. Cerca manuali, cataloghi ed esplosi ufficiali. Registra URL, titolo e cosa la fonte dimostra; un articolo generale non prova la misura di un componente specifico.
5. Confronta gli standard con la libreria prima della modellazione. Identità di telaio o marca non equivale a identità dei gruppi. Campi ignoti impediscono una conferma esatta. Anche la coincidenza degli standard richiede controllo di quantità, componenti e variante.
6. Se esiste una struttura reale documentata equivalente, dì: **Puoi usare il modello già caricato “[nome]”**. Importa soltanto una nuova scheda bici che riferisca il suo `structureId`.
7. Se la corrispondenza è parziale, presenta differenze e punti da verificare. Per ora una nuova struttura è un record completo; in futuro verranno condivisi singoli sottogruppi. Non affermare intercambiabilità di ricambi sulla sola somiglianza.
8. Se manca, ricostruisci un elenco completo dei pezzi dalle fonti, i gruppi, gli utensili, le dipendenze e le geometrie. Blocchi non documentati restano `unknown` e vengono elencati in `coverage`; la bici non è “completa” finché sono aperti.
9. Importa il dossier; controlla nel banco la corrispondenza tra pezzi e nodi. Una validazione informatica non certifica la correttezza meccanica: serve una revisione basata sui manuali o sulla bici reale.

## Contratto dei dati
Lo schema Zod autorevole è `lib/catalog.ts`; l’esempio concreto esportabile è `data/catalogo-didattico.json`.

Un dossier ha `{schemaVersion:1, structures:[], bikes:[]}`. Può contenere soltanto `bikes` per riutilizzare un ID esistente. Non reimportare la demo con gli stessi ID: il controllo respinge duplicati.

### Struttura
`id`, `name`, `version`, `kind` (`didactic`, `reference`, `verified`), `standards` (almeno cinque valori documentati), `coverage`, `parts`, `procedures`, opzionale `assetId`. `modelPath` è riservato ai GLB incorporati nel sorgente sotto `/models/`; l'API non lo accetta in dossier importati. Non usarlo insieme ad `assetId`.

Gli standard comprendono almeno telaio, serie sterzo, movimento, pedivelle, freni, mozzi, trasmissione, ruote e pedali per le configurazioni complete. Aggiungere sigle, varianti, diametri, filettature e quantità sufficienti a distinguere strutture realmente diverse. La firma è calcolata dagli standard ordinati, senza usare la marca della bici.

`reference` = struttura utile ma non interamente verificata. `verified` richiede pezzi con evidenza verificata e procedure con fonti; l’importazione controlla queste dichiarazioni, non ne prova la verità. L’IA deve verificare i contenuti prima di usare il livello.

### Pezzo
`id`, `name`, `group`, `description`, `procedureId`, `dependsOn`, `evidence`, `serviceability`, `geometry`, `explode`, opzionale `meshName`.
- `dependsOn`: ID dei componenti da rimuovere prima, in un grafo aciclico.
- `evidence`: `verified`, `indicative`, `unknown`.
- `serviceability`: `serviceable`, `specialist`, `inseparable`.
- `geometry`: `kind` (`tube`, `ring`, `box`, `ball`, `cylinder`), `position`, `size`, `color`, opzionali `end` e `rotation`. Coordinate in metri e rotazioni in radianti. Un tube richiede un end. Le size sono raggio/lunghezza per cylinder, raggio principale/sezione per ring, raggio per ball, dimensioni xyz per box.
- `explode`: vettore di spostamento al 100%; deve separare davvero i pezzi interni senza perdere la leggibilità.
- `meshName`: nome del nodo mesh GLB, obbligatorio se la struttura usa un GLB. Ogni nodo è un oggetto fisicamente separabile; geometrie di un telaio saldato appartengono a un unico componente.

### Procedura
`id`, `title`, `steps`, `tools` (`name`, `size`, `certainty`), `warnings`, `sources` (`title`, URL HTTPS, `scope`). La procedura può essere condivisa da pezzi ripetuti, ma deve chiarire il passaggio specifico che consente di ottenere il pezzo scelto. `scope` distingue istruzioni generali da prove sul componente reale.

Non inserire coppie, sfere o misure “probabili” come verificate. Le misure mancanti sono esplicitamente da misurare. Specificare il punto di vista per i sensi di svitamento; BSA e italiano sono differenti. Fornire indicazioni di rimontaggio solo se documentate.

### Scheda bici
`id`, `name`, `brand`, `category` (`Città`, `Corsa`, `MTB`, `Gravel`, `BMX`, `Altre`), `subtype`, `year`, `structureId`, `status`, `notes`, `color`.
Più bici possono riferire la stessa struttura. Una struttura didattica può essere associata solo a schede didattiche.

## GLB e risorse
Formato GLB 2.0, massimo 25 MB per file, senza risorse esterne o estensioni di compressione richieste. Nomi dei nodi mesh univoci, semplici e stabili. Un pezzo per mesh nominata, materiali incorporati e scala metrica. Il JSON può essere importato con un singolo GLB per nuova struttura: il sito carica il file, inserisce assetId e controlla meshName. Gli asset di terzi richiedono licenza compatibile; non copiare modelli proprietari senza autorizzazione.

## API del progetto
Il dispatcher del Site privato autorizza gli accessi; nessun token deve finire nel client o nel dossier.
- `GET /api/catalog`: catalogo aggiornato con demo e record persistiti.
- `POST /api/catalog`: valida e importa un dossier senza sovrascrivere record esistenti. Batch atomico per metadati.
- `POST /api/assets`: byte di foto o GLB, Content-Type appropriato; restituisce id, URL e nomi mesh.
- `GET /api/assets/:id`: file archiviato nel contesto autorizzato.
- `GET/POST /api/intakes`: lista o salvataggio di foto+note per la ricerca.

Gli endpoint condivisi si basano sull’accesso owner-private del Site. Prima di rendere pubblico il Site bisogna aggiungere autorizzazione esplicita alle scritture. Un’IA esterna non acquisisce accesso soltanto perché riceve un link: può richiedere un catalogo esportato o le foto allegate.

## Evoluzioni utili
1. Modellare e verificare la prima bici reale: è il passo più utile, perché guida sia precisione del 3D sia schede degli utensili.
2. Introdurre sottogruppi versionati condivisi: mozzi, serie sterzo, movimento centrale, freni. Una bici è una composizione e gli stessi gruppi non si rigenerano.
3. Checklist persistente di restauro con foto prima/dopo, etichette delle vaschette, stato dei pezzi e note su corrosione.
4. Distinta utensili deduplicata per intervento, con misure confermate e lista dei punti da misurare.
5. Aggiungere riordino/animazione della sequenza e istruzioni di rimontaggio con coppie ricavate dai manuali.
6. Collegare un servizio IA sul server per riconoscimento/ricerca con limite di spesa e approvazione dei risultati prima dell’importazione. Non acquistare crediti né configurare account implicitamente.

## Modelli dettagliati e portabilità (2 ottobre 2026)
La qualità della demo è insufficiente per riprodurre fedelmente parti reali. La direzione scelta è conservare originali modificabili Blender, eventualmente prodotti da CAD parametrico, ed esportare copie GLB per il browser. Aumentare i poligoni delle primitive non ricostruisce particolari assenti. Il limite upload attuale resta 25 MB e non sono stati aggiunti decoder di compressione o caricamento progressivo.

`docs/BLENDER_WORKFLOW.md` definisce unità, nomi, collection, budget e verifica. `tools/blender/export_officina.py` è collaudato con Blender portabile 4.5.14 LTS sull'esempio `models/fastener-example-v1`: vite con filetto esterno, rondella e dado con foro liscio. Sorgente `.blend`, GLB, dossier, report e anteprima sono inclusi. Il GLB contiene tre mesh selezionabili, 94.538 triangoli e pesa circa 6,97 MB; il caricamento Three.js verifica unità e corrispondenza degli oggetti. Nessun modello reale verificato di bicicletta è stato creato. `scripts/check-model.mjs` controlla un GLB rispetto al dossier prima del caricamento. Il downloader ripetibile `tools/blender/get-portable.ps1` verifica SHA-256 e conserva l'applicazione in `.tools`, esclusa da Git.

Per qualsiasi altra IA sono disponibili `AGENTS.md`, `docs/AI_HANDOFF.md` e `docs/ARCHITECTURE.md`. Lo sviluppo locale richiede Node/npm, senza plugin Codex o account Cloudflare: `npm ci`, `npm run db:init`, `npm run dev`. `docs/PORTABILITA.md` distingue il sorgente dai dati online. `npm run backup:source` crea ZIP e bundle Git dai commit; `.github/workflows/verify.yml` verifica il codice senza distribuire. Il repository confermato è `YagoBJJ9125/Bicycle_Disassembly`, pubblico come creato dal proprietario; `origin` punta a GitHub, mentre `sites` conserva la destinazione del sito privato. La CLI è stata autenticata dal proprietario per il caricamento del sorgente.

## Verifiche
L'esempio completo è in `models/elops-study-v1`; `scripts/prepare-city-example.mjs` sincronizza il suo dossier in `data/elops-study-v1.json` e il GLB in `public/models/`. `lib/built-in.ts` unisce questo riferimento alla demo Classica e rende entrambi disponibili senza dati persistiti. Dopo modifiche al sorgente, esportare e sincronizzare prima dei controlli. `scripts/check-city-example.mjs` verifica copie incorporate, catalogo e caricamento reale Three.js di tutti i 704 nomi, inclusi nomi che GLTFLoader modifica: il viewer usa le associazioni agli indici glTF originali.

`node scripts/check-catalog.mjs` verifica demo, dipendenze, rifiuto dei duplicati e comportamento con standard mancanti. `node node_modules/typescript/bin/tsc --noEmit` controlla i tipi. La build usa il workflow Sites; schema D1 tramite Drizzle. Prima della consegna verificare la distribuzione fino allo stato succeeded; non dichiarare pubblicato sulla sola base della creazione del Site.
