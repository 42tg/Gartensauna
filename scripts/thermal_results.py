#!/usr/bin/env python3
"""Independent balance/convergence audit and CAD-derived field visualisation."""
import argparse
import json
import re
from pathlib import Path
import numpy as np
from scipy.sparse.linalg import spsolve
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from simulate_ventilation import ROOT,transport_matrix

R=8314.462618/28.97
CP=1005.

def block(text,name):
    match=re.search(r'(?<![\w])'+re.escape(name)+r'\s*\{',text)
    if not match:raise ValueError('Missing block '+name)
    start=match.end();level=1;end=start
    while level:
        if text[end]=='{':level+=1
        elif text[end]=='}':level-=1
        end+=1
    return text[start:end-1]

def value(text,key,n,vector=False):
    match=re.search(r'\b'+re.escape(key)+r'\s+nonuniform\s+List<\w+>\s+(\d+)\s*\((.*?)\)\s*;',text,re.S)
    if match:
        count=int(match[1]);arr=np.fromstring(match[2].replace('(',' ').replace(')',' '),sep=' ')
        if vector:arr=arr.reshape(-1,3)
        if len(arr)!=n or count!=n:raise ValueError(f'Field count {key}: {count}, expected {n}')
        return arr
    match=re.search(r'\b'+re.escape(key)+r'\s+uniform\s+([^;]+);',text)
    if not match:raise ValueError('Missing field '+key)
    vals=np.fromstring(match[1].replace('(',' ').replace(')',' '),sep=' ')
    if len(vals)!=(3 if vector else 1):raise ValueError('Invalid uniform field')
    return np.tile(vals,(n,1)) if vector else np.full(n,vals[0])

def read_field(path,meta,vector=False,surface=False):
    text=path.read_text();n=meta['n_internal_faces'] if surface else meta['n_cells']
    internal=value(text,'internalField',n,vector);boundary={}
    b=block(text,'boundaryField')
    for name,p in meta['patches'].items():
        part=block(b,name)
        boundary[name]=np.zeros((p['count'],3)) if vector and 'noSlip' in part else value(part,'value',p['count'],vector)
    return internal,boundary

def weighted_percentile(data,w,p):
    order=np.argsort(data);cum=np.cumsum(w[order]);return float(np.interp(p/100*cum[-1],cum,data[order]))

