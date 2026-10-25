"""Run in Blender: blender -b -P scripts/create_blender.py -- [assembled|exploded]
Imports CAD-derived STL meshes, assigns visual materials, camera and lights.
Blender 4.1+ recommended. All STL coordinates are millimetres.
"""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "build/meshes/manifest.json").read_text())
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
variant = args[0] if args else "assembled"
if variant not in manifest["variants"]:
    raise ValueError(f"Unknown variant: {variant}")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0

colors = {
    "foundation": (0.43, 0.44, 0.46, 1),
    "floor": (0.56, 0.43, 0.30, 1),
    "walls": (0.72, 0.51, 0.31, 1),
    "roof": (0.22, 0.27, 0.29, 1),
    "upper_bench": (0.83, 0.66, 0.42, 1),
    "lower_bench": (0.77, 0.59, 0.36, 1),
    "chair": (0.55, 0.38, 0.24, 1),
    "glazing": (0.26, 0.66, 0.74, 0.35),
}
for part, relative in manifest["variants"][variant].items():
    path = ROOT / relative
    if not path.exists() or path.stat().st_size == 0:
        continue
    # Blender 4.x native STL importer
    bpy.ops.wm.stl_import(filepath=str(path), global_scale=0.001)
    obj = bpy.context.object
    obj.name = part
    material = bpy.data.materials.new(part)
    material.diffuse_color = colors[part]
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = colors[part]
        principled.inputs["Roughness"].default_value = 0.65
        if part == "glazing":
            principled.inputs["Alpha"].default_value = 0.35
    obj.data.materials.append(material)

def point_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

bpy.ops.object.camera_add(location=(7, -8, 6))
camera = bpy.context.object
point_at(camera, (1.6, -0.1, 1.0))
camera.data.type = "ORTHO"
camera.data.ortho_scale = 8
scene.camera = camera
for loc, power in [((2, -4, 7), 1800), ((-3, 3, 5), 1100)]:
    bpy.ops.object.light_add(type="AREA", location=loc)
    light = bpy.context.object
    light.data.energy = power
    light.data.shape = "DISK"
    light.data.size = 5
    point_at(light, (1.5, 0, 1))
scene.render.engine = "CYCLES"
scene.cycles.samples = 32
scene.render.resolution_x = 1600
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
out = ROOT / "build" / "blender"
out.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out / f"gartensauna_{variant}.blend"))
scene.render.filepath = str(out / f"gartensauna_{variant}.png")
bpy.ops.render.render(write_still=True)
print("Saved Blender and render for", variant)
