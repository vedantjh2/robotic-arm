"""A1: proximal actuator cassette, paired bone-inspired rails, two-axis remote wrist."""
from pathlib import Path
import json,math,csv
import numpy as np
import cadquery as cq
import trimesh
import build_cad as A0
R=Path(__file__).resolve().parents[1];P=json.loads((R/'cad/anatomy_parameters.json').read_text());H=A0.P.copy();H.update(P)
O=R/'output/A1';(O/'parts').mkdir(parents=True,exist_ok=True);(O/'assembly').mkdir(exist_ok=True)
PART={};INST=[];COL=A0.COL.copy();COL.update({'bone':'#e1d9c4','skin':'#b5c6cd','wrist':'#8fbbc2'})
box=A0.box;cyl=A0.cylinder;hole=A0.hole;tr=A0.translate;rot=A0.rot

def ry(d):
    a=math.radians(d);m=np.eye(4);m[0,0]=m[2,2]=math.cos(a);m[0,2]=math.sin(a);m[2,0]=-math.sin(a);return m

def part(k,s,material='PA12 / PETG',note=''):
    assert s.val().isValid(),k
    assert len(s.solids().vals())==1,(k,len(s.solids().vals()))
    PART[k]={'shape':s,'material':material,'note':note}
    cq.exporters.export(s,str(O/'parts'/f'{k}.step'))
    cq.exporters.export(s.translate((0,0,-s.val().BoundingBox().zmin)),str(O/'parts'/f'{k}.stl'),tolerance=.12,angularTolerance=.18)

def add(n,k,m=np.eye(4),kind='structure',group='fixed',visible=True):
    INST.append({'name':n,'key':k,'matrix':m.tolist(),'kind':kind,'group':group,'visible':visible})

# Reuse only the already checked modular finger and thumb parts.
for key in ['mcp_root','thumb_pivot_base','thumb_opposition_carrier']+[f'{d}_{i+1}' for d,ls in A0.P['finger_lengths'].items() for i in range(len(ls))]+[f'{d}_pad' for d in A0.P['finger_lengths']]:
    entry=A0.PARTS[key];part(key,entry['shape'],entry['material'],entry['note'])

outline=[(-25,0),(25,0),(34,18),(41,57),(42,76),(39,86),(20,92),(-6,95),(-32,90),(-42,80),(-45,55),(-57,47),(-60,27),(-48,17),(-34,11)]
palm=cq.Workplane('XY').polyline(outline).close().extrude(8).translate((0,0,-4))
# Longitudinal rib windows follow the metacarpal fan rather than a rectangular plate.
for x in (-21,0,21):
    slot=cq.Workplane('XY').center(x,45).slot2D(39,10,angle=90).extrude(12).translate((0,0,-6))
    palm=palm.cut(slot)
for d in ('index','middle','ring','little'):
    m=tr(A0.P['finger_x'][d],P['finger_root_y'][d],P['finger_root_z'][d])@rot('z',P['finger_splay_deg'][d])
    # Thin bosses compensate for a shallow transverse arch at the knuckle roots.
    z=P['finger_root_z'][d]-8.4
    if z>4.01:
        boss=box(18,10,z-4,(0,-11,(z+4)/2-P['finger_root_z'][d]))
        palm=palm.union(cq.Workplane(obj=A0.transform_shape(boss,m)))
    for x in (-5,5):
        q=m@np.array([x,-11,0,1]);palm=hole(palm,1.65,15,(q[0],q[1],-6))
palm=hole(palm,9.4,16,(-57,32,-8))
for x in (-48,-39):
    for y in (22,42):palm=hole(palm,1.65,12,(x,y,-6))
for x in (-28,28):palm=hole(palm,1.65,12,(x,22,-6))
for x in (-18,18):
    for y in (8,18):palm=hole(palm,1.65,12,(x,y,-6))
part('metacarpal_frame',palm,note='Contoured palm, staggered knuckles and longitudinal metacarpal ribs')

# A rounded section wire, approximated with short arcs, makes a manufacturable tapered skin.
def profile(y,w,h,r):
    pts=[]
    for cx,cz,start in ((w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)):
        for a in np.linspace(start,start+90,9):
            t=math.radians(a);pts.append(cq.Vector(cx+r*math.cos(t),y,cz+r*math.sin(t)))
    pts.append(pts[0]);return cq.Wire.makePolygon(pts)
