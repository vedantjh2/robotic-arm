"""A0 tendon hand concept. mm. CAD source, not a qualified production design."""
from pathlib import Path
import json, math, csv
import numpy as np
import cadquery as cq
import trimesh

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT/'cad/parameters.json').read_text())
OUT = ROOT/'output'
for sub in ('parts','assembly','renders'):(OUT/sub).mkdir(parents=True,exist_ok=True)
PARTS = {}
COL = {'structure': '#d9e5eb', 'link': '#77afbb', 'motor': '#253947', 'metal': '#a2b6bf', 'spool':'#dfac56', 'tendon':'#e66c3b', 'return':'#69ad80', 'pad':'#485969', 'cover':'#b8ced7'}

def box(w,l,h,center=(0,0,0)):
    return cq.Workplane('XY').box(w,l,h).translate(center)

def cylinder(radius,length,origin,direction=(0,0,1)):
    return cq.Workplane(obj=cq.Solid.makeCylinder(radius,length,cq.Vector(*origin),cq.Vector(*direction)))

def hole(obj,r,length,origin,direction=(0,0,1)):
    return obj.cut(cylinder(r,length,origin,direction))

def part(name,shape,material='PETG / PA12',note=''):
    assert shape.val().isValid(), name
    assert len(shape.solids().vals())==1, (name,len(shape.solids().vals()))
    PARTS[name]={'shape':shape, 'material':material, 'note':note}
    cq.exporters.export(shape,str(OUT/'parts'/f'{name}.step'))
    # Export single parts in a stable manufacturing coordinate system, lowest z = 0.
    zmin=shape.val().BoundingBox().zmin
    cq.exporters.export(shape.translate((0,0,-zmin)),str(OUT/'parts'/f'{name}.stl'),tolerance=0.10,angularTolerance=0.16)
    return name

def fork(y=0):
    # Ear clearance 0.4 mm per side about 8.2 mm lug. Steel pin never printed.
    f=None
    for x in (-6.75,6.75):
        e=box(4.5,10,8,(x,y-5,0)).union(cylinder(6,4.5,(x-2.25,y,0),(1,0,0)))
        f=e if f is None else f.union(e)
    # Dorsal rail joins ears; riser supports next body's underside at zero flexion.
    f=f.union(box(18,6,8,(0,y-9,0)))
    f=f.union(box(8.0,21,2,(0,y-0.5,-7.4))).union(box(8,6,4,(0,y-9,-5.4)))
    f=f.union(box(8.0,3,4.4,(0,y+8.5,-6.2)))
    return hole(f,P['pin_bore']/2,24,(-12,y,0),(1,0,0))

def guide(obj,y):
    g=box(6,5,7.5,(0,y,6.75))
    g=hole(g,P['tendon_guide_bore']/2,7,(0,y-3.5,7.5),(0,1,0))
    return obj.union(g)

def return_eye(obj,y):
    # Transverse dorsal loop hole for one elastic return per joint.
    e=box(7,5,5,(0,y,-5.5))
    e=hole(e,1.1,9,(-4.5,y,-6.0),(1,0,0))
    return obj.union(e)

def link(length,tip=False):
    s=cylinder(6,8.2,(-4.1,0,0),(1,0,0)).union(box(8.2,12,8,(0,6,0)))
    end=length+3 if tip else length-8
    s=s.union(box(18,end-8,8,(0,(end+8)/2,0)))
    if not tip: s=s.union(fork(length))
    else:
        # End cap and transverse tendon anchor: cord is looped around a removable pin.
        s=s.union(box(14,6,8,(0,length,0)))
        s=hole(s,1.15,20,(-10,length-3,1.0),(1,0,0))
        s=s.cut(box(8,5,4,(0,length-3,5)))
    s=hole(s,P['pin_bore']/2,12,(-6,0,0),(1,0,0))
    s=guide(s,14)
    if length>28: s=guide(s,length-12)
    s=return_eye(s,14)
    if not tip and length>=32: s=return_eye(s,length-13)
    return s

