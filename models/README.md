# Libreria dei sorgenti 3D

Non sono ancora presenti modelli Blender reali. Organizzare le nuove strutture così:

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