sections=[(-253,90,70,12),(-144,88,68,12),(-120,68,52,11),(-55,58,40,10),(-35,56,36,9)]
outer=cq.Solid.makeLoft([profile(*s) for s in sections],True)
inner=cq.Solid.makeLoft([profile(y,w-6,h-6,max(3,r-3)) for y,w,h,r in sections],True)
skin=cq.Workplane(obj=outer.cut(inner))
# Each half is an editable shell. Seam fastening strips are added inside the radial edge.
for name,upper in [('dorsal_shell',False),('palmar_shell',True)]:
    half=skin.intersect(box(250,350,110,(0,-140,55 if upper else -55)))
    # Small seam tabs at wider proximal section, clear of the actuator envelopes.
    for x in (-39,39):
        for y in (-245,-148):
            tab=box(8,8,3,(x,y,1.5 if upper else -1.5))
            tab=hole(tab,1.65,8,(x,y,-4))
            # Radial skin taper at front means a tab at -148 still reaches the shell.
            half=half.union(tab)
    part(name,half,note='3 mm wall removable anatomical taper; M3 seam fasteners provisional')

# Eight motors in 2 opposing banks × 2 levels × 2 rows. All bodies in the proximal 84 mm.
positions=[]
for y in P['motor_body_centers_y']:
    for z in P['motor_levels_z']:
        for x in P['motor_banks_x']:positions.append((x,y,z))
cassette=box(4,110,58,(0,-196,0)).union(box(70,8,24,(0,-143,-10)))
cassette=cassette.union(box(76,8,60,(0,-255,0)))
for x in (-26,26):
    for z in (-18,18):cassette=hole(cassette,3.25,12,(x,-262,z),(0,1,0))
for x in (-22,22):cassette=hole(cassette,2.15,12,(x,-150,-10),(0,1,0))
for i,(x,y,z) in enumerate(positions):
    m=tr(x,y,z)@ry(90 if x>0 else -90)
    cradle=box(28,40,4,(0,0,-15))
    for dx in (-12,12):
        for dy in (-13,-3):
            cradle=cradle.union(box(3,6,26,(dx,dy,0)))
            cradle=hole(cradle,1.25,8,(dx,dy,7))
    cassette=cassette.union(cq.Workplane(obj=A0.transform_shape(cradle,m)))
part('proximal_motor_cassette',cassette,note='8 micro-servo cradles fused to central spine, proximal M6 mounting flange')
clamp=box(30,6,3,(0,0,14.5))
for x in (-12,12):clamp=hole(clamp,1.5,7,(x,0,11))
part('micro_servo_clamp',clamp,note='16 clamps; secure selected motor with compliant shim')

# Bone-inspired dual rails: actual load paths, not cosmetic floating anatomy.
for d,sgn in [('radius_rail',-1),('ulna_rail',1)]:
    wires=[];inside=[]
    for y,x,z,a,b in [(-139,22*sgn,-10,8,10),(-90,19*sgn,-8,6.5,8),(-35,17*sgn,-4,7,8)]:
        pl=cq.Plane(origin=(x,y,z),xDir=(1,0,0),normal=(0,1,0))
        wires.append(cq.Workplane(pl).ellipse(a,b).val());inside.append(cq.Workplane(pl).ellipse(a-3,b-3).val())
    rail=cq.Workplane(obj=cq.Solid.makeLoft(wires,False).cut(cq.Solid.makeLoft(inside,False)))
    # Solid end caps carry axial M4 fasteners; bores are through clearance, nuts are external.
    for y,x,z,a,b in [(-139,22*sgn,-10,8,10),(-39,17*sgn,-4,7,8)]:
        pl=cq.Plane(origin=(x,y,z),xDir=(1,0,0),normal=(0,1,0))
        cap=cq.Workplane(pl).ellipse(a+1,b+1).extrude(4)
        rail=rail.union(cap)
        rail=hole(rail,2.15,12,(x,y-4,z),(0,1,0))
    part(d,rail,note='Hollow 3 mm wall structural rail, capped ends with M4 axial attachment')

# Fixed radiocarpal fork. Flexion axis X, then deviation axis Z on the moving carpal ring.
wrist=box(50,14,16,(0,-28,-4))
for x in (-21,21):
    ear=box(8,24,16,(x,-12,0)).union(cyl(9,8,(x-4,0,0),(1,0,0)))
    wrist=wrist.union(ear)
    wrist=hole(wrist,4.1,10,(x-5,0,0),(1,0,0))
