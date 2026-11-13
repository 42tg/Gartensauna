// Mechanical ventilation concept; mm. Clear apertures before grille blades.
// Supply above heater; exhaust below far end of upper bench; drying closed in use.
vent_supply_x = 1550;
vent_supply_z = 1080;
vent_supply_w = 150;
vent_supply_h = 80;
vent_exhaust_y = 500;
vent_exhaust_z = 220;
vent_exhaust_w = 300;
vent_exhaust_h = 160;
vent_drying_z = height - 220; // Preserve 60 mm from clear aperture top to ceiling
vent_border = 8;
vent_blade = 7;
vent_pitch = 20;
module ventilation_openings() {
    translate([vent_supply_x-2,-wing_extension-1,vent_supply_z-2])
        cube([vent_supply_w+4,wall+2,vent_supply_h+4]);
    for(z=[vent_exhaust_z,vent_drying_z])
        translate([main_width-wall-1,vent_exhaust_y-2,z-2])
            cube([wall+2,vent_exhaust_w+4,vent_exhaust_h+4]);
}
// Local x=width, y=wall depth, z=height. Sleeve seals wall cavity conceptually.
module vent_unit(w,h,closed=false) {
    difference(){
        translate([-2,0,-2])cube([w+4,wall,h+4]);
        translate([0,-1,0])cube([w,wall+2,h]);
    }
    for(y=[-4,wall]) {
        difference(){
            translate([-vent_border,y,-vent_border])cube([w+2*vent_border,4,h+2*vent_border]);
            translate([0,y-1,0])cube([w,6,h]);
        }
        for(z=[0:vent_pitch:h-vent_blade])translate([0,y,z])cube([w,4,vent_blade]);
    }
    if(closed)translate([0,wall/2,0])cube([w,2,h]);
}
module ventilation_part(name) {
    if(name=="vent_supply") translate([vent_supply_x,-wing_extension,vent_supply_z])
        vent_unit(vent_supply_w,vent_supply_h);
    if(name=="vent_exhaust" || name=="vent_drying")
        translate([main_width,vent_exhaust_y,name=="vent_drying"?vent_drying_z:vent_exhaust_z])
            rotate([0,0,90])vent_unit(vent_exhaust_w,vent_exhaust_h,name=="vent_drying");
}
