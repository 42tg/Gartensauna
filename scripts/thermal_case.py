#!/usr/bin/env python3
"""Generate an orthogonal, CAD-parameter-aligned finite-volume OpenFOAM mesh.
Heater and benches are closed envelope approximations. No fictional streamlines.
"""
import argparse
import json
import hashlib
from collections import defaultdict
from pathlib import Path
import numpy as np
from simulate_ventilation import geometry,ROOT

PATCHES=('supply','exhaust','heater','benches','glass','roof','floor','walls')

def header(kind,name):
    return f'FoamFile\n{{version 2.0; format ascii; class {kind}; object {name};}}\n'

def write_list(path,kind,values):
    path.write_text(header(kind,path.name)+str(len(values))+'\n(\n'+'\n'.join(values)+'\n)\n')

def mesh(g,cfg,dest):
    lo=np.array(g['room'][0])/1000;hi=np.array(g['room'][1])/1000
    notch=g['room'][2]/1000
    boxes={k:(np.array(g[k][0])/1000,np.array(g[k][0])/1000+np.array(g[k][1])/1000) for k in ('heater','upper','lower')}
    ports={k:(np.array(g[v][0])/1000,np.array(g[v][1])/1000) for k,v in [('supply','supply'),('exhaust',cfg['exhaust'])]}
    if 'exhaust_y_m' in cfg:ports['exhaust'][0][1]=cfg['exhaust_y_m']
    critical=[[lo[k],hi[k]] for k in range(3)];critical[0].append(notch);critical[1].append(0)
    for p,q in boxes.values():
        for k in range(3):critical[k].extend([p[k],q[k]])
    for p,s in ports.values():
        for k in range(3):critical[k].extend([p[k],p[k]+s[k]])
    axes=[]
    for k in range(3):
        cs=sorted(set(round(float(v),8) for v in critical[k] if lo[k]-1e-8<=v<=hi[k]+1e-8))
        vals=[cs[0]]
        for start,end in zip(cs[:-1],cs[1:]):
            vals.extend(np.linspace(start,end,int(np.ceil((end-start)/cfg['grid_m']))+1)[1:])
        axes.append(np.array(vals))
    centers=np.stack(np.meshgrid(*[(a[1:]+a[:-1])/2 for a in axes],indexing='ij'),axis=-1)
    dx=np.stack(np.meshgrid(*[np.diff(a) for a in axes],indexing='ij'),axis=-1)
    shape=centers.shape[:3];material=np.full(shape,'air',dtype='<U10')
    material[(centers[...,1]>=0)&(centers[...,0]<notch)]='walls'
    for name,(p,q) in boxes.items():material[np.all((centers>p)&(centers<q),axis=-1)]='heater' if name=='heater' else 'benches'
    air=material=='air';ids=np.full(shape,-1);ids[air]=np.arange(air.sum())
    points=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1).reshape(-1,3)
    pointids=np.arange(len(points)).reshape(tuple(len(a) for a in axes))
    # Outward-oriented vertices, direction, axis, sign.
    specs=[([(0,0,0),(0,0,1),(0,1,1),(0,1,0)],(-1,0,0),0,-1),
           ([(1,0,0),(1,1,0),(1,1,1),(1,0,1)],(1,0,0),0,1),
           ([(0,0,0),(1,0,0),(1,0,1),(0,0,1)],(0,-1,0),1,-1),
           ([(0,1,0),(0,1,1),(1,1,1),(1,1,0)],(0,1,0),1,1),
           ([(0,0,0),(0,1,0),(1,1,0),(1,0,0)],(0,0,-1),2,-1),
           ([(0,0,1),(1,0,1),(1,1,1),(0,1,1)],(0,0,1),2,1)]
    internal=[];boundary=defaultdict(list)
    for index in np.argwhere(air):
        ijk=tuple(index);owner=int(ids[ijk])
        for offsets,direction,k,sign in specs:
            neighbour_index=index+direction;inside=all(0<=neighbour_index[j]<shape[j] for j in range(3))
            ni=tuple(neighbour_index);neighbour=int(ids[ni]) if inside else -1
            if neighbour>=0 and neighbour<owner:continue
            vertices=[int(pointids[tuple(index+o)]) for o in offsets]
            face_center=points[vertices].mean(axis=0);area=float(np.prod(np.delete(dx[ijk],k)))
            normal=np.zeros(3);normal[k]=sign
            record=(vertices,owner,neighbour,area,face_center.tolist(),normal.tolist())
            if neighbour>=0:internal.append(record);continue
            patch=material[ni] if inside else ('floor' if k==2 and sign<0 else 'roof' if k==2 else 'glass' if k==0 and sign<0 and face_center[1]<0 else 'walls')
            for name,(p,s) in ports.items():
                axis=1 if name=='supply' else 0
                if k==axis and np.isclose(face_center[k],p[k]) and all(p[j]-1e-8<=face_center[j]<=p[j]+s[j]+1e-8 for j in range(3) if j!=k):patch=name
            boundary[str(patch)].append(record)
    internal.sort(key=lambda f:(f[1],f[2]));faces=internal.copy();patchmeta={};cursor=len(faces)
    for name in PATCHES:
        ff=boundary[name]
        if not ff:raise ValueError('Empty patch '+name)
        patchmeta[name]={'start':cursor,'count':len(ff),'area_m2':sum(f[3] for f in ff)};cursor+=len(ff);faces.extend(ff)
    for name,(p,s) in ports.items():
        expected=float(np.prod(s[s>0]));actual=patchmeta[name]['area_m2']
        if not np.isclose(actual,expected,rtol=1e-7):raise ValueError(f'{name}: requested area {expected}, meshed {actual}')
    poly=dest/'constant/polyMesh';poly.mkdir(parents=True,exist_ok=True)
    # Remove unused vertices; preserve deterministic topology and point ordering.
    used=sorted({p for f in faces for p in f[0]});remap={old:new for new,old in enumerate(used)}
    write_list(poly/'points','vectorField',['('+ ' '.join(f'{v:.10g}' for v in p)+')' for p in points[used]])
    write_list(poly/'faces','faceList',['4('+ ' '.join(str(remap[v]) for v in f[0])+')' for f in faces])
    write_list(poly/'owner','labelList',[str(f[1]) for f in faces])
    write_list(poly/'neighbour','labelList',[str(f[2]) for f in internal])
    entries=[f'{name}\n{{type {"patch" if name in ("supply","exhaust") else "wall"}; nFaces {m["count"]}; startFace {m["start"]};}}' for name,m in patchmeta.items()]
    write_list(poly/'boundary','polyBoundaryMesh',entries)
    meta={'config':cfg,'geometry':g,'geometry_sha256':hashlib.sha256(json.dumps(g,sort_keys=True).encode()).hexdigest(),
          'patches':patchmeta,'n_cells':int(air.sum()),'n_internal_faces':len(internal),'air_volume_m3':float(np.prod(dx,axis=-1)[air].sum())}
    (dest/'case.json').write_text(json.dumps(meta,indent=2)+'\n')
    np.savez_compressed(dest/'mesh_arrays.npz',centers=centers[air],volumes=np.prod(dx,axis=-1)[air],
        owner=np.array([f[1] for f in faces]),neighbour=np.array([f[2] for f in internal]),
        face_area=np.array([f[3] for f in faces]),face_center=np.array([f[4] for f in faces]),face_normal=np.array([f[5] for f in faces]),
        ids=ids,x=axes[0],y=axes[1],z=axes[2])
    return meta

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',default='thermal_planned');p.add_argument('--iterations',type=int);args=p.parse_args()
    config=json.loads((ROOT/'simulation/thermal/config.json').read_text());case=next(c for c in config['cases'] if c['name']==args.case)
    cfg={**config['base'],**case};
    if args.iterations is not None:cfg['iterations']=args.iterations
    dest=ROOT/'build/thermal'/args.case;dest.mkdir(parents=True,exist_ok=True)
    meta=mesh(geometry(),cfg,dest)
    from thermal_fields import write_case
    write_case(dest,meta)
    print(json.dumps({'case':args.case,'cells':meta['n_cells'],'volume':meta['air_volume_m3'],'patches':meta['patches']},indent=2))

if __name__=='__main__':main()
