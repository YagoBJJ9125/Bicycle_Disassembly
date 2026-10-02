# Continuare da un altro PC o da un'altra IA

## Copia locale e Git

Il progetto è già una cartella autonoma con repository Git. Per una copia del sorgente aggiornata, registrare le modifiche con un commit e avviare `npm run backup:source`. Si ottengono `outputs/officina-source.zip` e `outputs/officina-history.bundle`; il secondo conserva anche la cronologia. Il comando rifiuta modifiche non registrate per evitare un archivio apparentemente aggiornato.

Estrarre lo ZIP in una cartella oppure clonare il bundle offline:

```powershell
git clone officina-history.bundle Bicycle_Disassembly
cd Bicycle_Disassembly
npm ci
npm run db:init
npm run dev
```

Il sorgente è utilizzabile da qualunque editor o IA con accesso ai file. Il runtime non richiede Codex, Blender o una chiave IA. Blender serve solo per creare/esportare i modelli dettagliati.

Su un PC nuovo `npm ci` scarica le dipendenze: eseguirlo quando la rete lo permette, per esempio sulla connessione hotspot indicata dal proprietario. Su questo PC sono già installate. Non disabilitare TLS e non avviare installazioni pesanti di Blender o CAD senza necessità. Il pacchetto del sorgente esclude `node_modules`; l'avvio su una macchina completamente offline richiede dipendenze già disponibili per quel sistema operativo.

## GitHub

Destinazione prevista: repository privato dedicato, scelto dal proprietario. Il remote `sites` già presente è del provider di hosting ed è separato da GitHub. Conservare entrambi: `origin` per il codice, `sites` per l'eventuale distribuzione del sito.

Se la CLI GitHub non è autenticata, il proprietario può completare `gh auth login` sul proprio PC. Dopo la creazione del repository vuoto, collegare il remote effettivo e pubblicare il branch esistente. Esempio da adattare al repository confermato:

```powershell
git remote add origin https://github.com/<account>/<repository>.git
git push -u origin HEAD
```

Per lavorare altrove:

```powershell
git clone https://github.com/<account>/<repository>.git
cd <repository>
npm ci
npm run db:init
npm run dev
```

La visibilità privata richiede accesso esplicito per una nuova IA o un nuovo collaboratore. Il workflow `.github/workflows/verify.yml` controlla database locale, catalogo, tipi e build. Non è un deployment e non richiede segreti.

## Cosa non viaggia con il codice

Il sito online conserva catalogo aggiunto, dossier, foto e GLB in D1/R2. Non sono inclusi nel repository, nello ZIP o nel bundle. Il JSON esportato dalla libreria conserva solo il catalogo e gli ID degli asset: per un backup dei dati bisogna conservare anche i file originali o scaricare gli asset nel contesto autorizzato, oltre ai dossier. Un clone locale non legge il database online e non acquisisce i diritti sul sito privato.

I `.blend` creati successivamente devono essere conservati nella cartella `models` o in un archivio sorgenti documentato, non soltanto esportati nel sito. Le copie di recupero Blender sono ignorate da Git. Non inserire credenziali in file versionati; `.env*`, cache e storage locale sono esclusi.
