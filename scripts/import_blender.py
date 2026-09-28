"""Run in Blender's Scripting workspace or `blender --background --python scripts/import_blender.py`.
Builds editable named meshes, hinge rig, illustrative poses, tendon route curves and .blend.
"""
from pathlib import Path
import json, math
import bpy
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'viewer/model.json').read_text());P=D['parameters']
# Only replace this generator's collection; preserve unrelated scene objects.
old=bpy.data.collections.get('Tendon Hand '+P['revision'])
if old:
    for obj in list(old.all_objects):bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.collections.remove(old)
collection=bpy.data.collections.new('Tendon Hand '+P['revision']);bpy.context.scene.collection.children.link(collection)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='MILLIMETERS';scene.unit_settings.scale_length=1
materials={}
for name,color in D['colors'].items():
    mat=bpy.data.materials.new('A0 '+name);rgb=tuple(int(color[i:i+2],16)/255 for i in (1,3,5));mat.diffuse_color=(*rgb,1);materials[name]=mat
meshes={}
for key,data in D['meshes'].items():
    verts=list(zip(*(iter(data['vertices']),)*3));faces=list(zip(*(iter(data['faces']),)*3));mesh=bpy.data.meshes.new(key);mesh.from_pydata([tuple(v*.001 for v in p) for p in verts],[],faces);mesh.update();meshes[key]=mesh
objects={}
def matrix(a):
    m=Matrix(a);m.translation*=.001;return m
for inst in D['instances']:
    obj=bpy.data.objects.new(inst['name'],meshes[inst['key']]);collection.objects.link(obj);obj.matrix_world=matrix(inst['matrix']);obj.data.materials.clear();obj.data.materials.append(materials[inst['kind']]);obj.hide_render=not inst['visible'];obj.hide_set(not inst['visible']);objects[inst['name']]=obj

hand_rest=Matrix.Translation(tuple(v*.001 for v in P.get('hand_rest_translation',[0,0,0])))
def empty(name,world):
    o=bpy.data.objects.new(name,None);collection.objects.link(o);o.empty_display_type='ARROWS';o.empty_display_size=.008;o.matrix_world=world;return o

def parent_preserve(obj,parent):
    world=obj.matrix_world.copy();obj.parent=parent;obj.matrix_world=world
rigs={}
wrist_flex=wrist_dev=hand_root=None
if P['revision']=='A1':
    wrist_flex=empty('Wrist flexion axis',Matrix.Identity(4))
    wrist_dev=empty('Wrist deviation axis',Matrix.Translation((0,.012,0)));parent_preserve(wrist_dev,wrist_flex)
    hand_root=empty('Moving hand',hand_rest);parent_preserve(hand_root,wrist_dev)
    for inst in D['instances']:
        if inst['group']=='wrist_flex':parent_preserve(objects[inst['name']],wrist_flex)
        elif inst['group']=='wrist_deviation':parent_preserve(objects[inst['name']],wrist_dev)
        elif inst['group']=='hand' or inst['group'] in D['chains']:parent_preserve(objects[inst['name']],hand_root)
thumb_root=empty('Thumb opposition axis',hand_rest @ Matrix.Translation(tuple(v*.001 for v in P['thumb_pivot'])))
if hand_root:parent_preserve(thumb_root,hand_root)
parent_preserve(objects['Thumb opposition carrier'],thumb_root)
parent_preserve(objects['thumb root'],thumb_root)
for digit,ch in D['chains'].items():
    previous=thumb_root if digit=='thumb' else hand_root
    for i,link in enumerate(ch['links']):
        hinge=empty(f'{digit} hinge {i+1}',hand_rest @ matrix(link['matrix']))
        if previous:parent_preserve(hinge,previous)
        parent_preserve(objects[f'{digit} phalanx {i+1}'],hinge)
        parent_preserve(objects[f'{digit} hinge pin {i+1}'],hinge)
        rigs[(digit,i)]=hinge;previous=hinge
    parent_preserve(objects[f'{digit} contact pad'],previous)
# Objects are in meters; each hinge rotates about local X from its rest matrix.
rest={k:o.rotation_euler.copy() for k,o in rigs.items()};thumb_rest=thumb_root.rotation_euler.copy()
for frame,curl,opposition in ((1,0,0),(60,.75,.65),(120,0,0),(180,.48,.90),(240,0,0)):
    for (digit,i),o in rigs.items():
        digit_curl=.4 if frame==60 and digit=='thumb' else curl
        a=(P['max_thumb_flex_deg'] if digit=='thumb' else P['max_flex_deg'])[i]*digit_curl
        if frame==180 and digit not in ('index','thumb'):a*=.1
        o.rotation_euler=rest[(digit,i)].copy();o.rotation_euler.x+=math.radians(a);o.keyframe_insert(data_path='rotation_euler',frame=frame)
    thumb_root.rotation_euler=thumb_rest.copy();thumb_root.rotation_euler.z+=math.radians(-90*opposition);thumb_root.keyframe_insert(data_path='rotation_euler',frame=frame)
    if wrist_flex:
        wrist_flex.rotation_euler.x=math.radians(10 if frame==60 else 12 if frame==180 else 0);wrist_flex.keyframe_insert(data_path='rotation_euler',frame=frame)
        wrist_dev.rotation_euler.z=math.radians(5 if frame==180 else 0);wrist_dev.keyframe_insert(data_path='rotation_euler',frame=frame)
scene.frame_start=1;scene.frame_end=240;scene.frame_set(1)
for frame,label in ((1,'Open'),(60,'Illustrative power grasp'),(120,'Open'),(180,'Illustrative pinch'),(240,'Open')):scene.timeline_markers.new(label,frame=frame)
# Static schematic routes hidden by default: show only at rest for routing discussion.
for route in D['routes']:
    data=bpy.data.curves.new(route['name'],'CURVE');data.dimensions='3D';data.bevel_depth=.0004;data.bevel_resolution=2;spline=data.splines.new('POLY');spline.points.add(len(route['points'])-1)
    for p,co in zip(spline.points,route['points']):p.co=(*[v*.001 for v in co],1)
    obj=bpy.data.objects.new('Schematic '+route['name'],data);collection.objects.link(obj);data.materials.append(materials[route['kind']]);obj.hide_set(True);obj.hide_render=True
cam_data=bpy.data.cameras.new('A0 camera');cam=bpy.data.objects.new('A0 camera',cam_data);collection.objects.link(cam);cam.location=(.34,.17,.52);target=Matrix.Translation((0,-.032,.006)).translation;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam_data.type='ORTHO';cam_data.ortho_scale=.55;scene.camera=cam
for name,location,power,size in [('A0 key',(.1,.1,.5),50,.3),('A0 fill',(-.2,-.1,.2),25,.3)]:
    ld=bpy.data.lights.new(name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size;light=bpy.data.objects.new(name,ld);collection.objects.link(light);light.location=location;light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()
scene.render.resolution_x=1600;scene.render.resolution_y=1800;scene.render.resolution_percentage=100
scene['design_status']=P['revision']+' digital concept: motion is illustrative; motor/horn interfaces provisional. Not load-qualified.'
path=ROOT/'output/A1/assembly/anatomy_tendon_hand_A1.blend' if P['revision']=='A1' else ROOT/'output/assembly/tendon_hand_A0.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path));print('Saved',path)
