"""Sample digital solid interference; not a physics, force, or durability test."""
from pathlib import Path
import json,math
import numpy as np
import cadquery as cq
from OCP.gp import gp_Trsf
R=Path(__file__).resolve().parents[1];D=json.loads((R/'viewer/model.json').read_text());P=D['parameters']
S={}
for inst in D['instances']:
    key=inst['key']
    if key in S or key.startswith(('motor_body','pin_')) or key=='thumb_axle':continue
    path=R/'output/parts'/f'{key}.step'
    if path.exists():S[key]=cq.importers.importStep(str(path)).val()
def tr(x,y,z):m=np.eye(4);m[:3,3]=[x,y,z];return m
def rot(axis,a):
    c=math.cos(math.radians(a));s=math.sin(math.radians(a));m=np.eye(4)
    if axis=='x':m[1:3,1:3]=[[c,-s],[s,c]]
    else:m[:2,:2]=[[c,-s],[s,c]]
    return m
def shape(key,m):
    g=gp_Trsf();g.SetValues(*[float(v) for v in m[:3,:4].reshape(-1)])
    return S[key].located(cq.Location(g))
def overlap(a,b):
    ba=a.BoundingBox();bb=b.BoundingBox()
    if any(getattr(ba,ax+'max')<=getattr(bb,ax+'min')+.01 or getattr(bb,ax+'max')<=getattr(ba,ax+'min')+.01 for ax in 'xyz'):return 0
    return a.intersect(b).Volume()
checks=[]
for curl,opp,thumb_curl,label in [(0,0,0,'open'),(0,.25,0,'opposition sweep 25%'),(0,.5,0,'opposition sweep 50%'),(0,.75,0,'opposition sweep 75%'),(0,1,0,'opposition sweep 100%'),(.25,.25,.25,'partial curl'),(.5,.5,.5,'half curl'),(.75,.65,.4,'power grasp'),(.48,.9,.48,'pinch'),(1,0,0,'fingers full curl, thumb spread'),(1,1,1,'excluded: simultaneous full curl / full opposition')]:
    items=[]
    for key in ('palm_frame','thumb_pivot_base','fixed_wrist_bridge'):
        m=tr(*P['thumb_pivot']) if key=='thumb_pivot_base' else np.eye(4)
        items.append((key,shape(key,m)))
    items.append(('thumb carrier',shape('thumb_opposition_carrier',tr(*P['thumb_pivot'])@rot('z',55-90*opp))))
    for digit,ch in D['chains'].items():
        base=np.array(ch['base']) if digit!='thumb' else tr(*P['thumb_pivot'])@rot('z',55-90*opp)@tr(0,28,P['thumb_root_height'])
        items.append((digit+' root',shape('mcp_root',base)))
        m=base.copy()
        for i,link in enumerate(ch['links']):
            angle=(P['max_thumb_flex_deg'] if digit=='thumb' else P['max_flex_deg'])[i]*(thumb_curl if digit=='thumb' else (.1*curl if label=='pinch' and digit!='index' else curl))
            m=m@rot('x',angle)
            items.append((link['key'],shape(link['key'],m)))
            m=m@tr(0,link['length'],0)
    hits=[]
    for i,(name,a) in enumerate(items):
        for name2,b in items[i+1:]:
            v=overlap(a,b)
            if v>.5:hits.append({'a':name,'b':name2,'intersection_mm3':round(v,2)})
    checks.append({'pose':label,'curl_fraction':curl,'thumb_curl_fraction':thumb_curl,'opposition_fraction':opp,'interferences':hits})
    print(f'curl {curl:.2f} opposition {opp:.2f}: {len(hits)} solid interferences',flush=True)
# Forearm static packaging: modeled parts only, purchased servo envelope separately.
items=[]
for inst in D['instances']:
    if inst['group']!='fixed' or inst['key']=='forearm_cover' or inst['key'].startswith(('pin_','thumb_')):continue
    if inst['key'].startswith('motor_body'):
        body=cq.Workplane().box(*P['motor_envelope']).translate((0,0,-3)).val()
        g=gp_Trsf();g.SetValues(*[float(v) for v in np.array(inst['matrix'])[:3,:4].reshape(-1)]);a=body.located(cq.Location(g))
    elif inst['key'] in S:a=shape(inst['key'],np.array(inst['matrix']))
    else:continue
    items.append((inst['name'],a))
hits=[]
for i,(n,a) in enumerate(items):
    for n2,b in items[i+1:]:
        v=overlap(a,b)
        if v>.5:hits.append({'a':n,'b':n2,'intersection_mm3':round(v,2)})
result={'method':'Exact BRep common volume, bounding-box prefilter; report overlap > 0.5 mm^3. Eleven illustrative hand poses, including an explicitly excluded self-contact pose. Pins, pads, hardware heads, elastic deformation and cords excluded. Does not prove all-motion clearance.','hand_pose_checks':checks,'forearm_open_static_interferences':hits}
(R/'output/motion_report.json').write_text(json.dumps(result,indent=2))
print(f'Forearm modeled-static interferences: {len(hits)}')
