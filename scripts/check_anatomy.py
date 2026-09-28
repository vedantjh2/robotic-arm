from pathlib import Path
import json,math
import numpy as np
import cadquery as cq
from OCP.gp import gp_Trsf
R=Path(__file__).resolve().parents[1];O=R/'output/A1';D=json.loads((O/'model.json').read_text());P=D['parameters'];S={}
for inst in D['instances']:
 k=inst['key'];path=O/'parts'/f'{k}.step'
 if k not in S and path.exists():S[k]=cq.importers.importStep(str(path)).val()
def tr(x,y,z):m=np.eye(4);m[:3,3]=[x,y,z];return m
def rot(axis,a):
 c=math.cos(math.radians(a));s=math.sin(math.radians(a));m=np.eye(4)
 if axis=='x':m[1:3,1:3]=[[c,-s],[s,c]]
 else:m[:2,:2]=[[c,-s],[s,c]]
 return m
def transformed(s,m):
 g=gp_Trsf();g.SetValues(*[float(v) for v in m[:3,:4].reshape(-1)]);return s.located(cq.Location(g))
def overlap(a,b):
 aa=a.BoundingBox();bb=b.BoundingBox()
 if any(getattr(aa,x+'max')<=getattr(bb,x+'min')+.01 or getattr(bb,x+'max')<=getattr(aa,x+'min')+.01 for x in 'xyz'):return 0
 return a.intersect(b).Volume()
def pairs(items):
 hits=[]
 for i,(n,a) in enumerate(items):
  for n2,b in items[i+1:]:
   v=overlap(a,b)
   if v>.5:hits.append({'a':n,'b':n2,'volume_mm3':round(v,2)})
 return hits
# Verify motor body bounds separately from CAD vendor placeholders.
fixed=[]
for inst in D['instances']:
 if inst['group']!='fixed' or inst['key'] in ('dorsal_shell','palmar_shell'):continue
 k=inst['key'];m=np.array(inst['matrix'])
 s=cq.Workplane().box(*P['motor_envelope']).val() if k.startswith('micro_motor') else S.get(k)
 if s:fixed.append((inst['name'],transformed(s,m)))
fixedhits=pairs(fixed);print('Proximal/shaft packaging:',len(fixedhits),flush=True)
# Exact shell against stationary parts: detects whether the anatomy skin actually fits the cassette.
shellhits=[]
for skin in ('dorsal_shell','palmar_shell'):
 for n,s in fixed:
  v=overlap(S[skin],s)
  if v>.5:shellhits.append({'a':skin,'b':n,'volume_mm3':round(v,2)})
print('Shell clearance:',len(shellhits),flush=True)
poses=[('neutral',0,0,0,0,0),('flexion',40,0,0,0,0),('extension',-30,0,0,0,0),('radial',0,20,0,0,0),('ulnar',0,-20,0,0,0),('combined',25,15,0,0,0),('power',10,0,.75,.4,.65),('pinch',12,5,.48,.48,.9)]
reports=[]
for label,f,d,curl,tc,opp in poses:
 wf=rot('x',f);wd=wf@tr(0,12,0)@rot('z',d)@tr(0,-12,0);hand=wd@tr(*P['hand_rest_translation']);inv=np.linalg.inv(tr(*P['hand_rest_translation']));items=[]
 for inst in D['instances']:
  k=inst['key'];group=inst['group']
  if k not in S or k.endswith('_pad') or group in D['chains'] or k=='thumb_opposition_carrier':continue
  if group=='fixed' and k not in ('radiocarpal_fork','tendon_retinaculum'):continue
  m=np.array(inst['matrix'])
  if group=='wrist_flex':m=wf@m
  elif group=='wrist_deviation':m=wd@m
  elif group=='hand':m=hand@inv@m
  items.append((inst['name'],transformed(S[k],m)))
 for digit,ch in D['chains'].items():
  base=hand@(np.array(ch['base']) if digit!='thumb' else tr(*P['thumb_pivot'])@rot('z',55-90*opp)@tr(0,28,P['thumb_root_height']))
  items.append((digit+' root',transformed(S['mcp_root'],base)));m=base.copy()
  for i,link in enumerate(ch['links']):
   a=(P['max_thumb_flex_deg'] if digit=='thumb' else P['max_flex_deg'])[i]*(tc if digit=='thumb' else curl*(.1 if label=='pinch' and digit!='index' else 1));m=m@rot('x',a)
   items.append((link['key'],transformed(S[link['key']],m)));m=m@tr(0,link['length'],0)
 items.append(('Thumb opposition carrier',transformed(S['thumb_opposition_carrier'],hand@tr(*P['thumb_pivot'])@rot('z',55-90*opp))))
 hits=pairs(items);reports.append({'pose':label,'wrist_flexion_deg':f,'wrist_deviation_deg':d,'interferences':hits});print(label,len(hits),flush=True)
result={'method':'Exact BRep common volume > 0.5 mm^3, 8 wrist/hand poses. Hardware heads, deformable pads, tendons and sheath deformation excluded. This is a sampled geometry test, not a load or full workspace qualification.','fixed_packaging_interferences':fixedhits,'shell_interferences':shellhits,'pose_checks':reports}
(O/'motion_report.json').write_text(json.dumps(result,indent=2));print('Wrote A1 motion report',flush=True)
