# Officina · Atlante della bicicletta

Una piattaforma italiana per studiare una bici prima di smontarla. Leggi `progetto.md` per obiettivo, stato reale, contratto dei dati e protocollo IA. Qualsiasi IA o sviluppatore può lavorare sui file: iniziare da `AGENTS.md` e [passaggio di consegne](docs/AI_HANDOFF.md).

## Avvio semplice su Windows

Apri la cartella del progetto e fai doppio clic su **Avvia-Officina.cmd**. Il browser apre http://127.0.0.1:5173/ con la bici di esempio già caricata. Tieni aperta la finestra dell'avvio; `Ctrl+C` ferma il programma. Sul primo avvio in un nuovo PC serve Node.js 22.13 o successivo e Internet per installare le dipendenze. Blender non serve per usare il banco. [Guida e prova guidata](docs/AVVIO.md).

## Utilizzo
1. Apri **Banco 3D**: trascina per ruotare, scorri o usa il gesto di zoom. Il cursore **Esploso** separa i componenti. Scegli un pezzo nel modello o nell’elenco, poi **Isola pezzo**.
2. Leggi **Descrizione** e **Come ottenerlo**: ruolo, procedura, dipendenze, strumenti e misure con attendibilità.
3. In **Libreria** filtra per categoria/marca o cerca modello e sottotipo.
4. **Aggiungi una bici** salva foto e note nell’archivio e scarica un dossier Markdown per l’IA. Passalo a una conversazione collegata al progetto insieme alle foto quando il sito privato non è accessibile all’IA.
5. L’IA ricerca il modello e gli standard, consulta il catalogo esistente e prepara un dossier JSON. **Controlla e importa** carica quel dossier e un eventuale GLB. Le bici possono condividere una struttura esistente.

Sono disponibili due bici: **Elops Speed 500 · esempio 3D**, ricostruita in Blender con 718 elementi selezionabili nella revisione 2, e la precedente **Classica**, demo procedurale con 656 elementi. La revisione migliora dentatura, catena a passo 12,7 mm, fissaggi delle guaine, pinze, mozzi, sterzo e minuteria. L'esempio Elops mostra l'intera bicicletta e si basa su specifiche pubbliche, ma geometria, quantità e interni non documentati sono illustrativi: non è una distinta OEM completa. Ruota libera, cartuccia movimento, interni delle leve ed elettronica restano gruppi. [Fonti e limiti dell'esempio](models/elops-study-v2/MODEL.md).

Il riconoscimento fotografico automatico e la generazione CAD automatica non sono collegati. Le procedure sono generali dove indicato, non istruzioni verificate sulla tua bici.

## Eseguire il progetto
Stack: React 19, Vinext/Vite, Three.js, componenti Radix/Shadcn, D1/SQLite, R2, Zod e Drizzle. Richiede Node.js 22.13 o successivo, npm e Git. Nessuna chiave IA o autenticazione Cloudflare è necessaria per lo sviluppo locale.

```powershell
npm ci
npm run db:init
npm run dev
```

Se il computer usa un proxy aziendale, configura npm con il proxy autorizzato prima dell’installazione. Non disabilitare la verifica TLS.

Aprire http://127.0.0.1:5173/. `db:init` è ripetibile: applica le migrazioni senza azzerare i dati locali. Per verificare:
```powershell
npm run check:catalog
node scripts/check-city-example.mjs
npm run check:types
npm run build
```

Il Site privato è identificato da `.openai/hosting.json`. Distribuire tramite il flusso Sites preservando l’identità e le migrazioni. Il database locale non è quello del sito online.

## Modelli migliori e lavoro da altri PC

Il [modello della bici Elops](models/elops-study-v2/MODEL.md) comprende sorgente modificabile `.blend`, GLB da circa 19 MB con oltre un milione di triangoli, schede, report, anteprima e viste ravvicinate. È incorporato nel programma senza upload manuale; la versione 1 resta archiviata. I poligoni aggiunti descrivono fori, filetti, sedi dei rulli e sezioni cave. I vincoli geometrici della catena sono registrati in `assembly-constraints.json` e controllati sul GLB reale. Il flusso per creare sorgenti modificabili, opzionalmente da CAD parametrico, ed esportare GLB con ogni pezzo indipendente è stato collaudato con Blender 4.5.14 LTS: [procedura Blender](docs/BLENDER_WORKFLOW.md), [cartella modelli](models/README.md). Il controllo `npm run check:model -- modello.glb dossier.json structure-id` verifica l'abbinamento dei pezzi prima dell'importazione.

È incluso un [esempio di minuteria](models/fastener-example-v1/MODEL.md) con sorgente Blender, GLB, dossier, report e anteprima: vite con filetto esterno geometrico, rondella e dado. È un test illustrativo di tre pezzi, non un ricambio verificato; il dado ha foro liscio. Questo primo collaudo non sostituisce la revisione di modelli e procedure di una bicicletta reale.

Per capire il codice: [architettura](docs/ARCHITECTURE.md). Per copiare il progetto, usare GitHub o produrre ZIP e bundle della cronologia: [portabilità](docs/PORTABILITA.md). Dopo un commit, `npm run backup:source` salva entrambi in `outputs/`. Il workflow GitHub verifica il codice, senza pubblicare automaticamente il sito. Foto, GLB e dati caricati online richiedono un backup separato.

Repository del sorgente: [YagoBJJ9125/Bicycle_Disassembly](https://github.com/YagoBJJ9125/Bicycle_Disassembly), pubblico come creato dal proprietario. Il sito e il relativo archivio hanno accesso separato dal repository.

## Fonti della demo
Le fonti generali sono collegate alle schede con il loro ambito: [pedali](https://www.parktool.com/en-us/blog/repair-help/pedal-installation-and-removal), [pedivelle](https://www.parktool.com/en-us/blog/repair-help/crank-removal-and-installation-three-piece), [mozzi](https://www.parktool.com/en-us/blog/repair-help/hub-overhaul-and-adjustment), [serie sterzo](https://www.parktool.com/en-us/blog/repair-help/threaded-headset-service), [movimento centrale regolabile](https://www.parktool.com/en-us/blog/repair-help/bottom-bracket-service-adjustable-cup-and-cone). Non identificano i pezzi della demo come un modello reale e non certificano misure o quantità.
