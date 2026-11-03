#!/usr/bin/env python3
"""3-D conservative finite-volume potential flow + steady mean age of air.
NOT Navier-Stokes / thermal CFD. Geometry from evaluated OpenSCAD parameters.
Slip, impermeable walls; specified supply/exhaust flow; closed door/drying vent.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import spsolve
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

def geometry():
    target = ROOT / 'build/ventilation/metadata.csg'
    target.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(['openscad', '-o', str(target), '-D', 'part="metadata"', str(ROOT/'cad/ventilation-metadata.scad')], capture_output=True, text=True, check=True)
    if 'ERROR:' in result.stderr or 'WARNING:' in result.stderr:
        raise RuntimeError(result.stderr)
    records = [json.loads(line[6:]) for line in result.stderr.splitlines() if line.startswith('ECHO: ')]
    return {r[0]: r[1:] for r in records}

def laplacian(n, a, b, conductance):
    return coo_matrix((np.concatenate([conductance,conductance,-conductance,-conductance]),
                      (np.concatenate([a,b,a,b]),np.concatenate([a,b,b,a]))),shape=(n,n)).tocsr()

def transport_matrix(n, a, b, flux, diffusion, inlet, outlet):
    # Upwind face flux, symmetric diffusive flux; inlet age=0, outflow zero gradient.
    up = np.where(flux>=0,a,b); down = np.where(flux>=0,b,a)
    mag = np.abs(flux)
    adv = coo_matrix((np.r_[mag,-mag],(np.r_[up,down],np.r_[up,up])),shape=(n,n)).tocsr()
    return adv + laplacian(n,a,b,diffusion) + diags(outlet + inlet*0)

def solve(g, cfg):
    lo=np.array(g['room'][0])/1000; hi=np.array(g['room'][1])/1000
    shape=np.ceil((hi-lo)/cfg['grid_m']).astype(int); ds=(hi-lo)/shape
    axes=[lo[i]+(np.arange(shape[i])+0.5)*ds[i] for i in range(3)]
    xyz=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1)
    air=~((xyz[...,1]>=0)&(xyz[...,0]<g['room'][2]/1000))
    # Solid envelopes include bench rails; slat gaps/legs/people are not resolved.
    for name in ('upper','lower','heater'):
        p=np.array(g[name][0])/1000; q=p+np.array(g[name][1])/1000
        air &= ~np.all((xyz+ds/2>p)&(xyz-ds/2<q),axis=-1)
    ids=np.full(tuple(shape),-1); ids[air]=np.arange(air.sum()); n=int(air.sum())
    pairs=[]; conductances=[]; directions=[]
    for k in range(3):
        left=[slice(None)]*3;right=left.copy();left[k]=slice(None,-1);right[k]=slice(1,None)
        aa=ids[tuple(left)].ravel();bb=ids[tuple(right)].ravel();valid=(aa>=0)&(bb>=0)
        pairs.append((aa[valid],bb[valid])); conductances.append(np.full(valid.sum(),np.prod(ds)/ds[k]**2));directions.append(np.full(valid.sum(),k))
    a=np.concatenate([p[0] for p in pairs]); b=np.concatenate([p[1] for p in pairs]); c=np.concatenate(conductances); direction=np.concatenate(directions)
    q=cfg['flow_m3h']/3600
    def port(name):
        p=np.array(g[name][0])/1000;s=np.array(g[name][1])/1000
        if name != 'supply' and 'exhaust_y_m' in cfg:p[1]=cfg['exhaust_y_m']
        normal=1 if name=='supply' else 0
        boundary=0 if name=='supply' else shape[0]-1
        weights=np.ones(tuple(shape))
        for k in range(3):
            if k==normal:
                weights*=np.indices(tuple(shape))[k]==boundary
            else:
                weights*=np.maximum(0,np.minimum(xyz[...,k]+ds[k]/2,p[k]+s[k])-np.maximum(xyz[...,k]-ds[k]/2,p[k]))
        expected=np.prod(s[s>0]); actual=weights[air].sum()
        if not np.isclose(actual,expected,rtol=1e-8):
            raise ValueError(f'{name} blocked/outside room: {actual} vs {expected}')
        return weights[air]/actual*q
    inlet=port('supply');outlet=port(cfg['exhaust']);rhs=inlet-outlet
    L=laplacian(n,a,b,c)
    # One pressure-potential reference; global sum(rhs)=0 ensures conservation.
    potential=np.zeros(n);potential[1:]=spsolve(L[1:,1:],rhs[1:])
    flux=c*(potential[a]-potential[b])
    balance=np.bincount(a,weights=flux,minlength=n)-np.bincount(b,weights=flux,minlength=n)-rhs
    flow_error=float(np.max(np.abs(balance))/q)
    if flow_error>1e-7:raise AssertionError(f'Flux conservation {flow_error}')
    T=transport_matrix(n,a,b,flux,c*cfg['mixing_diffusivity_m2s'],inlet,outlet)
    volume=np.prod(ds);age=spsolve(T,np.full(n,volume))
    residual=float(np.max(np.abs(T@age-volume))/volume)
    nominal=n*volume/q
    outlet_age=float(outlet@age/q)
    if not np.all(np.isfinite(age)) or age.min()<0 or residual>1e-7:raise AssertionError('Age solve failed')
    if not np.isclose(outlet_age,nominal,rtol=1e-7):raise AssertionError('Global age balance failed')
    points=xyz[air];occupied=np.zeros(n,dtype=bool)
    for name in ('upper','lower'):
        p=np.array(g[name][0])/1000;s=np.array(g[name][1])/1000
        occupied|=(points[:,0]>p[0])&(points[:,0]<p[0]+s[0])&(points[:,1]>p[1])&(points[:,1]<p[1]+s[1])&(points[:,2]>p[2]+s[2]+0.1)&(points[:,2]<min(hi[2],p[2]+s[2]+1.0))
    if not occupied.any():raise AssertionError('Empty occupied zone')
    velocity=np.zeros((n,3));count=np.zeros((n,3))
    for k in range(3):
        sel=direction==k;area=volume/ds[k]
        for ix in (a[sel],b[sel]):
            np.add.at(velocity[:,k],ix,flux[sel]/area);np.add.at(count[:,k],ix,1)
    velocity/=np.maximum(count,1)
    factor=float(age[occupied].mean()/nominal)
    report={**cfg,'cells':n,'cell_size_m':ds.tolist(),'air_volume_m3':float(n*volume),
        'air_changes_per_hour':float(cfg['flow_m3h']/(n*volume)),
        'nominal_age_min':float(nominal/60),'occupied_mean_age_min':float(age[occupied].mean()/60),
        'occupied_p95_age_min':float(np.percentile(age[occupied],95)/60),
        'occupied_age_factor':factor,'occupied_fraction_age_gt_2_nominal':float(np.mean(age[occupied]>2*nominal)),
        'outlet_age_min':outlet_age/60,'max_cell_mass_error_relative_to_Q':flow_error,'age_residual_relative':residual,
        'free_supply_area_m2':g['supply'][1][0]*g['supply'][1][2]/1e6*(1-g['grille'][0]/g['grille'][1]),
        'warning':'ISOTHERMAL potential-flow screening. No buoyancy, turbulence, heat, humidity, CO2, fan curve or comfort certification.'}
    report['supply_free_area_velocity_ms']=q/report['free_supply_area_m2']
    field=np.full(tuple(shape),np.nan);field[air]=age/60
    vfield=np.zeros((*shape,3));vfield[air]=velocity
    return report,(axes,field,vfield)

def plot_case(report,data,dest):
    axes,age,v=data
    fig,axs=plt.subplots(1,2,figsize=(12,5),constrained_layout=True)
    z=int(np.argmin(abs(axes[2]-1.3)));x=int(np.argmin(abs(axes[0]-2.5)))
    vmax=np.nanpercentile(age,98)
    for ax,xx,yy,zz,uu,vv,title in [
        (axs[0],axes[0],axes[1],age[:,:,z].T,v[:,:,z,0].T,v[:,:,z,1].T,f'Horizontal bei z={axes[2][z]:.2f} m'),
        (axs[1],axes[1],axes[2],age[x,:,:].T,v[x,:,:,1].T,v[x,:,:,2].T,f'Laengsschnitt bei x={axes[0][x]:.2f} m')]:
        im=ax.pcolormesh(xx,yy,zz,cmap='viridis',vmin=0,vmax=vmax,shading='nearest')
        # Arrows show projected local computed vectors; not invented streamline paths.
        ax.quiver(xx[::2],yy[::2],uu[::2,::2],vv[::2,::2],color='white',alpha=.7)
        ax.set_title(title);ax.set_aspect('equal');ax.set_xlabel('CAD-Koordinate [m]');ax.set_ylabel('CAD-Koordinate [m]')
    fig.colorbar(im,ax=axs,label='Mittleres Luftalter [min]')
    fig.suptitle(f"{report['name']} | {report['flow_m3h']} m³/h | Luftalterfaktor {report['occupied_age_factor']:.2f}\nIsothermes Orientierungsmodell – ohne Waermeauftrieb")
    fig.savefig(dest,dpi=150);plt.close(fig)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',default='simulation/cases.json');args=parser.parse_args()
    config=json.loads((ROOT/args.config).read_text());g=geometry();out=ROOT/'build/ventilation'
    (out/'geometry.json').write_text(json.dumps(g,indent=2)+'\n')
    results=[]
    for case in config['cases']:
        cfg={k:v for k,v in config.items() if k!='cases'};cfg.update(case)
        report,data=solve(g,cfg);results.append(report);plot_case(report,data,out/f"{case['name']}.png")
        print(case['name'],round(report['occupied_age_factor'],3),flush=True)
    baseline=results[0]
    for r in results:r['age_factor_change_percent']=100*(r['occupied_age_factor']/baseline['occupied_age_factor']-1)
    fine=next(r for r in results if r['name']=='planned_fine')
    mesh_delta=abs(fine['occupied_age_factor']/baseline['occupied_age_factor']-1)
    report={'model':config['model'],'geometry_sha256':hashlib.sha256(json.dumps(g,sort_keys=True).encode()).hexdigest(),
        'mesh_factor_relative_change':mesh_delta,'mesh_warning':mesh_delta>0.1,
        'interpretation':'Lower occupied_age_factor means fresher occupied-zone air only within this model. No thermal ranking.', 'cases':results}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['# Lüftungsvergleich – isothermes Orientierungsmodell','',
        '**Keine thermische CFD und keine Bau-/Komfortfreigabe.** Luftalterfaktor = mittleres Luftalter im Aufenthaltsbereich / (Luftvolumen / Volumenstrom). Kleiner ist innerhalb dieses Modells besser; 1 entspricht dem mittleren Luftalter idealer vollständiger Durchmischung.','',
        '| Variante | m³/h | Luftwechsel / h | Luftalter Ø / min | Luftalter P95 / min | Faktor ↓ |', '|---|---:|---:|---:|---:|---:|']
    for r in results:lines.append(f"| {r['name']} | {r['flow_m3h']} | {r['air_changes_per_hour']:.2f} | {r['occupied_mean_age_min']:.2f} | {r['occupied_p95_age_min']:.2f} | {r['occupied_age_factor']:.3f} |")
    lines+=['',f'Gittervergleich 12 → 8 cm: {100*mesh_delta:.1f}% Änderung des Faktors. Zwei Gitter sind kein vollständiger Konvergenznachweis.',
        'Mischungskoeffizient ist eine unkalibrierte Annahme (0,003 m²/s); Sensitivitäten 0,001 und 0,01 werden mitgerechnet.',
        'Alternativpositionen sind virtuelle Rechenfälle; im CAD gebaut ist ausschließlich planned. Hohe Abluft ist kein empfohlener Saunabetrieb.']
    (out/'comparison.md').write_text('\n'.join(lines)+'\n')
    fig,ax=plt.subplots(figsize=(10,5),constrained_layout=True)
    ax.barh([r['name'] for r in results],[r['occupied_age_factor'] for r in results],color='#287c9b');ax.invert_yaxis();ax.axvline(1,color='gray',ls='--')
    ax.set_xlabel('Luftalterfaktor im Aufenthaltsbereich (kleiner = frischer im Modell)')
    ax.set_title('Variantenvergleich – isotherm, ohne Wärmeauftrieb\nMischungsannahmen und Gitterweite beeinflussen die Werte')
    fig.savefig(out/'comparison.png',dpi=150);plt.close(fig)

if __name__=='__main__':main()
