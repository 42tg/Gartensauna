#!/usr/bin/env python3
"""Physical-time statistics, storage-aware balances, and explicit sampling audits."""
import argparse,json,re
from pathlib import Path
import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from thermal_results import read_field,CP,R,weighted_percentile
from simulate_ventilation import transport_matrix

def time_mean(t,a,start,end):
    """Trapezoidal integral, including interpolated exact window endpoints."""
    t=np.asarray(t,float);a=np.asarray(a)
    if not np.all(np.diff(t)>0) or start<t[0] or end>t[-1] or end<=start:raise ValueError('Invalid averaging window')
    def interp(x):
        j=min(np.searchsorted(t,x,side='right'),len(t)-1);i=max(j-1,0)
        return a[i]+(a[j]-a[i])*(x-t[i])/(t[j]-t[i])
    take=(t>start)&(t<end);tt=np.r_[start,t[take],end];aa=np.concatenate([interp(start)[None],a[take],interp(end)[None]])
    return np.trapezoid(aa,tt,axis=0)/(end-start)

def time_diagnostics(log):
    dt=[float(x) for x in re.findall(r'^deltaT = ([0-9.eE+-]+)',log,re.M)]
    co=[];initial_co=[];completed=False
    for line in log.splitlines():
        if line.startswith('Build  :'):completed=False
        if line.startswith('ExecutionTime ='):completed=True
        match=re.match(r'Courant Number mean: [0-9.eE+-]+ max: ([0-9.eE+-]+)',line)
        if match:
            (co if completed else initial_co).append(float(match[1]));completed=False
    return dt,co,initial_co

def regions(meta,xyz):
    result={};g=meta['geometry']
    for name in ('upper','lower'):
        b=np.array(g[name][0])/1000;s=np.array(g[name][1])/1000
        result[name]=(xyz[:,0]>b[0])&(xyz[:,0]<b[0]+s[0])&(xyz[:,1]>b[1])&(xyz[:,1]<b[1]+s[1])&(xyz[:,2]>b[2]+s[2]+.1)&(xyz[:,2]<min(g['room'][1][2]/1000,b[2]+s[2]+1))
    return result

def sample(path,meta,m):
    c=meta['config'];n=meta['n_cells'];nf=meta['n_internal_faces'];v=m['volumes'];own=m['owner'];nei=m['neighbour'];area=m['face_area'];fc=m['face_center'];xyz=m['centers']
    T,Tb=read_field(path/'T',meta);U,Ub=read_field(path/'U',meta,True);p,_=read_field(path/'p',meta)
    phi,phib=read_field(path/'phi',meta,surface=True);nut,_=read_field(path/'nut',meta);_,ab=read_field(path/'alphat',meta);_,qr=read_field(path/'qr',meta)
    if not all(np.isfinite(a).all() for a in (T,U,p,phi,nut)) or T.min()<200 or T.max()>1500 or p.min()<=0:raise ValueError('Nonphysical snapshot '+str(path))
    rho=p/(R*T);div=np.bincount(own[:nf],weights=phi,minlength=n)-np.bincount(nei,weights=phi,minlength=n)
    inflow=np.zeros(n);outflow=np.zeros(n);heat=0.;mass=0.;inmass=0.;radiation=0.;bcerrors={};patchdata={}
    for name,patch in meta['patches'].items():
        sl=slice(patch['start'],patch['start']+patch['count']);o=own[sl];f=phib[name];s=area[sl]
        np.add.at(div,o,f);np.add.at(inflow,o,np.maximum(-f,0));np.add.at(outflow,o,np.maximum(f,0))
        mass+=f.sum();inmass+=np.maximum(-f,0).sum();rad=float(qr[name]@s);radiation+=rad
        mu=1.458e-6*Tb[name]**1.5/(Tb[name]+110.4);cv=CP-R;kappa=mu*cv*(1.32+1.77*R/cv)+CP*ab[name]
        cond=float((kappa*(Tb[name]-T[o])/np.linalg.norm(fc[sl]-xyz[o],axis=1))@s)
        if name in ('supply','exhaust'):
            flux=float(f@(CP*Tb[name]+.5*np.sum(Ub[name]**2,axis=1)+c['gravity_m_s2']*fc[sl,2]))+rad-cond
        elif name in ('walls','roof','floor','glass'):
            key={'walls':'wall','roof':'roof','floor':'floor','glass':'glass'}[name]+'_conductance_W_m2K'
            flux=float((c[key]*(Tb[name]-273.15-c['outside_temperature_C']))@s);bcerrors[name]=cond-rad+flux
        else:
            flux=0.;bcerrors[name]=cond-rad-(c['heater_power_W'] if name=='heater' else 0)
        heat+=flux;patchdata[name]=flux
    distance=np.linalg.norm(xyz[own[:nf]]-xyz[nei],axis=1)
    diffusion=(rho[own[:nf]]+rho[nei])/2*(2e-5+(nut[own[:nf]]+nut[nei])/1.4)*area[:nf]/distance
    A=transport_matrix(n,own[:nf],nei,phi,diffusion,inflow,outflow)
    stored=float((rho*v*((CP-R)*T+.5*np.sum(U**2,axis=1)+c['gravity_m_s2']*xyz[:,2])).sum())
    return {'T':T,'U':U,'rhoV':rho*v,'div':div,'A':A,'heat_out':heat,'mass_out':mass,'inmass':inmass,'stored_energy':stored,'radiation':radiation,'bc_error':max(abs(x) for x in bcerrors.values()),'patch_heat':patchdata,'minT':float(T.min()),'maxT':float(T.max())}