root=fork().union(box(18,9,8,(0,-11,0))).union(box(18,10,4.4,(0,-11,-6.2)))
for x in (-5,5): root=hole(root,1.65,14,(x,-11,-7))
root=guide(root,-10)
root=return_eye(root,-12)
part('mcp_root',root,note='4 finger roots + 1 thumb root; M3 through bolts')
for digit,lengths in P['finger_lengths'].items():
    for i,L in enumerate(lengths):
        part(f'{digit}_{i+1}',link(L,i==len(lengths)-1))
    L=lengths[-1]
    pad=box(14,max(8,L-13),2,(0,(L+13)/2,5.2))
    part(f'{digit}_pad',pad,'TPU / silicone', 'Bond to distal palmar face; trim clear of tendon anchor')

palm=box(P['palm_width'],82,8,(0,41,0))
# Service windows reduce mass without cutting the MCP and wrist bolt ligaments.
for x in (-22,0,22): palm=palm.cut(box(13,36,12,(x,43,0)))
for x in P['finger_x'].values():
    for dx in (-5,5): palm=hole(palm,1.65,12,(x+dx,78,-6))
for x in (-30,30):
    for y in (8,18): palm=hole(palm,1.65,12,(x,y,-6))
# Thumb support side ledge.
palm=palm.union(box(22,28,8,(-48,32,0)))
palm=hole(palm,9.4,16,(-57,32,-8))
for x in (-48,-39):
    for y in (22,42): palm=hole(palm,1.65,12,(x,y,-6))
part('palm_frame',palm)

# Thumb vertical-axis pivot on radial side, outside finger flexion sweep.
thumbbase=box(26,28,5,(8,0,-6.5)).union(cylinder(9,11,(0,0,-4)))
thumbbase=hole(thumbbase,2.65,25,(0,0,-12))
# Attachment relative to pivot (-57,32).
for x in (9,18):
    for y in (-10,10): thumbbase=hole(thumbbase,1.65,15,(x,y,-11))
part('thumb_pivot_base',thumbbase,note='M5 axle; design mechanical opposition stops after thumb sweep verification')
carrier=cylinder(14,4,(0,0,7.4))
carrier=hole(carrier,2.65,8,(0,0,5))
carrier=carrier.union(box(18,25,5,(0,12.5,9.9))).union(box(18,12,12,(0,17,18.4)))
for x in (-5,5): carrier=hole(carrier,1.65,25,(x,17,6))
# Cylindrical sector acts as a tendon take-up drum; two cord anchors for flexor / elastic.
for y in (-8,8): carrier=hole(carrier,1.1,8,(9,y,6))
part('thumb_opposition_carrier',carrier,note='12 mm nominal tendon lever; carrier height separates CMC and MCP')

# Wrist riser bolts palm to tray; fixed wrist in A0.
bridge=box(82,42,16,(0,1,-12))
bridge=bridge.cut(box(40,42,10,(0,1,-15))).cut(box(12,8,20,(-41.5,21,-12)))
for x in (-30,30):
    for y in (-14,-6,8,18): bridge=hole(bridge,1.65,24,(x,y,-25))
part('fixed_wrist_bridge',bridge)

motor_positions=[(-23,-44),(23,-44),(-23,-113),(23,-113),(-23,-182),(23,-182)]
tray=box(106,240,6,(0,-120,-23))
for x in (-51,51): tray=tray.union(box(4,240,60,(x,-120,10)))
for x in (-30,30):
    for y in (-14,-6): tray=hole(tray,1.65,12,(x,y,-29))
# Floor ventilation, each row clear of motor seats and clamp columns.
for y in (-78,-147,-216):
    tray=tray.cut(box(48,12,10,(0,y,-23)))
# Integral four-post cradles secure body without assuming vendor threaded-hole patterns.
for x,y in motor_positions:
    for dx in (-19,19):
        for dy in (-18,-6):
            tray=tray.union(box(5,7,35,(x+dx,y+dy,-2.5)))
            tray=hole(tray,1.5,11,(x+dx,y+dy,5))
    # Shallow side locating rails leave a nominal 0.5 mm body clearance on each side.
    for dx in (-16,16): tray=tray.union(box(2.5,42,4,(x+dx,y,-18)))