for x in (-17,17):wrist=hole(wrist,2.15,20,(x,-39,-4),(0,1,0))
for x in (-21,21):wrist=hole(wrist,1.5,20,(x,-28,-10))
part('radiocarpal_fork',wrist,note='5 mm D axle in 8 mm OD round bushings. Flexion about X. Fit bushings before loading')
gimbal=box(32,36,8,(0,0,0)).cut(box(20,24,12,(0,0,0)))
gimbal=gimbal.union(cyl(8,8,(0,12,-4)))
gimbal=hole(gimbal,4.1,14,(0,12,-7))
for x in (-13,13):
    bore=cyl(2.6,8,(x-4,0,0),(1,0,0)).intersect(box(12,12,12,(x,0,-3.9)))
    gimbal=gimbal.cut(bore)
    gimbal=hole(gimbal,1.5,12,(x,-12,0),(0,1,0))
part('carpal_gimbal',gimbal,note='Crossed-axis wrist simplification; radial/ulnar axis Z at y=12 mm')
carrier=cyl(16,2,(0,12,6)).union(cyl(14,4,(0,12,8))).union(cyl(16,2,(0,12,12)))
carrier=carrier.union(box(18,30,6,(0,27,11))).union(box(48,28,4,(0,51,14)))
# Carrier/palm contact at z16, palmar frame sits on this plane.
carrier=hole(carrier,2.6,14,(0,12,4))
for x in (-18,18):
    for y in (46,56):carrier=hole(carrier,1.65,12,(x,y,9))
for x in (-12,12):carrier=hole(carrier,.6,10,(x,12,6))
part('carpal_hand_carrier',carrier,note='14 mm opposed tendon sector, 4 mm bolt plate; palm bolts at ±18 mm')
sector=cyl(16,2,(-31,0,0),(1,0,0)).union(cyl(14,4,(-29,0,0),(1,0,0))).union(cyl(16,2,(-25,0,0),(1,0,0)))
sector=sector.cut(cyl(2.6,12,(-33,0,0),(1,0,0)).intersect(box(16,12,12,(-27,0,-3.9))))
sector=hole(sector,1.5,15,(-27,0,14),(0,0,-1))
for z in (-12,12):sector=hole(sector,.6,12,(-33,0,z),(1,0,0))
sector=sector.translate((-3,0,0))
part('wrist_flexion_sector',sector,note='14 mm opposing cord sector on clamped 5 mm shaft; D bore flat at 2.1 mm, M3 set screw; verify steel D shaft and grub screw torque capacity')

spool=cyl(8,3,(0,0,16)).union(cyl(10,1,(0,0,19))).union(cyl(8,3,(0,0,20))).union(cyl(10,1,(0,0,23)))
spool=hole(spool,2.1,12,(0,0,15))
for a in (0,90,180,270):
    t=math.radians(a);spool=hole(spool,1,12,(5.5*math.cos(t),5.5*math.sin(t),15))
spool=hole(spool,.6,6,(4,0,21),(1,0,0))
part('micro_tendon_spool',spool,note='6 finger/opposition spools; provisional 11 mm bolt circle, no guessed motor spline')
dual=cyl(8,1,(0,0,16)).union(cyl(10,1,(0,0,17)))
for h in (18,21):dual=dual.union(cyl(8,2,(0,0,h))).union(cyl(10,1,(0,0,h+2)))
dual=hole(dual,2.1,12,(0,0,15))
for a in (0,90,180,270):
    t=math.radians(a);dual=hole(dual,1,12,(5.5*math.cos(t),5.5*math.sin(t),15))
for h in (19,22):dual=hole(dual,.6,6,(4,0,h),(1,0,0))
part('wrist_dual_spool',dual,note='2 motors, each opposing pair winds in opposite directions; matched 8 mm groove radii')
# Retinaculum-inspired bridge and a hand-mounted reaction anchor.
ret=box(48,6,8,(0,-28,16))
for x in (-21,21):
    ret=ret.union(box(4,6,10,(x,-28,9)))
    ret=hole(ret,1.65,22,(x,-28,2))
for x in (-10,-6,-2,2,6,10):ret=hole(ret,1.65,10,(x,-33,16),(0,1,0))
part('tendon_retinaculum',ret,note='Distal tendon guide bridge, 3.3 mm guide holes; M3 feet bolt to fixed wrist fork')
anchor=box(78,6,14,(0,22,11))
for x in (-27.5,-16.5,-5.5,5.5,16.5,27.5):anchor=hole(anchor,3.3,10,(x,17,11),(0,1,0))
for x in (-28,28):anchor=hole(anchor,1.65,20,(x,22,1))
part('palmar_bowden_anchor',anchor,note='6 commercial M6 barrel adjusters with locknuts; moves with hand to isolate wrist motion')

