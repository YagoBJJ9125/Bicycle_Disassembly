"""Revision 2: connected brakes, roller seats and an exact-pitch teaching chain.

Load the version-1 .blend. It is read only; save a separate version-2 source.
Use --overwrite only while intentionally iterating this revision.
"""
import sys,math,json
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
import detail_geometry as g

DEST=ROOT/'models/elops-study-v2'
if Path(bpy.data.filepath).resolve()!=(ROOT/'models/elops-study-v1/source/assembly.blend').resolve():
    raise RuntimeError('Aprire il sorgente v1: questa revisione conserva la base originale.')
if (DEST/'source/assembly.blend').exists() and '--overwrite' not in sys.argv:
    raise RuntimeError('Revisione esistente: usare --overwrite per modificarla intenzionalmente.')
collection=bpy.data.collections['OFFICINA_EXPORT'];g.setup(collection)
bundle=json.loads((ROOT/'models/elops-study-v1/catalog.json').read_text(encoding='utf-8'))
structure=bundle['structures'][0];parts=structure['parts'];byid={p['id']:p for p in parts}
templates=[]

def put(id,obj,description=None,name=None,group='Freni',proc='brake',deps=(),service='serviceable',evidence='indicative',explode=None):
    old=bpy.data.objects.get(id)
    if old:bpy.data.objects.remove(old,do_unlink=True)
    obj.name=id;obj['part_id']=id
    if id not in byid:
        part={'id':id,'meshName':id,'name':name or id,'group':group,'procedureId':proc,'dependsOn':list(deps),'serviceability':service,'evidence':evidence,'explode':explode or [.10,.12,.32]}
        parts.append(part);byid[id]=part
    part=byid[id]
    if description:part['description']=description
    corners=[obj.matrix_world@Vector(v) for v in obj.bound_box]
    c=sum(corners,Vector())/8
    part['geometry']={'kind':'box','position':[c.x,c.z,-c.y],'size':[.01,.01,.01],'color':'#70808b'}
    return obj

pitch=.0127;zf=.047;Rf=pitch/(2*math.sin(math.pi/44));Rr=pitch/(2*math.sin(math.pi/18))
front_steps=24;rear_steps=8;straight_steps=34
fhalf=front_steps*math.pi/44;rhalf=rear_steps*math.pi/18
offset_x=Rf*math.cos(fhalf)-Rr*math.cos(math.pi-rhalf)
offset_y=Rf*math.sin(fhalf)-Rr*math.sin(math.pi-rhalf)
distance=math.sqrt((straight_steps*pitch)**2-offset_y**2)-offset_x
rear_x=-math.sqrt(distance**2-.062**2)
bb=(0,.285,0);rear=(rear_x,.347,0);front=(.62,.347,0);seat=(-.16,.825,0);ht=(.415,.88,0);hb=(.465,.735,0)
theta=math.atan2(bb[1]-rear[1],bb[0]-rear[0]);fphase=theta+fhalf;rphase=theta+math.pi-rhalf
for part in parts:
    if part['group']=='Ruota posteriore':bpy.data.objects[part['id']].location.x+=rear_x+.43

# Hollow tube ends, bottom bracket shell, brake bridge and actual wheel mounts.
frame=[g.tube(bb,seat,.016,.0128),g.tube(seat,ht,.015,.0138),g.tube(bb,hb,.021,.0198),g.ring(bb,.021,.0178,.068,mat='frame'),g.tube(hb,ht,.018,.017)]
for z in [-.055,.055]:
    frame.extend([g.tube((0,.285,z*.4),(rear_x,.347,z),.010,.0088),g.tube(seat,(rear_x,.347,z),.008,.0068)])
    dropout=g.extrude([(-.016,-.015),(.019,-.012),(.013,.021),(-.012,.018)],center=(rear_x,.347,z),h=.005,mat='frame')
    g.boolean(dropout,g.cyl((rear_x,.347,z),.0053,.025));frame.append(g.bevel(dropout,.001))
