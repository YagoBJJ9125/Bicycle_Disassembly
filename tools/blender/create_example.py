"""Create an illustrative fastener assembly for testing the Blender pipeline.

Run in a fresh background Blender process. This is not an OEM bicycle part,
an ISO-certified fastener, or a manufacturing model.
"""
import json
import math
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'models' / 'fastener-example-v1'
if bpy.data.filepath:
    raise RuntimeError('Eseguire in un processo Blender nuovo, senza aprire un file esistente.')
if (DEST / 'source' / 'assembly.blend').exists():
    raise RuntimeError('Esempio gia presente: aprire il sorgente o creare una nuova versione.')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1.0
collection = bpy.data.collections.new('OFFICINA_EXPORT')
bpy.context.scene.collection.children.link(collection)
material = bpy.data.materials.new('Steel metallic roughness')
material.use_nodes = True
shader = material.node_tree.nodes.get('Principled BSDF')
shader.inputs['Base Color'].default_value = (0.42, 0.47, 0.52, 1)
shader.inputs['Metallic'].default_value = 0.9
shader.inputs['Roughness'].default_value = 0.26


def move_to_export(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def cylinder(radius, depth, z, vertices=128):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=(0, 0, z))
    return move_to_export(bpy.context.object)


def bevel(obj, width):
    modifier = obj.modifiers.new('Machined edge illustration', 'BEVEL')
    modifier.width = width
    modifier.segments = 4


def combine(objects, name):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = name
    return obj


def ring(name, outer, inner, height, z, segments=192):
    vertices, faces = [], []
    for radius, level in [(outer, -height/2), (inner, -height/2), (outer, height/2), (inner, height/2)]:
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            vertices.append((radius * math.cos(angle), radius * math.sin(angle), z + level))
    for i in range(segments):
        j = (i + 1) % segments
        faces.extend([(i, j, j+segments, i+segments),
                      (i+2*segments, i+3*segments, j+3*segments, j+2*segments),
                      (i, i+2*segments, j+2*segments, j),
                      (i+segments, j+segments, j+3*segments, i+3*segments)])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    mesh.materials.append(material)
    bevel(obj, 0.00012)
    return obj


# External helical thread, with an intentionally illustrative triangular profile.
vertices, faces = [], []
turns, steps_per_turn, pitch = 21, 128, 0.001
for i in range(turns * steps_per_turn + 1):
    angle = 2 * math.pi * i / steps_per_turn
    z = 0.003 + pitch * i / steps_per_turn
    for radius, offset in [(0.00245, -pitch*0.42), (0.003, 0), (0.00245, pitch*0.42)]:
        vertices.append((radius*math.cos(angle), radius*math.sin(angle), z+offset))
    if i:
        for k in range(3):
            a, b = (i-1)*3+k, (i-1)*3+(k+1)%3
            faces.append((a, b, b+3, a+3))
faces.extend([(2, 1, 0), (len(vertices)-3, len(vertices)-2, len(vertices)-1)])
thread_mesh = bpy.data.meshes.new('Illustrative helical thread')
thread_mesh.from_pydata(vertices, [], faces)
thread_mesh.update()
thread = bpy.data.objects.new('Thread geometry', thread_mesh)
collection.objects.link(thread)
thread_mesh.materials.append(material)
head = cylinder(0.005/math.cos(math.pi/6), 0.004, -0.002, vertices=6)
bevel(head, 0.0003)
bolt = combine([head, cylinder(0.00245, 0.026, 0.013), thread], 'example-bolt')
washer = ring('example-washer', 0.006, 0.0032, 0.001, 0.0195)
nut = cylinder(0.005/math.cos(math.pi/6), 0.005, 0.0225, vertices=6)
hole = cylinder(0.0032, 0.010, 0.0225)
boolean = nut.modifiers.new('Through hole; internal thread omitted', 'BOOLEAN')
boolean.operation = 'DIFFERENCE'
boolean.solver = 'EXACT'
boolean.object = hole
bpy.context.view_layer.objects.active = nut
bpy.ops.object.modifier_apply(modifier=boolean.name)
bpy.data.objects.remove(hole, do_unlink=True)
nut.name = 'example-nut'
bevel(nut, 0.0002)

parts = []
for identifier, name, description, deps, explode in [
    ('example-bolt', 'Vite illustrativa', 'Testa esagonale, gambo e filetto elicoidale esterno. Dimensioni progettate per il test, senza attribuzione a una bicicletta reale.', ['example-washer'], [-0.018, 0, 0]),
    ('example-washer', 'Rondella illustrativa', 'Anello con foro passante e bordi smussati, rappresentato con una vera geometria anulare.', ['example-nut'], [0.015, 0.007, 0]),
    ('example-nut', 'Dado illustrativo', 'Esagono con foro passante. Il filetto interno e le tolleranze di accoppiamento non sono modellati.', [], [0, 0.018, 0]),
]:
    parts.append({'id': identifier, 'meshName': identifier, 'name': name, 'group': 'Minuteria di esempio',
                  'description': description, 'procedureId': 'example-disassembly', 'dependsOn': deps,
                  'evidence': 'indicative', 'serviceability': 'serviceable', 'explode': explode,
                  'geometry': {'kind': 'cylinder', 'position': [0, 0, 0], 'size': [0.003, 0.026, 0], 'color': '#8c99a6'}})
bundle = {'schemaVersion': 1, 'bikes': [], 'structures': [{
    'id': 'fastener-example-v1', 'name': 'Test Blender: vite, rondella e dado', 'version': 1,
    'kind': 'didactic',
    'standards': {'purpose': 'export-test', 'brand': 'none', 'diameter': 'illustrative-6mm',
                  'pitch': 'illustrative-1mm', 'internalThread': 'not-modeled'},
    'coverage': 'Tre componenti illustrativi per collaudo informatico. Nessuna attribuzione OEM, certificazione ISO o idoneita produttiva. Filetto interno del dado e tolleranze assenti. Non e una bicicletta.',
    'parts': parts,
    'procedures': [{'id': 'example-disassembly', 'title': 'Separazione del gruppo illustrativo',
                    'steps': ['Nel banco isolare il dado, poi la rondella e infine la vite. Questa sequenza rappresenta il test e richiede verifica sul componente reale.'],
                    'tools': [{'name': 'Chiave per esagono del modello', 'size': '10 mm progettati per questo esempio; misurare il componente reale', 'certainty': 'indicative'}],
                    'warnings': ['Modello dimostrativo senza filetto interno del dado. Non usare come manuale di una bici reale.'], 'sources': []}],
}]}
(DEST / 'source').mkdir(parents=True, exist_ok=True)
(DEST / 'web').mkdir(exist_ok=True)
(DEST / 'catalog.json').write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(DEST / 'source' / 'assembly.blend'))
print('Sorgente illustrativo creato:', DEST)
