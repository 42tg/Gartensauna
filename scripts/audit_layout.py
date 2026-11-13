#!/usr/bin/env python3
"""Independent 2D envelope/swing check against an actual OpenSCAD wall section.
Units mm. Planning proxies, not hardware certification or construction approval.
Requires shapely; optional --plan additionally requires matplotlib.
"""
import argparse,json,math,re,subprocess,tempfile,xml.etree.ElementTree as ET
from pathlib import Path
from shapely.geometry import box,LineString,Polygon,GeometryCollection
from shapely.ops import unary_union
from shapely.affinity import rotate,translate
ROOT=Path(__file__).resolve().parents[1]

def svg_geometry(path):
    # OpenSCAD SVG uses only M/L/z, even-odd contour filling and negated CAD y.
    result=GeometryCollection()
    for item in ET.parse(path).iter():
        if not item.tag.endswith('path'):continue
        for contour in re.findall(r'M\s*(.*?)\s*z',item.attrib['d'],re.S):
            numbers=[float(n) for n in re.findall(r'-?\d+(?:\.\d+)?(?:e[+-]?\d+)?',contour,re.I)]
            poly=Polygon([(numbers[i],-numbers[i+1]) for i in range(0,len(numbers),2)])
            result=result.symmetric_difference(poly)
    return result