rear_pivot_x=rear_x+(.675-.347)/(.825-.347)*(-.16-rear_x)
frame.append(g.bar((rear_pivot_x,.675,-.020),(rear_pivot_x,.675,.020),.007,'frame'))
put('frame',g.merge(frame),'Telaio saldato con tubi cavi, scatola movimento aperta, forcellini forati e ponticello freno collegato ai foderi. Quote di studio, non tolleranze OEM.')
head_axis=(Vector(ht)-Vector(hb)).normalized()
def head_at(y):return Vector((ht[0]-(y-ht[1])*.05/.145,y,0))
fork=[g.tube(head_at(.705),head_at(.967),.0143,.0128),g.bar((.479,.705,-.035),(.479,.705,.035),.015,'frame')]
for z in [-.050,.050]:
    fork.append(g.path([(.479,.705,z*.7),(.54,.55,z),(.62,.347,z)],.013,'frame'))
    end=g.extrude([(-.013,-.015),(.016,-.015),(.012,.023),(-.013,.019)],center=(.62,.347,z),h=.005,mat='frame')
    g.boolean(end,g.cyl((.62,.347,z),.0053,.025));fork.append(g.bevel(end,.001))
put('fork',g.merge(fork),'Forcella con cannotto cavo, corona collegata alle gambe e forcellini forati. Il perno della pinza attraversa la corona; quote illustrative.')

# Five openings and bolt bores replace cylindrical spokes in the chainring.
chainring=g.sprocket((0,.285,zf),44,fphase,.024,.0026)
for i in range(5):
    angle=i*math.tau/5
    points=[]
    for j in range(17):
        a=angle+math.radians(14+44*j/16);points.append((.076*math.cos(a),.076*math.sin(a)))
    for j in range(17):
        a=angle+math.radians(58-44*j/16);points.append((.032*math.cos(a),.032*math.sin(a)))
    g.boolean(chainring,g.extrude(points,center=(0,.285,zf),h=.025))
    g.boolean(chainring,g.cyl((.055*math.cos(angle),.285+.055*math.sin(angle),zf),.0041,.025))
put('chainring',g.bevel(chainring,.00015),'Corona piatta 44 denti con cinque finestre, fori di fissaggio e sedi circolari per i rulli. Cerchio primitivo calcolato dal passo 12,7 mm. Disegno a cinque attacchi illustrativo; non profilo di fabbricazione OEM.')

for side,label in [(-1,'left'),(1,'right')]:
    z=side*.068;end=Vector((side*.13,.285+side*.11));direction=end-Vector(bb[:2]);angle=math.atan2(direction.y,direction.x)
    body=g.capsule(direction.length,.014,.016)
    g.boolean(body,g.cyl((-direction.length/2,0,0),.007,.06));g.boolean(body,g.cyl((direction.length/2,0,0),.0072,.06))
    body.rotation_euler.y=-angle;body.location=g.xyz(((end.x)/2,(.285+end.y)/2,z))
    members=[g.bevel(body,.0012)]
    if side==1:
        # The spider belongs to the crank, not to the removable chainring.
        members.append(g.ring((0,.285,.055),.023,.007,.020))
        for i in range(5):
            a=i*math.tau/5;tip=(.055*math.cos(a),.285+.055*math.sin(a),zf-.0048)
            arm=g.capsule(.04,.006,.007);arm.rotation_euler.y=-a
            arm.location=g.xyz((.035*math.cos(a),.285+.035*math.sin(a),zf-.0048))
            g.bake(g.bevel(arm,.0006));members.extend([arm,g.ring(tip,.008,.0041,.007)])
    put('crank-'+label,g.merge(members),'Pedivella sagomata con sedi del perno e del pedale; nominale 170 mm. La destra comprende il ragno di sostegno della corona. Dettagli e impronte illustrative.')
    put('crank-bolt-'+label,g.bolt((0,.285,z+side*.004),(0,0,side),.0038,.017,.001),'Vite con filetto geometrico e impronta esagonale incassata. Profilo utensile indicativo da confrontare col ricambio.')
for i in range(5):
    a=i*math.tau/5;c=(.055*math.cos(a),.285+.055*math.sin(a),zf-.0047)
    put('chainring-fixing-'+str(i),g.bolt(c,radius=.0038,length=.012,pitch=.001),'Fissaggio della corona con impronta e filetto geometrici. Cinque fissaggi e loro quote sono illustrativi, non identificazione del componente OEM.')
    put('chainring-nut-'+str(i),g.nut((c[0],c[1],zf-.008),.006,.0039,.003),'Controparte del fissaggio illustrativo della corona.',name='Dado fissaggio corona',group='Trasmissione',proc='crank',deps=['chainring-fixing-'+str(i)],evidence='unknown',explode=[0,0,-.27])
