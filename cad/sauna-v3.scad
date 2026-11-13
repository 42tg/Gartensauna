// Gartensauna V3 – parametrisches geometrisches Konzept, Einheiten mm.
// Export: openscad -o wall.stl -D 'part="walls"' -D 'view="assembled"' sauna-v3.scad
// Wichtig: KEINE geprüfte Baukonstruktion. Öffnungen und Materialien sind Platzhalter.
// Overall width is derived from the requested CLEAR changing-room width.
// Provisional new-build footprint, pending on-site measurement (ADR 0013).
main_depth = 1700;
wing_width = 2000;       // Annahme, zu bestätigen
wing_extension = 2000;   // Nutzerangabe als zusätzlicher Schenkel interpretiert
include <envelope.scad>
changing_clear_width = 1400;
partition_lining = 19;
partition_stud = 70;
partition_gap = 20;
partition_t = 2*partition_lining + partition_stud + vapour_t + partition_gap;
main_width = wing_width + changing_clear_width + wall; // 3605 mm; ADR 0014
wing_start_x = main_width-wing_width;
clear_internal_height = 2200; // Decision 0012: finished floor to finished ceiling, mm
height = clear_internal_height; // Shared wall/glazing/ceiling datum; NOT exterior height
floor_thickness = 120;
// roof_thickness from envelope.scad; roof top = height + roof_thickness.
// Floor underside = -floor_thickness; terrain/foundation datum still unconfirmed.
assert(abs((main_width-wing_width-wall)-changing_clear_width)<0.01, "Changing-room clear width mismatch");
assert(height > 2050, "Ceiling must clear the 2050 mm door openings");
include <bench-layout.scad>
view = "assembled";
include <doors.scad>
include <ventilation.scad>
// Fail before expensive exports if envelope changes consume usable space.
assert(bench_lower_x-(main_width-wing_width+45)>=500, "Window aisle below 500 mm planning minimum");
assert(main_depth-wall-(bench_start_y+bench_length)>=600, "Rear landing below 600 mm");
assert(bench_upper_x-(bench_lower_x+bench_depth)>=bench_gap, "Lying surfaces overlap");
assert(wall+20+850<=main_width-wing_width-wall/2, "Entrance intersects partition");
part = "all";            // ["all","foundation","floor","walls","roof","upper_bench","lower_bench","chair","glazing"]
// view set before door parameters; command-line -D overrides it.
offset = view == "exploded" ? 420 : 0;
// Grundriss: x von 0..main_width, y von -wing_extension..main_depth.
// Umkleide links im Bestandsrechteck; Saunaflügel rechts.
module footprint(){
    union(){
        square([main_width, main_depth]);
        translate([main_width-wing_width,-wing_extension]) square([wing_width,wing_extension]);
    }
}
module footprint_3d(h){
    linear_extrude(height=h) footprint();
}
module foundation(){
    translate([0,0,-300-offset*2]) footprint_3d(180);
}
module floor(){
    translate([0,0,-floor_thickness-offset]) footprint_3d(floor_thickness);
}
module walls(){
    difference(){
        union(){
            cube([wall,main_depth,height]);
            translate([0,main_depth-wall,0])cube([main_width,wall,height]);
            translate([main_width-wall,-wing_extension,0])cube([wall,main_depth+wing_extension,height]);
            cube([wing_start_x,wall,height]);
            // Front wall meets the glazing frame: no 160 mm open corner.
            translate([wing_start_x+45,-wing_extension,0])cube([wing_width-45,wall,height]);
            translate([wing_start_x,0,0])cube([partition_t,main_depth-wall,height]);
        }
        ventilation_openings();
        translate([wing_start_x-1,sauna_door_y,-1])cube([partition_t+2,door_rough_width,door_rough_height+1]);
        translate([entrance_door_x,-1,-1])cube([door_rough_width,wall+2,door_rough_height+1]);
    }
}
module roof(){
    translate([0,0,height+offset])
        linear_extrude(height=roof_thickness)
        offset(r=80) footprint();
}
module upper_bench(){
    translate([bench_upper_x,bench_start_y,bench_upper_z-27])
        cube([bench_depth,bench_length,55]);
}
module lower_bench(){
    translate([bench_lower_x,bench_start_y,bench_lower_z-27])
        cube([bench_depth,bench_length,55]);
}
module chair(){
    // Only illustrative chair: seat + backrest + legs
    translate([250,main_depth-720,0])
    union(){
        translate([0,0,440])cube([470,470,40]);
        translate([0,430,440])cube([470,40,480]);
        for(x=[20,410]) for(y=[20,410]) translate([x,y,0])cube([40,40,440]);
    }
}
module glazing(){
    // Full-height/full-width glazing; 40 mm assembly placeholder, not glass specification
    translate([main_width-wing_width,-wing_extension,0])
        cube([40,wing_extension,height]);
}
if(part=="all" || part=="foundation") color("gray") foundation();
if(part=="all" || part=="floor") color("burlywood") floor();
if(part=="all" || part=="walls") color("tan",0.65) walls();
if(part=="all" || part=="roof") color("dimgray") roof();
if(part=="all" || part=="upper_bench") color("wheat") upper_bench();
if(part=="all" || part=="lower_bench") color("peru") lower_bench();
if(part=="all" || part=="chair") color("saddlebrown") chair();
if(part=="all" || part=="glazing") color("lightblue",0.5) glazing();