# Guide comb mounts on side rails and guide feet.
for y in (-14,-83,-152):
    for x in (-46,46):
        tray=tray.union(box(6,8,51,(x,y,5.5)))
        tray=hole(tray,1.5,10,(x,y,22))
# Proximal mounting flange is connected to base and side rails.
tray=tray.union(box(110,8,72,(0,-244,4)))
for x in (-38,38):
    for z in (-18,26): tray=hole(tray,3.25,12,(x,-251,z),(0,1,0))
# Cover screw holes.
for x in (-51,51):
    for y in (-32,-101,-170,-230): tray=hole(tray,1.3,12,(x,y,30))
part('forearm_chassis',tray,note='Large part 110 x 248 x 72 mm; industrial print or split in downstream CAD')
strap=box(43,7,3,(0,0,16.5))
for x in (-19,19): strap=hole(strap,1.65,8,(x,0,12))
part('motor_clamp',strap,note='12 clamps; thin elastomer shim under each; verify body clearance')
comb=box(98,6,9,(0,0,35.5))
for x in (-46,46): comb=hole(comb,1.65,14,(x,0,28))
channels=[-35,-21,-7,7,21,35]
for x in channels: comb=hole(comb,2.2,9,(x,-4.5,36),(0,1,0))
part('bowden_comb',comb,note='2 intermediate combs; 4 mm OD lined sheaths')
anchor=box(98,6,14,(0,0,38))
for x in (-46,46): anchor=hole(anchor,1.65,18,(x,0,29))
for x in channels: anchor=hole(anchor,3.3,9,(x,-4.5,38),(0,1,0))
part('bowden_anchor',anchor,note='6 commercial M6 cable barrel adjusters + opposing locknuts; 6.6 mm clearance holes')
cover=box(106,240,3,(0,-120,41.5)).cut(box(98,10,8,(0,-14,41.5)))
for y in range(-215,-20,15):
    for x in (-26,26): cover=cover.cut(box(28,5,6,(x,y,41.5)))
for x in (-51,51):
    for y in (-32,-101,-170,-230): cover=hole(cover,1.65,8,(x,y,38))
part('forearm_cover',cover,note='Optional removable cover; shown hidden in assembly preview')

r=P['spool_radius']; rf=P['spool_flange_radius']
spool=cylinder(12,5,(0,0,17)).union(cylinder(rf,1.5,(0,0,22)))
spool=spool.union(cylinder(r,3,(0,0,23.5))).union(cylinder(rf,1.5,(0,0,26.5)))
spool=hole(spool,P['horn_pilot_diameter']/2,14,(0,0,16))
for a in range(0,360,90):
    t=math.radians(a);x=P['horn_bolt_circle_radius']*math.cos(t);y=P['horn_bolt_circle_radius']*math.sin(t)
    spool=hole(spool,1.1,14,(x,y,16))
    spool=hole(spool,1.9,2,(x,y,26.2))
spool=hole(spool,.65,8,(r-4,0,24.8),(1,0,0))
part('tendon_spool',spool,note='6 spools. Horn bolt pattern PROVISIONAL. 24 mm core, 30 mm flange')

# Coupon makes tolerances reviewable without printing an entire hand.
coupon=box(55,28,5,(0,0,2.5))
for i,d in enumerate((2.8,3.0,3.2,3.3,3.4)):
    coupon=hole(coupon,d/2,8,(-20+i*10,-5,-1))
for i,d in enumerate((2.2,2.4,2.6,2.8)):
    coupon=hole(coupon,d/2,8,(-15+i*10,7,-1))
part('fit_coupon',coupon,note='First row bores 2.8/3.0/3.2/3.3/3.4; second 2.2/2.4/2.6/2.8 mm')

# Rigid transforms shared by CAD, mesh preview and motion inspection.
def translate(x,y,z):
    t=np.eye(4);t[:3,3]=[x,y,z];return t

def rot(axis,a):
    a=math.radians(a);c=math.cos(a);s=math.sin(a);m=np.eye(4)
    if axis=='x':m[1:3,1:3]=[[c,-s],[s,c]]
    if axis=='z':m[:2,:2]=[[c,-s],[s,c]]
    return m

