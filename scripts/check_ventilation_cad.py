#!/usr/bin/env python3
"""Fail if ventilation rough openings cut framing/battens or miss facade."""
import subprocess
import tempfile
from pathlib import Path
from simulate_ventilation import ROOT,geometry

g=geometry()
assert g['supply'][0][2]>=400
assert g['exhaust'][0][2]+g['exhaust'][1][2]<=600
assert g['drying'][0][2]+g['drying'][1][2]<g['room'][1][2]
# Verify against actual evaluated CAD geometry rather than duplicated stud spacings.
with tempfile.TemporaryDirectory() as td:
    src=Path(td)/'collision.scad';out=Path(td)/'collision.stl'
    src.write_text(f'''include <{ROOT/'cad/sauna-detailed.scad'}>
intersection() {{ ventilation_openings();
union() {{ for(f=faces)face(f){{
layer_local("wall_studs",f[2]);
layer_local("wall_battens",f[2]);
layer_local("service_battens",f[2]);
}} }} }}
''')
    r=subprocess.run(['openscad','-D','part="check"','-o',str(out),str(src)],capture_output=True,text=True)
    if out.exists() or 'Current top level object is empty' not in r.stderr:
        raise RuntimeError('Opening/frame collision or CAD failure: '+r.stderr)
print('Ventilation: no stud/batten intersections; height checks pass.')
