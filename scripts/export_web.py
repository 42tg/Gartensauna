"""Blender CLI: export_web.py -- BLENDER_DIRECTORY OUTPUT_DIRECTORY [SCAN.blend].
Exports evaluated CAD geometry (including reversible cutaway modifiers) to GLB.
Scan stays private: supply it locally; never commit captured surroundings to GitHub.
"""
import bpy, json, sys
from pathlib import Path
import numpy as np
args=sys.argv[sys.argv.index('--')+1:]
source,out=map(Path,args[:2]); out.mkdir(parents=True,exist_ok=True)
for variant in ('assembled','exploded','cutaway'):
 bpy.ops.wm.open_mainfile(filepath=str(source/f'gartensauna_{variant}.blend'))
 bpy.ops.object.select_all(action='DESELECT')
 for obj in bpy.context.scene.objects:
  if obj.type=='MESH' and obj.get('cad_part') and not obj.hide_render:
   obj.hide_set(False); obj.select_set(True)
   # Portable material approximation. Geometry is exact; procedural Blender
   # shaders are not glTF portable, so use their existing ramp midpoint.
   for mat in obj.data.materials:
    if not mat or not mat.use_nodes: continue
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    ramps=[n for n in mat.node_tree.nodes if n.type=='VALTORGB']
    if ramps:
     colors=[e.color for e in ramps[0].color_ramp.elements]
     for link in list(bsdf.inputs['Base Color'].links):mat.node_tree.links.remove(link)
     bsdf.inputs['Base Color'].default_value=tuple(sum(c[i] for c in colors)/len(colors) for i in range(4))
 bpy.ops.export_scene.gltf(filepath=str(out/f'{variant}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_yup=False)
meta=json.loads((source/'gartensauna_assembled.json').read_text())
exploded=json.loads((source/'gartensauna_exploded.json').read_text())
for name,p in meta['parts'].items():
 p['explosion']=[exploded['parts'][name]['bounds_min'][i]-p['bounds_min'][i] for i in range(3)]
(out/'model.json').write_text(json.dumps(meta))
if len(args)>2:
 bpy.ops.wm.open_mainfile(filepath=str(Path(args[2]).resolve()))
 obj=max((o for o in bpy.data.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
 n=len(obj.data.vertices); xyz=np.empty(n*3,dtype=np.float32); obj.data.vertices.foreach_get('co',xyz); xyz=xyz.reshape(-1,3)
 matrix=np.array(obj.matrix_world); xyz=(xyz@matrix[:3,:3].T+matrix[:3,3]).astype('<f4')
 col=np.empty(n*4,dtype=np.float32); obj.data.color_attributes['scan_color'].data.foreach_get('color',col)
 # Keep original linear vertex colors; three.js consumes linear colors.
 rgb=col.reshape(-1,4)[:,:3].astype('<f4')
 xyz.tofile(out/'scan.positions.bin');rgb.tofile(out/'scan.colors.bin')
 (out/'scan.json').write_text(json.dumps({'count':n,'units':'m','source':'Saunaecke_Punktwolke.blend','status':'Vorläufig an 3,20 m Bestandsbreite ausgerichtet. Keine vermessene Genauigkeit.','bounds':[xyz.min(axis=0).tolist(),xyz.max(axis=0).tolist()]}))
