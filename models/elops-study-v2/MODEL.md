# Speed 500: revisione meccanica 2

Ricostruzione originale di studio per esplorare la bicicletta nell'applicazione. Non è un CAD del produttore. La base `models/elops-study-v1` rimane intatta; `tools/blender/refine_city_bike.py` e `detail_geometry.py` producono questa revisione con 718 mesh nominate. Sorgente modificabile, GLB, report e dossier sono versionati insieme. Nessun asset 3D di terzi è stato copiato.

## Miglioramenti

- Guaina posteriore cava lungo il tubo superiore, tre clip rimovibili e tre viti separate. Curve libere vicino alle leve per consentire lo sterzo. Terminali inseriti nei registri delle pinze; cavo metallico continuo dentro la guaina e scoperto al serraggio.
- Pinze collegate a corona forcella e ponticello dei foderi. Pattini orientati sulla tangente della pista dei cerchi, scanalature, portapattini, registri forati e viti con impronta.
- Corona piana 44T con cinque aperture e sedi dei fissaggi; spider integrato nella pedivella destra, bulloni e dadi separati. Pignone 18T e corpo della ruota libera concentrici al mozzo. I denti hanno sedi per i rulli, anziché un profilo da ingranaggio generico.
- Catena chiusa a passo geometrico di 12,7 mm, con 100 perni, rulli cavi, piastre interne/esterne forate e teste ribadite. Il piccolo spostamento dell'asse posteriore chiude geometricamente la catena: non è una misura ricavata dalla bici reale.
- Tubi e cannotto cavi, forcellini e flange forati, raggi con gomito nei fori delle flange. Viti con filetto esterno elicoidale e impronta esagonale incassata. Dadi con foro liscio: il filetto interno non è modellato.
- Serie sterzo orientata sul cannotto inclinato, distanziale illustrativo, tappo appoggiato all'attacco; viti del frontalino e del morsetto nelle rispettive sedi. Staffe visibili per luci e catarifrangenti, che restano gruppi chiusi.
- Superfici piane e spigoli distinti dalle superfici curve, evitando l'effetto arrotondato dei precedenti elementi.

## Fonti e ambito

- [Decathlon: Speed 500, ID 8749510](https://www.decathlon.it/p/bici-citta-single-speed-500-grigia/306292/c383m8749510): riferimento per l'allestimento pubblico 44×18, catena 1/2×1/8 e dimensioni nominali riportate nelle schede. Non fornisce quote CAD né distinta interna completa.
- [Ricambio serie sterzo Speed 500](https://compatible-spare-parts.decathlon.com/it-IT/categories/6/products/8563558/spare-part-nature/12066): compatibilità Ahead EC34 della variante indicata. Non dimostra forma delle piste, cuscinetti o altezza del distanziale.
- [Park Tool: cavi e guaine con manubrio diritto](https://www.parktool.com/en-us/blog/repair-help/brake-housing-cable-installation-upright-bars): metodo generale per curve, ingressi nei registri e sostegno sul telaio. Il percorso e le tre clip rappresentati sono una soluzione di studio; non sono stati identificati sull'esemplare Decathlon.
- [KMC: catena singlespeed S1](https://www.kmcchain.com/en/product/bicycle-chain-s1-single-speed): esempio del formato 1/2×1/8. Non attribuisce marca KMC o struttura interna S1 alla bici modellata.

## Limiti e verifica

Il dossier resta `reference`; gli standard interni `unknown` impediscono un riutilizzo esatto certificato per altre bici. Numero di raggi, maglie, sfere, fissaggi, clip e distanziale sono illustrativi. Il profilo dei denti è una costruzione geometrica coerente con i rulli, non una specifica industriale di produzione. Quote, utensili, tolleranze e interni non pubblicati devono essere confrontati con l'esemplare reale. Ruota libera, cartuccia movimento, leve, luci e campanello non sono completamente scomposti.

`assembly-constraints.json` registra passo, posizioni dei perni, fase della dentatura, linea catena, supporti guaina e punti di montaggio delle pinze. `scripts/check-city-example.mjs` carica il GLB con Three.js e verifica tutti i collegamenti catalogo/nodi, le posizioni reali dei perni e lo spessore della corona. Questo controllo informatico non certifica resistenza, tensionamento, funzionamento dei freni o tolleranze OEM. Il modello è statico: non implementa una simulazione dinamica.

## Rigenerazione

Da PowerShell nella radice del repository, con Blender portabile già recuperato:

```powershell
& '.tools/blender-4.5.14-windows-x64/blender.exe' --background models/elops-study-v1/source/assembly.blend --python-exit-code 1 --python tools/blender/refine_city_bike.py -- --overwrite
& '.tools/blender-4.5.14-windows-x64/blender.exe' --background models/elops-study-v2/source/assembly.blend --python-exit-code 1 --python tools/blender/export_officina.py -- --catalog models/elops-study-v2/catalog.json --structure elops-study-v2 --output models/elops-study-v2/web/assembly.glb --overwrite
node scripts/prepare-city-example.mjs
node scripts/check-city-example.mjs
npm run check:model -- models/elops-study-v2/web/assembly.glb models/elops-study-v2/catalog.json elops-study-v2
```

L'esportatore legge il sorgente senza salvarlo. Il GLB incorporato è `public/models/elops-study-v2.glb`; il dossier è `data/elops-study-v2.json`. Il caricamento GLB esterno nell'applicazione usa invece `assetId`, non `modelPath`. Per ulteriori revisioni conservare la storia e aggiornare insieme sorgente, dossier, copia pubblica, test e documentazione.

Per i render usare `tools/blender/render_city_bike.py` sul sorgente v2, senza salvare la scena modificata: vista intera, oppure `-- --view chainring`, `rear-drive` e `routing`. Le immagini non dimostrano l'identità meccanica degli interni.
