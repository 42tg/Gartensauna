// Planning geometry, NOT a specified door product or hinge installation detail.
// Door dimensions below distinguish rough opening, frame clearance and leaf.
door_clear_width=800;
door_clear_height=2000;
door_jamb=40;
door_rough_width=door_clear_width+2*door_jamb;
door_rough_height=door_clear_height+door_jamb;
door_leaf_width=door_clear_width-6;
entrance_door_x=300;
sauna_hinge=[wing_start_x-5,sauna_door_y+door_jamb+door_clear_width-3,0];
entrance_hinge=[entrance_door_x+door_jamb+3,-31,0];
door_angle=(view=="cutaway" || view=="plan") ? 90 : 0;
module sauna_leaf_pose(angle=door_angle){translate(sauna_hinge)rotate([0,0,-angle])children();}
module entrance_leaf_pose(angle=door_angle){translate(entrance_hinge)rotate([0,0,-angle])children();}
module sauna_frame(){
    for(y=[sauna_door_y,sauna_door_y+door_jamb+door_clear_width])
        translate([wing_start_x,y,0])cube([partition_t,door_jamb,door_rough_height]);
    translate([wing_start_x,sauna_door_y+door_jamb,door_clear_height])cube([partition_t,door_clear_width,door_jamb]);
}
module entrance_frame(){
    for(x=[entrance_door_x,entrance_door_x+door_jamb+door_clear_width])
        translate([x,0,0])cube([door_jamb,wall,door_rough_height]);
    translate([entrance_door_x+door_jamb,0,door_clear_height])cube([door_clear_width,wall,door_jamb]);
}
module door_part(n){
    if(n=="sauna_door_frame")sauna_frame();
    if(n=="entrance_door_frame")entrance_frame();
    if(n=="sauna_door_glass")sauna_leaf_pose()translate([-4,-door_leaf_width,20])cube([8,door_leaf_width,1977]);
    if(n=="entrance_door_leaf")entrance_leaf_pose()translate([0,-30,10])cube([door_leaf_width,60,1987]);
    // Paired wooden pull handles; no locking mechanism on sauna door.
    if(n=="sauna_door_handles")sauna_leaf_pose(){
        for(x=[-39,4]){
            for(z=[850,1050])translate([x,-door_leaf_width+65,z])cube([35,20,20]);
            translate([x<0?-39:24,-door_leaf_width+65,850])cube([15,20,220]);
        }
    }
    if(n=="entrance_door_handles")entrance_leaf_pose(){
        for(y=[-65,30])translate([door_leaf_width-100,y,950])cube([100,35,20]);
    }
    if(n=="door_hinges"){
        for(z=[350,1650]){
            translate([sauna_hinge[0],sauna_hinge[1],z])cylinder(r=5,h=80,$fn=16);
            translate([entrance_hinge[0],entrance_hinge[1],z])cylinder(r=7,h=80,$fn=16);
        }
    }
}