def summarize(path):
    meta=json.loads((path/'case.json').read_text());c=meta['config'];m=np.load(path/'mesh_arrays.npz');patches=meta['patches']
    times=sorted([p for p in path.iterdir() if p.is_dir() and p.name.replace('.','',1).isdigit() and float(p.name)>0],key=lambda p:float(p.name))
    if len(times)<2:raise ValueError('Need at least two saved final fields for drift audit')
    latest=times[-1];n=meta['n_cells'];nf=meta['n_internal_faces']
    T,Tb=read_field(latest/'T',meta);U,Ub=read_field(latest/'U',meta,True);p,pb=read_field(latest/'p',meta)
    phi,phib=read_field(latest/'phi',meta,surface=True);nut,_=read_field(latest/'nut',meta)
    alphat,alphatb=read_field(latest/'alphat',meta)
    qr,qrb=read_field(latest/'qr',meta) if c['radiation'] else (np.zeros(n),{k:np.zeros(v['count']) for k,v in patches.items()})
    if not all(np.isfinite(x).all() for x in (T,U,p,phi,nut)) or T.min()<150 or T.max()>1500:raise ValueError('Nonphysical/nonfinite solution')
    rho=p/(R*T);vol=m['volumes'];xyz=m['centers'];owner=m['owner'];nei=m['neighbour'];area=m['face_area'];fc=m['face_center'];normal=m['face_normal']
    inward=np.zeros(n);outward=np.zeros(n);balance=np.bincount(owner[:nf],weights=phi,minlength=n)-np.bincount(nei,weights=phi,minlength=n)
    powers={};mass={};radiation={};conductive={}
    for name,patch in patches.items():
        sl=slice(patch['start'],patch['start']+patch['count']);own=owner[sl];f=phib[name]
        np.add.at(balance,own,f);np.add.at(inward,own,np.maximum(-f,0));np.add.at(outward,own,np.maximum(f,0))
        mass[name]=float(f.sum());radiation[name]=float(qrb[name]@area[sl])
        # Independent conductive heat into air from actual solved surface fields.
        mu=1.458e-6*Tb[name]**1.5/(Tb[name]+110.4)
        cv=CP-R;kappa=mu*cv*(1.32+1.77*R/cv)+CP*alphatb[name]
        dist=np.linalg.norm(fc[sl]-xyz[own],axis=1)
        conductive[name]=float((kappa*(Tb[name]-T[own])/dist)@area[sl])
        if name in ('supply','exhaust'):
            # Total sensible + kinetic + gravitational energy out through port.
            energies=CP*Tb[name]+.5*np.sum(Ub[name]**2,axis=1)+c['gravity_m_s2']*fc[sl,2]
            powers[name]=float(f@energies)
        elif name in ('walls','roof','floor','glass'):
            key={'walls':'wall','roof':'roof','floor':'floor','glass':'glass'}[name]+'_conductance_W_m2K'
            powers[name]=float((c[key]*(Tb[name]-273.15-c['outside_temperature_C']))@area[sl])
    mdot=float(inward.sum());nominal=float((rho*vol).sum()/mdot)
    distances=np.linalg.norm(xyz[owner[:nf]]-xyz[nei],axis=1)
    rhof=(rho[owner[:nf]]+rho[nei])/2;D=2e-5+(nut[owner[:nf]]+nut[nei])/2/.7
    A=transport_matrix(n,owner[:nf],nei,phi,rhof*D*area[:nf]/distances,inward,outward)
    age=spsolve(A,rho*vol)
    age_res=float(np.max(np.abs(A@age-rho*vol))/np.max(rho*vol))
    g=meta['geometry'];occupied=np.zeros(n,dtype=bool);regions={}
    for name in ('upper','lower'):
        b=np.array(g[name][0])/1000;s=np.array(g[name][1])/1000
        sel=(xyz[:,0]>b[0])&(xyz[:,0]<b[0]+s[0])&(xyz[:,1]>b[1])&(xyz[:,1]<b[1]+s[1])&(xyz[:,2]>b[2]+s[2]+.1)&(xyz[:,2]<min(g['room'][1][2]/1000,b[2]+s[2]+1))
        occupied|=sel
        regions[name]={'temperature_mean_C':float(np.average(T[sel]-273.15,weights=vol[sel])),
            'temperature_p10_C':weighted_percentile(T[sel]-273.15,vol[sel],10),'temperature_p90_C':weighted_percentile(T[sel]-273.15,vol[sel],90),
            'speed_p95_m_s':weighted_percentile(np.linalg.norm(U[sel],axis=1),vol[sel],95)}
    hp=np.array(g['heater'][0])/1000;hs=np.array(g['heater'][1])/1000
    plume=(xyz[:,0]>=hp[0])&(xyz[:,0]<=hp[0]+hs[0])&(xyz[:,1]>=hp[1])&(xyz[:,1]<=hp[1]+hs[1])&(xyz[:,2]>hp[2]+hs[2]+.1)&(xyz[:,2]<hp[2]+hs[2]+.7)
    prevT,_=read_field(times[-2]/'T',meta);prevU,_=read_field(times[-2]/'U',meta,True)
    driftT=float(np.average(np.abs(T-prevT),weights=vol));driftU=float(np.average(np.linalg.norm(U-prevU,axis=1),weights=vol))
    meanage=float(np.average(age[occupied],weights=vol[occupied]));radports=radiation['supply']+radiation['exhaust']
    # fvDOM qr is net radiative flux toward the surface: positive leaves the air domain.
    heatout=sum(powers.values())+radports
    error=(c['heater_power_W']-heatout)/max(c['heater_power_W'],1)
    boundary_errors={'heater':conductive['heater']-radiation['heater']-c['heater_power_W'],
                     'benches':conductive['benches']-radiation['benches']}
    for name in ('walls','glass','roof','floor'):
        boundary_errors[name]=conductive[name]-radiation[name]+powers[name]
    boundary_error=max(abs(v) for v in boundary_errors.values())/max(c['heater_power_W'],1)
    stats={
        'case':c['name'],'config':c,'iteration':float(latest.name),'cells':n,'geometry_sha256':meta['geometry_sha256'],
        'air_volume_m3':meta['air_volume_m3'],'supply_mass_flow_kg_s':-mass['supply'],'exhaust_mass_flow_kg_s':mass['exhaust'],
        'mass_balance_relative':abs(sum(mass.values()))/mdot,'local_mass_residual_L1_relative':float(np.sum(abs(balance))/mdot),
        'energy_balance_relative':float(error),'heat_out_W':float(heatout),'energy_terms_W':powers,'net_radiation_to_patches_W':radiation,'conductive_heat_to_air_W':conductive,
        'boundary_heat_balance_relative':float(boundary_error),'boundary_heat_residuals_W':boundary_errors,
        'radiation_closure_relative':float(abs(sum(radiation.values()))/max(c['heater_power_W'],1)),
        'temperature_volume_mean_C':float(np.average(T-273.15,weights=vol)),
        'heater_surface_mean_C':float(np.mean(Tb['heater'])-273.15),
        'plume_mean_vertical_velocity_m_s':float(np.average(U[plume,2],weights=vol[plume])),
        'regions':regions,'occupied_mean_age_min':meanage/60,'occupied_p95_age_min':weighted_percentile(age[occupied],vol[occupied],95)/60,
        'occupied_age_factor':meanage/nominal,'nominal_mass_residence_min':nominal/60,'age_equation_residual':age_res,
        'temperature_field_drift_K':driftT,'velocity_field_drift_m_s':driftU,'drift_iteration_interval':float(latest.name)-float(times[-2].name),
        'minimum_air_temperature_C':float(T.min()-273.15),'maximum_air_temperature_C':float(T.max()-273.15),
        'exhaust_backflow_fraction':float(np.maximum(-phib['exhaust'],0).sum()/mdot)}
    failures=[]
    for name,val,limit in [('mass_balance',stats['mass_balance_relative'],.005),('local_mass',stats['local_mass_residual_L1_relative'],.02),('energy_balance',abs(error),.05),('boundary_heat_balance',boundary_error,.05),('radiation_closure',stats['radiation_closure_relative'],.02),('temperature_drift',driftT,.5),('velocity_drift',driftU,.01),('age_residual',age_res,1e-7)]:
        if val>limit:failures.append(f'{name}: {val:.5g} > {limit}')
    if float(latest.name)<max(c['iterations'],c.get('ramp_iterations',0)+200):failures.append('target iterations / post-ramp window not reached')
    if age.min()<0 or not np.isfinite(age).all():failures.append('nonphysical age')
    stats['quality_pass']=not failures;stats['quality_failures']=failures
    (path/'results.json').write_text(json.dumps(stats,indent=2)+'\n')
    plot(path,meta,m,T,U,age,stats)
    return stats

