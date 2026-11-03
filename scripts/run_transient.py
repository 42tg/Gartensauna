#!/usr/bin/env python3
"""Continue a finite thermal field with physical-time buoyantPimpleFoam."""
import argparse, hashlib, json, re, shutil, subprocess, os
from pathlib import Path
from run_thermal import foam_env
from thermal_case import header
from thermal_results import read_field
import numpy as np

def prepare(seed, dest, end=600., sample=5., max_co=.5, max_dt=.1, outer=3):
    if dest.exists(): raise ValueError(f'Refusing to overwrite {dest}')
    meta=json.loads((seed/'case.json').read_text())
    times=sorted([p for p in seed.iterdir() if p.is_dir() and p.name.replace('.','',1).isdigit()],key=lambda p:float(p.name))
    latest=times[-1]
    for field in ('T','p','U'):
        a,_=read_field(latest/field,meta,field=='U')
        if not np.isfinite(a).all(): raise ValueError('Nonfinite seed '+field)
        if field=='T' and (a.min()<200 or a.max()>1500): raise ValueError('Nonphysical seed temperature')
        if field=='p' and a.min()<=0: raise ValueError('Nonpositive seed pressure')
    dest.mkdir(parents=True)
    for directory in ('constant','system'):shutil.copytree(seed/directory,dest/directory)
    shutil.copytree(latest,dest/'0')
    for file in ('case.json','mesh_arrays.npz'):shutil.copy2(seed/file,dest/file)
    # Reset physical clock without reapplying the steady solver's power ramp.
    for p in (dest/'0').iterdir():
        if p.is_file():
            s=p.read_text();s=re.sub(r'\blocation\s+"[^"]*";', 'location "0";',s)
            if p.name=='T':s=re.sub(r'\brampIterations\s+[^;]+;', 'rampIterations 0;',s)
            p.write_text(s)
    s=(dest/'system/fvSchemes').read_text().replace('default steadyState','default Euler').replace('bounded Gauss','Gauss')
    (dest/'system/fvSchemes').write_text(s)
    (dest/'system/fvSolution').write_text(header('dictionary','fvSolution')+f'''
solvers {{
 "rho.*" {{ solver PCG; preconditioner DIC; tolerance 0; relTol 0; }}
 p_rgh {{ solver GAMG; smoother GaussSeidel; tolerance 1e-8; relTol 0; maxIter 200; }}
 p_rghFinal {{ $p_rgh; }}
 Ii {{ solver smoothSolver; smoother symGaussSeidel; tolerance 1e-7; relTol 0; maxIter 100; }}
 "(U|h|k|epsilon).*" {{ solver PBiCGStab; preconditioner DILU; tolerance 1e-8; relTol 0; }}
}}
PIMPLE {{ momentumPredictor yes; nOuterCorrectors {outer}; nCorrectors 2; nNonOrthogonalCorrectors 0; pRefCell 0; pRefValue 101325; turbOnFinalIterOnly false; }}
relaxationFactors {{ equations {{ ".*" 1; }} }}
''')
    (dest/'system/controlDict').write_text(header('dictionary','controlDict')+f'''
application buoyantPimpleFoam;
libs ("libsaunaThermal.so");
startFrom latestTime; startTime 0; stopAt endTime; endTime {end}; deltaT 0.005;
adjustTimeStep yes; maxCo {max_co}; maxDeltaT {max_dt};
writeControl adjustableRunTime; writeInterval {sample}; purgeWrite 0;
writeFormat ascii; writePrecision 10; writeCompression off; timeFormat general; timePrecision 10;
runTimeModifiable false;
functions {{ }}
''')
    info={'solver':'buoyantPimpleFoam','seed_case':meta['config']['name'],'seed_time_directory':latest.name,
          'seed_T_sha256':hashlib.sha256((latest/'T').read_bytes()).hexdigest(),'seed_U_sha256':hashlib.sha256((latest/'U').read_bytes()).hexdigest(),
          'end_time_s':end,'sample_interval_s':sample,'max_Co':max_co,'max_delta_t_s':max_dt,'outer_correctors':outer,
          'power_W':meta['config']['heater_power_W'],'power_ramp':'disabled: full constant power from physical t=0',
          'initial_condition':'Preheated numerical field, not a cold-start heating-time prediction.'}
    (dest/'transient.json').write_text(json.dumps(info,indent=2)+'\n');(dest/'sauna.foam').touch()
    return info