def transform_shape(s,m):
    # CadQuery rigid Location avoids general affine transforms / spline conversion.
    from OCP.gp import gp_Trsf
    g=gp_Trsf();g.SetValues(*[float(v) for v in m[:3,:4].reshape(-1)])
    return s.val().located(cq.Location(g))

def rgb(hexcolor):return tuple(int(hexcolor[i:i+2],16)/255 for i in (1,3,5))

INST=[]

def add(name,key,m=np.eye(4),kind='structure',group='fixed',visible=True):
    INST.append({'name':name,'key':key,'matrix':m.tolist(),'kind':kind,'group':group,'visible':visible})

add('Forearm chassis','forearm_chassis')
add('Wrist bridge','fixed_wrist_bridge')
add('Palm frame','palm_frame')
add('Forearm cover','forearm_cover',kind='cover',visible=False)
for j,y in enumerate((-83,-152)):add(f'Sheath comb {j+1}','bowden_comb',translate(0,y,0))
add('Adjustable sheath anchor','bowden_anchor',translate(0,-14,0))
for i,(x,y) in enumerate(motor_positions):
    key=f'motor_body_{i}'
    PARTS[key]={'shape':box(28.5,46.5,34,(0,0,-3)),'material':'Purchased','note':'Simplified verified body envelope; provisional shaft origin'}
    add(f'Motor M{i+1}',key,translate(x,y,0),'motor')
    add(f'Spool M{i+1}','tendon_spool',translate(x,y+P['motor_axis_y_offset'],0),'spool')
    for dy in (-18,-6):add(f'M{i+1} clamp {dy}','motor_clamp',translate(x,y+dy,0))

# Hand transforms: flexion into +z. Thumb swivel about +z, fixed cant about x.
FINGER_CHAINS={}
for digit,lengths in P['finger_lengths'].items():
    if digit!='thumb': base=translate(P['finger_x'][digit],P['finger_root_y'],12.4)
    else:base=translate(*P['thumb_pivot'])@rot('z',55)@translate(0,28,P['thumb_root_height'])
    add(f'{digit} root','mcp_root',base,'structure',digit)
    chain=[];distance=0
    for i,L in enumerate(lengths):
        m=base@translate(0,distance,0)
        add(f'{digit} phalanx {i+1}',f'{digit}_{i+1}',m,'link',digit)
        chain.append({'key':f'{digit}_{i+1}','length':L,'matrix':m.tolist()})
        pin_key=f'pin_{digit}_{i}'
        PARTS[pin_key]={'shape':cylinder(1.5,22,(-11,0,0),(1,0,0)),'material':'Purchased steel','note':'Simplified pin. Retention hardware not modeled'}
        add(f'{digit} hinge pin {i+1}',pin_key,m,'metal',digit)
        distance+=L
    add(f'{digit} contact pad',f'{digit}_pad',m,'pad',digit)
    FINGER_CHAINS[digit]={'base':base.tolist(),'links':chain}
add('Thumb pivot housing','thumb_pivot_base',translate(*P['thumb_pivot']))
add('Thumb opposition carrier','thumb_opposition_carrier',translate(*P['thumb_pivot'])@rot('z',55),'spool','thumb')
PARTS['thumb_axle']={'shape':cylinder(2.5,30,(0,0,-14)),'material':'Purchased steel','note':'M5 shoulder screw + washer + locknut'}
add('Thumb pivot axle','thumb_axle',translate(*P['thumb_pivot']),'metal','thumb')