# Assembly: hand components all share a wrist-parent rigid transform.
add('Proximal actuator cassette','proximal_motor_cassette')
add('Radius inspired rail','radius_rail',kind='bone')
add('Ulna inspired rail','ulna_rail',kind='bone')
add('Distal retinaculum','tendon_retinaculum',kind='wrist')
add('Dorsal forearm shell','dorsal_shell',kind='skin',visible=True)
add('Palmar forearm shell','palmar_shell',kind='skin',visible=False)
add('Radiocarpal fork','radiocarpal_fork',kind='wrist')
add('Carpal gimbal','carpal_gimbal',kind='wrist',group='wrist_flex')
add('Wrist flexion sector','wrist_flexion_sector',kind='spool',group='wrist_flex')
add('Carpal hand carrier','carpal_hand_carrier',kind='wrist',group='wrist_deviation')
rest=tr(*P['hand_rest_translation']);add('Metacarpal frame','metacarpal_frame',rest,'bone','hand')
add('Palmar tendon anchor','palmar_bowden_anchor',rest,'structure','hand')
CHAINS={}
for d,ls in A0.P['finger_lengths'].items():
    base=tr(A0.P['finger_x'][d],P['finger_root_y'][d],P['finger_root_z'][d])@rot('z',P['finger_splay_deg'][d]) if d!='thumb' else tr(*A0.P['thumb_pivot'])@rot('z',55)@tr(0,28,A0.P['thumb_root_height'])
    add(f'{d} root','mcp_root',rest@base,'structure',d)
    ch=[];m=base.copy()
    for i,L in enumerate(ls):
        key=f'{d}_{i+1}';add(f'{d} phalanx {i+1}',key,rest@m,'link',d);ch.append({'key':key,'length':L,'matrix':m.tolist()})
        keypin=f'pin_{d}_{i}';PART[keypin]=A0.PARTS[keypin];add(f'{d} hinge pin {i+1}',keypin,rest@m,'metal',d)
        if i==len(ls)-1:add(f'{d} contact pad',f'{d}_pad',rest@m,'pad',d)
        m=m@tr(0,L,0)
    CHAINS[d]={'base':base.tolist(),'links':ch}
add('Thumb pivot housing','thumb_pivot_base',rest@tr(*A0.P['thumb_pivot']),'structure','hand')
add('Thumb opposition carrier','thumb_opposition_carrier',rest@tr(*A0.P['thumb_pivot'])@rot('z',55),'spool','thumb')
PART['thumb_axle']=A0.PARTS['thumb_axle'];add('Thumb pivot axle','thumb_axle',rest@tr(*A0.P['thumb_pivot']),'metal','hand')
for k,s in [('flexion_axle',cyl(2.5,65,(-35,0,0),(1,0,0)).cut(box(70,10,10,(0,0,7)))),('deviation_axle',cyl(2.5,26,(0,12,-8)))]:
    PART[k]={'shape':s,'material':'Purchased steel','note':'5 mm axle / shoulder screw; heads and keepers omitted'};add(k,k,kind='metal',group='wrist_flex')
for i,(x,y,z) in enumerate(positions):
    m=tr(x,y,z)@ry(90 if x>0 else -90);key=f'micro_motor_{i}'
    PART[key]={'shape':box(20,34,26),'material':'Purchased XC330 envelope','note':'Shaft offset 8 mm and horn plane provisional; verify supplier drawing'}
    add(f'Motor M{i+1}',key,m,'motor');key='micro_tendon_spool' if i<6 else 'wrist_dual_spool';add(f'Spool M{i+1}',key,m@tr(0,8,0),'spool')
    for dy in (-13,-3):add(f'M{i+1} clamp {dy}','micro_servo_clamp',m@tr(0,dy,0))