def plot(path,meta,m,T,U,age,stats):
    ids=m['ids'];g=meta['geometry'];fields=[]
    for arr in (T-273.15,age/60):
        ff=np.full(ids.shape,np.nan);mask=ids>=0;ff[mask]=arr[ids[mask]];fields.append(ff)
    vv=np.zeros((*ids.shape,3));vv[ids>=0]=U[ids[ids>=0]]
    axes=[(m[k][1:]+m[k][:-1])/2 for k in 'xyz']
    fig,axs=plt.subplots(1,2,figsize=(13,5.5),constrained_layout=True)
    lo=float(np.nanpercentile(fields[0],2));hi=float(np.nanpercentile(fields[0],98))
    for ax,x,title in zip(axs,[(g['heater'][0][0]+g['heater'][1][0]/2)/1000,2.5],['Ofen / Zuluft','Bankbereich']):
        ix=int(np.argmin(abs(axes[0]-x)));sl=fields[0][ix].T
        im=ax.pcolormesh(m['y'],m['z'],sl,cmap='inferno',vmin=lo,vmax=hi,shading='flat')
        ax.quiver(axes[1][::2],axes[2][::2],vv[ix,::2,::2,1].T,vv[ix,::2,::2,2].T,color='cyan',alpha=.65)
        ax.set_title(f'{title} | x={axes[0][ix]:.2f} m');ax.set_xlabel('Längsrichtung y [m]');ax.set_ylabel('Höhe [m]');ax.set_aspect('equal')
    fig.colorbar(im,ax=axs,label='Berechnete Lufttemperatur [°C]')
    state='numerische Qualitätskriterien erfüllt' if stats['quality_pass'] else 'NICHT KONVERGIERT – keine Rangfolge ableiten'
    fig.suptitle(f"{stats['case']} | {meta['config']['heater_power_W']} W | {state}\nIdealgas-RANS + Wärmestrahlung; unkalibrierte Randbedingungen")
    fig.savefig(path/'temperature_flow.png',dpi=150);plt.close(fig)
    np.savez_compressed(path/'fields.npz',centers=m['centers'],T_C=T-273.15,U=U,age_s=age)

def main():
    p=argparse.ArgumentParser();p.add_argument('case');p.add_argument('--require-quality',action='store_true');args=p.parse_args()
    r=summarize(ROOT/'build/thermal'/args.case)
    print(json.dumps(r,indent=2))
    if args.require_quality and not r['quality_pass']:raise SystemExit('Thermal quality criteria not met')
if __name__=='__main__':main()
