"""Original metric teaching geometries; not manufacturing tolerances."""
import math
import bpy
import bmesh
from mathutils import Vector,Matrix

TAU=math.tau
COLLECTION=None
MATERIALS={}

def setup(collection):
    global COLLECTION,MATERIALS
    COLLECTION=collection
    MATERIALS={m.name:m for m in bpy.data.materials}

def xyz(p):return Vector((p[0],-p[2],p[1]))

def finish(obj,mat='alloy'):
    for c in list(obj.users_collection):c.objects.unlink(obj)
    COLLECTION.objects.link(obj)
    if not obj.data.materials:obj.data.materials.append(MATERIALS[mat])
    return obj

def mesh(vertices,faces,mat='alloy'):
    data=bpy.data.meshes.new('Metric detail');data.from_pydata([xyz(v) for v in vertices],[],faces);data.update()
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    obj=bpy.data.objects.new('detail',data);COLLECTION.objects.link(obj);data.materials.append(MATERIALS[mat]);return obj

def cyl(p,r,h,axis=(0,0,1),mat='alloy',segments=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments,radius=r,depth=h,location=xyz(p))
    obj=finish(bpy.context.object,mat)
    obj.rotation_euler=Vector((0,0,1)).rotation_difference(xyz(axis).normalized()).to_euler()
    return obj

def bar(a,b,r,mat='alloy'):
    a,b=Vector(a),Vector(b);return cyl((a+b)/2,r,(b-a).length,b-a,mat)

def ring(p,outer,inner,h,mat='alloy',segments=64):
    vertices=[];faces=[]
    for z,r in [(-h/2,outer),(h/2,outer),(h/2,inner),(-h/2,inner)]:
        vertices.extend([(p[0]+r*math.cos(i*TAU/segments),p[1]+r*math.sin(i*TAU/segments),p[2]+z) for i in range(segments)])
    for j in range(4):
        for i in range(segments):
            q=(i+1)%segments;k=(j+1)%4
            faces.append((j*segments+i,j*segments+q,k*segments+q,k*segments+i))
    return mesh(vertices,faces,mat)

def tube(a,b,outer,inner,mat='frame'):
    a,b=Vector(a),Vector(b);obj=ring((0,0,0),outer,inner,(b-a).length,mat)
    obj.rotation_euler=xyz((0,0,1)).rotation_difference(xyz(b-a).normalized()).to_euler();obj.location=xyz((a+b)/2);return obj

def lathe(center,profile,segments=64,mat='alloy'):
    vertices=[];faces=[]
    for radius,z in profile:
        vertices.extend([(center[0]+radius*math.cos(i*TAU/segments),center[1]+radius*math.sin(i*TAU/segments),center[2]+z) for i in range(segments)])
    for j in range(len(profile)):
        k=(j+1)%len(profile)
        for i in range(segments):
            q=(i+1)%segments;faces.append((j*segments+i,j*segments+q,k*segments+q,k*segments+i))
    return mesh(vertices,faces,mat)