# Display tendons are explicit schematic routes, not solid printable parts.
ROUTES=[]
for i,digit in enumerate(('index','middle','ring','little','thumb')):
    x,y=motor_positions[i];ch=channels[i]
    pts=[[x+r,y+P['motor_axis_y_offset'],25],[x+r,y+34,36],[ch,y+42,36],[ch,-14,38],[ch,12,25]]
    base=np.array(FINGER_CHAINS[digit]['base']);dist=0
    for k,L in enumerate(P['finger_lengths'][digit]):
        for q in (14,max(14,L-12)):
            v=base@np.array([0,dist+q,7.5,1]);pts.append(v[:3].tolist())
        dist+=L
    v=base@np.array([0,dist-3,5,1]);pts.append(v[:3].tolist())
    ROUTES.append({'name':f'{digit} flexor','points':pts,'kind':'tendon','group':digit})
    dist=0
    for k,L in enumerate(P['finger_lengths'][digit]):
        a=base@np.array([0,dist-12 if k==0 else dist-13 if P['finger_lengths'][digit][k-1]>=32 else dist-P['finger_lengths'][digit][k-1]+14,-6,1]);b=base@np.array([0,dist+14,-6,1])
        ROUTES.append({'name':f'{digit} return {k+1}','points':[a[:3].tolist(),b[:3].tolist()],'kind':'return','group':digit})
        dist+=L
x,y=motor_positions[5]
ROUTES.append({'name':'thumb opposition flexor','points':[[x+r,y+10.5,25],[35,y+40,36],[35,-14,38],[-52,12,18],[-66,28,10]],'kind':'tendon','group':'thumb'})
ROUTES.append({'name':'thumb opposition return','points':[[-42,40,1],[-48,44,10]],'kind':'return','group':'thumb'})

# CAD assembly includes solid parts only; routes intentionally excluded to keep solids editable.
assy=cq.Assembly(name='TendonHand_A0')
scene=trimesh.Scene();meshes={};quantities={}
for inst in INST:
    if inst['key'] not in meshes:
        verts,tri=PARTS[inst['key']]['shape'].val().tessellate(.18,.22)
        mesh=trimesh.Trimesh(vertices=[v.toTuple() for v in verts],faces=tri,process=True)
        meshes[inst['key']]=mesh
    quantities[inst['key']]=quantities.get(inst['key'],0)+1
    m=np.array(inst['matrix'])
    shape=transform_shape(PARTS[inst['key']]['shape'],m)
    assy.add(shape,name=inst['name'].replace(' ','_'),color=cq.Color(*rgb(COL[inst['kind']])))
    if inst['visible']:
        mesh=meshes[inst['key']].copy();mesh.visual.face_colors=[int(c*255) for c in rgb(COL[inst['kind']])]+[255]
        scene.add_geometry(mesh,geom_name=inst['name'],node_name=inst['name'],transform=m)
assy.export(str(OUT/'assembly'/'tendon_hand_A0.step'))
# GLB units meters, explicitly scale once and preserve assembly in STEP mm.
scene_m=scene.copy();scene_m.apply_scale(.001)
(OUT/'assembly'/'tendon_hand_A0.glb').write_bytes(scene_m.export(file_type='glb'))

report=[]
for key,entry in PARTS.items():
    s=entry['shape'].val();bb=s.BoundingBox()
    mesh=meshes.get(key)
    report.append({'part':key,'solid_valid':s.isValid(),'solids':len(entry['shape'].solids().vals()),'volume_mm3':round(s.Volume(),2),'dimensions_mm':[round(bb.xlen,2),round(bb.ylen,2),round(bb.zlen,2)],'mesh_watertight':None if mesh is None else bool(mesh.is_watertight),'quantity':quantities.get(key,1),'material':entry['material'],'note':entry['note']})
(OUT/'geometry_report.json').write_text(json.dumps(report,indent=2))
with (ROOT/'docs'/'parts_manifest.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['part','quantity','material','volume_mm3','note'])
    for row in report:w.writerow([row['part'],row['quantity'],row['material'],row['volume_mm3'],row['note']])

# Store indexed meshes once for a lightweight inspectable browser preview.
data={'parameters':P,'colors':COL,'instances':INST,'routes':ROUTES,'chains':FINGER_CHAINS,'meshes':{}}
for key,mesh in meshes.items():
    data['meshes'][key]={'vertices':np.round(mesh.vertices,3).reshape(-1).tolist(),'faces':mesh.faces.reshape(-1).tolist()}
(ROOT/'viewer'/'model.json').write_text(json.dumps(data,separators=(',',':')))
print(f'Exported {len(report)} part definitions; {len(INST)} assembly instances. STEP + STL + GLB.')
