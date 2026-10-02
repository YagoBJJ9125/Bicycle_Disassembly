# Elops Speed 500: esempio di studio della bici intera

Ricostruzione originale per testare la piattaforma, non modello CAD del produttore. Il sorgente è generato da `tools/blender/create_city_bike.py`; sono conservati `.blend`, GLB, report e dossier. La copia web incorporata è `public/models/elops-study-v1.glb`, registrata in `data/elops-study-v1.json`.

## Fonti

- [Decathlon: Speed 500, ID 8749510](https://www.decathlon.it/p/bici-citta-single-speed-500-grigia/306292/c383m8749510): allestimento in acciaio, trasmissione 44×18, ruote 622×17C, pneumatici 700×32, interassi mozzi 100/120 mm, attacco 60 mm, manubrio 520 mm, reggisella 25,4 mm, pedivelle 170 mm, perno movimento THUN TOPAZ 119 mm. Quote non pubblicate non sono dedotte come certe.
- [Ricambio serie sterzo Speed 500](https://compatible-spare-parts.decathlon.com/it-IT/categories/6/products/8563558/spare-part-nature/12066): riferimento Ahead EC34 per la variante indicata nel portale; non prova l'inventario interno di ogni anno o allestimento.
- Le procedure collegano articoli Park Tool per metodi generali; questi non certificano la misura dell'utensile sul componente Decathlon.

## Cosa rappresenta

Bici intera con 704 mesh nominate: telaio e forcella, ruote, camere e valvole, 64 raggi e relativi nippli, mozzi con interni illustrativi, serie sterzo Ahead, cockpit, sella, trasmissione, catena con perni/rulli/piastrine, pedali, pinze, pattini, cavi e accessori. Le geometrie includono veri fori, sezioni dei cerchi, denti della corona e del pignone, tubi formati e catena distribuita attorno alla trasmissione. I tubi saldati restano un solo componente; i gruppi chiusi sono indicati come tali.

## Limiti

- Forma del telaio, tolleranze, filetto dei fissaggi e dettagli degli utensili non sono quotati OEM.
- Numero e costruzione di sfere, raggi, maglie, fissaggi della corona e interni del pedale sono illustrativi. Non attribuire questa distinta alla bici reale.
- Meccanismo della ruota libera, interno della cartuccia movimento, leveraggi delle leve, luci e campanello non sono scomposti integralmente.
- Alcune parti sono rese singolarmente per comprendere la funzione; questo non significa che siano ricambi o che si possano riutilizzare dopo l'apertura.
- Le misure degli utensili sono indicative o da verificare. La fonte conferma dimensioni di alcuni componenti, non tutte le chiavi.

Il modello è `reference`, non `verified`. Gli standard interni `unknown` impediscono di confermare un riutilizzo esatto per un'altra bici. È pronto per esplorare e testare il programma, ma la completezza OEM di ogni singolo pezzo resta da documentare.

Per rigenerare in una nuova versione: creare il `.blend`, esportare con `tools/blender/export_officina.py`, controllare con `npm run check:model`, poi eseguire `node scripts/prepare-city-example.mjs` per sincronizzare copia pubblica e dossier incorporato. Il dossier sorgente contiene `modelPath`, riservato agli asset distribuiti con il codice; per importare un GLB esterno usare il normale caricamento con `assetId`.
