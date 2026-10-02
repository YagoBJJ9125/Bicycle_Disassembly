"""Full-bike learning model using published Elops Speed 500 specifications.

Original geometry; OEM dimensions/internal inventories that are not published
remain indicative or unknown. Not a manufacturing model or an exact OEM clone.
"""
import json
import math
from pathlib import Path
from mathutils import Vector
import bpy

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'models/elops-study-v1'
if bpy.data.filepath:
    raise RuntimeError('Avviare un processo Blender nuovo senza un documento aperto.')
if (DEST / 'source/assembly.blend').exists():
    raise RuntimeError('Sorgente esistente: creare una nuova versione per rigenerare.')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new('OFFICINA_EXPORT')
bpy.context.scene.collection.children.link(collection)
materials = {}
for name, color, metal, rough in [('frame',(0.10,0.15,0.19,1),.55,.28),('alloy',(.55,.61,.66,1),.85,.24),('dark',(.025,.035,.045,1),.2,.38),('rubber',(.022,.025,.027,1),0,.7),('skinwall',(.35,.22,.10,1),0,.66),('brass',(.43,.27,.07,1),.7,.32),('red',(.5,.015,.01,1),0,.3),('white',(.8,.84,.8,1),0,.3)]:
    m=bpy.data.materials.new(name);m.use_nodes=True
    shader=m.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=color
    shader.inputs['Metallic'].default_value=metal
    shader.inputs['Roughness'].default_value=rough
    materials[name]=m

def coord(v): return Vector((v[0],-v[2],v[1]))
def place(obj, material):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    collection.objects.link(obj);obj.data.materials.append(materials[material]);return obj
def cyl(center,radius,length,axis=(0,0,1),segments=32,mat='alloy'):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments,radius=radius,depth=length,location=coord(center))
    o=place(bpy.context.object,mat);o.rotation_euler=Vector((0,0,1)).rotation_difference(coord(axis).normalized()).to_euler();return o
def bar(a,b,radius,mat='alloy',segments=24):
    a,b=Vector(a),Vector(b);return cyl((a+b)/2,radius,(b-a).length,b-a,segments,mat)
