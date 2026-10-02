# Libreria dei sorgenti 3D

La bici attiva nel banco è `elops-study-v2`, riferimento con 718 elementi, catena/dentatura e fissaggi migliorati; conserva sorgente Blender, report, vincoli geometrici e render ravvicinati. `elops-study-v1` resta la base originale archiviata con 704 elementi. È presente anche `fastener-example-v1`, esempio originale di tre pezzi per collaudare il flusso. Tutti hanno sorgente Blender modificabile. Non sono ancora presenti distinte complete verificate di biciclette reali. Organizzare le nuove strutture così:

```text
models/<structure-id>/
  catalog.json           dossier importabile (schemaVersion 1)
  MODEL.md               provenienza, quote, limiti, licenza, revisione
  source/assembly.blend  originale modificabile
  source/assembly.FCStd  opzionale sorgente parametrico
  web/assembly.glb       copia incorporata per la piattaforma
  web/assembly.report.json
```

Seguire `docs/BLENDER_WORKFLOW.md`. Nomi degli oggetti uguali ai `meshName` del dossier; originali e mesh esportate versionati insieme. Per file molto pesanti concordare Git LFS o un archivio asset separato e documentarne il recupero. Nessun modello generato sostituisce l'identificazione del componente reale.
