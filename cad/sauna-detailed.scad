// Detailed concept geometry. Millimetres; all construction dimensions are assumptions.
// The V3 room layout and openings remain the authoritative footprint.
include <sauna-v3.scad>
include <heater-drop.scad>
part = "detailed_all";
// Shared envelope totals 205 mm. Membrane dimensions are planning allowances.
d_vent=cladding_t;
d_sheath=d_vent+vent_t;
d_wind=d_sheath+sheathing_t;
d_stud=d_wind+wind_t;
d_vapour=d_stud+stud_t;
d_service=d_vapour+vapour_t;
d_lining=d_service+service_t;
z_vapour=height+ceiling_t+ceiling_gap;
z_insulation=z_vapour+vapour_t;
z_wind=z_insulation+roof_insulation_t;
z_vent=z_wind+wind_t;
z_deck=z_vent+roof_vent_t;
z_cover=z_deck+roof_deck_t;
faces = [[wing_start_x,-wing_extension,wing_width,0],
         [main_width,-wing_extension,main_depth+wing_extension,90],
         [main_width,main_depth,main_width,180],[0,main_depth,main_depth,270],
         [0,0,wing_start_x,0]];
layer_names = ["wall_cladding","wall_battens","wall_sheathing","wind_barrier","wall_studs",
               "wall_insulation","vapour_barrier","service_battens","interior_boards"];
module face(f) { translate([f[0],f[1],0]) rotate([0,0,f[3]]) children(); }
module strips(length,d,t,width=120,gap=3) {
    // Horizontal boards on vertical battens keep vertical air paths continuous.
    for(z=[0:width:height-0.1]) translate([0,d,z])
        cube([length,t,min(width-gap,height-z)]);
}
module panel_frame(length,d,t) {
    for(u=[0:600:length-45]) translate([u,d,45]) cube([45,t,height-90]);
    translate([length-45,d,45])cube([45,t,height-90]);
    for(z=[0,height-45])translate([0,d,z])cube([length,t,45]);
}
module layer_local(name,length) {
    if(name=="wall_cladding") strips(length,0,cladding_t);
    if(name=="wall_battens")
        for(u=[0:600:length-45])translate([u,d_vent,0])cube([45,vent_t,height]);
    if(name=="wall_sheathing")translate([0,d_sheath,0])cube([length,sheathing_t,height]);
    if(name=="wind_barrier")translate([0,d_wind,0])cube([length,wind_t,height]);
    if(name=="wall_studs")panel_frame(length,d_stud,stud_t);
    if(name=="wall_insulation")difference(){
        translate([0,d_stud,0])cube([length,stud_t,height]);
        panel_frame(length,d_stud-1,stud_t+2);
    }
    if(name=="vapour_barrier")translate([0,d_vapour,0])cube([length,vapour_t,height]);
    if(name=="service_battens")
        for(u=[0:600:length-40])translate([u,d_service,0])cube([40,service_t,height]);
    if(name=="interior_boards")strips(length,d_lining,lining_t,95,1.5);
}
module wall_layer(name) {
    intersection(){walls(); union(){for(f=faces)face(f)layer_local(name,f[2]);}}
}
module perimeter_mask(){
    linear_extrude(height=height)difference(){footprint();offset(delta=-wall)footprint();}
}
module partition_mask(){intersection(){walls();translate([wing_start_x,0,0])cube([partition_t,main_depth-wall,height]);}}
module partition_studs(){
    x=wing_start_x+partition_lining;
    for(y=[0,sauna_door_y-45,sauna_door_y+door_rough_width])translate([x,y,0])cube([partition_stud,45,height]);
    for(z=[0,height-45,door_rough_height])translate([x,0,z])cube([partition_stud,main_depth-wall,45]);
}
module partition_frame(){intersection(){partition_mask();partition_studs();}}
module partition_boards(){
    intersection(){partition_mask();union(){
        for(x=[wing_start_x,wing_start_x+partition_t-partition_lining])for(y=[0:95:main_depth])
            translate([x,y,0])cube([partition_lining,93.5,height]);
    }}
}
module partition_layer(n){
    intersection(){partition_mask();
        if(n=="partition_insulation")difference(){
            translate([wing_start_x+partition_lining,0,0])cube([partition_stud,main_depth,height]);partition_studs();
        }else if(n=="partition_vapour")translate([wing_start_x+partition_lining+partition_stud,0,0])cube([vapour_t,main_depth,height]);
        else if(n=="partition_battens")union(){for(y=[0:400:main_depth])
            translate([wing_start_x+partition_lining+partition_stud+vapour_t,y,0])cube([partition_gap,40,height]);}
    }
}
module floor_joists(){intersection(){
    translate([0,0,-108])footprint_3d(88);
    union(){for(x=[0:400:main_width])translate([x,-wing_extension,-108])cube([45,main_depth+wing_extension,88]);}
}}
module floor_insulation(){difference(){
    translate([0,0,-108])footprint_3d(88);floor_joists();
}}
module floor_boards(){intersection(){
    translate([0,0,-20])footprint_3d(20);
    union(){for(x=[0:120:main_width])translate([x,-wing_extension,-20])cube([118,main_depth+wing_extension,20]);}
}}
module roof_mask(z,t){translate([0,0,z])linear_extrude(height=t)offset(r=80)footprint();}
module roof_joists(){intersection(){roof_mask(z_insulation,roof_insulation_t);union(){
    for(x=[-80:600:main_width+80])translate([x,-wing_extension-80,z_insulation])cube([60,main_depth+wing_extension+160,roof_insulation_t]);
}}}
module roof_insulation(){difference(){roof_mask(z_insulation,roof_insulation_t);roof_joists();}}
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
    for(y=[-wing_extension,-35])translate([wing_start_x,y,0])cube([45,35,height]);
    for(z=[0,height-35])translate([wing_start_x,-wing_extension,z])cube([45,wing_extension,35]);
}
module select_part(name){
    heater_part(name);
    door_part(name);
    if(name=="partition_insulation" || name=="partition_vapour" || name=="partition_battens")partition_layer(name);
    ventilation_part(name);
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
    if(name=="ceiling_boards")roof_boards(height,ceiling_t,95);
    if(name=="ceiling_battens")intersection(){roof_mask(height+ceiling_t,ceiling_gap); union(){
        for(x=[-80:600:main_width+80])translate([x,-wing_extension-80,height+ceiling_t])cube([45,main_depth+wing_extension+160,ceiling_gap]);}}
    if(name=="ceiling_vapour")roof_mask(z_vapour,vapour_t);
    if(name=="roof_wind")roof_mask(z_wind,wind_t);
    if(name=="roof_vent_battens")intersection(){roof_mask(z_vent,roof_vent_t); union(){
        for(x=[-80:600:main_width+80])translate([x,-wing_extension-80,z_vent])cube([60,main_depth+wing_extension+160,roof_vent_t]);}}
    if(name=="roof_joists")roof_joists();
    if(name=="roof_insulation")roof_insulation();
    if(name=="roof_deck")roof_boards(z_deck,roof_deck_t,140);
    if(name=="roof_covering")roof_mask(z_cover,roof_cover_t);
    if(name=="roof_fascia")difference(){roof_mask(height,roof_thickness-roof_cover_t);translate([0,0,height-1])
        linear_extrude(height=roof_thickness+2)offset(r=60)footprint();}
    if(name=="bench_upper")bench_slats(bench_upper_x,bench_start_y,bench_upper_z,bench_depth,bench_length);
    if(name=="bench_lower")bench_slats(bench_lower_x,bench_start_y,bench_lower_z,bench_depth,bench_length);
    if(name=="changing_chair")chair();
    if(name=="glass_front")translate([wing_start_x+7,-wing_extension+35,35])cube([24,wing_extension-70,height-70]);
    if(name=="glass_frame")window_frame();
}
names = ["concrete_piers","floor_underside","floor_joists","floor_insulation","floor_boards",
         "wall_cladding","wall_battens","wall_sheathing","wind_barrier","wall_studs","wall_insulation",
         "vapour_barrier","service_battens","interior_boards","partition_frame","partition_boards",
         "ceiling_boards","ceiling_battens","ceiling_vapour","roof_wind","roof_vent_battens","roof_joists","roof_insulation","roof_deck","roof_covering","roof_fascia",
         "bench_upper","bench_lower","changing_chair","glass_front","glass_frame",
         "heater_cage","heater_mount","heater_stones","vent_supply","vent_exhaust","vent_drying","partition_insulation","partition_vapour","partition_battens","sauna_door_frame","sauna_door_glass","sauna_door_handles","entrance_door_frame","entrance_door_leaf","entrance_door_handles","door_hinges"];
