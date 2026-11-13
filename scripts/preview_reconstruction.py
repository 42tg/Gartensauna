#!/usr/bin/env python3
"""Render reconstructed SfM points only; no interpolation or surface completion."""
import argparse
import json
from pathlib import Path
import numpy as np
import pycolmap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('model', type=Path)
p.add_argument('output', type=Path)
p.add_argument('--reference', help='Registered image filename; defaults to the middle image by filename')
a = p.parse_args()
r = pycolmap.Reconstruction(a.model)
points = [v for v in r.points3D.values() if v.track.length() >= 3 and v.error < 2]
if not points:
    p.error('No points pass the display filter')
xyz = np.array([v.xyz for v in points])
colors = np.array([v.color for v in points]) / 255
images = sorted(r.images.values(), key=lambda i: i.name)
ref = next((im for im in images if im.name == a.reference), None) if a.reference else images[len(images)//2]
if ref is None:
    p.error('Reference image is not registered in this model')
pose = ref.cam_from_world()
xyz = xyz @ pose.rotation.matrix().T + pose.translation
center = np.median(xyz, axis=0)
xyz -= center
lo, hi = np.quantile(xyz, [0.01, 0.99], axis=0)
mask = ((xyz >= lo) & (xyz <= hi)).all(axis=1)
xyz, colors = xyz[mask], colors[mask]
fig = plt.figure(figsize=(15, 8), facecolor='#111b23')
for index, angle in enumerate([0, 28]):
    ax = fig.add_subplot(1, 2, index+1, projection='3d', facecolor='#111b23')
    ax.scatter(xyz[:,0], xyz[:,2], -xyz[:,1], c=colors, s=1.1, depthshade=False)
    ax.set_box_aspect(np.maximum(hi-lo,0.01)[[0,2,1]])
    ax.view_init(elev=6, azim=-90+angle)
    ax.set_axis_off()
    ax.set_box_aspect(np.maximum(hi-lo,0.01)[[0,2,1]], zoom=1.45)
    ax.set_title(['Referenzblick','Um 28° gedrehte Punktwolke'][index], color='white', pad=0)
fig.suptitle('Videorekonstruktion · Punktwolke',color='white',fontsize=22,y=0.94)
fig.text(.5,.075, f'{r.num_reg_images()} registrierte Bilder · {r.num_points3D():,} 3D-Punkte insgesamt'.replace(',','.'), ha='center',color='#cbd9df',fontsize=13)
fig.text(.5,.035,'Sparse Photogrammetrie · unskaliert · Lücken sind nicht ergänzt · keine vermessene CAD-Geometrie',ha='center',color='#9aaeb8',fontsize=11)
fig.subplots_adjust(left=0,right=1,bottom=.12,top=.89,wspace=0)
a.output.parent.mkdir(parents=True,exist_ok=True)
fig.savefig(a.output,dpi=150,facecolor=fig.get_facecolor())
print(json.dumps({'reference':ref.name,'displayed_points':len(xyz),'summary':r.summary()}))