fw=g.sprocket((rear_x,.347,zf),18,rphase,.018,.0028,mat='alloy')
fwparts=[g.bevel(fw,.00015),g.ring((rear_x,.347,zf-.009),.027,.0175,.013,mat='dark'),g.ring((rear_x,.347,zf+.001),.020,.0175,.003)]
for i in range(4):
    a=i*math.pi/2
    g.boolean(fwparts[2],g.cyl((rear_x+.019*math.cos(a),.347+.019*math.sin(a),zf+.001),.0011,.02))
put('freewheel',g.merge(fwparts),'Ruota libera con pignone 18 denti sottile, sedi dei rulli, corpo concentrico al mozzo e dettagli della ghiera. L’interno resta un gruppo chiuso; impronta e quote non sono OEM verificate.')

# Discrete polygonal chain: every consecutive pin is exactly 12.7 mm apart.
A=Vector(rear[:2]);B=Vector(bb[:2])
def point(center,r,a):return center+Vector((math.cos(a),math.sin(a)))*r
ru=point(A,Rr,rphase);fu=point(B,Rf,fphase)
fd=point(B,Rf,fphase-front_steps*math.tau/44);rd=point(A,Rr,rphase+rear_steps*math.tau/18)
positions=[ru.lerp(fu,j/straight_steps) for j in range(straight_steps)]
positions += [point(B,Rf,fphase-j*math.tau/44) for j in range(front_steps)]
positions += [fd.lerp(rd,j/straight_steps) for j in range(straight_steps)]
positions += [point(A,Rr,rphase+rear_steps*math.tau/18-j*math.tau/18) for j in range(rear_steps)]
errors=[abs((positions[(i+1)%len(positions)]-p).length-pitch) for i,p in enumerate(positions)]
assert max(errors)<1e-7
assert len(positions)==100

def plate(inner):
    obj=g.capsule(pitch,.0041,.0009,waist=.0025)
    for x in [-pitch/2,pitch/2]:g.boolean(obj,g.cyl((x,0,0),.0017,.02,segments=32))
    items=[g.bevel(obj,.00018)]
    if inner:
        # Formed collars are integral to the inner plate of this teaching geometry.
        for x in [-pitch/2,pitch/2]:items.append(g.ring((x,0,-.0011),.00225,.0017,.0014,segments=32))
    return g.merge(items)
inner_template=g.bake(plate(True));outer_template=g.bake(plate(False));templates += [inner_template,outer_template]
roller_template=g.bake(g.bevel(g.ring((0,0,0),.00385,.0023,.003175,segments=40),.00015));templates.append(roller_template)
pin_template=g.merge([g.cyl((0,0,0),.00155,.0075,segments=24),g.cyl((0,0,-.00375),.00205,.0007,segments=32),g.cyl((0,0,.00375),.00205,.0007,segments=32)]);templates.append(pin_template)
for i,p in enumerate(positions):
    nxt=positions[(i+1)%len(positions)];center=(p+nxt)/2;angle=math.atan2((nxt-p).y,(nxt-p).x)
    put('chain-pin-'+str(i),g.instance(pin_template,(p.x,p.y,zf)),'Rivetto con testa e estremità ribattuta. Interasse geometrico 12,7 mm; forma di studio, non rivetto riutilizzabile certificato.')
    put('chain-roller-'+str(i),g.instance(roller_template,(p.x,p.y,zf)),'Rullo cavo tra le piastrine. Siede nella gola tra due denti senza attraversare il metallo; diametri e gioco di studio.')
    for side in [-1,1]:
        inner=(i%2==0);level=.0020375 if inner else .0030875
        obj=g.instance(inner_template if inner else outer_template,(center.x,center.y,zf+side*level),angle)
        if inner and side==-1:
            # Mirror the formed collar inward without negative scale in the export.
            obj.data=obj.data.copy()
            for v in obj.data.vertices:v.co.y=-v.co.y
            bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
        put(f'chain-plate-{i}-{side}',obj,'Piastrina sagomata con due fori, bordi smussati e, per le interne, collari integrati. Passo 12,7 mm; costruzione interna illustrativa e non distinta del marchio montato.')
