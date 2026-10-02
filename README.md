# Officina · Atlante della bicicletta

Una piattaforma italiana per studiare una bici prima di smontarla. Leggi `progetto.md` per obiettivo, stato reale, contratto dei dati e protocollo IA. Le nuove conversazioni con Codex leggono anche `AGENTS.md`.

## Utilizzo
1. Apri **Banco 3D**: trascina per ruotare, scorri o usa il gesto di zoom. Il cursore **Esploso** separa i componenti. Scegli un pezzo nel modello o nell’elenco, poi **Isola pezzo**.
2. Leggi **Descrizione** e **Come ottenerlo**: ruolo, procedura, dipendenze, strumenti e misure con attendibilità.
3. In **Libreria** filtra per categoria/marca o cerca modello e sottotipo.
4. **Aggiungi una bici** salva foto e note nell’archivio e scarica un dossier Markdown per l’IA. Passalo a una conversazione collegata al progetto insieme alle foto quando il sito privato non è accessibile all’IA.
5. L’IA ricerca il modello e gli standard, consulta il catalogo esistente e prepara un dossier JSON. **Controlla e importa** carica quel dossier e un eventuale GLB. Le bici possono condividere una struttura esistente.

La demo ha 656 elementi. È un atlante schematico parziale, con quantità illustrative; non rappresenta una bici commerciale. La ruota libera resta un gruppo, alcuni interni e minuterie non sono ricostruiti. Il riconoscimento fotografico automatico e la generazione CAD automatica non sono collegati. Le procedure della demo sono generali, non istruzioni verificate su una tua bici.

## Eseguire il progetto
Stack: React 19, Vinext/Vite, Three.js, componenti Radix/Shadcn, D1/SQLite, R2, Zod e Drizzle.

```powershell
npm ci
npm run dev
```

Se il computer usa un proxy aziendale, configura npm con il proxy autorizzato prima dell’installazione. Non disabilitare la verifica TLS.

Per inizializzare D1 locale crea un file ignorato `.sites-runtime/wrangler-test.json` con:
```json
{"name":"officina-local","compatibility_date":"2026-05-15","d1_databases":[{"binding":"DB","database_name":"site-creator-d1","database_id":"00000000-0000-4000-8000-000000000000","migrations_dir":"../drizzle"}]}
```
Poi:
```powershell
node node_modules/wrangler/bin/wrangler.js d1 migrations apply site-creator-d1 --local --persist-to .wrangler/state --config .sites-runtime/wrangler-test.json
node scripts/check-catalog.mjs
node node_modules/typescript/bin/tsc --noEmit
npm run build
```

Il Site privato è identificato da `.openai/hosting.json`. Distribuire tramite il flusso Sites preservando l’identità e le migrazioni. Il database locale non è quello del sito online.

## Fonti della demo
Le fonti generali sono collegate alle schede con il loro ambito: [pedali](https://www.parktool.com/en-us/blog/repair-help/pedal-installation-and-removal), [pedivelle](https://www.parktool.com/en-us/blog/repair-help/crank-removal-and-installation-three-piece), [mozzi](https://www.parktool.com/en-us/blog/repair-help/hub-overhaul-and-adjustment), [serie sterzo](https://www.parktool.com/en-us/blog/repair-help/threaded-headset-service), [movimento centrale regolabile](https://www.parktool.com/en-us/blog/repair-help/bottom-bracket-service-adjustable-cup-and-cone). Non identificano i pezzi della demo come un modello reale e non certificano misure o quantità.
