# Come avviare Officina

## Su questo PC Windows

1. Apri la cartella `C:\Users\federico.angelini\Documents\ChatGPT\Bicycle_Disassembly`.
2. Fai doppio clic su **Avvia-Officina.cmd**.
3. Attendi l'apertura del browser su **http://127.0.0.1:5173/**. Tieni aperta la finestra dell'avvio. Per fermare il programma premi `Ctrl+C` in quella finestra.

Non servono importazioni o Blender per usare l'esempio: la bici intera **Elops Speed 500 · esempio 3D** è incorporata e si apre automaticamente. Se l'applicazione è già in esecuzione, l'avvio riutilizza quella stessa istanza. Il database viene preparato senza cancellare i tuoi dati.

Se il programma è già avviato, la finestra mostra l'indirizzo e rimane aperta fino alla pressione di un tasto: puoi chiudere quella finestra senza fermare il server originale. Se il browser non si apre automaticamente, copia http://127.0.0.1:5173/ nella sua barra degli indirizzi. La finestra resta aperta anche in caso di errore, così il messaggio è leggibile.

Su un nuovo PC occorre prima installare Node.js 22.13 o successivo e scaricare/clonare il repository. L'avvio installa le dipendenze mancanti con `npm ci`, perciò la prima configurazione richiede Internet. Su questo PC sono già disponibili. Blender serve per modificare il sorgente 3D, non per ruotare e scomporre la bici nell'applicazione.

## Prova guidata

1. Trascina la bici per ruotarla; usa la rotella per avvicinarti.
2. Premi **Scomponi** o sposta il cursore **Esploso**.
3. Seleziona un pezzo nel modello o nell'elenco. Usa **Isola pezzo** e ruotalo da vicino.
4. Apri **Come ottenerlo** per procedura, dipendenze, utensili e attendibilità delle misure.
5. Per vedere un interno, filtra **Ruota anteriore** e cerca **Sfera**; per vedere una maglia cerca **Piastrina**.
6. In **Libreria** puoi passare alla precedente demo Classica o aggiungere una tua bici.

L'esempio rappresenta l'intera bicicletta con 718 elementi separati e geometrie originali Blender. La revisione 2 migliora catena, corona e pignone, fissaggi dei cavi al telaio, pinze, mozzi e sterzo. Per vedere le aggiunte cerca «Clip guaina», «Registro tensione» o «Distanziale» nell'elenco. Si basa sull'allestimento pubblico della Elops Speed 500, ma **non è una replica OEM verificata fino a ogni vite**. Percorso cavi, clip, distanziale, numero di raggi/maglie, cuscinetti e minuteria sono illustrativi. Ruota libera, cartuccia movimento, interni delle leve ed elettronica restano gruppi non completamente aperti. I limiti compaiono nelle schede e sotto il banco; leggi `models/elops-study-v2/MODEL.md`.

## Avvio manuale, anche da altri sistemi

```powershell
git clone https://github.com/YagoBJJ9125/Bicycle_Disassembly.git
cd Bicycle_Disassembly
npm ci
npm run db:init
npm run dev
```

Apri http://127.0.0.1:5173/. Il codice locale e il sito online hanno archivi distinti. GitHub conserva il codice e gli esempi incorporati; caricare codice su GitHub non avvia l'applicazione.

## Se non parte

- **node non riconosciuto:** installa Node.js, riapri la finestra e riprova.
- **Download delle dipendenze bloccato:** usa la connessione che consente il download; non disabilitare TLS.
- **Porta 5173 occupata:** se è già Officina, riapri il suo indirizzo. Se è un altro programma, chiudilo oppure chiedi di configurare una porta diversa. L'avvio non termina altri programmi.
- **Archivio non disponibile:** usa `npm run db:init`, poi riavvia. L'esempio incorporato resta disponibile anche se l'archivio non risponde.
