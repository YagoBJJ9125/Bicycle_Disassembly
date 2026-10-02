# Vite, rondella e dado: esempio di collaudo

Modello originale generato da `tools/blender/create_example.py`, per verificare il flusso Blender → GLB → selezione dei pezzi. Tre oggetti indipendenti, unità metriche, filetto esterno geometrico, rondella con foro reale e dado esagonale forato.

È un esempio illustrativo, non un ricambio di una bici o una geometria certificata secondo una norma. Diametro esterno progettato circa 6 mm, passo illustrativo 1 mm, esagoni progettati da 10 mm. Il dado ha foro liscio: **il filetto interno e le tolleranze non sono modellati**. Le superfici della vite sono unite nello stesso oggetto ma non costituiscono un solido CAD validato per produzione.

Le misure dichiarano il disegno di questo esempio e non sono dedotte da foto o manuali. Le schede restano `indicative`, la struttura `didactic`; il dossier non contiene una scheda bicicletta e non va presentato come restauro reale. Può essere usato nel repository e nella piattaforma del progetto.

Per riprodurre: avviare Blender in un nuovo processo background con `--python tools/blender/create_example.py`; esportare con `export_officina.py` secondo `docs/BLENDER_WORKFLOW.md`. Il sorgente già presente non viene sovrascritto dallo script di creazione. Sono conservati `.blend`, `.glb`, dossier e report per qualsiasi IA o modellatore che riprenda il progetto.