function explode_z(n) = n=="concrete_piers" ? -800 : n=="floor_underside" ? -600 :
    n=="floor_joists" || n=="floor_insulation" ? -350 : n=="floor_boards" ? -120 :
    n=="ceiling_boards" ? 800 : n=="ceiling_battens" || n=="ceiling_vapour" ? 1000 : n=="roof_wind" || n=="roof_vent_battens" ? 1450 : n=="roof_joists" || n=="roof_insulation" ? 1200 :
    n=="roof_deck" ? 1700 : n=="roof_covering" ? 2050 : n=="roof_fascia" ? 1500 : 0;
if(part=="audit_walls") {
    projection(cut=true)translate([0,0,-1000])union(){walls();sauna_frame();entrance_frame();}
}else if(part=="plan") {
    projection(cut=false) union(){
        // Horizontal wall section through openings; omit door lintels in plan.
        intersection(){ walls(); translate([-100,-wing_extension-100,1000])cube([main_width+200,main_depth+wing_extension+200,1]); }
        for(n=["bench_upper","bench_lower","changing_chair","glass_frame","heater_cage","heater_mount","sauna_door_glass","sauna_door_handles","entrance_door_leaf","entrance_door_handles"])select_part(n);
        // Section frames at 1 m; their heads must not fill the plan opening.
        intersection(){union(){sauna_frame();entrance_frame();}translate([-100,-2100,1000])cube([main_width+200,4000,1]);}
    }
}else if(view=="wall_detail"){
    for(i=[0:len(layer_names)-1])if(part==layer_names[i] || part=="detailed_all")
        translate([i*1400,0,0])layer_local(layer_names[i],1200);
}else{
    for(n=names)if(part==n || part=="detailed_all")
        translate([0,0,view=="exploded" ? explode_z(n) : 0])select_part(n);
}


