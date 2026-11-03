#!/usr/bin/env python3
"""Bounded 60-minute URANS study worker with compact, failure-preserving exports."""
import argparse,json,subprocess,shutil,gzip,tarfile,traceback,re
from pathlib import Path
from study_cases import case,settings
from thermal_case import mesh
from thermal_fields import write_case
from run_thermal import foam_env
from run_transient import prepare,run
from transient_results import summarize
from simulate_ventilation import ROOT

def execute(variant,scenario='nominal',smoke=False,ranks=None):
    g,c,provenance=case(variant,scenario);s=settings();name=c['name'];seed=ROOT/'build/study-seeds'/name;dest=ROOT/'build/study'/name;export=ROOT/'build/study-artifacts'/name
    export.mkdir(parents=True,exist_ok=True)
    try:
        if seed.exists() or dest.exists():raise ValueError('Existing study case; preserve it instead of overwriting')
        seed.mkdir(parents=True);meta=mesh(g,c,seed);write_case(seed,meta);env=foam_env()
        if 'heater_emissivity' in c:
            p=seed/'constant/boundaryRadiationProperties';text=p.read_text();e=c['heater_emissivity']
            text=re.sub(r'heater\s*\{[^}]+\}',f'heater {{type lookup; emissivity {e}; absorptivity {e}; transmissivity 0;}}',text)
            p.write_text(text)
        with (seed/'log.checkMesh').open('w') as f:subprocess.run(['checkMesh','-case',str(seed)],env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=180)
        if 'Mesh OK.' not in (seed/'log.checkMesh').read_text():raise ValueError('Seed mesh failed')
        with (seed/'log.seed').open('w') as f:subprocess.run(['buoyantSimpleFoam','-noFunctionObjects','-case',str(seed)],env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=2400)
        end=10 if smoke else s['end_time_s'];sample=1 if smoke else s['sample_s']
        prepare(seed,dest,end,sample,provenance['max_Co'],provenance['max_delta_t_s'],1)
        provenance.update({'study_id':s['id'],'smoke':smoke,'seed_iterations':c['iterations']})
        (dest/'study_case.json').write_text(json.dumps(provenance,indent=2)+'\n')
        run(dest,timeout=18000,ranks=ranks or s['ranks'])
        r=summarize(dest,5 if smoke else s['mean_start_s'])
        print(json.dumps({'case':name,'thermal':r['thermal_window_pass'],'age':r['age_quality_pass'],'failures':r['quality_failures']+r['age_quality_failures']}),flush=True)
    except Exception as e:
        (export/'failure.json').write_text(json.dumps({'case':name,'error':str(e),'traceback':traceback.format_exc()},indent=2)+'\n');raise
    finally:
        for folder in (seed,dest):
            if folder.exists():
                for p in folder.glob('log.*'):
                    with p.open('rb') as src,gzip.open(export/(folder.parent.name+'-'+p.name+'.gz'),'wb') as target:shutil.copyfileobj(src,target)
        if dest.exists():
            for pattern in ('*.json','*.png','mean_fields.npz'):
                for p in dest.glob(pattern):shutil.copy2(p,export/p.name)
            # A compact restart is retained for failures or longer follow-up runs.
            times=sorted([p for p in dest.iterdir() if p.is_dir() and p.name.replace('.','',1).isdigit()],key=lambda p:float(p.name))
            if times:
                with tarfile.open(export/'restart.tar.gz','w:gz') as tar:
                    for p in [times[-1],dest/'constant',dest/'system',dest/'case.json',dest/'mesh_arrays.npz',dest/'transient.json']:
                        if p.exists():tar.add(p,arcname=p.name)
    if not smoke and not (r['thermal_window_pass'] and r['age_quality_pass']):raise RuntimeError('Study window not qualified; diagnostic exports retained')
    return export

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('variant');p.add_argument('--scenario',default='nominal');p.add_argument('--smoke',action='store_true');p.add_argument('--ranks',type=int);a=p.parse_args();execute(a.variant,a.scenario,a.smoke,a.ranks)