def extrude(points,center=(0,0,0),h=.003,mat='alloy'):
    n=len(points);vertices=[(center[0]+x,center[1]+y,center[2]+z) for z in [-h/2,h/2] for x,y in points]
    faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]
    faces.extend([(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])
    return mesh(vertices,faces,mat)

def boolean(obj,cutter):
    bpy.context.view_layer.objects.active=obj
    mod=obj.modifiers.new('Functional opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
    return obj

def bevel(obj,width=.0003,segments=2):
    mod=obj.modifiers.new('Machined edge','BEVEL');mod.width=width;mod.segments=segments
    mod.limit_method='ANGLE';mod.angle_limit=math.radians(35)
    return obj

def bake(obj):
    bpy.context.view_layer.objects.active=obj
    for mod in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj

def merge(objects):
    if len(objects)==1:return objects[0]
    for obj in objects:bake(obj)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();return bpy.context.object

def path(points,radius,mat='dark',smooth=True):
    # Local handles prevent the AUTO overshoot that lifted the old cable off the frame.
    curve=bpy.data.curves.new('Supported cable','CURVE');curve.dimensions='3D';curve.resolution_u=10
    curve.bevel_depth=radius;curve.bevel_resolution=3;curve.use_fill_caps=True
    spline=curve.splines.new('BEZIER');spline.bezier_points.add(len(points)-1)
    for i,(handle,point) in enumerate(zip(spline.bezier_points,points)):
        handle.co=xyz(point);handle.handle_left_type='FREE';handle.handle_right_type='FREE'
        prev=xyz(points[max(0,i-1)]);nxt=xyz(points[min(len(points)-1,i+1)])
        tangent=(nxt-prev).normalized()
        handle.handle_left=handle.co-tangent*(handle.co-prev).length*.24
        handle.handle_right=handle.co+tangent*(nxt-handle.co).length*.24
    obj=bpy.data.objects.new('cable',curve);COLLECTION.objects.link(obj);curve.materials.append(MATERIALS[mat])
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.object.convert(target='MESH');return bpy.context.object

def hollow_path(points,outer=.0025,inner=.0020,mat='dark'):
    points=[Vector(p) for p in points];samples=[]
    for i in range(len(points)-1):
        p,q=points[i:i+2];length=(q-p).length
        a=p+(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized()*length*.24
        b=q-(points[min(i+2,len(points)-1)]-points[i]).normalized()*length*.24
        for j in range(12):
            t=j/12;s=1-t;samples.append(p*s**3+a*(3*s*s*t)+b*(3*s*t*t)+q*t**3)
    samples.append(points[-1]);vertices=[];faces=[];sides=24
    for i,p in enumerate(samples):
        tangent=(samples[min(i+1,len(samples)-1)]-samples[max(0,i-1)]).normalized()
        reference=Vector((0,0,1)) if abs(tangent.z)<.95 else Vector((0,1,0))
        u=tangent.cross(reference).normalized();v=tangent.cross(u).normalized()
        for radius in [outer,inner]:
            for k in range(sides):
                pos=p+radius*(u*math.cos(k*TAU/sides)+v*math.sin(k*TAU/sides));vertices.append(tuple(pos))
    for i in range(len(samples)-1):
        for shell in range(2):
            for k in range(sides):
                q=(k+1)%sides;a=i*sides*2+shell*sides;b=(i+1)*sides*2+shell*sides
                face=(a+k,a+q,b+q,b+k);faces.append(face if not shell else tuple(reversed(face)))
    for i in [0,len(samples)-1]:
        base=i*sides*2
        for k in range(sides):
            q=(k+1)%sides;faces.append((base+k,base+sides+k,base+sides+q,base+q))
    return mesh(vertices,faces,mat)

def sprocket(center,teeth,phase,inner,h,roller_radius=.00385,mat='alloy'):
    pitch=.0127;radius=pitch/(2*math.sin(math.pi/teeth));seat=roller_radius+.00012
    vertices=[];faces=[];samples=teeth*32;outer=[]
    half=math.pi/teeth;seat_angle=math.asin(seat/radius)
    for i in range(samples):
        angle=phase+i*TAU/samples;local=((angle-phase+half)%(2*half))-half;absolute=abs(local)
        # Roller seats are circular clearances, not involute spur-gear teeth.
        if absolute<=seat_angle:
            r=radius*math.cos(local)-math.sqrt(max(0,seat*seat-radius*radius*math.sin(local)**2))
        else:
            join=radius*math.cos(seat_angle);tip=radius+.0022
            t=(absolute-seat_angle)/(half-seat_angle)
            r=join+(tip-join)*min(1,t/.8)
        outer.append((r*math.cos(angle),r*math.sin(angle)))
    for z in [-h/2,h/2]:
        for points in [outer,[(inner*math.cos(phase+i*TAU/samples),inner*math.sin(phase+i*TAU/samples)) for i in range(samples)]]:
            vertices.extend([(center[0]+x,center[1]+y,center[2]+z) for x,y in points])
    for i in range(samples):
        j=(i+1)%samples;n=samples
        faces.extend([(i,j,2*n+j,2*n+i),(n+i,3*n+i,3*n+j,n+j),(i,n+i,n+j,j),(2*n+i,2*n+j,3*n+j,3*n+i)])
    return mesh(vertices,faces,mat)

def capsule(length,r,h,mat='alloy',waist=None):
    points=[];n=20
    for i in range(n+1):
        a=-math.pi/2+i*math.pi/n;points.append((length/2+r*math.cos(a),r*math.sin(a)))
    if waist:points.append((0,waist))
    for i in range(n+1):
        a=math.pi/2+i*math.pi/n;points.append((-length/2+r*math.cos(a),r*math.sin(a)))
    if waist:points.append((0,-waist))
    return extrude(points,h=h,mat=mat)

def hex_points(r):return [(r*math.cos(i*TAU/6),r*math.sin(i*TAU/6)) for i in range(6)]

def bolt(center,axis=(0,0,1),radius=.0025,length=.016,pitch=.0008):
    # A continuous helical profile; all dimensions remain illustrative.
    turns=length/pitch;rows=math.ceil(turns*10);segments=24;vertices=[];faces=[]
    for j in range(rows+1):
        z=-length/2+length*j/rows
        for i in range(segments):
            a=i*TAU/segments;f=((z/pitch-a/TAU)%1);peak=max(0,1-abs(f-.5)/.34)
            r=radius-.00035+peak*.00035;vertices.append((r*math.cos(a),r*math.sin(a),z))
    for j in range(rows):
        for i in range(segments):
            q=(i+1)%segments;faces.append((j*segments+i,j*segments+q,(j+1)*segments+q,(j+1)*segments+i))
    faces.extend([tuple(reversed(range(segments))),tuple(range(rows*segments,(rows+1)*segments))])
    shank=mesh(vertices,faces)
    head=cyl((0,0,length/2+.0017),radius*1.65,.0035)
    boolean(head,extrude(hex_points(radius*.92),center=(0,0,length/2+.0033),h=.003))
    obj=merge([shank,bevel(head,.0002)])
    obj.rotation_euler=xyz((0,0,1)).rotation_difference(xyz(axis).normalized()).to_euler();obj.location=xyz(center)
    return obj

def nut(center,radius=.004,inner=.0026,h=.004):
    obj=extrude(hex_points(radius),center=center,h=h)
    boolean(obj,cyl(center,inner,h*3));return bevel(obj,.00025)

def instance(template,center,angle=0):
    obj=bpy.data.objects.new('detail',template.data);COLLECTION.objects.link(obj)
    obj.matrix_world=Matrix.Translation(xyz(center))@Matrix.Rotation(-angle,4,'Y')@template.matrix_world
    return obj
