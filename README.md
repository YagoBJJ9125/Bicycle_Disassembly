# Officina · Atlante della bicicletta

Una piattaforma italiana per studiare una bici prima di smontarla. Leggi `progetto.md` per obiettivo, stato reale, contratto dei dati e protocollo IA. Qualsiasi IA o sviluppatore può lavorare sui file: iniziare da `AGENTS.md` e [passaggio di consegne](docs/AI_HANDOFF.md).

## Utilizzo
1. Apri **Banco 3D**: trascina per ruotare, scorri o usa il gesto di zoom. Il cursore **Esploso** separa i componenti. Scegli un pezzo nel modello o nell’elenco, poi **Isola pezzo**.
2. Leggi **Descrizione** e **Come ottenerlo**: ruolo, procedura, dipendenze, strumenti e misure con attendibilità.
3. In **Libreria** filtra per categoria/marca o cerca modello e sottotipo.
4. **Aggiungi una bici** salva foto e note nell’archivio e scarica un dossier Markdown per l’IA. Passalo a una conversazione collegata al progetto insieme alle foto quando il sito privato non è accessibile all’IA.
5. L’IA ricerca il modello e gli standard, consulta il catalogo esistente e prepara un dossier JSON. **Controlla e importa** carica quel dossier e un eventuale GLB. Le bici possono condividere una struttura esistente.

La demo ha 656 elementi. È un atlante schematico parziale, con quantità illustrative; non rappresenta una bici commerciale. La ruota libera resta un gruppo, alcuni interni e minuterie non sono ricostruiti. Il riconoscimento fotografico automatico e la generazione CAD automatica non sono collegati. Le procedure della demo sono generali, non istruzioni verificate su una tua bici.

## Eseguire il progetto
Stack: React 19, Vinext/Vite, Three.js, componenti Radix/Shadcn, D1/SQLite, R2, Zod e Drizzle. Richiede Node.js 22.13 o superiore nella famiglia 22, npm e Git. Nessuna chiave IA o autenticazione Cloudflare è necessaria per lo sviluppo locale.

```powershell
npm ci
npm run db:init
npm run dev
```

Se il computer usa un proxy aziendale, configura npm con il proxy autorizzato prima dell’installazione. Non disabilitare la verifica TLS.

Aprire http://127.0.0.1:5173/. `db:init` è ripetibile: applica le migrazioni senza azzerare i dati locali. Per verificare:
```powershell
npm run check:catalog
npm run check:types
npm run build
```

Il Site privato è identificato da `.openai/hosting.json`. Distribuire tramite il flusso Sites preservando l’identità e le migrazioni. Il database locale non è quello del sito online.

## Modelli migliori e lavoro da altri PC

La demo non è stata convertita in un modello Blender fedele. Il flusso per creare sorgenti modificabili `.blend`, opzionalmente da CAD parametrico, ed esportare GLB con ogni pezzo indipendente è stato collaudato con Blender 4.5.14 LTS: [procedura Blender](docs/BLENDER_WORKFLOW.md), [cartella modelli](models/README.md). Il controllo `npm run check:model -- modello.glb dossier.json structure-id` verifica l'abbinamento dei pezzi prima dell'importazione.

È incluso un [esempio di minuteria](models/fastener-example-v1/MODEL.md) con sorgente Blender, GLB, dossier, report e anteprima: vite con filetto esterno geometrico, rondella e dado. È un test illustrativo di tre pezzi, non un ricambio verificato; il dado ha foro liscio. Questo primo collaudo non sostituisce la revisione di modelli e procedure di una bicicletta reale.

Per capire il codice: [architettura](docs/ARCHITECTURE.md). Per copiare il progetto, usare GitHub o produrre ZIP e bundle della cronologia: [portabilità](docs/PORTABILITA.md). Dopo un commit, `npm run backup:source` salva entrambi in `outputs/`. Il workflow GitHub verifica il codice, senza pubblicare automaticamente il sito. Foto, GLB e dati caricati online richiedono un backup separato.

Repository del sorgente: [YagoBJJ9125/Bicycle_Disassembly](https://github.com/YagoBJJ9125/Bicycle_Disassembly), pubblico come creato dal proprietario. Il sito e il relativo archivio hanno accesso separato dal repository.

## Fonti della demo
Le fonti generali sono collegate alle schede con il loro ambito: [pedali](https://www.parktool.com/en-us/blog/repair-help/pedal-installation-and-removal), [pedivelle](https://www.parktool.com/en-us/blog/repair-help/crank-removal-and-installation-three-piece), [mozzi](https://www.parktool.com/en-us/blog/repair-help/hub-overhaul-and-adjustment), [serie sterzo](https://www.parktool.com/en-us/blog/repair-help/threaded-headset-service), [movimento centrale regolabile](https://www.parktool.com/en-us/blog/repair-help/bottom-bracket-service-adjustable-cup-and-cone). Non identificano i pezzi della demo come un modello reale e non certificano misure o quantità.
