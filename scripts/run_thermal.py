#!/usr/bin/env python3
"""Run version-pinned OpenFOAM with startup continuation and explicit audits."""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from simulate_ventilation import ROOT
from thermal_case import mesh
from thermal_fields import write_case
from thermal_results import summarize


def foam_env():
    env=os.environ.copy()
    if root:=env.get('FOAM_RUNTIME_ROOT'):
        prefix=Path(root)/'usr'
        env['PATH']=str(prefix/'bin')+os.pathsep+env['PATH']
        env['LD_LIBRARY_PATH']=os.pathsep.join([str(prefix/'lib'),str(prefix/'lib/x86_64-linux-gnu'),env.get('LD_LIBRARY_PATH','')])
        env['WM_PROJECT_DIR']=str(prefix/'share/openfoam');env['FOAM_LIBBIN']=str(prefix/'lib')
    else:
        env.setdefault('WM_PROJECT_DIR','/usr/share/openfoam');env.setdefault('FOAM_LIBBIN','/usr/lib')
    lib=ROOT/'build/thermal-lib'
    env['LD_LIBRARY_PATH']=str(lib)+os.pathsep+env.get('LD_LIBRARY_PATH','')
    env['FOAM_USER_LIBBIN']=str(lib)
    return env


def continue_power(path,power):
    text=path.read_text();text=re.sub(r'\bQ\s+[-+\d.eE]+;',f'Q {power};',text)
    path.write_text(text)



def run(name,iterations=None):
    env=foam_env();version=subprocess.run(['buoyantSimpleFoam','-help'],env=env,capture_output=True,text=True,check=True)
    if '1912' not in version.stdout+version.stderr:raise RuntimeError('Validated runtime required: OpenFOAM OpenCFD v1912 (Ubuntu 24.04 package).')
    config=json.loads((ROOT/'simulation/thermal/config.json').read_text());cfg={**config['base'],**next(c for c in config['cases'] if c['name']==name)}
    if iterations is not None:cfg['iterations']=iterations
    from simulate_ventilation import geometry
    dest=ROOT/'build/thermal'/name
    if dest.exists() and any(p.is_dir() and p.name.isdigit() and p.name!='0' for p in dest.iterdir()):
        raise RuntimeError(f'{dest} already has results. Preserve or move them before starting a fresh run.')
    dest.mkdir(parents=True,exist_ok=True);meta=mesh(geometry(),cfg,dest);write_case(dest,meta)
    (dest/'runtime.txt').write_text(version.stdout+version.stderr)
    def execute(cmd,log,timeout):
        with (dest/log).open('w') as f:
            subprocess.run(cmd+['-case',str(dest)],stdout=f,stderr=subprocess.STDOUT,env=env,check=True,timeout=timeout)
    execute(['checkMesh'],'log.checkMesh',120)
    if 'Mesh OK.' not in (dest/'log.checkMesh').read_text():raise RuntimeError('Mesh quality failed')
    print(f'{name}: {meta["n_cells"]} cells, {cfg["heater_power_W"]} W, {cfg["iterations"]} SIMPLE iterations; power ramp {cfg["ramp_iterations"]} iterations',flush=True)
    (dest/'sauna.foam').touch()
    execute(['buoyantSimpleFoam','-noFunctionObjects'],'log.solver',2100)
    r=summarize(dest);print(json.dumps(r,indent=2),flush=True)
    return r


def main():
    p=argparse.ArgumentParser();p.add_argument('case');p.add_argument('--iterations',type=int);p.add_argument('--require-quality',action='store_true');args=p.parse_args()
    try:
        r=run(args.case,args.iterations)
    except Exception as exc:
        dest=ROOT/'build/thermal'/args.case
        if dest.is_dir():
            (dest/'failure.json').write_text(json.dumps({'case':args.case,'error':str(exc),'quality_pass':False},indent=2)+'\n')
        raise
    if args.require_quality and not r['quality_pass']:raise SystemExit('Thermal quality criteria failed; inspect results.json and plots, do not rank this case.')
if __name__=='__main__':main()
