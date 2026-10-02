# Modelli dettagliati: CAD, Blender e piattaforma

## Perché cambiare metodo

La demo attuale usa cilindri, anelli e primitive con pochi dettagli. Aumentare i segmenti rende i bordi più tondi, ma non aggiunge filetti, sedi, gole, cave, guarnizioni o la geometria degli interni. Per studiare il restauro servono prima la distinta dei pezzi e le quote del componente.

Blender è adatto al modello modificabile, ai materiali, alla rifinitura e all'esportazione glTF. Per componenti costruiti su dimensioni vincolate, FreeCAD è una possibile base parametrica: conservare anche `.FCStd`/STEP e trasferire a Blender una tessellazione adeguata. È un'opzione, non un requisito di avvio della piattaforma.

Documentazione ufficiale: [esportazione Blender](https://docs.blender.org/api/main/bpy.ops.export_scene.html), [caratteristiche FreeCAD](https://freecad.github.io/Website/features/). Consultare anche la documentazione della versione installata prima di cambiare l'esportatore.

## Sorgente e copia per il web

Conservare il sorgente `.blend` ricco di dettagli e modificatori. Esportare una copia `.glb` per il browser, senza alterare il sorgente. La piattaforma ha attualmente un limite di **25.000.000 byte per file** e nessun decoder Draco/Meshopt configurato. Non promettere una qualità illimitata aumentando i poligoni.

Il budget deve derivare dall'ispezione alla distanza utile: zoom sul singolo pezzo, forme leggibili, filetti e utensili quando rilevanti. Un primo budget sperimentale potrebbe essere 100–500 mila triangoli per un modello web, ma non è una soglia garantita: misurare fluidità, memoria, tempo di caricamento e dimensione sul PC reale. Non decimare indiscriminatamente bordi funzionali, sedi di cuscinetti o impronte delle viti. I poligoni non sostituiscono quote corrette.

I dettagli che definiscono forma e accoppiamento devono essere geometrici. Rugosità e normal map possono rappresentare finiture, senza fingere aperture o componenti interni mancanti. Usare materiali metallic-roughness compatibili con glTF; effetti procedurali complessi vanno semplificati o convertiti in texture incorporate.

## Preparazione della scena

1. Identificare il componente effettivamente montato e raccogliere manuale, esploso, foto e quote. Riutilizzare prima i gruppi già documentati. Registrare parti ignote in `coverage`.
2. Impostare una unità Blender = **1 metro**, `Unit Scale = 1.0`. Una vite lunga 20 mm ha lunghezza 0,020 unità. La conversione Blender Z-up → glTF Y-up è eseguita dall'esportatore.
3. Creare una collection visibile **OFFICINA_EXPORT**. Vi appartengono soltanto mesh dei pezzi da importare e, eventualmente, empty di organizzazione.
4. Una mesh foglia per ogni pezzo fisico. Due dadi identici sono due oggetti separati, con nomi diversi; possono condividere i dati della mesh. Un telaio saldato resta un solo pezzo. Un oggetto può contenere più superfici/materiali.
5. Usare nomi stabili, preferibilmente uguali agli ID: `front-hub-axle`, `front-hub-ball-left-01`. Riportarli in `parts[].meshName`. Non affidarsi ai nomi automatici `Cylinder.001`.
6. Posizionare i pezzi nello stato assemblato. Correggere normali, trasformazioni specchiate e geometrie vuote. Non mettere oggetti figli sotto una mesh: il viewer attuale li duplicherebbe nella separazione dei pezzi.
7. Preparare il dossier JSON secondo `lib/catalog.ts`. Anche un modello GLB richiede i campi `geometry` previsti dallo schema; possono essere un ripiego indicativo e devono usare unità corrette. `explode` è espresso in metri negli assi glTF, quindi Y è verticale.
8. Salvare il sorgente con versione e conservare fonti, quote note/ignote e licenza in una scheda accanto al file. Nessuna geometria generata è automaticamente `verified`.

## Esportazione assistita

È incluso `tools/blender/export_officina.py`, da eseguire **dentro Blender**. Non scarica pacchetti, non salva il `.blend` e non crea da solo gli interni della bicicletta. Controlla nomi, pezzi, unità, triangoli e compatibilità del file esportato, applicando i modificatori alla copia web.

Esempio PowerShell dalla radice del progetto, sostituendo il percorso con quello della versione installata:

```powershell
& 'C:\percorso\blender.exe' --background 'models\mia-struttura-v1\source\assembly.blend' --python-exit-code 1 --python 'tools\blender\export_officina.py' -- --catalog 'models\mia-struttura-v1\catalog.json' --structure 'mia-struttura-v1' --output 'models\mia-struttura-v1\web\assembly.glb'
npm run check:model -- models/mia-struttura-v1/web/assembly.glb models/mia-struttura-v1/catalog.json mia-struttura-v1
```

L'esportatore crea anche `assembly.report.json` con versione Blender, quantità di mesh, triangoli e peso. Usa `--overwrite` soltanto per sostituire intenzionalmente un'esportazione esistente; per nuove revisioni preferire una nuova versione. Se il controllo fallisce dopo l'esportazione, il GLB resta sul disco per diagnosi e non va importato come valido.

**Stato di verifica:** Blender non era installato nel PC al momento della preparazione. Il codice dell'esportatore è predisposto ma non ancora provato dentro Blender; prima del primo utilizzo reale eseguire un export piccolo e controllarlo nel banco. Il controllo Node è eseguibile con le dipendenze già presenti.

## Accettazione del modello

- Distinta e fonti coprono ciascun pezzo rappresentato; i limiti dichiarano le parti assenti.
- Dimensioni e accoppiamenti sono coerenti con quote misurate o documentate.
- Il controllo GLB passa; ogni parte si seleziona e si isola nel banco senza trascinare altri pezzi.
- La vista assemblata combacia e l'esploso separa gli interni in modo leggibile.
- Lo zoom mostra sedi, impronte e particolari utili; il modello resta utilizzabile sul PC destinato al lavoro.
- Descrizione, dipendenze e utensili sono verificati separatamente dalla geometria.

Un'idea utile è mantenere, in futuro, dettagli diversi per bici intera e pezzo isolato: il banco carica un modello leggero, mentre l'ispezione carica la versione dettagliata del pezzo. Questo richiede asset per componente e caricamento progressivo, ancora da implementare.
