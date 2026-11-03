"""Procedural construction materials; visual only, no change to CAD geometry."""
import bpy

def material_for(part):
    part = {"ceiling_vapour": "vapour_barrier", "roof_wind": "wind_barrier"}.get(part, part)
    material = bpy.data.materials.new(part)
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = 0.48
    if part.startswith("vent_"):
        bsdf.inputs["Base Color"].default_value = {"vent_supply": (0.08,0.35,0.52,1), "vent_exhaust": (0.55,0.18,0.06,1), "vent_drying": (0.22,0.24,0.26,1)}[part]
        bsdf.inputs["Metallic"].default_value = 0.7
        return material
    if part in ("heater_cage", "heater_mount"):
        bsdf.inputs["Base Color"].default_value = (0.42, 0.46, 0.49, 1)
        bsdf.inputs["Metallic"].default_value = 0.95
        bsdf.inputs["Roughness"].default_value = 0.27
        return material
    if part == "glass_front":
        bsdf.inputs["Base Color"].default_value = (0.92, 0.98, 0.97, 1)
        bsdf.inputs["Transmission Weight"].default_value = 1
        bsdf.inputs["IOR"].default_value = 1.45
        bsdf.inputs["Roughness"].default_value = 0.055
        return material
    if part in ("glass_frame", "roof_covering", "wind_barrier", "vapour_barrier"):
        color = {"glass_frame": (0.035,0.045,0.05,1), "roof_covering": (0.045,0.05,0.055,1),
                 "wind_barrier": (0.09,0.11,0.12,1), "vapour_barrier": (0.7,0.72,0.75,1)}[part]
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Metallic"].default_value = 0.9 if part in ("glass_frame","vapour_barrier") else 0
        bsdf.inputs["Roughness"].default_value = 0.32 if part == "vapour_barrier" else 0.62
        return material
    tex = nodes.new("ShaderNodeTexCoord")
    scale = nodes.new("ShaderNodeVectorMath")
    scale.operation = "MULTIPLY"
    links.new(tex.outputs["Object"], scale.inputs[0])
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 1
    noise.inputs["Detail"].default_value = 4
    noise.inputs["Roughness"].default_value = 0.7
    links.new(scale.outputs[0], noise.inputs["Vector"])
    ramp = nodes.new("ShaderNodeValToRGB")
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.22
    bump.inputs["Distance"].default_value = 0.001
    if part == "heater_stones":
        scale.inputs[1].default_value = (95,95,95)
        low, high = (0.065,0.075,0.08,1), (0.28,0.30,0.29,1)
        bsdf.inputs["Roughness"].default_value = 0.92
    elif "insulation" in part:
        scale.inputs[1].default_value = (180,180,180)
        low, high = (0.30,0.23,0.08,1), (0.79,0.68,0.35,1)
        bump.inputs["Distance"].default_value = 0.003
        bsdf.inputs["Roughness"].default_value = 0.95
    elif part == "concrete_piers":
        scale.inputs[1].default_value = (35,35,35)
        low, high = (0.22,0.23,0.22,1), (0.51,0.50,0.46,1)
        bsdf.inputs["Roughness"].default_value = 0.85
    else:
        scale.inputs[1].default_value = (24,24,1.3)
        if part in ("floor_boards", "floor_joists", "roof_joists", "bench_upper", "bench_lower"):
            scale.inputs[1].default_value = (24,1.3,24)
        if part in ("roof_deck", "ceiling_boards", "wall_battens", "service_battens"):
            scale.inputs[1].default_value = (1.3,24,24)
        low, high = (0.35,0.19,0.075,1), (0.72,0.49,0.25,1)
        if part in ("interior_boards", "partition_boards", "bench_upper", "bench_lower", "ceiling_boards"):
            low, high = (0.55,0.37,0.18,1), (0.88,0.73,0.48,1)
        if part == "wall_cladding":
            low, high = (0.22,0.105,0.04,1), (0.54,0.31,0.13,1)
    ramp.color_ramp.elements[0].position = 0.2
    ramp.color_ramp.elements[0].color = low
    ramp.color_ramp.elements[1].position = 0.8
    ramp.color_ramp.elements[1].color = high
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    material.diffuse_color = high
    return material


