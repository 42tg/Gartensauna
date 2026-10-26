// Detailed concept geometry. Millimetres; all construction dimensions are assumptions.
// The V3 room layout and openings remain the authoritative footprint.
include <sauna-v3.scad>
include <heater-drop.scad>
part = "detailed_all";
// Layer depths from outside: 18 + 20 + 2 + 100 + 1 + 19 + 20 = 180 mm.
faces = [[1200,-2000,2000,0],[3200,-2000,3700,90],
         [3200,1700,3200,180],[0,1700,1700,270],[0,0,1200,0]];
layer_names = ["wall_cladding","wall_battens","wind_barrier","wall_studs",
               "wall_insulation","vapour_barrier","service_battens","interior_boards"];
module face(f) { translate([f[0],f[1],0]) rotate([0,0,f[3]]) children(); }
module strips(length,d,t,width=120,gap=3) {
    for(u=[0:width:length-0.1]) translate([u,d,0])
        cube([min(width-gap,length-u),t,height]);
}
module panel_frame(length,d,t) {
    for(u=[0:600:length-45]) translate([u,d,45]) cube([45,t,height-90]);
    translate([length-45,d,45])cube([45,t,height-90]);
    for(z=[0,height-45])translate([0,d,z])cube([length,t,45]);
}
module layer_local(name,length) {
    if(name=="wall_cladding") strips(length,0,18);
    if(name=="wall_battens")
        for(z=[150:550:height-50])translate([0,18,z])cube([length,20,45]);
    if(name=="wind_barrier")translate([0,38,0])cube([length,2,height]);
    if(name=="wall_studs")panel_frame(length,40,100);
    if(name=="wall_insulation")difference(){
        translate([0,40,0])cube([length,100,height]);
        panel_frame(length,39,102);
    }
    if(name=="vapour_barrier")translate([0,140,0])cube([length,1,height]);
    if(name=="service_battens")
        for(z=[150:550:height-50])translate([0,141,z])cube([length,19,40]);
    if(name=="interior_boards")strips(length,160,20,95,1.5);
}
module wall_layer(name) {
    intersection(){walls(); union(){for(f=faces)face(f)layer_local(name,f[2]);}}
}
module perimeter_mask(){
    linear_extrude(height=height)difference(){footprint();offset(delta=-wall)footprint();}
}
module partition_mask(){difference(){walls();perimeter_mask();}}
module partition_frame(){
    intersection(){partition_mask();union(){
        for(y=[0:600:main_depth])translate([1110,y,0])cube([270,45,height]);
        for(z=[0,height-45])translate([1110,0,z])cube([270,main_depth,45]);
    }}
}
module partition_boards(){
    intersection(){partition_mask();union(){
        for(x=[1110,1360])for(y=[0:95:main_depth])
            translate([x,y,0])cube([20,93.5,height]);
    }}
}
module floor_joists(){intersection(){
    translate([0,0,-108])footprint_3d(88);
    union(){for(x=[0:400:main_width])translate([x,-wing_extension,-108])cube([45,3700,88]);}
}}
module floor_insulation(){difference(){
    translate([0,0,-108])footprint_3d(88);floor_joists();
}}
module floor_boards(){intersection(){
    translate([0,0,-20])footprint_3d(20);
    union(){for(x=[0:120:main_width])translate([x,-wing_extension,-20])cube([118,3700,20]);}
}}
module roof_mask(z,t){translate([0,0,z])linear_extrude(height=t)offset(r=80)footprint();}
module roof_joists(){intersection(){roof_mask(height+15,120);union(){
    for(x=[-80:600:main_width+80])translate([x,-wing_extension-80,height+15])cube([60,3860,120]);
}}}
module roof_insulation(){difference(){roof_mask(height+15,120);roof_joists();}}
module roof_boards(z,t,width){intersection(){roof_mask(z,t);union(){
    for(y=[-wing_extension-80:width:main_depth+80])
        translate([-80,y,z])cube([main_width+160,width-1.5,t]);
}}}
module bench_slats(x,y,z,w,l){
    n=ceil(w/85); gap=5; slat_w=(w-(n-1)*gap)/n;
    for(i=[0:n-1])translate([x+i*(slat_w+gap),y,z])cube([slat_w,l,28]);
    for(dy=[0:650:l-45])translate([x,y+dy,z-50])cube([w,45,50]);
    for(dy=[0,l-60])for(dx=[0,w-45])translate([x+dx,y+dy,0])cube([45,45,z-50]);
}
module window_frame(){
    // Concept aluminium perimeter, no invented glass segmentation.
    for(y=[-wing_extension,-35])translate([1200,y,0])cube([45,35,height]);
    for(z=[0,height-35])translate([1200,-wing_extension,z])cube([45,wing_extension,35]);
}
module select_part(name){
    heater_part(name);
    if(name=="concrete_piers")intersection(){
        translate([0,0,-300])footprint_3d(180);
        union(){for(x=[0:900:main_width])for(y=[-wing_extension:900:main_depth])
            translate([x,y,-300])cube([250,250,180]);}
    }
    if(name=="floor_underside")translate([0,0,-120])footprint_3d(12);
    if(name=="floor_joists")floor_joists();
    if(name=="floor_insulation")floor_insulation();
    if(name=="floor_boards")floor_boards();
    for(n=layer_names)if(name==n)wall_layer(n);
    if(name=="partition_frame")partition_frame();
    if(name=="partition_boards")partition_boards();
    if(name=="ceiling_boards")roof_boards(height,15,95);
    if(name=="roof_joists")roof_joists();
    if(name=="roof_insulation")roof_insulation();
    if(name=="roof_deck")roof_boards(height+135,22,140);
    if(name=="roof_covering")roof_mask(height+157,3);
    if(name=="roof_fascia")difference(){roof_mask(height,157);translate([0,0,height-1])
        linear_extrude(height=160)offset(r=60)footprint();}
    if(name=="bench_upper")bench_slats(bench_upper_x,bench_start_y,bench_upper_z,bench_depth,bench_length);
    if(name=="bench_lower")bench_slats(bench_lower_x,bench_start_y,bench_lower_z,bench_depth,bench_length);
    if(name=="changing_chair")chair();
    if(name=="glass_front")translate([1207,-wing_extension+35,35])cube([24,wing_extension-70,height-70]);
    if(name=="glass_frame")window_frame();
}
names = ["concrete_piers","floor_underside","floor_joists","floor_insulation","floor_boards",
         "wall_cladding","wall_battens","wind_barrier","wall_studs","wall_insulation",
         "vapour_barrier","service_battens","interior_boards","partition_frame","partition_boards",
         "ceiling_boards","roof_joists","roof_insulation","roof_deck","roof_covering","roof_fascia",
         "bench_upper","bench_lower","changing_chair","glass_front","glass_frame",
         "heater_cage","heater_mount","heater_stones"];
function explode_z(n) = n=="concrete_piers" ? -800 : n=="floor_underside" ? -600 :
    n=="floor_joists" || n=="floor_insulation" ? -350 : n=="floor_boards" ? -120 :
    n=="ceiling_boards" ? 800 : n=="roof_joists" || n=="roof_insulation" ? 1200 :
    n=="roof_deck" ? 1700 : n=="roof_covering" ? 2050 : n=="roof_fascia" ? 1500 : 0;
if(part=="plan") {
    projection(cut=false) union(){
        // Horizontal wall section through openings; omit door lintels in plan.
        intersection(){ walls(); translate([-100,-2100,1000])cube([3400,3900,1]); }
        for(n=["bench_upper","bench_lower","changing_chair","glass_frame","heater_cage","heater_mount"])select_part(n);
    }
}else if(view=="wall_detail"){
    for(i=[0:len(layer_names)-1])if(part==layer_names[i] || part=="detailed_all")
        translate([i*1400,0,0])layer_local(layer_names[i],1200);
}else{
    for(n=names)if(part==n || part=="detailed_all")
        translate([0,0,view=="exploded" ? explode_z(n) : 0])select_part(n);
}

