"""Generate dimensioned SVG projections from current OpenSCAD source (mm)."""
from pathlib import Path
import subprocess,json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]; out=ROOT/'web/assets';out.mkdir(parents=True,exist_ok=True)
r=subprocess.run(['openscad','-o','/tmp/web-params.csg','-D','part="metadata"',str(ROOT/'cad/layout-metadata.scad')],capture_output=True,text=True,check=True)
g=dict((v[0],v[1:]) for v in (json.loads(l[6:]) for l in r.stderr.splitlines() if l.startswith('ECHO: ')))
w,d,x,e,t,p,h,roof=g['layout'];lo,up,by,bw,bl,lz,uz=g['benches'];sh,eh,l,sy,ex,cw,ch,rw,rh=g['doors']
(out/'dimensions.json').write_text(json.dumps(g))
def dim(a,b,label,vertical=False):
 x1,y1=a;x2,y2=b
 tx=(x1+x2)/2;ty=(y1+y2)/2-35
 rotate=f'transform="rotate(-90 {tx-35} {(y1+y2)/2})"' if vertical else ''
 if vertical:tx-=35;ty=(y1+y2)/2
 return f'<g class="dim"><path d="M{x1} {y1}L{x2} {y2}" marker-start="url(#arrow)" marker-end="url(#arrow)"/><text x="{tx}" y="{ty}" {rotate}>{label}</text></g>'
def rect(a,b,c,f,cls='wood'):
 return f'<rect class="{cls}" x="{a}" y="{b}" width="{c}" height="{f}"/>'
def svg(body,viewbox):
 return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}"><defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10" fill="none" stroke="#217566" stroke-width="1.4"/></marker></defs><style>path,rect,line{{vector-effect:non-scaling-stroke}}.wall{{fill:#dedbd1;stroke:#354b45;stroke-width:1.4}}.wood{{fill:#eadbc3;stroke:#8d7757;stroke-width:1}}.glass{{fill:#c9e1df;stroke:#648c8b;stroke-width:1}}.dim{{fill:none;stroke:#217566;stroke-width:1}}text{{font:64px sans-serif;fill:#217566;stroke:none;text-anchor:middle}}.label{{fill:#63716b;font:65px sans-serif}}.swing{{fill:none;stroke:#87968e;stroke-width:1;stroke-dasharray:5 4}}</style>{body}</svg>'''
subprocess.run(['openscad','-o','/tmp/web-walls.svg','-D','part="audit_walls"',str(ROOT/'cad/sauna-detailed.scad')],capture_output=True,check=True)
paths=''.join('<path class="wall" fill-rule="evenodd" d="'+q.attrib['d']+'"/>' for q in ET.parse('/tmp/web-walls.svg').iter() if q.tag.endswith('path'))
body=paths+rect(lo,-by-bl,bw,bl)+rect(up,-by-bl,bw,bl)+rect(x,0,45,e,'glass')+rect(250,-d+250,470,470)
for hinge,is_sauna in [(sh,True),(eh,False)]:
 hx,hy=hinge[:2]
 if is_sauna:
  body+=f'<path class="swing" d="M{hx} {-hy+l} A{l} {l} 0 0 1 {hx-l} {-hy} L{hx} {-hy} Z"/>'
 else:body+=f'<path class="swing" d="M{hx+l} {-hy} A{l} {l} 0 0 1 {hx} {-hy+l} L{hx} {-hy} Z"/>'
body+=dim((0,-d-220),(w,-d-220),f'{w:g} mm')+dim((w+250,-d),(w+250,e),f'{d+e:g} mm',True)
body+=dim((lo+80,-by-bl),(lo+80,-by),f'{bl:g} mm',True)+dim((lo,700),(lo+bw,700),f'{bw:g}')
body+=dim((t,-600),(x,-600),f'{x-t:g} mm lichte Breite')
body+=f'<text class="label" x="800" y="-1050">Vorraum</text><text class="label" x="2500" y="-1100">Sauna</text>'
(out/'plan.svg').write_text(svg(body,f'-420 {-d-500} {w+1050} {d+e+950}'))
# Side/front: true CAD projection, not a hand-drawn substituted model.
for name,rotation,span in [('front',[-90,0,0],w),('side',[-90,0,90],d+e)]:
 src=ROOT/'build'/f'web-{name}.scad';src.parent.mkdir(exist_ok=True)
 # Project the CAD mesh exports used by Blender.
 # Use individually exported assembled meshes; bypass main selector.
 meshparts=['wall_cladding','glass_front','glass_frame','roof_covering','roof_fascia','floor_boards','entrance_door_leaf','entrance_door_frame','concrete_piers']
 src.write_text('projection()rotate('+json.dumps(rotation)+')union(){'+''.join('import("'+str(ROOT/'build/meshes'/f'assembled_{p}.stl')+'");' for p in meshparts)+'}')
 target=ROOT/'build'/f'{name}.svg';subprocess.run(['openscad','-o',str(target),str(src)],capture_output=True,check=True)
 tree=ET.parse(target);root=tree.getroot();raw=''.join('<path class="wall" fill-rule="evenodd" d="'+q.attrib['d']+'"/>' for q in root.iter() if q.tag.endswith('path'))
 xx,yy,ww,hh=map(float,root.attrib['viewBox'].split())
 raw+=dim((xx,-h),(xx,0),f'{h:g} mm lichte Höhe',True)
 start=0 if name=='front' else -d
 raw+=dim((start,500),(start+span,500),f'{span:g} mm Außenmaß ohne Dach')
 raw+=f'<text class="label" x="{xx+ww/2}" y="700">Fertigboden ±0 · Dachoberkante +{h+roof:g} mm</text>'
 (out/f'{name}.svg').write_text(svg(raw,f'{xx-400} {yy-200} {ww+800} {hh+1100}'))