clip=g.capsule(pitch,.0025,.0005,mat='dark');g.boolean(clip,g.capsule(pitch,.0016,.01,mat='dark'))
clip.location=g.xyz(((positions[0].x+positions[1].x)/2,(positions[0].y+positions[1].y)/2,zf+.0043));clip.rotation_euler.y=-math.atan2((positions[1]-positions[0]).y,(positions[1]-positions[0]).x)
put('chain-master',clip,'Clip esterna di collegamento illustrativo: tipo di maglia di giunzione da identificare sulla bici reale.')

# Spoke holes, bearing cavities and an outboard threaded freewheel seat.
for tag,cx,width in [('front',.62,.10),('rear',rear_x,.12)]:
    left=-width*.30;right=.021 if tag=='rear' else width*.30
    half=width*.325
    profile=[(.019,-half),(.019,-.013),(.017,.013)]
    if tag=='rear':profile += [(.0168,.028),(.0174,.031),(.0174,.044),(.013,.044),(.013,.031)]
    else:profile += [(.019,half)]
    profile += [(.0148,width*.20),(.009,.009),(.009,-.009),(.0148,-width*.20),(.013,-half)]
    hubpieces=[g.lathe((cx,.347,0),profile)]
    for side,z in [(-1,left),(1,right)]:
        flange=g.ring((cx,.347,z),.034,.017,.005,segments=96)
        for i in range(32):
            if (1 if i%2 else -1)!=side:continue
            a=i*math.tau/32;b=a+(.37 if i%2 else -.37)
            start=(cx+.030*math.cos(b),.347+.030*math.sin(b),z)
            g.boolean(flange,g.cyl(start,.00125,.020,segments=20))
            end=(cx+.305*math.cos(a),.347+.305*math.sin(a),0)
            elbow=(start[0],start[1],z+side*.005)
            put(f'{tag}-spoke-{i}',g.path([start,elbow,end],.001,'alloy'),'Raggio con gomito a J inserito nel foro della flangia. La raggiatura a 32 elementi è illustrativa, non distinta OEM.')
        hubpieces.append(g.bevel(flange,.0003))
    put(tag+'-hub',g.merge(hubpieces),'Corpo mozzo con cavità per i cuscinetti e flange forate. Il posteriore ha sede esterna concentrica per la ruota libera e flangia destra arretrata per lasciare spazio al gruppo. Quote e architettura illustrativi.')

# Calipers meet their fork/frame bridges and their pads meet the rim tracks.
calipers={};routing={}
def tilt_pad(obj,center,angle):
    pivot=g.xyz(center)
    obj.matrix_world=Matrix.Translation(pivot)@Matrix.Rotation(-angle,4,'Y')@Matrix.Translation(-pivot)@obj.matrix_world
    return obj