def evaluate():
    with tempfile.TemporaryDirectory() as td:
        out=Path(td)
        r=subprocess.run(['openscad','-o',str(out/'params.csg'),'-D','part="metadata"',str(ROOT/'cad/layout-metadata.scad')],capture_output=True,text=True,check=True)
        assert 'WARNING' not in r.stderr,r.stderr
        g=dict((v[0],v[1:]) for v in (json.loads(l[6:]) for l in r.stderr.splitlines() if l.startswith('ECHO: ')))
        subprocess.run(['openscad','-o',str(out/'walls.svg'),'-D','part="audit_walls"',str(ROOT/'cad/sauna-detailed.scad')],capture_output=True,text=True,check=True)
        actual_walls=svg_geometry(out/'walls.svg')
    w,d,x,e,t,p,h,roof=g['layout'];lo,up,by,bw,bl,lz,uz=g['benches'];sh,eh,l,sy,ex,cw,ch,rw,rh=g['doors']
    walls=unary_union([box(0,0,t,d),box(0,d-t,w,d),box(w-t,-e,w,d),box(0,0,x,t),box(x+45,-e,w,-e+t),box(x,0,x+p,d-t)]).difference(unary_union([box(x-1,sy,x+p+1,sy+rw),box(ex,-1,ex+rw,t+1)]))
    frames=unary_union([box(x,sy,x+p,sy+40),box(x,sy+40+cw,x+p,sy+rw),box(ex,0,ex+40,t),box(ex+40+cw,0,ex+rw,t)])
    assert actual_walls.symmetric_difference(unary_union([walls,frames])).area<1,'Independent wall-section mismatch (mm²)'
    chair=box(250,d-720,720,d-250)
    benches=unary_union([box(lo,by,lo+bw,by+bl),box(up,by,up+bw,by+bl)])
    glass=box(x,-e,x+45,0)
    sauna_local=unary_union([box(-4,-l,4,0),box(-39,-l+65,39,-l+85)])
    entry_local=unary_union([box(0,-30,l,30),box(l-100,-65,l,65)])
    def pose(poly,hinge,a):return translate(rotate(poly,-a,origin=(0,0)),hinge[0],hinge[1])
    obstacles=unary_union([actual_walls,chair,benches,glass])
    swing={}
    # Samples every 0.05 degrees, with a conservative inter-sample motion bound.
    for name,poly,hinge in [('sauna',sauna_local,sh),('entrance',entry_local,eh)]:
        sampled=[pose(poly,hinge,i/20) for i in range(1801)]
        radius=max(math.hypot(a,b) for part in ([poly] if poly.geom_type=='Polygon' else poly.geoms) for a,b in part.exterior.coords)
        uncertainty=radius*math.radians(.05)/2
        separation=min(leaf.distance(obstacles) for leaf in sampled)
        assert separation>uncertainty,(name,separation,uncertainty)
        swing[name]={'sample_step_deg':.05,'conservative_obstacle_gap_mm':separation-uncertainty,
                     'chair_gap_lower_bound_mm':min(leaf.distance(chair) for leaf in sampled)-uncertainty,
                     'inter_sample_bound_mm':uncertainty}
    # Simultaneous door operation: the complete sweep bounding regions are disjoint.
    assert sh[1]-math.hypot(l,39)>eh[1]+65
    openob=unary_union([obstacles,pose(sauna_local,sh,90),pose(entry_local,eh,90)])
    route=LineString([(2600,1120),(1850,1120),(1850,1100),(1050,1100),(1050,600),(740,500),(740,-1000)])
    radius=route.distance(openob)
    assert radius>=299.99,'600 mm circular planning gauge cannot traverse rear entry route'
    area=((w-t)-(x+45))*(e-t)+(w-t-(x+p))*(d-t)
    volume=area*h/1e9
    door_recess=(x+p-(sh[0]+4))*cw*ch/1e9
    glass_area=(e-70)*(h-70)/1e6+l*1977/1e6
    report={'status':'geometric planning checks passed; construction approval NOT established',
        'cad_parameters':g,'width_mm':w,'partition_mm':p,'changing_room_mm':[x-t,d-2*t],
        'clear_height_mm':h,'roof_top_above_floor_mm':h+roof,'roof_external_bounds_mm':[w+160,d+e+160],
        'bench_mm':[bw,bl],'bench_top_mm':[lz,uz],'headroom_above_upper_mm':h-uz,
        'rear_landing_mm':d-t-by-bl,'window_aisle_mm':lo-x-45,'side_aisle_at_partition_mm':lo-x-p,
        'door_frame_clearance_mm':[cw,ch],'rough_opening_mm':[rw,rh],
        'sauna_leaf_open_clear_width_mm':(sh[1]-4)-(sy+40),
        'entrance_leaf_open_clear_width_mm':ex+40+cw-(eh[0]+30),
        'door_sweeps':swing,'route_gauge_diameter_mm':2*radius,
        'sauna_main_floor_area_m2':area/1e6,'sauna_main_volume_m3':volume,
        'door_recess_allowance_m3':door_recess,'glass_area_m2':glass_area,
        'huum_effective_volume_with_recess_m3':volume+door_recess+glass_area,
        'six_air_changes_m3h':6*(volume+door_recess),
        'nominal_80m3h_air_changes':80/(volume+door_recess),
        'footprint_m2':(w*d+2000*e)/1e6,'exterior_perimeter_m':2*(w+d+e)/1000,
        'unresolved':['Bench access: rises 535 and 440 mm; no safe stair designed.',
        'Heater DROP reference rated to 13 m³: effective volume exceeds range.',
        'Doors are planning proxies; chosen product, seals, rebate, hinge fixings and opening tolerances unconfirmed.',
        'External door sweep and new footprint need on-site measurement.',
        'Structure, foundations, roof drainage, glazing, moisture details and electrical installation unverified.',
        'Airflow is nominal; actual pressure losses, fan curve and thermal CFD are not validated.']}
    return report,route

