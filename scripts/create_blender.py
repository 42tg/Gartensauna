"""Run in Blender: blender -b -P scripts/create_blender.py -- [assembled|exploded|wall_detail|cutaway]
Imports CAD-derived STL meshes, assigns visual materials, camera and lights.
Blender 4.0+. All STL coordinates are millimetres.
"""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector
from math import radians
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cad_materials import material_for

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "build/meshes/manifest.json").read_text())
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
variant = args[0] if args else "assembled"
source_variant = "assembled" if variant == "heater_detail" else variant
if source_variant not in manifest["variants"]:
    raise ValueError(f"Unknown variant: {variant}")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
scene["cad_source"] = manifest["source"]
scene["cad_variant"] = source_variant
scene["presentation"] = variant
scene["source_units"] = manifest["units"]
if manifest["units"] != "mm":
    raise ValueError("Expected CAD coordinates in millimetres")
cad_objects = []

for part, relative in manifest["variants"][source_variant].items():
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
    for polygon in obj.data.polygons:
        polygon.use_smooth = False
    obj.data.materials.append(material_for(part))

if variant == "heater_detail":
    for obj in cad_objects:
        if not obj.name.startswith("heater_"):
            obj.hide_render = True
            obj.hide_set(True)

# Guard the published product envelope against mm/metre conversion regressions.
heater = bpy.data.objects.get("heater_cage")
if heater is not None:
    bpy.context.view_layer.update()
    for actual, expected in zip(heater.dimensions, (0.390, 0.335, 0.590)):
        if abs(actual - expected) > 0.002:
            raise ValueError(f"Heater envelope mismatch: {list(heater.dimensions)}")

# A presentation-only cutaway. Original imported meshes remain intact in the .blend.
# Roof and glass can be shown again; wall cuts are reversible Boolean modifiers.
if variant == "cutaway":
    hidden_parts = {"ceiling_boards", "ceiling_battens", "ceiling_vapour", "roof_wind", "roof_vent_battens", "roof_joists", "roof_insulation", "roof_deck",
                    "roof_covering", "roof_fascia", "glass_front", "glass_frame"}
    wall_parts = {"wall_cladding", "wall_battens", "wall_sheathing", "wind_barrier", "wall_studs",
                  "wall_insulation", "vapour_barrier", "service_battens", "interior_boards"}
    # CAD footprint is in metres here. Remove only the camera-facing facades.
    # Follow actual imported geometry when the changing room/wing moves.
    bpy.context.view_layer.update()
    def bounds(part):
        obj = bpy.data.objects[part]
        pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        return ([min(p[i] for p in pts) for i in range(3)],
                [max(p[i] for p in pts) for i in range(3)])
    floor_lo, floor_hi = bounds("floor_boards")
    glass_lo, glass_hi = bounds("glass_frame")
    ceiling_lo, _ = bounds("ceiling_boards")
    wing_x, wing_y = glass_lo[0], glass_lo[1]
    cut_h = ceiling_lo[2] + 0.02
    cuts = [((0, 0, -0.01), (wing_x+0.001, 0.206, cut_h)),
            ((wing_x-0.001, wing_y-0.001, -0.01),
             (floor_hi[0]-wing_x+0.002, 0.207, cut_h)),
            ((-0.001, 0, -0.01), (0.207, floor_hi[1]+0.001, cut_h))]
    # Cut disconnected sauna end first, then side, then changing-room facade.
    # The reverse order can reintroduce framing faces in Blender Boolean evaluation.
    cuts = [cuts[1], cuts[2], cuts[0]]
    cutters = []
    for index, (origin, size) in enumerate(cuts):
        bpy.ops.mesh.primitive_cube_add(size=1, location=Vector(origin)+Vector(size)*0.5)
        cutter = bpy.context.object
        cutter.name = f"Cutaway facade mask {index+1}"
        cutter.dimensions = size
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        cutter.hide_render = True
        cutter.hide_set(True)
        cutters.append(cutter)
    for obj in cad_objects:
        if obj.name in hidden_parts:
            obj.hide_render = True
            obj.hide_set(True)
        elif obj.name in wall_parts:
            for cutter in cutters:
                modifier = obj.modifiers.new(name=cutter.name, type="BOOLEAN")
                modifier.operation = "DIFFERENCE"
                modifier.solver = "EXACT"
                modifier.use_self = True
                modifier.use_hole_tolerant = True
                modifier.object = cutter
    # Test evaluated geometry: successful rendering alone can hide Boolean artifacts.
    bpy.context.view_layer.update()
    for obj in cad_objects:
        if obj.name not in wall_parts:
            continue
        evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        points = [obj.matrix_world @ mesh.vertices[i].co for face in mesh.polygons for i in face.vertices]
        assert points, (obj.name, "cutaway unexpectedly removed entire wall group")
        assert min(v.y for v in points) >= wing_y + .205 - .0001, (obj.name, "phantom front wall after Boolean cut")
        assert min(v.x for v in points) >= .205 - .0001, (obj.name, "phantom left wall after Boolean cut")
        assert not any(v.x < wing_x-.002 and v.y < .205-.0001 for v in points), (obj.name, "phantom changing-room facade")
        evaluated.to_mesh_clear()
    scene["cutaway_note"] = "Presentation only: roof, glazing and three garden-facing facade sections hidden. Disable wall Boolean modifiers to restore facades."

