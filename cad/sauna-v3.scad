// Gartensauna V3 – parametrisches geometrisches Konzept, Einheiten mm.
// Export: openscad -o wall.stl -D 'part="walls"' -D 'view="assembled"' sauna-v3.scad
// Wichtig: KEINE geprüfte Baukonstruktion. Öffnungen und Materialien sind Platzhalter.
main_width = 3200;
main_depth = 1700;
wing_width = 2000;       // Annahme, zu bestätigen
wing_extension = 2000;   // Nutzerangabe als zusätzlicher Schenkel interpretiert
include <envelope.scad>
clear_internal_height = 2200; // Decision 0012: finished floor to finished ceiling, mm
height = clear_internal_height; // Shared wall/glazing/ceiling datum; NOT exterior height
floor_thickness = 120;
// roof_thickness from envelope.scad; roof top = height + roof_thickness.
// Floor underside = -floor_thickness; terrain/foundation datum still unconfirmed.
assert(height > 2050, "Ceiling must clear the 2050 mm door openings");
include <bench-layout.scad>
include <ventilation.scad>
// Fail before expensive exports if envelope changes consume usable space.
assert(bench_lower_x-(main_width-wing_width+45)>=500, "Window aisle below 500 mm planning minimum");
assert(main_depth-wall-(bench_start_y+bench_length)>=600, "Rear landing below 600 mm");
assert(bench_upper_x-(bench_lower_x+bench_depth)>=bench_gap, "Lying surfaces overlap");
assert(wall+20+850<=main_width-wing_width-wall/2, "Entrance intersects partition");
part = "all";            // ["all","foundation","floor","walls","roof","upper_bench","lower_bench","chair","glazing"]
view = "assembled";      // ["assembled","exploded"]
offset = view == "exploded" ? 420 : 0;
// Grundriss: x von 0..3200, y von -2000..1700.
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
        footprint_3d(height);
        ventilation_openings();
        // inset voids: room on left, and right L wing, with open connection
        translate([wall,wall,-1]) cube([main_width-wing_width-wall*1.5,main_depth-2*wall,height+2]);
        translate([main_width-wing_width+wall,-wing_extension+wall,-1])
            cube([wing_width-2*wall,wing_extension+main_depth-2*wall,height+2]);
        // passage from dressing room into sauna wing
        translate([main_width-wing_width-wall-5,sauna_door_y,0]) cube([wall*2+10,sauna_door_width,2050]);
        // outside entrance on left front (y=0)
        translate([wall+20,-10,0]) cube([850,wall+20,2050]);
        // Full garden-facing front: floor to roof underside, entire projecting wing
        translate([main_width-wing_width-1,-wing_extension-1,-1])
            cube([wall+2,wing_extension+1,height+2]);
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

