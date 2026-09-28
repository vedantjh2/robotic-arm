# Anatomy-inspired tendon hand — A1

Current design: five-finger right hand with independently actuated fingers, eight motors in a proximal forearm cassette, two structural radius/ulna-inspired rails, removable tapered shell, and a two-axis wrist. A0 remains available as the first fixed-wrist layout.

## Open the design

- `viewer/index.html`: interactive CAD preview with independent finger controls, grasp poses, wrist motion, shell toggles and exploded view. The model is embedded; the Three.js library needs internet access. Open it in a browser, or use the local preview command below.
- `output/A1/assembly/anatomy_tendon_hand_A1.step`: editable solid assembly, in **millimeters**, including both shell halves. Import into FreeCAD, Fusion, SolidWorks or another STEP-compatible CAD tool. STEP preserves solids; the editable parameter source is the Python/JSON CAD generator.
- `output/A1/assembly/anatomy_tendon_hand_A1.glb`: colored cutaway assembly, in **meters**, for Blender and 3D viewers.
- `output/A1/parts/`: individual STEP and STL parts. STLs use millimeters and each part's lowest z is moved to zero; a slicer should orient and center it for the selected printing process.
- `docs/anatomy_revision_A1.md`: anatomy references, motor selection assumptions, tendon routing, power considerations, manufacturing notes and unresolved interfaces.
- `output/A1/parts_manifest.csv`: modeled parts, quantities, materials and interface notes.
- `output/A1/geometry_report.json`: CAD validity and mesh closure.
- `output/A1/motion_report.json`: sampled exact-solid interference checks.

## Parametric CAD and regeneration

Parameters: `cad/parameters.json` for the original finger mechanism and `cad/anatomy_parameters.json` for the A1 forearm, motor cassette and wrist. Python source: `scripts/build_cad.py` and `scripts/build_anatomy.py`.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/build_anatomy.py
.venv/bin/python scripts/check_anatomy.py
.venv/bin/python scripts/build_viewer.py
.venv/bin/python scripts/render_model.py
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/viewer/index.html`. `build_anatomy.py` reuses and regenerates the A0 finger mechanism before generating A1. The current preview always shows the last generated revision.

## Blender

Import the GLB for the colored cutaway geometry. For all named meshes, both shell halves, editable hinge parents and illustrative grasp/wrist animation, run `scripts/import_blender.py` in Blender's Scripting workspace, or:

```sh
blender --background --python scripts/import_blender.py
```

This writes `output/A1/assembly/anatomy_tendon_hand_A1.blend`. Blender was not installed in the authoring environment, so this scene-builder has been syntax-checked but not executed there. The provided STEP and GLB files were generated and inspected.

## Design status

A1 is a mechanical concept and CAD prototype, not a tested physical robot or an unconditional fabrication release. All generated solids were valid, all meshed assembly parts were watertight, and exact-solid checks found no interference in the stationary packaging, shell clearance and eight sampled wrist/grasp poses. This does not establish full workspace clearance or structural strength.

Before sending for manufacture: verify actual motor shaft/horn interfaces, detail mechanical range stops and shaft retention, select sheath ferrules and tensioners, check sheath bend radii through wrist travel, and validate printed material, joint loads, tendon friction, current limits and motor duty. Read the A1 notes before choosing a motor supply: the compact XC330 reference is 5 V-class; A0's XL430 power assumptions do not apply.

The VLM is a future task layer. No perception, motor control or NVIDIA integration is implemented in this hardware package.