def plan(report,route,dest):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as Patch,Arc
    fig,ax=plt.subplots(figsize=(11,11));fig.patch.set_facecolor('#f5f3ed');ax.set_facecolor('#f5f3ed')
    geom=svg_geometry(ROOT/'docs/visuals/grundriss-v3.svg')
    for poly in geom.geoms if hasattr(geom,'geoms') else [geom]:
        ax.add_patch(Patch(poly.exterior.coords,facecolor='#b5a58c',edgecolor='#554b3e',linewidth=.5))
        for hole in poly.interiors:ax.add_patch(Patch(hole.coords,facecolor='#f5f3ed',edgecolor='#554b3e',linewidth=.4))
    g=report['cad_parameters'];w,d,x,e,t,p,h,roof=g['layout'];sh,eh,l,*_=g['doors']
    for center,a,b in [(sh,180,270),(eh,270,360)]:ax.add_patch(Arc(center[:2],2*l,2*l,theta1=a,theta2=b,color='#087e8b',linestyle='--',linewidth=1.5))
    xx,yy=route.xy;ax.plot(xx,yy,color='#087e8b',lw=2,alpha=.65)
    def txt(a,b,s,size=10):ax.text(a,b,s,ha='center',va='center',fontsize=size,color='#26313b',bbox=dict(facecolor='#f5f3ed',alpha=.9,pad=2,edgecolor='none'))
    def dim(a,b,label,offset=0):
        ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='<->',color='#455568',lw=1));txt((a[0]+b[0])/2,(a[1]+b[1])/2+offset,label,10)
    dim((0,1870),(w,1870),'3.605 mm außen',85)
    dim((3820,-2000),(3820,1700),'3.700 mm',0)
    dim((205,420),(1605,420),'1.400 mm licht',-90)
    txt(800,750,'VORRAUM\n1.400 × 1.290 mm')
    txt(2480,-240,'untere Liege\n600 × 2.100\nHöhe 535 mm')
    txt(3090,-240,'obere Liege\n600 × 2.100\nHöhe 975 mm')
    txt(2510,1295,'675 mm hinter den Bänken')
    txt(1910,-850,'520 mm\nGang',9)
    ax.text(1500,-1350,'GLASFRONT ZUM GARTEN',rotation=90,ha='center',va='center',color='#087e8b',fontsize=10)
    txt(2120,-1640,'OFEN*',9)
    ax.annotate('Trennwand 128,1 mm\nVorraumseite bündig',xy=(1665,280),xytext=(2450,350),fontsize=10,ha='center',arrowprops=dict(arrowstyle='->',color='#455568'),bbox=dict(facecolor='#f5f3ed',edgecolor='none'))
    ax.annotate('Saunatür nach außen\n793 mm bei 90°',xy=(1350,1417),xytext=(850,1630),fontsize=9,ha='center',arrowprops=dict(arrowstyle='->',color='#087e8b'),bbox=dict(facecolor='#f5f3ed',edgecolor='none'))
    txt(760,-370,'Außentür nach außen\n767 mm bei 90°',9)
    txt(670,-1070,'Türblatt + Griff\nSchwenkbögen gestrichelt',9)
    fig.suptitle('Gartensauna · geprüfter CAD-Grundriss mit Türen',fontsize=17,y=.965)
    fig.text(.5,.925,'Neubau · lichte Höhe 2.200 mm · Türen bei 90° geöffnet',ha='center',fontsize=11)
    fig.text(.5,.06,'Türzargen nominal 800 × 2.000 mm; Produktmaße noch offen.\nTürschwenkwege kollisionsfrei; blaue Route mit Ø 600-mm-Prüfkörper geprüft.\n*DROP ist zu klein dimensioniert. Bankaufstieg weiterhin ungelöst.\nPlanungsgeometrie, kein Aufmaß oder Ausführungsplan.',ha='center',fontsize=10,color='#663e27',linespacing=1.5)
    ax.set_xlim(-200,4120);ax.set_ylim(-2200,2120);ax.set_aspect('equal');ax.axis('off');fig.subplots_adjust(top=.9,bottom=.15,left=.04,right=.96)
    fig.savefig(dest,dpi=180);plt.close(fig)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--plan',type=Path);parser.add_argument('--output',type=Path,default=ROOT/'build/audit/layout.json');args=parser.parse_args()
    report,route=evaluate();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    if args.plan:plan(report,route,args.plan)
    print(json.dumps(report,indent=2))
