"""Export separately selectable parts from a saved Blender scene.

Run with Blender, not system Python. See docs/BLENDER_WORKFLOW.md.
The source .blend is never saved or overwritten by this script.
"""
import argparse
import json
import math
from pathlib import Path
import struct
import sys

import bpy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', required=True)
    parser.add_argument('--structure', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--collection', default='OFFICINA_EXPORT')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    bundle = json.loads(Path(args.catalog).read_text(encoding='utf-8-sig'))
    structure = next((s for s in bundle.get('structures', []) if s['id'] == args.structure), None)
    if not structure:
        raise ValueError('Struttura non trovata nel dossier.')
    names = [p.get('meshName') for p in structure['parts']]
    if not names or not all(names) or len(names) != len(set(names)):
        raise ValueError('Ogni pezzo richiede un meshName presente e univoco.')
    collection = bpy.data.collections.get(args.collection)
    if not collection:
        raise ValueError('Creare la collection ' + args.collection)
    meshes = {o.name: o for o in collection.all_objects if o.type == 'MESH'}
    if set(names) != set(meshes):
        raise ValueError('Mesh mancanti: ' + str(set(names) - set(meshes)) +
                         '; mesh non assegnate: ' + str(set(meshes) - set(names)))
    if any(o.type not in {'MESH', 'EMPTY'} for o in collection.all_objects):
        raise ValueError('La collection di esportazione deve contenere solo mesh e empty di organizzazione.')
    if not math.isclose(bpy.context.scene.unit_settings.scale_length, 1.0):
        raise ValueError('Impostare scala unita 1.0: una unita Blender corrisponde a un metro.')
    if bpy.context.mode != 'OBJECT':
        raise ValueError('Passare a Object Mode prima di esportare.')
    output = Path(args.output).resolve()
    if output.suffix.lower() != '.glb':
        raise ValueError('Il file di destinazione deve terminare in .glb.')
    report_path = output.with_suffix('.report.json')
    if not args.overwrite and (output.exists() or report_path.exists()):
        raise ValueError('Output gia presente: usare una nuova versione oppure --overwrite.')

    stats = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for name in names:
        obj = meshes[name]
        if obj.children:
            raise ValueError(name + ': i pezzi devono essere mesh foglia, senza oggetti figli.')
        if obj.name not in bpy.context.view_layer.objects or not obj.visible_get():
            raise ValueError(name + ': rendere visibile la collection nel view layer attivo.')
        matrix = obj.matrix_world
        if matrix.determinant() <= 0 or not all(math.isfinite(v) for row in matrix for v in row):
            raise ValueError(name + ': correggere trasformazioni specchiate, nulle o non finite.')
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            if not mesh.loop_triangles:
                raise ValueError(name + ': nessuna superficie da esportare.')
            stats.append({'meshName': name, 'verticesBeforeGltfSplits': len(mesh.vertices),
                          'triangles': len(mesh.loop_triangles)})
        finally:
            evaluated.to_mesh_clear()

    # Filter optional flags against the installed Blender exporter version.
    options = {
        'filepath': str(output), 'export_format': 'GLB', 'use_selection': True,
        'export_apply': True, 'export_extras': True, 'export_yup': True,
        'export_materials': 'EXPORT', 'export_animations': False,
        'export_cameras': False, 'export_lights': False,
        'export_draco_mesh_compression_enable': False, 'export_use_gltfpack': False,
        'export_keep_originals': False, 'export_image_format': 'AUTO',
    }
    supported = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
    required = {'filepath', 'export_format', 'use_selection', 'export_apply', 'export_yup'}
    if not required.issubset(supported):
        raise RuntimeError('Esportatore glTF incompatibile: verificare la versione di Blender.')
    selected = list(bpy.context.selected_objects)
    active = bpy.context.view_layer.objects.active
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in meshes.values():
            obj.select_set(True)
        bpy.context.view_layer.objects.active = meshes[names[0]]
        result = bpy.ops.export_scene.gltf(**{k: v for k, v in options.items() if k in supported})
        if 'FINISHED' not in result:
            raise RuntimeError('Esportazione non completata.')
    finally:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = active

    data = output.read_bytes()
    if len(data) > 25_000_000:
        raise ValueError('GLB oltre 25 MB: ridurre geometrie/texture della copia web e riesportare.')
    if len(data) < 20 or struct.unpack_from('<III', data) != (0x46546C67, 2, len(data)):
        raise ValueError('GLB non valido.')
    length, chunk_type = struct.unpack_from('<II', data, 12)
    if chunk_type != 0x4E4F534A:
        raise ValueError('Primo chunk GLB non JSON.')
    doc = json.loads(data[20:20 + length].decode('utf-8'))
    exported = [n.get('name') for n in doc.get('nodes', []) if 'mesh' in n]
    if len(exported) != len(names) or set(exported) != set(names):
        raise ValueError('Nomi GLB cambiati durante esportazione: controllare oggetti e gerarchie.')
    if doc.get('extensionsRequired') or doc.get('extensions'):
        raise ValueError('Il viewer attuale richiede GLB senza estensioni obbligatorie o di scena.')
    if any('uri' in item for item in doc.get('buffers', []) + doc.get('images', [])):
        raise ValueError('Il GLB contiene risorse esterne.')
    report_path.write_text(json.dumps({
        'blenderVersion': bpy.app.version_string,
        'sourceBlend': Path(bpy.data.filepath).name,
        'structureId': structure['id'], 'units': 'meters',
        'glbBytes': len(data), 'meshCount': len(exported),
        'totalTrianglesBeforeExport': sum(p['triangles'] for p in stats),
        'parts': stats,
        'mechanicalVerification': 'Non certificata da questo script; confrontare con le fonti.',
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print('GLB esportato:', output)
    print('Report:', report_path)


if __name__ == '__main__':
    main()
