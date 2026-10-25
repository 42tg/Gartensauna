"""Run in Blender: blender -b -P scripts/create_blender.py -- [assembled|exploded]
Imports CAD-derived STL meshes, assigns visual materials, camera and lights.
Blender 4.0+. All STL coordinates are millimetres.
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
scene["cad_source"] = manifest["source"]
scene["cad_variant"] = variant
scene["source_units"] = manifest["units"]
if manifest["units"] != "mm":
    raise ValueError("Expected CAD coordinates in millimetres")
cad_objects = []

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
        raise FileNotFoundError(f"Missing or empty CAD mesh: {path}")
    # Blender 4.x native STL importer
    bpy.ops.wm.stl_import(filepath=str(path), global_scale=0.001)
    obj = bpy.context.object
    obj.name = part
    obj["cad_source"] = manifest["source"]
    obj["cad_mesh"] = relative
    obj["cad_part"] = part
    cad_objects.append(obj)
    if not obj.data.vertices:
        raise ValueError(f"Empty imported mesh: {part}")
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

# Fit the complete CAD assembly, including exploded parts, without changing geometry.
bpy.context.view_layer.update()
corners = [obj.matrix_world @ Vector(corner) for obj in cad_objects for corner in obj.bound_box]
minimum = Vector([min(p[i] for p in corners) for i in range(3)])
maximum = Vector([max(p[i] for p in corners) for i in range(3)])
center = (minimum + maximum) * 0.5
bpy.ops.object.camera_add(location=center + Vector((-7, -9, 6)))
camera = bpy.context.object
point_at(camera, center)
camera.data.type = "ORTHO"
rotation = camera.rotation_euler.to_matrix().transposed()
projected = [rotation @ (p - center) for p in corners]
width = max(p.x for p in projected) - min(p.x for p in projected)
height = max(p.y for p in projected) - min(p.y for p in projected)
camera.data.ortho_scale = max(width, height * 1600 / 1100) * 1.18
scene.camera = camera
for loc, power in [((2, -4, 7), 1800), ((-3, 3, 5), 1100)]:
    bpy.ops.object.light_add(type="AREA", location=loc)
    light = bpy.context.object
    light.data.energy = power
    light.data.shape = "DISK"
    light.data.size = 5
    point_at(light, (1.5, 0, 1))
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
# Ubuntu's Blender package has no OpenImageDenoiser.
scene.cycles.use_denoising = False
for layer in scene.view_layers:
    layer.cycles.use_denoising = False
scene.cycles.samples = 64
scene.render.resolution_x = 1600
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
out = ROOT / "build" / "blender"
out.mkdir(parents=True, exist_ok=True)
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(out / f"gartensauna_{variant}.png")
bpy.ops.wm.save_as_mainfile(filepath=str(out / f"gartensauna_{variant}.blend"))
report = {
    "source": manifest["source"], "variant": variant, "units": "m",
    "parts": {obj.name: {"dimensions": list(obj.dimensions),
                         "mesh": obj["cad_mesh"]} for obj in cad_objects},
    "bounds_min": list(minimum), "bounds_max": list(maximum),
}
(out / f"gartensauna_{variant}.json").write_text(json.dumps(report, indent=2) + "\n")
bpy.ops.render.render(write_still=True)
print("Saved Blender and render for", variant)