def box(center,size,mat='alloy',bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=coord(center));o=place(bpy.context.object,mat)
    o.scale=(size[0],size[2],size[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Edge radii','BEVEL');mod.width=bevel;mod.segments=3
    return o
def mesh(vertices,faces,mat='alloy'):
    m=bpy.data.meshes.new('Original study geometry');m.from_pydata([coord(v) for v in vertices],[],faces);m.update()
    o=bpy.data.objects.new('part',m);collection.objects.link(o);m.materials.append(materials[mat]);return o
def radial(center,profile,segments=64,axis='z',mat='alloy',hexagonal=False):
    vs,fs=[],[]
    for r,h in profile:
        for i in range(segments):
            a=2*math.pi*i/segments
            rr=r/math.cos((a+math.pi/6)%(math.pi/3)-math.pi/6) if hexagonal else r
            v=(rr*math.cos(a),rr*math.sin(a),h)
            if axis=='y':v=(v[0],v[2],v[1])
            vs.append([center[k]+v[k] for k in range(3)])
    for j in range(len(profile)):
        nxt=(j+1)%len(profile)
        for i in range(segments):
            q=(i+1)%segments;fs.append((j*segments+i,j*segments+q,nxt*segments+q,nxt*segments+i))
    return mesh(vs,fs,mat)
def ring(center,outer,inner,thickness,axis='z',mat='alloy',segments=48):
    return radial(center,[(outer,-thickness/2),(outer,thickness/2),(inner,thickness/2),(inner,-thickness/2)],segments,axis,mat)
def torus(center,radius,section,mat='rubber',segments=192,sides=12,axis='z'):
    return radial(center,[(radius+section*math.cos(a*math.pi*2/sides),section*math.sin(a*math.pi*2/sides)) for a in range(sides)],segments,axis,mat)
def sphere(center,radius,mat='alloy'):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=radius,location=coord(center));return place(bpy.context.object,mat)
def merge(objects):
    if len(objects)==1:return objects[0]
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();return bpy.context.object
def tube_path(points,radius,mat='alloy',sides=12):
    curve=bpy.data.curves.new('Formed tube','CURVE');curve.dimensions='3D';curve.resolution_u=12;curve.bevel_depth=radius;curve.bevel_resolution=2
    s=curve.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
    for p,v in zip(s.bezier_points,points):p.co=coord(v);p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    obj=bpy.data.objects.new('formed',curve);collection.objects.link(obj);curve.materials.append(materials[mat])
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.convert(target='MESH');return bpy.context.object
def gear(center,teeth,pitch_radius,thickness,mat='alloy'):
    # Four vertices around each tooth describe gaps and tip surfaces.
    vs,fs=[],[];n=teeth*4;inner=pitch_radius*.72
    for z in [-thickness/2,thickness/2]:
        for circle in [0,1]:
            for i in range(n):
                a=2*math.pi*i/n;r=inner if circle else pitch_radius+(.0018 if i%4 in [1,2] else -.0025)
                vs.append((center[0]+r*math.cos(a),center[1]+r*math.sin(a),center[2]+z))
    for i in range(n):
        j=(i+1)%n
        fs.extend([(i,j,2*n+j,2*n+i),(n+i,3*n+i,3*n+j,n+j),(i,n+i,n+j,j),(2*n+i,2*n+j,3*n+j,3*n+i)])
    return mesh(vs,fs,mat)

product='https://www.decathlon.it/p/bici-citta-single-speed-500-grigia/306292/c383m8749510'
headset='https://compatible-spare-parts.decathlon.com/it-IT/categories/6/products/8563558/spare-part-nature/12066'
park='https://www.parktool.com/en-us/blog/repair-help/'
def src(title,url,scope):return {'title':title,'url':url,'scope':scope}
spec=src('Decathlon · Speed 500',product,'Allestimento e dimensioni pubblicate; non fornisce quote CAD o inventario degli interni.')
procedures=[]
def recipe(id,title,steps,tools,warning='',url=None):
    procedures.append({'id':id,'title':title,'steps':steps,'tools':[{'name':n,'size':s,'certainty':c} for n,s,c in tools],
      'warnings':[warning] if warning else [],'sources':([src('Park Tool · procedura generale',park+url,'Metodo generale: non conferma misure o componenti OEM della Speed 500.')] if url else [])+[spec]})
recipe('frame','Liberare il telaio',['Fotografa collegamenti e allestimento. Rimuovi ruote, freni, sella, sterzo e trasmissione secondo le rispettive schede.','I tubi saldati restano un solo componente: non separare le saldature.'],[('Cavalletto da officina','Compatibile con il reggisella; non serrare tubi sottili','indicative')])
recipe('wheel','Rimuovere la ruota',['Scollega la tensione del freno per liberare il copertone.','Individua la misura dei dadi asse, allentali e sostieni la ruota. Per la posteriore libera la catena e conserva l’ordine delle rondelle.'],[('Chiave per dadi asse','Spesso 15 mm; misurare l’esagono reale. M10 indica il filetto, non la chiave','indicative')],url='wheel-removal-and-installation')
recipe('tire','Pneumatico, camera e valvola',['Estrai la ruota e sgonfia completamente.','Solleva un tallone con leve per copertoni e sfila la camera senza tirare la valvola.','La valvola e le sue parti sono illustrative: identifica il tipo montato prima di aprirla.'],[('Leve copertoni','Per cerchi bici, preferibilmente plastica','indicative'),('Pompa','Testa compatibile con la valvola effettiva','unknown')],url='tire-and-tube-removal-and-installation')
recipe('spoke','Raggi, nippli e cerchio',['Rimuovi pneumatico, camera e nastro paranippli.','Per smontare la ruota registra incroci, posizione e tensione dei raggi. Allenta progressivamente i nippli, poi sfila i raggi.'],[('Chiave tiraraggi','Profilo nipplo da misurare; frequentemente 3,23–3,45 mm','indicative')],'Numero e raggiatura nel modello sono illustrativi; dopo la ricostruzione servono centratura e controllo tensione.')
recipe('hub','Interni illustrativi del mozzo',['Togli la ruota. Conserva rondelle e distanziali nella posizione originale.','Se il mozzo reale è a coni e sfere, controtrattieni il cono, allenta il controdado e sfila asse e sfere sopra una vaschetta.','Se trovi cuscinetti a cartuccia, usa il manuale del mozzo invece di questa scomposizione.'],[('Chiavi per coni','13/14/15 mm sono comuni; profilo della bici non identificato','indicative'),('Chiave controdado','Da misurare sul mozzo effettivo','unknown')],'Architettura, quantità e diametro delle sfere non sono confermati per il mozzo OEM.',url='hub-overhaul-and-adjustment')
recipe('headset','Serie sterzo Ahead',['Sostieni la forcella. Allenta il serraggio laterale dell’attacco e rimuovi vite e tappo superiore.','Sfila attacco, distanziali, coperchio e cuscinetti mantenendo l’ordine.','Calotte e pista richiedono estrattori appropriati. La stella nel cannotto non è una rimozione ordinaria di manutenzione.'],[('Chiavi esagonali','4/5/6 mm secondo i fissaggi reali','indicative'),('Estrattore e pressa serie sterzo','Compatibili EC34; verificare pista e diametri','indicative')],'Cuscinetti e minuteria interni sono una ricostruzione didattica, non un esploso OEM.',url='threadless-headset-service')
recipe('cockpit','Manubrio e comandi',['Fotografa posizione di leve, cavi e manubrio.','Libera cavi e morsetti, poi le viti del frontalino dell’attacco. Conserva l’ordine dei fissaggi.'],[('Chiavi esagonali','Comunemente 4/5 mm; verificare i fissaggi','indicative')])
recipe('saddle','Sella e reggisella',['Segna l’altezza del reggisella. Allenta il collarino e sfila il reggisella.','Per separare la sella libera il suo morsetto e conserva piastre e dadi.'],[('Chiavi esagonali o aperte','Misura dipendente dal morsetto; da verificare','unknown')])
recipe('crank','Pedivelle e corona',['Apri e libera la catena. Rimuovi il fissaggio centrale della pedivella.','Per un perno quadro usa un estrattore compatibile, completamente avvitato nella pedivella.','Il fissaggio della corona è illustrativo: se è rivettata o solidale non separarla come una corona imbullonata.'],[('Chiave fissaggio pedivella','Spesso esagonale 8 mm oppure bussola 14 mm; verificare','indicative'),('Estrattore pedivelle','Compatibile con perno quadro e filetto della pedivella','indicative')],url='crank-removal-and-installation-three-piece')
recipe('bb','Cartuccia movimento centrale',['Rimuovi le pedivelle. Identifica profilo dell’utensile e filettatura della scatola.','Svita l’adattatore e la cartuccia secondo lo standard verificato. Nel BSA la destra è sinistrorsa; altri standard differiscono.','La cartuccia è un gruppo chiuso: i suoi interni non sono modellati come revisionabili.'],[('Estrattore movimento centrale','Profilo del THUN montato da verificare; non dedotto dalla foto','unknown')],'119 mm è la lunghezza del perno pubblicata, non la misura della chiave.',url='bottom-bracket-removal-and-installation-threaded')
recipe('pedal','Rimuovere i pedali',['Guardando dall’esterno: il pedale destro si svita in senso antiorario, il sinistro in senso orario.','Usa i piatti o l’esagono previsti. Gli interni del pedale qui rappresentati sono illustrativi: consulta il ricambio reale prima di aprirlo.'],[('Chiave pedali','Tipicamente 15 mm; alternativa esagonale 6/8 mm secondo modello','indicative')],url='pedal-installation-and-removal')
recipe('chain','Catena e suoi elementi',['Apri il collegamento compatibile oppure usa uno smagliacatena adatto a una catena singlespeed.','La scomposizione di ogni rivetto è didattica: non è una procedura ordinaria di restauro per riutilizzare la catena.'],[('Smagliacatena','Compatibile 1/2" × 1/8"','indicative'),('Pinza per collegamento','Solo se è presente un collegamento compatibile','unknown')],'Numero di maglie e costruzione delle boccole sono illustrativi; dopo l’apertura può servire un collegamento nuovo.')
recipe('freewheel','Ruota libera',['Rimuovi la ruota, identifica il profilo dell’estrattore e svita il gruppo dal mozzo.','L’interno resta chiuso nel modello: numero di cricchetti e molle non è pubblicato.'],[('Estrattore ruota libera','Profilo del componente montato da verificare','unknown'),('Chiave estrattore','Secondo utensile scelto','unknown')])
recipe('brake','Pinza, pattini e cavi',['Scarica la tensione del cavo e registra il suo percorso.','Libera il serracavo, poi dadi e rondelle dei pattini; conserva orientamento e ordine.','Per separare bracci, molla e perni occorre verificare che la pinza sia revisionabile e consultarne il manuale.'],[('Chiavi esagonali/aperta','4/5/6 mm o misura del dado effettivo; verificare','indicative'),('Tronchese cavi e guaine','Utensile specifico per cavi bici','indicative')],'Minuteria interna e utensili della pinza OEM non sono documentati. Prima dell’uso reale verificare frenata e serraggi.')
recipe('accessory','Accessori',['Rimuovi i morsetti conservando viti, dadi e rondelle.','Le luci e il campanello sono gruppi: circuiti elettronici e interni non sono ricostruiti.'],[('Cacciavite o esagonale','Profilo da verificare sul ricambio','unknown')])

parts=[]
def add(id,name,group,proc,obj,description,deps=(),service='serviceable',evidence='indicative',explode=None):
    obj.name=id;obj['part_id']=id
    p=tuple(obj.location);pos=(p[0],p[2],-p[1])
    for poly in obj.data.polygons:poly.use_smooth=True
    if explode is None:
        # Whole groups separate first; repeated items fan out without losing the axle axis.
        spread={'Ruota anteriore':(.32,.04,0),'Ruota posteriore':(-.32,.04,0),'Sterzo':(.03,.22,0),'Manubrio':(.08,.35,0),'Sella':(-.08,.38,0),'Movimento centrale':(0,-.15,0),'Trasmissione':(0,0,.3),'Catena':(0,0,.42),'Pedali':(0,-.12,.25),'Freni':(.10,.1,.3),'Accessori':(0,.3,.35),'Telaio':(0,0,0)}
        base=spread.get(group,(0,0,0));explode=[base[0],base[1],base[2]+(.15 if len(parts)%2 else -.15)]
    parts.append({'id':id,'meshName':id,'name':name,'group':group,'description':description,'procedureId':proc,'dependsOn':list(deps),'evidence':evidence,'serviceability':service,'explode':explode,'geometry':{'kind':'box','position':list(pos),'size':[.01,.01,.01],'color':'#70808b'}})
    return obj

bb=(0,.285,0);rear=(-.43,.347,0);front=(.62,.347,0);seat=(-.16,.825,0);headtop=(.415,.88,0);headbottom=(.465,.735,0)
# Welded frame and fork remain single physical parts.
framepieces=[bar(bb,seat,.016,'frame'),bar(seat,headtop,.015,'frame'),bar(bb,headbottom,.021,'frame'),cyl(bb,.021,.068,segments=64,mat='frame'),bar(headbottom,headtop,.018,'frame')]
for z in [-.055,.055]:
    framepieces += [bar((0,.285,z*.4),(-.43,.347,z),.01,'frame'),bar(seat,(-.43,.347,z),.008,'frame'),box((-.43,.347,z),(.025,.045,.006),'frame',.002)]
framepieces += [bar((-.29,.55,-.035),(-.29,.55,.035),.006,'frame')]
add('frame','Telaio saldato','Telaio','frame',merge(framepieces),'Telaio in acciaio. Geometria originale approssimata di una bici da città; quote dei tubi e dei forcellini non sono OEM.',service='inseparable',explode=[0,0,0])
forkpieces=[bar(headbottom,(.395,.96,0),.0143,'frame')]
for z in [-.05,.05]:
    forkpieces += [tube_path([(.48,.71,z*.7),(.54,.55,z),(.62,.347,z)],.013,'frame'),box((.62,.347,z),(.025,.04,.006),'frame',.002)]
forkpieces += [bar((.48,.71,-.035),(.48,.71,.035),.014,'frame')]
add('fork','Forcella','Sterzo','headset',merge(forkpieces),'Forcella rigida in acciaio; spazio nominale tra forcellini anteriori 100 mm. Forma e cannotto approssimati.',['stem','head-0-bearing'],explode=[.1,-.26,0])
for id,y,outer,inner,thick,title in [('head-topcap',.983,.017,.003,.003,'Tappo superiore Ahead'),('head-cover',.925,.019,.015,.005,'Coperchio serie sterzo'),('head-upper-cup',.888,.020,.0145,.009,'Calotta superiore'),('head-lower-cup',.741,.020,.015,.009,'Calotta inferiore'),('head-crown-race',.721,.018,.015,.004,'Pista sulla forcella'),('head-compression-ring',.914,.017,.0145,.003,'Anello di compressione')]:
    x=.415-(y-.88)*.33
    add(id,title,'Sterzo','headset',ring((x,y,0),outer,inner,thick,'y',segments=64),'Elemento illustrativo di una serie sterzo Ahead a calotte esterne. Profilo e dimensioni interni da verificare.',['head-top-bolt'] if id=='head-topcap' else ['stem'],explode=[0,(y-.7)*1.4,0])
add('head-top-bolt','Vite precarico sterzo','Sterzo','headset',cyl((.381,.970,0),.0025,.025,(0,1,0)),'Regola il precarico prima del serraggio dell’attacco. Non è il principale fissaggio del manubrio.',explode=[0,.46,0])
add('head-star','Stella nel cannotto','Sterzo','headset',merge([gear((.395,.942,0),8,.012,.002,'dark'),cyl((.395,.944,0),.004,.012,(0,1,0),mat='dark')]),'Ancora filettata interna. Forma illustrativa; rimozione specialistica.',service='specialist',evidence='unknown',explode=[.10,.28,0])
for j,y in enumerate([.897,.735]):
    objects=[]
    for i in range(16):
        a=i*math.tau/16;objects.append(sphere((.415+(.88-y)*.33+math.cos(a)*.016,y,math.sin(a)*.016),.0023))
    add(f'head-{j}-bearing',f'Cuscinetto sterzo {"superiore" if j==0 else "inferiore"}','Sterzo','headset',merge(objects),'Cuscinetto illustrativo a sfere in gabbia. Il ricambio della serie sterzo conferma EC34, non questa distinta interna.',['stem'],evidence='unknown',explode=[.09,.15+j*.12,0])

stem=merge([bar((.394,.951,0),(.452,.975,0),.017,'dark'),ring((.394,.951,0),.021,.0143,.035,'y','dark'),box((.46,.975,0),(.014,.034,.036),'dark',.002)])
add('stem','Attacco manubrio Ahead','Manubrio','cockpit',stem,'Collega il manubrio al cannotto. Lunghezza nominale pubblicata 60 mm; forma e viti illustrative.',['stem-side-bolt-0','stem-side-bolt-1','head-top-bolt'])
add('bar','Manubrio 520 mm','Manubrio','cockpit',tube_path([(.463,.975,-.26),(.452,.975,-.08),(.452,.975,.08),(.463,.975,.26)],.0127,'dark'),'Manubrio in alluminio, larghezza pubblicata 520 mm. Sagoma approssimata.',['stem-face-bolt-0','stem-face-bolt-1','stem-face-bolt-2','stem-face-bolt-3'])
for i in range(2):add(f'stem-side-bolt-{i}','Vite serraggio cannotto','Manubrio','cockpit',cyl((.38,.942+i*.014,.02),.003,.035),'Fissa l’attacco al cannotto; misura utensile da verificare.')
for i in range(4):add(f'stem-face-bolt-{i}',f'Vite frontalino · {i+1}','Manubrio','cockpit',cyl((.474,.966+(i//2)*.020,-.014+(i%2)*.028),.003,.017,(1,0,0)),'Fissa il frontalino; quantità illustrativa.')
for side in [-1,1]:
    add(f'grip-{side}','Manopola','Manubrio','cockpit',radial((.463,.975,side*.207),[(.016,-.052),(.016,.052),(.0128,.052),(.0128,-.052)],64,mat='rubber'),'Rivestimento di presa del manubrio.',['bar-end-'+str(side)])
    add('bar-end-'+str(side),'Tappo manubrio','Manubrio','cockpit',cyl((.463,.975,side*.263),.016,.005,mat='dark'),'Chiude il tubo del manubrio.')

post=bar(seat,(-.208,1.002,0),.0127,'alloy');add('seatpost','Reggisella Ø25,4 mm','Sella','saddle',post,'Reggisella con diametro pubblicato 25,4 mm; morsetto e quote restanti approssimati.',['seat-clamp-bolt'])
add('seat-clamp','Collarino reggisella','Sella','saddle',ring((-.16,.83,0),.018,.013,.013,'y','dark'),'Serraggio del reggisella sul telaio.',['seat-clamp-bolt'])
add('seat-clamp-bolt','Vite collarino','Sella','saddle',cyl((-.145,.83,.02),.003,.037),'Fissa il collarino; profilo da verificare.')
saddle=merge([box((-.225,1.025,0),(.14,.033,.137),'rubber',.013),box((-.135,1.020,0),(.13,.025,.055),'rubber',.012)])
add('saddle','Sella sport','Sella','saddle',saddle,'Appoggio del bacino. Sagoma didattica, non scansione della sella OEM.',['saddle-nut'])
for z in [-.021,.021]:add('saddle-rail-'+str(z),'Guida sella','Sella','saddle',bar((-.28,.998,z),(-.12,.998,z),.0035),'Guida metallica di sostegno; connessione alla scocca permanente.',service='inseparable')
add('saddle-nut','Fissaggio morsetto sella','Sella','saddle',cyl((-.204,.99,0),.005,.070),'Fissaggio illustrativo del carrello.')

for tag,center,width in [('front',front,.10),('rear',rear,.12)]:
    group='Ruota anteriore' if tag=='front' else 'Ruota posteriore';x,y,_=center
    add(f'{tag}-tire','Copertone 700 × 32',''+group,'tire',torus(center,.327,.016,'rubber',256,16),'Copertone: misura nominale pubblicata 700 × 32 mm. Profilo e battistrada approssimati.',[f'{tag}-nut-1'],explode=[.32 if tag=='front' else -.32,.15,.20])
    add(f'{tag}-tube','Camera d’aria',group,'tire',torus(center,.325,.012,'rubber',192,12),'Contiene aria; forma e tipo valvola illustrativi.',[f'{tag}-tire'],explode=[.32 if tag=='front' else -.32,.15,-.20])
    add(f'{tag}-rim','Cerchio doppia parete',group,'spoke',radial(center,[(.313,-.011),(.318,-.01),(.319,-.006),(.310,-.006),(.310,.006),(.319,.006),(.318,.01),(.313,.011),(.296,.008),(.296,-.008)],256),'Cerchio con sezione illustrativa a doppia parete, riferimento nominale 622 × 17C.',[f'{tag}-rim-tape'],service='specialist')
    add(f'{tag}-rim-tape','Nastro paranippli',group,'tire',ring(center,.311,.310,.018,mat='rubber',segments=192),'Protegge la camera dai fori e dai nippli.',[f'{tag}-tube'])
    add(f'{tag}-valve','Valvola illustrativa',group,'tire',cyl((x,y+.317,0),.003,.026,(0,1,0),mat='brass'),'Tipo valvola non confermato per questa variante: geometria illustrativa.',[f'{tag}-valve-cap'],evidence='unknown')
    add(f'{tag}-valve-cap','Tappo valvola',group,'tire',cyl((x,y+.336,0),.004,.010,(0,1,0),mat='dark'),'Protegge il terminale della valvola; variante da verificare.',evidence='unknown')
    hub=merge([ring(center,.019,.009,width*.65,segments=64)]+[ring((x,y,z),.034,.009,.005,segments=96) for z in [-width*.30,width*.30]])
    add(f'{tag}-hub','Corpo mozzo e flange',group,'hub',hub,'Collega i raggi all’asse. Mozzo illustrativo: profili e architettura interna OEM non pubblicati.',[f'{tag}-axle'],service='inseparable')
    add(f'{tag}-axle','Asse del mozzo',group,'hub',cyl(center,.005,width+.045),'Asse a dadi. M10 è pubblicato per il serraggio; lunghezza e filetti geometrici qui approssimati.',[f'{tag}-cone-1'])
    for side in [-1,1]:
        z=side*(width/2+.012)
        add(f'{tag}-nut-{side}',f'Dado asse {"destro" if side==1 else "sinistro"}',group,'wheel',radial((x,y,z),[(.0075,-.006),(.0075,.006),(.0051,.006),(.0051,-.006)],36,hexagonal=True),'Blocca la ruota sul forcellino. Foro reale rappresentato; esagono e profilo del filetto da verificare.')
        add(f'{tag}-washer-{side}','Rondella asse',group,'wheel',ring((x,y,side*(width/2+.004)),.010,.0051,.002),'Ripartisce il carico del dado.',[f'{tag}-nut-{side}'])
        for kind,r,h,zz,title in [('locknut',.007,.006,width*.43,'Controdado cono'),('cone',.010,.010,width*.30,'Cono cuscinetto'),('seal',.021,.002,width*.25,'Parapolvere mozzo')]:
            add(f'{tag}-{kind}-{side}',title,group,'hub',ring((x,y,side*zz),r,.0051,h,mat='dark' if kind=='seal' else 'alloy'), 'Componente illustrativo di un mozzo a coni e sfere; presenza e misura OEM da confermare.',[f'{tag}-nut-{side}'] if kind=='locknut' else [f'{tag}-locknut-{side}'],evidence='unknown',explode=[.3 if tag=='front' else -.3,.02,side*(.25+zz)])
        for i in range(9):
            a=i*math.tau/9
            add(f'{tag}-ball-{side}-{i}',f'Sfera mozzo {"destra" if side==1 else "sinistra"} · {i+1}',group,'hub',sphere((x+math.cos(a)*.012,y+math.sin(a)*.012,side*width*.20),.0025),'Sfera illustrativa. Numero nove per lato e diametro non identificano il mozzo OEM.',[f'{tag}-cone-{side}'],evidence='unknown',explode=[(.3 if tag=='front' else -.3)+math.cos(a)*.08,math.sin(a)*.08,side*.34])
    for i in range(32):
        a=i*math.tau/32;b=a+(0.37 if i%2 else -.37);z=width*.30*(1 if i%2 else -1);end=(x+math.cos(a)*.305,y+math.sin(a)*.305,0)
        add(f'{tag}-spoke-{i}',f'Raggio · {i+1}',group,'spoke',bar((x+math.cos(b)*.030,y+math.sin(b)*.030,z),end,.001,segments=12),'Raggio in acciaio. 32 raggi e incroci sono un’ipotesi didattica, non una distinta OEM.',[f'{tag}-nipple-{i}'])
        add(f'{tag}-nipple-{i}',f'Nipplo · {i+1}',group,'spoke',cyl(end,.002,.010,(math.cos(a),math.sin(a),0),segments=12,mat='brass'),'Dado filettato del raggio; misura della chiave da verificare.',[f'{tag}-rim-tape'],service='specialist')

add('bb-cartridge','Cartuccia movimento centrale','Movimento centrale','bb',merge([cyl(bb,.017,.068,segments=64,mat='dark'),cyl(bb,.008,.119,segments=32)]),'Riferimento all’allestimento THUN TOPAZ con perno nominale 119 mm. Cartuccia chiusa: interni non ricostruiti.', ['crank-left','crank-right'],service='inseparable',explode=[0,-.18,.18])
add('bb-adapter','Adattatore movimento centrale','Movimento centrale','bb',ring((0,.285,-.036),.018,.009,.010),'Adattatore illustrativo: profilo utensile e filettatura del ricambio da verificare.',['crank-left'],evidence='unknown')
for side,label in [(-1,'left'),(1,'right')]:
    z=side*.068;end=(side*.13,.285+side*.11,z)
    add('crank-'+label,'Pedivella '+('sinistra' if side==-1 else 'destra'),'Trasmissione','crank',merge([box((side*.065,.285+side*.055,z),(.145,.031,.022),'alloy',.008),cyl((0,.285,z),.019,.023)]),'Leva con riferimento nominale 170 mm; raccordi e fissaggi approssimati.',['crank-bolt-'+label])
    add('crank-bolt-'+label,'Vite pedivella','Trasmissione','crank',cyl((0,.285,z*1.15),.007,.022),'Fissa la pedivella al perno; impronta da verificare.')
    pedal_center=(end[0],end[1],side*.118)
    pedalpieces=[box((end[0]-.038,end[1],side*.12),(.018,.018,.090),'dark',.003),box((end[0]+.038,end[1],side*.12),(.018,.018,.090),'dark',.003)]
    for zz in [side*.079,side*.16]:pedalpieces.append(box((end[0],end[1],zz),(.087,.018,.012),'dark',.003))
    add('pedal-body-'+label,'Corpo pedale '+label,'Pedali','pedal',merge(pedalpieces),'Piattaforma aperta illustrativa; il prodotto identifica il tipo Grip 520, non la sua distinta interna.',['pedal-cap-'+label])
    add('pedal-axle-'+label,'Asse pedale','Pedali','pedal',cyl((end[0],end[1],side*.106),.004,.084),'Asse con filettature destro/sinistro; forme interne approssimate.',['pedal-body-'+label])
    add('pedal-cap-'+label,'Tappo pedale','Pedali','pedal',cyl((end[0],end[1],side*.166),.010,.003,mat='dark'),'Protezione esterna illustrativa.')
    for k in [-1,1]:
        add(f'pedal-bearing-{label}-{k}','Cuscinetto pedale illustrativo','Pedali','pedal',ring((end[0],end[1],side*.12+k*.022),.008,.0042,.006),'Cuscinetto rappresentato come gruppo; costruzione OEM non documentata.',evidence='unknown')

r1=.0127/(2*math.sin(math.pi/44));r2=.0127/(2*math.sin(math.pi/18));chainz=.047
chainringpieces=[gear((0,.285,chainz),44,r1,.003)]+[bar((0,.285,chainz),(.06*math.cos(i*math.tau/5),.285+.06*math.sin(i*math.tau/5),chainz),.006) for i in range(5)]
add('chainring','Corona 44 denti','Trasmissione','crank',merge(chainringpieces),'Corona con 44 denti secondo l’allestimento pubblicato. Profilo dei denti, bracci e fissaggio sono approssimati.',['chain-master','crank-right'])
for i in range(5):
    a=i*math.tau/5;add('chainring-fixing-'+str(i),'Fissaggio corona illustrativo','Trasmissione','crank',cyl((.058*math.cos(a),.285+.058*math.sin(a),chainz+.004),.0035,.012),'Fissaggio illustrativo: quantità e smontabilità OEM non confermate.',evidence='unknown')
add('freewheel','Ruota libera 18 denti','Trasmissione','freewheel',merge([gear((-.43,.347,chainz),18,r2,.006,'dark'),ring((-.43,.347,.041),.030,.016,.015,mat='dark')]),'Ruota libera 18 denti: l’interno resta un gruppo chiuso. Numero di ingaggi pubblicato non indica il numero dei cricchetti.',['rear-nut-1','chain-master'],service='specialist')

# Closed chain on external tangents: links follow gears instead of an ellipse.
A=Vector(rear[:2]);B=Vector(bb[:2]);d=B-A;D=d.length;d.normalize();perp=Vector((-d.y,d.x));c=-(r1-r2)/D;s=math.sqrt(1-c*c)
up=d*c+perp*s;down=d*c-perp*s
pa=A+up*r2;pb=B+up*r1;pc=B+down*r1;pd=A+down*r2
au=math.atan2(up.y,up.x);ad=math.atan2(down.y,down.x)
arc_big=(au-ad)%math.tau;arc_small=(ad-au)%math.tau
lengths=[(pb-pa).length,r1*arc_big,(pd-pc).length,r2*arc_small];total=sum(lengths);count=2*round(total/.0127/2)
def chainpoint(t):
    dist=t%total
    for j,length in enumerate(lengths):
        if dist<=length:
            q=dist/length
            if j==0:return pa.lerp(pb,q)
            if j==2:return pc.lerp(pd,q)
            a=(au-q*arc_big) if j==1 else (ad-q*arc_small);o=B if j==1 else A;r=r1 if j==1 else r2
            return o+Vector((math.cos(a),math.sin(a)))*r
        dist-=length
    return pa
for i in range(count):
    p=chainpoint(i*total/count);n=chainpoint((i+1)*total/count);center=(p+n)/2;axis=n-p;angle=math.atan2(axis.y,axis.x)
    add(f'chain-pin-{i}',f'Perno catena · {i+1}','Catena','chain',cyl((p.x,p.y,chainz),.0018,.010,segments=12),'Rivetto che tiene le piastrine; non presumere riutilizzabilità.',['chain-master'],service='specialist')
    add(f'chain-roller-{i}',f'Rullo catena · {i+1}','Catena','chain',ring((p.x,p.y,chainz),.0038,.0022,.0045,segments=16,mat='dark'),'Rullo forato che si appoggia sui denti della trasmissione.',['chain-pin-'+str(i)],service='specialist')
    for side in [-1,1]:
        zz=chainz+side*(.0034 if i%2==0 else .0044)
        ends=[ring((v.x,v.y,zz),.0042,.0019,.001,segments=12,mat='dark') for v in [p,n]]
        web=box((center.x,center.y,zz),(max(axis.length-.005, .002),.0042,.001),'dark');web.rotation_euler.z=0
        # Geometry for web is generated directly in the wheel plane, avoiding axis confusion.
        vec=axis.normalized();normal=Vector((-vec.y,vec.x));a=center-vec*(axis.length-.005)/2;b=center+vec*(axis.length-.005)/2
        bpy.data.objects.remove(web,do_unlink=True)
        verts=[]
        for z in [zz-.0005,zz+.0005]:
            for point in [a-normal*.0021,b-normal*.0021,b+normal*.0021,a+normal*.0021]:verts.append((point.x,point.y,z))
        ends.append(mesh(verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'dark'))
        add(f'chain-plate-{i}-{side}',f'Piastrina {"interna" if i%2==0 else "esterna"} · {i+1} / {side}','Catena','chain',merge(ends),'Piastrina con due fori. Quantità di maglie e costruzione del collegamento sono illustrative.',['chain-pin-'+str(i)],service='specialist')
add('chain-master','Collegamento catena illustrativo','Catena','chain',box((pa.x,pa.y,chainz+.006),(.014,.004,.001),'alloy'),'Punto di apertura illustrativo: identificare il collegamento effettivo.')

for tag,cx,cy in [('front',.61,.655),('rear',-.37,.649)]:
    for side in [-1,1]:
        arm=tube_path([(cx,cy+.025,.030),(cx+side*.045,cy+.017,side*.030),(cx,cy-.018,side*.023)],.005,'alloy')
        add(f'{tag}-brake-arm-{side}','Braccio pinza','Freni','brake',arm,'Braccio sagomato di una pinza a tiraggio laterale; profilo e articolazioni illustrativi.',['brake-pivot-'+tag])
        add(f'{tag}-pad-holder-{side}','Portapattino','Freni','brake',box((cx,cy-.014,side*.025),(.055,.013,.009),'alloy',.002),'Supporto della cartuccia freno; profilo da verificare.',['brake-pad-nut-'+tag+'-'+str(side)])
        add(f'{tag}-pad-{side}','Inserto pattino','Freni','brake',box((cx,cy-.014,side*.019),(.049,.010,.005),'rubber',.001),'Inserto di attrito sostituibile secondo l’allestimento pubblicato.',['brake-pad-screw-'+tag+'-'+str(side)])
        add('brake-pad-nut-'+tag+'-'+str(side),'Dado portapattino','Freni','brake',cyl((cx,cy-.014,side*.038),.005,.006),'Blocca il portapattino; utensile da identificare.')
        add('brake-pad-screw-'+tag+'-'+str(side),'Vite arresto pattino','Freni','brake',cyl((cx+.02,cy-.014,side*.026),.0015,.008,(0,1,0),segments=16),'Trattiene la cartuccia. Forma e profilo indicativi.')
        add(f'{tag}-pad-washer-{side}','Rondella portapattino','Freni','brake',ring((cx,cy-.014,side*.033),.007,.003,.0015),'Distribuisce il serraggio del portapattino.',['brake-pad-nut-'+tag+'-'+str(side)])
    add('brake-pivot-'+tag,'Perno pinza','Freni','brake',cyl((cx,cy+.025,0),.004,.072),'Articola e fissa la pinza.',['brake-fixing-'+tag])
    add('brake-fixing-'+tag,'Fissaggio pinza','Freni','brake',radial((cx,cy+.025,-.028),[(.005,-.005),(.005,.005),(.0025,.005),(.0025,-.005)],24,hexagonal=True),'Dado illustrativo di fissaggio della pinza.')
    add('brake-spring-'+tag,'Molla di ritorno','Freni','brake',tube_path([(cx-.035,cy+.03,.035),(cx-.020,cy+.045,.035),(cx+.015,cy+.025,.035),(cx+.030,cy+.04,.035)],.0012),'Riporta i bracci verso l’apertura. Forma illustrativa.',['brake-pivot-'+tag])
    add('brake-cable-bolt-'+tag,'Vite serracavo','Freni','brake',cyl((cx+.043,cy+.043,.03),.0025,.016),'Fissa il cavo alla pinza.')
    side=-1 if tag=='rear' else 1;start=(.485,.962,side*.17)
    points=[start,(.57,1.00,side*.19),(.55,.85,.04),(cx,cy+.08,.04)] if tag=='front' else [start,(.53,1.01,-.16),(.31,.96,-.03),(-.16,.87,-.027),(cx,cy+.08,.04)]
    add('brake-housing-'+tag,'Guaina freno','Freni','brake',tube_path(points,.0025,'dark'),'Guaina sagomata del comando; percorso illustrativo.',['brake-cable-bolt-'+tag])
    add('brake-cable-'+tag,'Cavo freno','Freni','brake',tube_path(points+[(cx+.043,cy+.043,.03)],.0006),'Cavo metallico; gli ultimi tratti collegano comando e serracavo.',['brake-cable-bolt-'+tag])
    add('brake-lever-'+tag,'Leva freno','Manubrio','cockpit',merge([ring((.463,.975,side*.156),.016,.0127,.014,segments=48,mat='dark'),tube_path([(.49,.965,side*.156),(.515,.944,side*.20),(.51,.933,side*.23)],.004,'alloy')]),'Comando della pinza. Interni della leva non ricostruiti come ricambio OEM.',['brake-lever-bolt-'+tag])
    add('brake-lever-bolt-'+tag,'Vite morsetto leva','Manubrio','cockpit',cyl((.477,.961,side*.154),.0025,.018,(0,1,0)),'Fissa il comando sul manubrio.')
    add('brake-ferrule-'+tag,'Terminale guaina','Freni','brake',ring((cx,cy+.08,.04),.003,.0026,.007),'Protegge l’estremità della guaina.',['brake-cable-'+tag])
    add('brake-endcap-'+tag,'Cappuccio terminale cavo','Freni','brake',cyl((cx+.046,cy+.036,.035),.0014,.008,segments=16),'Riduce lo sfilacciamento del cavo.',['brake-cable-'+tag])

for id,center,size,mat,name in [('front-light',(.48,.992,0),(.035,.028,.042),'white','Luce anteriore (gruppo)'),('rear-light',(-.26,.99,0),(.025,.032,.025),'red','Luce posteriore (gruppo)'),('front-reflector',(.485,.949,0),(.021,.028,.031),'white','Catarifrangente anteriore'),('rear-reflector',(-.207,.935,0),(.026,.029,.021),'red','Catarifrangente posteriore')]:
    add(id,name,'Accessori','accessory',box(center,size,mat,.004),'Accessorio illustrativo dell’allestimento. Circuiti, batterie e fissaggi interni non documentati.',service='inseparable',evidence='unknown')
add('bell','Campanello (gruppo)','Accessori','accessory',cyl((.453,1.00,-.08),.018,.018,(0,1,0),mat='dark'),'Campanello illustrativo; meccanismo interno non documentato.',service='inseparable',evidence='unknown')

bundle={'schemaVersion':1,'structures':[{'id':'elops-study-v1','name':'Speed 500 · bici intera in Blender','version':1,'kind':'reference',
    'standards':{'frame':'acciaio Hi-Ten; forma approssimata','headset':'Ahead EC34; interno da verificare','bottomBracket':'THUN TOPAZ perno 119 mm; standard filetto unknown','crank':'44 denti; pedivelle nominali 170 mm','brakes':'caliper con inserti sostituibili','frontHub':'interasse 100 mm; serraggio a dadi','rearHub':'flip-flop interasse 120 mm','drivetrain':'44x18; catena 1/2 x 1/8','wheels':'622x17C; copertoni 700x32','pedals':'Grip 520; interni da identificare','hubInternalInventory':'unknown','freewheelInternalInventory':'unknown'},
    'coverage':'Bicicletta intera ricostruita in Blender da specifiche pubbliche della Elops Speed 500: ruote, telaio, sterzo Ahead, trasmissione 44x18, freni, sella, pedali e accessori. Esempio pronto per test, non replica OEM completa fino a ogni vite: geometrie e minuteria sono approssimate; sfere dei mozzi, numero di raggi/maglie e fissaggi sono illustrativi. Interni ruota libera, cartuccia movimento, leve, luci e campanello restano gruppi. La fonte conferma allestimento e alcune misure, non quote CAD e inventario completo.','parts':parts,'procedures':procedures,'modelPath':'/models/elops-study-v1.glb'}],
    'bikes':[{'id':'elops-study-bike','name':'Elops Speed 500 · esempio 3D','brand':'Decathlon / ricostruzione Officina','category':'Città','subtype':'Singlespeed · esempio di studio','year':'Riferimento pubblico; anno non attribuito','structureId':'elops-study-v1','status':'reference','notes':'Esempio completo come vista della bici, con interni illustrativi e gruppi sigillati. Non è una distinta OEM verificata. Vedi i limiti e le fonti nelle schede.','color':'#53616b'}]}
(DEST/'source').mkdir(parents=True,exist_ok=True);(DEST/'web').mkdir(exist_ok=True)
(DEST/'catalog.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(DEST/'source/assembly.blend'))
print('Bici intera creata:',len(parts),'pezzi individuali')