def summarize(path,start=100.,end=None):
    meta=json.loads((path/'case.json').read_text());cfg=meta['config'];m=dict(np.load(path/'mesh_arrays.npz'));v=m['volumes'];xyz=m['centers'];reg=regions(meta,xyz);occupied=reg['upper']|reg['lower']
    dirs=sorted([p for p in path.iterdir() if p.is_dir() and p.name.replace('.','',1).isdigit()],key=lambda p:float(p.name));times=np.array([float(p.name) for p in dirs]);end=float(times[-1]) if end is None else end
    if len(dirs)<3 or start>=end:raise ValueError('Insufficient physical-time snapshots')
    allT=[];allU=[];allAge=[];allAgeDelta=[];rv=[];divs=[];rows=[];age=None;age0=None;prev_rv=None
    for i,d in enumerate(dirs):
        a=sample(d,meta,m);allT.append(a['T']);allU.append(a['U']);rv.append(a['rhoV']);divs.append(a['div'])
        if age is None:
            age=spsolve(a['A'],a['rhoV']);age0=np.zeros_like(age)
        else:
            dt=times[i]-times[i-1];B=a['A']+diags(a['rhoV']/dt)
            age=spsolve(B,a['rhoV']+prev_rv*age/dt);age0=spsolve(B,a['rhoV']+prev_rv*age0/dt)
        if not np.isfinite(age).all() or age.min()<0:raise ValueError('Nonphysical age')
        allAge.append(age.copy());allAgeDelta.append(age-age0);prev_rv=a['rhoV']
        row={'time_s':times[i],**{k:a[k] for k in ('heat_out','mass_out','inmass','stored_energy','radiation','bc_error','minT','maxT')}}
        for k,sel in reg.items():row[k+'_T_C']=float(np.average(a['T'][sel],weights=v[sel])-273.15);row[k+'_speed']=float(np.average(np.linalg.norm(a['U'][sel],axis=1),weights=v[sel]))
        row['age_min']=float(np.average(age[occupied],weights=v[occupied])/60);rows.append(row)
    allT=np.array(allT);allU=np.array(allU);rv=np.array(rv);divs=np.array(divs);allAge=np.array(allAge);allAgeDelta=np.array(allAgeDelta)
    mean=lambda a:time_mean(times,a,start,end)
    T=mean(allT);U=mean(allU);speed=mean(np.linalg.norm(allU,axis=2));age=mean(allAge);mid=(start+end)/2
    splitT=float(np.average(abs(time_mean(times,allT,start,mid)-time_mean(times,allT,mid,end)),weights=v))
    splitU=float(np.average(np.linalg.norm(time_mean(times,allU,start,mid)-time_mean(times,allU,mid,end),axis=1),weights=v))
    # Endpoint values use linear interpolation, consistent with quadrature.
    interp=lambda a,t:np.array([np.interp(t,times,a[:,j]) for j in range(a.shape[1])])
    mass_storage=(interp(rv,end)-interp(rv,start))/(end-start)
    local=mean(divs)+mass_storage
    mdot=float(mean([r['inmass'] for r in rows]));power=cfg['heater_power_W']
    energy=np.array([r['stored_energy'] for r in rows]);storage=(np.interp(end,times,energy)-np.interp(start,times,energy))/(end-start)
    heat=float(mean([r['heat_out'] for r in rows]));res=(power-heat-storage)/power
    use=(times>=start)&(times<=end);age_sensitivity=float(np.average(mean(allAgeDelta)[occupied],weights=v[occupied])/np.average(age[occupied],weights=v[occupied]))
    stats={'solver':'buoyantPimpleFoam','case':cfg['name'],'window_start_s':start,'window_end_s':end,'window_duration_s':end-start,'samples_total':len(times),'sample_interval_max_s':float(np.diff(times).max()),'cells':meta['n_cells'],
        'energy_balance_relative':res,'mean_heat_out_W':heat,'energy_storage_rate_W':float(storage),'mean_mass_in_kg_s':mdot,
        'mass_balance_relative':float(abs(local.sum())/mdot),'local_mass_balance_relative':float(np.abs(local).sum()/mdot),
        'radiation_closure_relative':float(mean(np.abs([r['radiation'] for r in rows]))/power),
        'boundary_heat_balance_relative':float(mean([r['bc_error'] for r in rows])/power),
        'split_window_temperature_difference_K':splitT,'split_window_velocity_difference_m_s':splitU,
        'air_temperature_min_C':min(r['minT'] for r in rows)-273.15,'air_temperature_max_C':max(r['maxT'] for r in rows)-273.15,
        'occupied_mean_age_min':float(np.average(age[occupied],weights=v[occupied])/60),'age_initial_condition_sensitivity_relative':age_sensitivity,
        'nominal_mass_residence_min':float(mean(rv.sum(axis=1))/mdot/60),'regions':{},'time_step_sensitivity_verified':False}
    stats['occupied_age_factor']=stats['occupied_mean_age_min']/stats['nominal_mass_residence_min']
    for k,sel in reg.items():
        stats['regions'][k]={'mean_temperature_C':float(np.average(T[sel],weights=v[sel])-273.15),'mean_speed_m_s':float(np.average(speed[sel],weights=v[sel])),
            'mean_temperature_spatial_p10_C':weighted_percentile(T[sel]-273.15,v[sel],10),'mean_temperature_spatial_p90_C':weighted_percentile(T[sel]-273.15,v[sel],90),
            'split_temperature_difference_K':float(abs(time_mean(times,[r[k+'_T_C'] for r in rows],start,mid)-time_mean(times,[r[k+'_T_C'] for r in rows],mid,end))),
            'split_speed_difference_m_s':float(abs(time_mean(times,[r[k+'_speed'] for r in rows],start,mid)-time_mean(times,[r[k+'_speed'] for r in rows],mid,end)))}
    # Sampling sensitivity: recompute time means from every second stored field.
    reduced=np.unique(np.r_[np.arange(0,len(times),2),len(times)-1]);stats['sampling_temperature_difference_K']=float(np.average(abs(time_mean(times[reduced],allT[reduced],start,end)-T),weights=v))
    failures=[]
    for name,limit in [('mass_balance_relative',.005),('local_mass_balance_relative',.02),('energy_balance_relative',.05),('radiation_closure_relative',.02),('boundary_heat_balance_relative',.05),('split_window_temperature_difference_K',.5),('split_window_velocity_difference_m_s',.01),('sampling_temperature_difference_K',.1)]:
        if abs(stats[name])>limit:failures.append(f'{name}: {stats[name]:.6g} > {limit}')
    for name,r in stats['regions'].items():
        if r['split_temperature_difference_K']>.5:failures.append(name+' bank temperature window drift >0.5 K')
        if r['split_speed_difference_m_s']>.01:failures.append(name+' bank speed window drift >0.01 m/s')
    if end-start<100:failures.append('averaging window shorter than 100 s')
    info=json.loads((path/'transient.json').read_text())
    if times[-1]<info['end_time_s']-1e-6:failures.append('planned end time not reached')
    log=(path/'log.transient').read_text()
    dt,co,initial_co=time_diagnostics(log)
    stats['actual_delta_t_min_s']=min(dt) if dt else None;stats['actual_delta_t_max_s']=max(dt) if dt else None
    stats['completed_step_reported_Co_max']=max(co) if co else None
    stats['initial_pre_adjustment_Co_max']=max(initial_co) if initial_co else None
    if not dt or not co:failures.append('missing solver time-step diagnostics')
    elif max(co)>1.2*info['max_Co']:failures.append('completed-step Courant exceeds configured limit by >20%')
    stats['thermal_window_pass']=not failures;stats['quality_failures']=failures;stats['age_initialization_pass']=age_sensitivity<=.05
    # No experimental validation or time-step independence is implied by this flag.
    (path/'transient_results.json').write_text(json.dumps(stats,indent=2)+'\n');(path/'time_series.json').write_text(json.dumps(rows,indent=2)+'\n')
    np.savez_compressed(path/'mean_fields.npz',T_C=T-273.15,U=U,mean_speed=speed,age_s=age,centers=xyz,volumes=v)
    plot(path,meta,m,T,U,rows,stats)
    return stats