ROUTES=[]
# Finger tendons run down the shaft, then in sheaths/service loops to hand-mounted endpoints.
channels=[-10,-6,-2,2,6,10]
for i,d in enumerate(('index','middle','ring','little','thumb')):
    x,y,z=positions[i];sgn=1 if x>0 else -1;ch=channels[i]
    pts=[[sgn*37,y+8,z+8],[sgn*34,y+25,z+8],[ch,-139,14],[ch,-65,12],[ch,-40,10],[ch,-15,25],[ch,15,31]]
    base=rest@np.array(CHAINS[d]['base']);dist=0
    for L in A0.P['finger_lengths'][d]:
        for q in (14,max(14,L-12)):pts.append((base@np.array([0,dist+q,7.5,1]))[:3].tolist())
        dist+=L
    pts.append((base@np.array([0,dist-3,5,1]))[:3].tolist())
    ROUTES.append({'name':f'{d} flexor','points':pts,'kind':'tendon','group':d,'hand_point_start':7})
    dist=0
    for k,L in enumerate(A0.P['finger_lengths'][d]):
        prev=-12 if k==0 else (dist-13 if A0.P['finger_lengths'][d][k-1]>=32 else dist-A0.P['finger_lengths'][d][k-1]+14)
        pts2=[(base@np.array([0,prev,-6,1]))[:3].tolist(),(base@np.array([0,dist+14,-6,1]))[:3].tolist()]
        ROUTES.append({'name':f'{d} return {k+1}','points':pts2,'kind':'return','group':d});dist+=L
x,y,z=positions[5];ROUTES.append({'name':'thumb opposition flexor','points':[[37,y+8,z+8],[28,-139,14],[10,-60,12],[10,-15,25],[-52,50,34],[-66,66,26]],'kind':'tendon','group':'thumb'})
# Opposed tendon pairs for wrist axes. Paths are schematic; sheaths isolate changing wrist geometry.
for i,label in [(6,'wrist flexion'),(7,'wrist deviation')]:
    x,y,z=positions[i];sgn=1 if x>0 else -1
    for side in (-1,1):
        end=[-30,0,side*14] if i==6 else [side*14,12,10]
        ROUTES.append({'name':label+(' A' if side<0 else ' B'),'points':[[sgn*39,y+8,z+side*8],[sgn*30,-143,side*10],[side*7,-70,side*9],[side*12,-24,side*10],end],'kind':'tendon','group':'wrist_flex'})

assy=cq.Assembly(name='Anatomy_Tendon_Hand_A1');scene=trimesh.Scene();meshes={};qty={}
for inst in INST:
    k=inst['key'];qty[k]=qty.get(k,0)+1
    if k not in meshes:
        vs,fs=PART[k]['shape'].val().tessellate(.2,.22);meshes[k]=trimesh.Trimesh(vertices=[v.toTuple() for v in vs],faces=fs,process=True)
    m=np.array(inst['matrix']);assy.add(A0.transform_shape(PART[k]['shape'],m),name=inst['name'].replace(' ','_'),color=cq.Color(*A0.rgb(COL[inst['kind']])))
    if inst['visible']:
        mesh=meshes[k].copy();mesh.visual.face_colors=[round(v*255) for v in A0.rgb(COL[inst['kind']])]+[255];scene.add_geometry(mesh,geom_name=inst['name'],node_name=inst['name'],transform=m)
assy.export(str(O/'assembly/anatomy_tendon_hand_A1.step'));scene.apply_scale(.001);(O/'assembly/anatomy_tendon_hand_A1.glb').write_bytes(scene.export(file_type='glb'))
report=[]
for k,e in PART.items():
    s=e['shape'].val();b=s.BoundingBox();report.append({'part':k,'quantity':qty.get(k,1),'material':e['material'],'note':e['note'],'solid_valid':s.isValid(),'solids':len(e['shape'].solids().vals()),'mesh_watertight':None if k not in meshes else bool(meshes[k].is_watertight),'volume_mm3':round(s.Volume(),2),'dimensions_mm':[round(b.xlen,2),round(b.ylen,2),round(b.zlen,2)]})
(O/'geometry_report.json').write_text(json.dumps(report,indent=2))
with (O/'parts_manifest.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['part','quantity','material','volume_mm3','note']);[w.writerow([a[k] for k in ['part','quantity','material','volume_mm3','note']]) for a in report]
data={'parameters':H,'colors':COL,'instances':INST,'routes':ROUTES,'chains':CHAINS,'meshes':{}}
for k,m in meshes.items():data['meshes'][k]={'vertices':np.round(m.vertices,3).reshape(-1).tolist(),'faces':m.faces.reshape(-1).tolist()}
(R/'viewer/model.json').write_text(json.dumps(data,separators=(',',':')));(O/'model.json').write_text(json.dumps(data,separators=(',',':')))
print(f'A1: {len(PART)} part definitions, {len(INST)} instances; 8 motors in proximal cassette, 2-axis wrist.',flush=True)
