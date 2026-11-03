"""Five CAD-derived virtual vent layouts. No modification of the construction CAD."""
import copy,json,hashlib
from pathlib import Path
import numpy as np
from simulate_ventilation import ROOT,geometry

def implementation_hash():
    files=['scripts/study_cases.py','scripts/study_run.py','scripts/transient_results.py','scripts/run_transient.py','scripts/thermal_case.py','scripts/thermal_fields.py','simulation/thermal/config.json','simulation/ventilation-study.json']
    h=hashlib.sha256()
    for file in files:h.update(file.encode());h.update((ROOT/file).read_bytes())
    return h.hexdigest()

def settings():return json.loads((ROOT/'simulation/ventilation-study.json').read_text())

def case(variant,scenario='nominal',g=None):
    s=settings();v=next(x for x in s['variants'] if x['name']==variant)
    c=json.loads((ROOT/'simulation/thermal/config.json').read_text())['base']
    scenario_cfg={} if scenario=='nominal' else next(x for x in s['validation_scenarios'] if x['name']==scenario)
    c={**c,**{k:x for k,x in scenario_cfg.items() if k not in ('name','max_Co','max_delta_t_s')},'name':variant+'__'+scenario,'iterations':s['seed_iterations']}
    source=geometry() if g is None else g;g=copy.deepcopy(source)
    g['supply'][0][2]=1000*v['supply_center_z_m']-g['supply'][1][2]/2
    g['exhaust'][0][1]=1000*v['exhaust_center_y_m']-g['exhaust'][1][1]/2
    g['exhaust'][0][2]=1000*v['exhaust_center_z_m']-g['exhaust'][1][2]/2
    validate(g)
    return g,c,{'variant':v,'scenario':scenario,'source_geometry_sha256':hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest(),
                'implementation_sha256':implementation_hash(),
                'max_Co':scenario_cfg.get('max_Co',s['max_Co']),'max_delta_t_s':scenario_cfg.get('max_delta_t_s',s['max_delta_t_s'])}

def validate(g):
    lo,hi=map(np.asarray,g['room'][:2]);hp,hs=map(np.asarray,g['heater']);supply,ss=map(np.asarray,g['supply']);ex,es=map(np.asarray,g['exhaust'])
    if not np.isclose(supply[1],lo[1]) or not np.isclose(ex[0],hi[0]):raise ValueError('Ports must lie on the intended exterior walls')
    if not (supply[2]>=hp[2]+hs[2] and supply[2]+ss[2]<hi[2]):raise ValueError('Supply must be above the heater envelope, below roof')
    if not (0<=ex[2] and ex[2]+es[2]<=600):raise ValueError('Operating exhaust must stay below 600 mm')
    if not (ex[1]>=0 and ex[1]+es[1]<hi[1]):raise ValueError('Exhaust must stay on far half of side wall')
    for p,size,axis in [(supply,ss,1),(ex,es,0)]:
        for k in range(3):
            if k!=axis and not (lo[k]<=p[k] and p[k]+size[k]<=hi[k]):raise ValueError('Port outside room')
        for name in ('heater','upper','lower'):
            b,bs=map(np.asarray,g[name]);q=b+bs
            if b[axis]-1e-9<=p[axis]<=q[axis]+1e-9 and all(min(p[k]+size[k],q[k])>max(p[k],b[k]) for k in range(3) if k!=axis):raise ValueError('Port blocked by '+name)

if __name__=='__main__':
    for v in settings()['variants']:
        g,c,p=case(v['name']);print(v['name'],g['supply'],g['exhaust'])