for tag,cx,cy,padx in [('front',.479,.705,.510),('rear',rear_pivot_x,.675,-.290)]:
    wheel_x=.62 if tag=='front' else rear_x
    pady=.347+math.sqrt(.309**2-(padx-wheel_x)**2)
    pad_angle=math.atan2(-(padx-wheel_x),pady-.347)
    adjust=(cx+.033,cy+.036,.030);clamp=(cx+.033,cy+.004,.030)
    calipers[tag]={'pivot':[cx,cy,0],'pad':[padx,pady,.014],'adjuster':list(adjust),'clamp':list(clamp)}
    for side in [-1,1]:
        arm=g.path([(cx,cy,.026),(cx+side*.012,cy+.017,side*.038),(padx,pady+.014,side*.028),(padx,pady,side*.023)],.0045,'alloy')
        if side==1:arm=g.merge([arm,g.bar((cx,cy,.026),adjust,.0035)])
        put(f'{tag}-brake-arm-{side}',arm,'Braccio sagomato della pinza, collegato al perno sulla corona forcella o sul ponticello dei foderi. Architettura illustrativa.')
        holder=g.extrude([(-.025,-.006),(.025,-.006),(.025,.006),(-.025,.006)],center=(padx,pady,side*.021),h=.009)
        put(f'{tag}-pad-holder-{side}',tilt_pad(g.bevel(holder,.001),(padx,pady,side*.021),pad_angle),'Portapattino allineato alla tangente della pista del cerchio, con sede dell’inserto illustrativa.')
        pad=g.extrude([(-.024,-.005),(.024,-.005),(.024,.005),(-.024,.005)],center=(padx,pady,side*.015),h=.005,mat='rubber')
        for dx in [-.012,0,.012]:
            cutter=g.extrude([(-.001,-.007),(.001,-.007),(.001,.007),(-.001,.007)],center=(padx+dx,pady,side*.013),h=.0015)
            g.boolean(pad,cutter)
        put(f'{tag}-pad-{side}',tilt_pad(g.bevel(pad,.0005),(padx,pady,side*.015),pad_angle),'Pattino con scanalature di scarico, allineato alla tangente del cerchio; profilo illustrativo.')
        put(f'brake-pad-nut-{tag}-{side}',g.nut((padx,pady,side*.034),.005,.0027,.004),'Dado esagonale forato del portapattino; misura da verificare.')
        put(f'{tag}-pad-washer-{side}',g.ring((padx,pady,side*.030),.006,.0028,.0015),'Rondella del fissaggio del pattino.')
        put(f'brake-pad-screw-{tag}-{side}',tilt_pad(g.bolt((padx+.018,pady,side*.021),(0,1,0),.0015,.008,.0005),(padx,pady,side*.021),pad_angle),'Vite di arresto dell’inserto con impronta e filetto illustrativi.')
    put('brake-pivot-'+tag,g.bolt((cx,cy,0),radius=.003,length=.060,pitch=.001),'Perno filettato passante, fissato alla forcella o al ponticello del telaio.')
    put('brake-fixing-'+tag,g.nut((cx,cy,-.028),.006,.0031,.006),'Dado esagonale di fissaggio della pinza sul suo supporto.')
    put('brake-spring-'+tag,g.path([(cx-.018,cy+.006,.025),(cx-.020,cy+.016,.028),(cx,cy+.021,.030),(cx+.020,cy+.016,.028),(cx+.018,cy+.006,.025)],.0009,'dark'),'Molla di ritorno ancorata ai bracci; sagoma illustrativa.')
    put('brake-cable-bolt-'+tag,g.bolt(clamp,radius=.0025,length=.012),'Vite serracavo con testa esagonale incassata e filetto, allineata al tratto scoperto del cavo.')
    locknut=g.nut((0,0,0),.006,.0022,.003);locknut.rotation_euler.x=-math.pi/2;locknut.location=g.xyz((adjust[0],adjust[1]-.006,adjust[2]))
    barrel=g.tube((adjust[0],adjust[1]-.008,adjust[2]),(adjust[0],adjust[1]+.008,adjust[2]),.0045,.0021,'alloy')
    put('brake-adjuster-'+tag,g.merge([barrel,locknut]),'Registro cavo forato montato sul braccio della pinza e allineato con l’ingresso della guaina; forma e utensili indicativi.',name='Registro tensione cavo',deps=['brake-cable-'+tag])
    put('brake-ferrule-'+tag,g.tube((adjust[0],adjust[1]+.008,adjust[2]),(adjust[0],adjust[1]+.017,adjust[2]),.0032,.0026,'alloy'),'Terminale della guaina inserito nel registro della pinza.')
    tail=(clamp[0],clamp[1]-.018,clamp[2])
    put('brake-endcap-'+tag,g.cyl(tail,.0013,.006,(0,1,0),mat='alloy',segments=24),'Terminale anti-sfilacciamento sul tratto di cavo oltre il serraggio.')
    side=1 if tag=='front' else -1;lever=(.485,.962,side*.17)
    ferrule_end=(adjust[0],adjust[1]+.014,adjust[2])
    if tag=='front':
        points=[lever,(.553,.944,.16),(.57,.889,.10),(.561,.811,.055),(adjust[0],adjust[1]+.045,.030),ferrule_end]
    else:
        supports=[]
        for k,x in enumerate([.325,.105,-.10]):
            y=.825+(x+.16)/(.415+.16)*(.88-.825);p=(x,y+.014,-.021);supports.append(p)
            # A removable clip holds the housing; a visible bridge meets the tube.
            band=g.ring((0,0,0),.0166,.0152,.008,mat='dark')
            axis=Vector(ht)-Vector(seat);band.rotation_euler=g.xyz((0,0,1)).rotation_difference(g.xyz(axis).normalized()).to_euler();band.location=g.xyz((x,y,0))
            direction=axis.normalized()
            saddle=g.tube(Vector(p)-direction*.006,Vector(p)+direction*.006,.0040,.00275,'dark')
            bridge=g.bar((x,y+.011,-.011),p,.003,'dark')
            lug=g.bar((x-.005,y-.010,-.014),(x+.005,y-.010,-.014),.003,'dark')
            put('rear-housing-clip-'+str(k),g.merge([band,saddle,bridge,lug]),'Clip rimovibile che mantiene la guaina vicino al tubo superiore. Fissaggio illustrativo, non identificazione OEM.',name='Clip guaina sul telaio · '+str(k+1),deps=['rear-housing-clip-bolt-'+str(k)],evidence='unknown')
            put('rear-housing-clip-bolt-'+str(k),g.bolt((x,y-.010,-.014),tuple(direction),radius=.0018,length=.008,pitch=.0006),'Vite di chiusura della clip illustrativa, separata dal passaggio della guaina; misura da verificare.',name='Vite clip guaina · '+str(k+1),evidence='unknown')
        points=[lever,(.51,.937,-.16),(.497,.89,-.08),(.42,.88,-.026),*supports,(-.174,.826,-.021),(-.235,.792,-.014),(adjust[0],adjust[1]+.044,.030),ferrule_end]
        routing['rearSupports']=[list(p) for p in supports]
    put('brake-housing-'+tag,g.hollow_path(points),'Guaina cava collegata alla leva e inserita nel registro della pinza. Il posteriore segue il tubo superiore ed è sostenuto da tre clip; il tratto sullo sterzo conserva una curva libera. Percorso di studio da confermare sulla variante reale.')
    wire=g.merge([g.path(points,.00065,'alloy'),g.path([ferrule_end,adjust,clamp,tail],.00065,'alloy')])
    put('brake-cable-'+tag,wire,'Cavo continuo dentro la guaina e scoperto solo al registro, al serracavo e alla coda terminale.')
    routing[tag]=[list(p) for p in points]