# Text is a visual annotation; exported CAD meshes remain unchanged.
if variant == "wall_detail":
    labels = ["1  Fassade / Bretter", "2  Hinterlueftung / Lattung", "3  Aussenplatte 15 mm", "4  Winddichtung",
              "5  Holzstaender 100 mm", "6  Daemmung 100 mm", "7  Alu-Dampfsperre",
              "8  Luft / Lattung 20 mm", "9  Saunaholz 19 mm"]
    for i, label in enumerate(labels):
        bpy.ops.object.text_add(location=(i*1.4, -0.06, 2.58), rotation=(radians(90), 0, 0))
        obj = bpy.context.object
        obj.data.body = label
        obj.data.size = 0.075
        obj.name = label
        text_material = bpy.data.materials.new("Label ink")
        text_material.diffuse_color = (0.015, 0.02, 0.025, 1)
        obj.data.materials.append(text_material)

def point_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

# Fit the complete CAD assembly, including exploded parts, without changing geometry.
bpy.context.view_layer.update()
corners = [obj.matrix_world @ Vector(corner) for obj in cad_objects if not obj.hide_render for corner in obj.bound_box]
minimum = Vector([min(p[i] for p in corners) for i in range(3)])
maximum = Vector([max(p[i] for p in corners) for i in range(3)])
center = (minimum + maximum) * 0.5
bpy.ops.object.camera_add(location=center + Vector((2, -12, 4) if variant == "wall_detail" else (-7, -10, 6 if variant == "assembled" else 8)))
camera = bpy.context.object
point_at(camera, center)
camera.data.type = "ORTHO"
rotation = camera.rotation_euler.to_matrix().transposed()
projected = [rotation @ (p - center) for p in corners]
width = max(p.x for p in projected) - min(p.x for p in projected)
height = max(p.y for p in projected) - min(p.y for p in projected)
camera.data.ortho_scale = max(width, (height + (0.4 if variant == "wall_detail" else 0)) * 1600 / 1100) * 1.18
scene.camera = camera
for loc, power in [((2, -4, 7), 1800), ((-3, 3, 5), 1100)]:
    bpy.ops.object.light_add(type="AREA", location=loc)
    light = bpy.context.object
    light.data.energy = power
    light.data.shape = "DISK"
    light.data.size = 5
    point_at(light, (1.5, 0, 1))
# Neutral studio ground and daylight make material surfaces legible.
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.65, 0.72, 0.82, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.45
bpy.ops.mesh.primitive_plane_add(size=200, location=(center.x, center.y, minimum.z-0.06))
ground = bpy.context.object
mat = bpy.data.materials.new("Studio floor")
mat.diffuse_color = (0.24, 0.27, 0.25, 1)
ground.data.materials.append(mat)
bpy.ops.object.light_add(type="SUN", location=(0, -5, 8))
bpy.context.object.rotation_euler = (radians(25), radians(-20), radians(-25))
bpy.context.object.data.energy = 1.5
bpy.context.object.data.angle = radians(12)
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
# Ubuntu's Blender package has no OpenImageDenoiser.
scene.cycles.use_denoising = False
for layer in scene.view_layers:
    layer.cycles.use_denoising = False
scene.cycles.samples = 64
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.045
scene.cycles.transparent_max_bounces = 8
scene.render.resolution_x = 1600
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
out = ROOT / "build" / "blender"
out.mkdir(parents=True, exist_ok=True)
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(out / f"gartensauna_{variant}.png")
bpy.ops.wm.save_as_mainfile(filepath=str(out / f"gartensauna_{variant}.blend"))
report = {
    "source": manifest["source"], "variant": variant, "source_variant": source_variant, "units": "m",
    "parts": {obj.name: {"dimensions": list(obj.dimensions),
                         "mesh": obj["cad_mesh"], "hidden_in_render": obj.hide_render,
                         "bounds_min": [min((obj.matrix_world @ Vector(c))[i] for c in obj.bound_box) for i in range(3)],
                         "bounds_max": [max((obj.matrix_world @ Vector(c))[i] for c in obj.bound_box) for i in range(3)],
                         "cutaway_modifiers": len(obj.modifiers)} for obj in cad_objects},
    "bounds_min": list(minimum), "bounds_max": list(maximum),
}
(out / f"gartensauna_{variant}.json").write_text(json.dumps(report, indent=2) + "\n")
bpy.ops.render.render(write_still=True)
print("Saved Blender and render for", variant)