def plot(path,meta,m,T,U,rows,stats):
    ids=m['ids'];mask=ids>=0;temp=np.full(ids.shape,np.nan);temp[mask]=T[ids[mask]]-273.15;vel=np.zeros((*ids.shape,3));vel[mask]=U[ids[mask]]
    axes=[(m[k][1:]+m[k][:-1])/2 for k in 'xyz'];fig,axs=plt.subplots(1,2,figsize=(13,5.5),constrained_layout=True)
    g=meta['geometry'];x0=(g['supply'][0][0]+g['supply'][1][0]/2)/1000
    for ax,x,title in zip(axs,[x0,2.5],['Ofen / Zuluft','Bankbereich']):
        ix=int(np.argmin(abs(axes[0]-x)));im=ax.pcolormesh(m['y'],m['z'],temp[ix].T,cmap='inferno',vmin=np.floor(np.nanmin(temp)/5)*5,vmax=np.ceil(np.nanmax(temp)/5)*5)
        q=ax.quiver(axes[1][::2],axes[2][::2],vel[ix,::2,::2,1].T,vel[ix,::2,::2,2].T,color='cyan',scale=3);ax.quiverkey(q,.8,.96,.2,'0,2 m/s')
        ax.set(title=title,xlabel='Längsrichtung y [m]',ylabel='Höhe [m]');ax.set_aspect('equal')
    fig.colorbar(im,ax=axs,label='Zeitlich gemittelte Lufttemperatur [°C]')
    status='Fensterprüfungen bestanden' if stats['thermal_window_pass'] else 'Mittelwerte noch nicht freigegeben'
    fig.suptitle(f"Zeitmittel {stats['window_start_s']:g}–{stats['window_end_s']:g} s | {status}\nURANS, {meta['config']['heater_power_W']:g} W; angenommene Randbedingungen; Zeitschrittvergleich separat")
    fig.savefig(path/'transient_mean.png',dpi=150);plt.close(fig)
    fig,axs=plt.subplots(2,1,figsize=(10,6),sharex=True,constrained_layout=True);t=[r['time_s'] for r in rows]
    for k,label in [('upper','Obere Bank'),('lower','Untere Bank')]:
        axs[0].plot(t,[r[k+'_T_C'] for r in rows],label=label);axs[1].plot(t,[r[k+'_speed'] for r in rows],label=label)
    for ax in axs:ax.axvspan(stats['window_start_s'],stats['window_end_s'],color='green',alpha=.1);ax.grid(alpha=.2);ax.legend()
    axs[0].set_ylabel('Raummittel über Bank [°C]');axs[1].set_ylabel('Mittlerer Geschwindigkeitsbetrag [m/s]');axs[1].set_xlabel('Physikalische Zeit ab warmem Startfeld [s]')
    fig.savefig(path/'transient_history.png',dpi=150);plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('case',type=Path);p.add_argument('--start',type=float,default=100);p.add_argument('--end',type=float);a=p.parse_args();print(json.dumps(summarize(a.case,a.start,a.end),indent=2))
