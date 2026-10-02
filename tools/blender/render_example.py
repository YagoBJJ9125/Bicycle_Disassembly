"""Render the exported example as an exploded preview without saving the source."""
from pathlib import Path

import bpy
from mathutils import Vector

root = Path(__file__).resolve().parents[2]
scene = bpy.context.scene
if set(o.name for o in bpy.data.collections['OFFICINA_EXPORT'].all_objects) != {'example-bolt', 'example-washer', 'example-nut'}:
    raise RuntimeError('Aprire il sorgente fastener-example-v1 prima del render.')
bpy.data.objects['example-bolt'].location.x -= 0.017
bpy.data.objects['example-washer'].location.x += 0.005
bpy.data.objects['example-washer'].location.z += 0.012
bpy.data.objects['example-nut'].location.x += 0.025
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.view_settings.exposure = -2
scene.render.resolution_x = 1100
scene.render.resolution_y = 760
scene.render.resolution_percentage = 100
scene.world = bpy.data.worlds.new('Preview world')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.32, 0.36, 0.4, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.5
bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, -0.007))
floor = bpy.context.object
floor_material = bpy.data.materials.new('Preview floor')
floor_material.diffuse_color = (0.18, 0.22, 0.24, 1)
floor.data.materials.append(floor_material)
for position, power, size in [((0.03, -0.05, 0.09), 2, 0.06), ((-0.04, 0.02, 0.06), 1.5, 0.05), ((0.04, 0.06, 0.04), 1, 0.04)]:
    light = bpy.data.lights.new('Studio panel', 'AREA')
    light.energy = power
    light.shape = 'DISK'
    light.size = size
    obj = bpy.data.objects.new(light.name, light)
    scene.collection.objects.link(obj)
    obj.location = position
    obj.rotation_euler = (Vector((0, 0, 0.01)) - obj.location).to_track_quat('-Z', 'Y').to_euler()
camera_data = bpy.data.cameras.new('Preview camera')
camera = bpy.data.objects.new('Preview camera', camera_data)
scene.collection.objects.link(camera)
camera.location = (0.064, -0.10, 0.075)
camera.rotation_euler = (Vector((0.005, 0, 0.014)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera_data.lens = 58
camera_data.clip_start = 0.001
scene.camera = camera
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(root / 'models/fastener-example-v1/preview.png')
bpy.ops.render.render(write_still=True)
