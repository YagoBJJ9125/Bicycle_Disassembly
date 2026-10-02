from pathlib import Path
import sys
import bpy
from mathutils import Vector

root=Path(__file__).resolve().parents[2]
model=Path(bpy.data.filepath).parents[1]
view='whole'
if '--view' in sys.argv:view=sys.argv[sys.argv.index('--view')+1]
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1300;scene.render.resolution_y=850;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.35,.4,.44,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.001))
floor=bpy.context.object;material=bpy.data.materials.new('Floor');material.use_nodes=True
material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.15,.18,.21,1)
floor.data.materials.append(material)
for pos,power,size in [((2,-3,4),500,4),((-3,1,3),400,3),((0,3,2),300,2)]:
    light=bpy.data.lights.new('Studio panel','AREA');light.energy=power;light.size=size
    obj=bpy.data.objects.new(light.name,light);scene.collection.objects.link(obj);obj.location=pos
    obj.rotation_euler=(Vector((0,0,.5))-obj.location).to_track_quat('-Z','Y').to_euler()
camdata=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camdata);scene.collection.objects.link(cam)
cam.location=(1.3,-3.0,1.55);cam.rotation_euler=(Vector((.1,0,.53))-cam.location).to_track_quat('-Z','Y').to_euler()
camdata.lens=52;scene.camera=cam;scene.render.image_settings.file_format='PNG'
details={'chainring':((.22,-.59,.47),(0,-.047,.285),70),'rear-drive':((-.26,-.44,.47),(-.43,-.047,.347),70),'routing':((.20,1.50,1.15),(.03,0,.87),65)}
if view in details:
    position,target,lens=details[view];cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camdata.lens=lens
    scene.render.resolution_x=1100;scene.render.resolution_y=800
scene.render.filepath=str(model/('preview.png' if view=='whole' else 'detail-'+view+'.png'));bpy.ops.render.render(write_still=True)