byid['brake-housing-rear']['dependsOn'] += ['rear-housing-clip-'+str(i) for i in range(3)]
byid['chainring']['dependsOn'] += ['chainring-nut-'+str(i) for i in range(5)]

# Align the steering stack with its inclined axis; eliminate the old floating cap.
def on_axis(obj,center,axis=head_axis):
    obj.rotation_euler=g.xyz((0,0,1)).rotation_difference(g.xyz(axis).normalized()).to_euler()
    obj.location=g.xyz(center);return obj
for tag,base,sign in [('upper',Vector(ht),1),('lower',Vector(hb),-1)]:
    axis=head_axis*sign
    cup=g.lathe((0,0,0),[(.0195,-.006),(.0205,.006),(.0185,.006),(.0185,-.003),(.0143,-.003),(.0143,-.006)])
    put('head-'+tag+'-cup',on_axis(cup,base+axis*.006,axis),'Calotta orientata sull’asse del cannotto, inserita nel tubo e con sede cava per il cuscinetto. Profilo illustrativo EC34, non distinta OEM.')
    bearing=bpy.data.objects['head-'+('0' if sign==1 else '1')+'-bearing']
    old_y=.897 if sign==1 else .735;old_center=Vector((.415+(.88-old_y)*.33,old_y,0))
    rot=g.xyz((0,1,0)).rotation_difference(g.xyz(head_axis)).to_matrix().to_4x4()
    bearing.matrix_world=Matrix.Translation(g.xyz(base+axis*.009))@rot@Matrix.Translation(-g.xyz(old_center))@bearing.matrix_world