def run(dest,timeout=14400,ranks=1):
    env=foam_env()
    version=subprocess.run(['buoyantPimpleFoam','-help'],env=env,capture_output=True,text=True,check=True)
    if '1912' not in version.stdout+version.stderr:raise RuntimeError('OpenCFD v1912 runtime required')
    (dest/'runtime.txt').write_text(version.stdout+version.stderr)
    check=subprocess.run(['checkMesh','-case',str(dest.resolve())],env=env,capture_output=True,text=True,check=True)
    (dest/'log.checkMesh').write_text(check.stdout+check.stderr)
    if 'Mesh OK.' not in check.stdout:raise RuntimeError('Mesh quality failed')
    command=['buoyantPimpleFoam','-noFunctionObjects','-case',str(dest.resolve())]
    if ranks>1:
        prefix=Path(env.get('FOAM_RUNTIME_ROOT','/'))/'usr'
        mpi=shutil.which('mpirun',path=env['PATH']) or shutil.which('mpirun.openmpi',path=env['PATH'])
        if not mpi:raise RuntimeError('Install openmpi-bin for parallel execution')
        env['LD_LIBRARY_PATH']=str(prefix/'lib/openmpi-system')+os.pathsep+env['LD_LIBRARY_PATH']
        if env.get('FOAM_RUNTIME_ROOT'):env['OPAL_PREFIX']=str(prefix)
        env['OMPI_MCA_btl_vader_single_copy_mechanism']='none'
        if os.getuid()==0:env['OMPI_ALLOW_RUN_AS_ROOT']='1';env['OMPI_ALLOW_RUN_AS_ROOT_CONFIRM']='1'
        (dest/'system/decomposeParDict').write_text(header('dictionary','decomposeParDict')+f'numberOfSubdomains {ranks}; method simple; simpleCoeffs {{ n ({2 if ranks%2==0 else 1} {ranks//2 if ranks%2==0 else ranks} 1); delta 0.001; }}\n')
        with (dest/'log.decompose').open('w') as f:
            subprocess.run(['decomposePar','-latestTime','-force','-case',str(dest.resolve())],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
        command=[mpi,'-np',str(ranks),*command,'-parallel']
    provenance=dest/'execution.json'
    history=json.loads(provenance.read_text()) if provenance.exists() else []
    history.append({'ranks':ranks,'command':command,'status':'started'})
    provenance.write_text(json.dumps(history,indent=2)+'\n')
    try:
        with (dest/'log.transient').open('a') as f:
            subprocess.run(command,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=timeout)
        if ranks>1:
            with (dest/'log.reconstruct').open('w') as f:
                subprocess.run(['reconstructPar','-newTimes','-case',str(dest.resolve())],env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=600)
        history[-1]['status']='completed'
    except Exception as exc:
        history[-1]['status']='failed';history[-1]['error']=str(exc)
        raise
    finally:provenance.write_text(json.dumps(history,indent=2)+'\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--seed',type=Path,required=True);p.add_argument('--dest',type=Path,required=True)
    p.add_argument('--end',type=float,default=600);p.add_argument('--sample',type=float,default=5);p.add_argument('--max-co',type=float,default=.5);p.add_argument('--max-dt',type=float,default=.1);p.add_argument('--outer',type=int,default=3);p.add_argument('--prepare-only',action='store_true');p.add_argument('--ranks',type=int,default=1);a=p.parse_args()
    if min(a.end,a.sample,a.max_co,a.max_dt,a.outer,a.ranks)<=0: p.error('Positive time and solver controls required')
    print(json.dumps(prepare(a.seed,a.dest,a.end,a.sample,a.max_co,a.max_dt,a.outer)),flush=True)
    if not a.prepare_only:run(a.dest,ranks=a.ranks)
if __name__=='__main__':main()