cover_center=Vector(ht)+head_axis*.0155
put('head-cover',on_axis(g.ring((0,0,0),.020,.0144,.007),cover_center),'Coperchio appoggiato alla calotta superiore e orientato sul cannotto; profilo illustrativo.')
put('head-compression-ring',on_axis(g.ring((0,0,0),.0156,.0144,.0015),Vector(ht)+head_axis*.012),'Anello illustrativo sotto il coperchio, allineato alla serie sterzo.')
put('head-crown-race',on_axis(g.ring((0,0,0),.0178,.0144,.006),Vector(hb)-head_axis*.016),'Pista inferiore collegata al cannotto, sotto la calotta. Profilo illustrativo.')
stem_center=head_at(.951);stem_bottom=stem_center-head_axis*.0175;stem_top=stem_center+head_axis*.0175
spacer_start=Vector(ht)+head_axis*.019;spacer_length=(stem_bottom-spacer_start).length
put('head-spacer',on_axis(g.ring((0,0,0),.018,.0144,spacer_length),(stem_bottom+spacer_start)/2),'Distanziale che colma lo spazio tra coperchio e attacco manubrio. Altezza illustrativa, non componente identificato sul modello reale.',name='Distanziale serie sterzo',group='Sterzo',proc='headset',deps=['stem'])
stem_ring=on_axis(g.ring((0,0,0),.021,.0144,.035,mat='dark'),stem_center)
# Rear clamp ears keep the screws outside the steerer bore.
ears=g.extrude([(-.008,-.016),(.008,-.016),(.008,.016),(-.008,.016)],center=(stem_center.x-.024,.951,0),h=.048,mat='dark')
for i in range(2):g.boolean(ears,g.cyl((stem_center.x-.024,.942+i*.014,0),.0027,.060))
body=g.merge([stem_ring,g.bevel(ears,.001),g.bar(stem_center,(.452,.975,0),.017,'dark'),g.extrude([(-.007,-.017),(.007,-.017),(.007,.017),(-.007,.017)],center=(.46,.975,0),h=.036,mat='dark')])
for i in range(4):
    center=(.4585,.966+(i//2)*.020,-.014+(i%2)*.028)
    g.boolean(body,g.cyl(center,.0027,.050,(1,0,0)))
    put('stem-face-bolt-'+str(i),g.bolt(center,(1,0,0),.0025,.017),'Vite del frontalino appoggiata alla faccia dell’attacco, con filetto e impronta esagonale illustrativi.')
put('stem',body,'Attacco sul cannotto inclinato, con sedi delle viti e orecchie di serraggio. Lunghezza nominale 60 mm; sagoma e fissaggi illustrativi.')
for i in range(2):put('stem-side-bolt-'+str(i),g.bolt((stem_center.x-.024,.942+i*.014,0),radius=.0025,length=.048),'Vite serraggio attacco inserita nelle orecchie del morsetto; filetto e impronta illustrativi.')
cap_center=stem_top+head_axis*.0015
put('head-topcap',on_axis(g.ring((0,0,0),.020,.0027,.003),cap_center),'Tappo superiore appoggiato all’attacco e orientato lungo il cannotto.')
top_bolt_center=cap_center+head_axis*(.0015-.0125)
put('head-top-bolt',g.bolt(top_bolt_center,tuple(head_axis),.0025,.025),'Vite di precarico appoggiata al tappo, con impronta incassata; il suo serraggio non sostituisce quello dell’attacco.')
star=g.extrude([((.012 if i%2==0 else .007)*math.cos(i*math.tau/16),(.012 if i%2==0 else .007)*math.sin(i*math.tau/16)) for i in range(16)],h=.002,mat='dark')
g.boolean(star,g.cyl((0,0,0),.0027,.010))
put('head-star',on_axis(g.merge([star,g.tube((0,0,-.006),(0,0,.006),.004,.0023,'dark')]),head_at(.948)),'Ancora interna della vite di precarico, allineata al cannotto. Costruzione illustrativa, non inventario OEM.')
post_axis=Vector((-.208,1.002,0))-Vector(seat)
collar=on_axis(g.ring((0,0,0),.017,.01285,.010,mat='dark'),Vector(seat)+post_axis.normalized()*.005,post_axis)
collar_ears=g.extrude([(-.0055,-.004),(.0055,-.004),(.0055,.004),(-.0055,.004)],center=(-.142,.83,0),h=.038,mat='dark')
g.boolean(collar_ears,g.cyl((-.142,.83,0),.0027,.050))
put('seat-clamp',g.merge([collar,collar_ears]),'Collarino sul reggisella con orecchie forate e vite appoggiata al morsetto; costruzione illustrativa.')
put('seat-clamp-bolt',g.bolt((-.142,.83,0),radius=.0025,length=.038),'Vite collarino inserita nel morsetto, con filetto e sede utensile illustrativi.')

# Accessory mounts are represented within their still-closed groups.
for id,target,mount in [('rear-light',(-.26,.99,0),(-.196,.96,0)),('rear-reflector',(-.207,.935,0),(-.190,.936,0)),('front-light',(.48,.992,0),(.452,.975,0)),('front-reflector',(.485,.949,0),(.452,.975,0))]:
    accessory=bpy.data.objects[id]
    accessory.name='detail-accessory'
    support=g.bar(mount,target,.004,'dark')
    put(id,g.merge([accessory,support]),'Accessorio come gruppo chiuso con staffa di sostegno collegata al manubrio o al reggisella. Forma e attacco illustrativi.')

for obj in templates:bpy.data.objects.remove(obj,do_unlink=True)
for obj in collection.objects:
    g.bake(obj)
    bm=bmesh.new();bm.from_mesh(obj.data)
    flat_plate=obj.name in {'chainring','freewheel'} or obj.name.startswith('chain-plate-')
    for face in bm.faces:
        # Preserve the planar caps of sheet metal: smoothing them with the
        # bevel walls creates false raised ribs in the interactive viewer.
        face.smooth=not(flat_plate and abs(face.normal.y)>.999)
    for edge in bm.edges:edge.smooth=(edge.calc_face_angle(0)<math.radians(35))
    bm.to_mesh(obj.data);bm.free();obj.data.update()
    assert not obj.children

structure.update(id='elops-study-v2',version=2,name='Speed 500 · revisione meccanica',modelPath='/models/elops-study-v2.glb')
structure['coverage']='Ricostruzione di studio migliorata: cavi ancorati con clip sul tubo superiore e registri sulle pinze, pattini sulla pista dei cerchi, corona 44T e ruota libera 18T con sedi dei rulli e catena a passo geometrico 12,7 mm; serie sterzo e fissaggi collegati. Non è una simulazione dinamica né una replica OEM: percorso, clip, distanziale sterzo, attacchi corona, tolleranze e interni non pubblicati sono illustrativi. Ruota libera, cartuccia, leve ed elettronica restano gruppi chiusi.'
bundle['bikes'][0]['structureId']=structure['id']
for recipe in structure['procedures']:
    if recipe['id']=='brake':
        recipe['steps'].insert(1,'Per liberare la guaina posteriore apri le clip, conserva le viti e sfila i terminali dai registri. La curva vicino al manubrio deve permettere lo sterzo.')
        recipe['sources'].append({'title':'Park Tool · percorso cavi e guaine','url':'https://www.parktool.com/en-us/blog/repair-help/brake-housing-cable-installation-upright-bars','scope':'Metodo generale: sostegno al telaio, curve libere per lo sterzo e ingresso nei registri; non prova il percorso OEM della Speed 500.'})
    if recipe['id']=='chain':recipe['sources'].append({'title':'KMC · esempio catena singlespeed','url':'https://www.kmcchain.com/en/product/bicycle-chain-s1-single-speed','scope':'Conferma il formato 1/2 x 1/8 di una catena singlespeed. Non attribuisce marca o costruzione degli interni alla bici modellata.'})
constraints={'revision':2,'chainPitchMeters':pitch,'chainPinCount':len(positions),'maxPitchErrorMeters':max(errors),'frontTeeth':44,'rearTeeth':18,'frontPitchRadius':Rf,'rearPitchRadius':Rr,'frontPhase':fphase,'rearPhase':rphase,'rearAxleShiftMeters':rear_x+.43,'chainLineMeters':zf,'chainPins':[[p.x,p.y,zf] for p in positions],'calipers':calipers,'routing':routing,'verification':'Geometric teaching constraints, not OEM tolerances or a dynamic simulation.'}
(DEST/'source').mkdir(parents=True,exist_ok=True);(DEST/'web').mkdir(exist_ok=True)
(DEST/'catalog.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding='utf-8')
(DEST/'assembly-constraints.json').write_text(json.dumps(constraints,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(DEST/'source/assembly.blend'))
print('Revisione meccanica salvata:',len(parts),'pezzi; errore massimo passo:',max(errors))
