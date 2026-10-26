// HUUM DROP-inspired visual proxy, NOT manufacturer's construction geometry.
// Published outer dimensions W/D/H: 390/335/590 mm.
// https://huum.eu/product/drop-electric-sauna-heater/ (2026-10-25)
heater_width = 390;
heater_depth = 335;
heater_height = 590;
heater_bottom = 310; // provisional mounting height, not installation approval
heater_x = 1700;
heater_back_y = -wing_extension+wall; // interior of end wall beside garden glazing
heater_rotation = 180; // face into the sauna, bracket against the end wall
heater_wire = 6;
// Smooth, open-topped basket, narrow foot and rounded shoulder.
heater_profile = [[0,0.20],[0.08,0.48],[0.20,0.73],[0.35,0.92],
                  [0.50,1],[0.65,0.98],[0.80,0.89],[1,0.72]];
function drop_radius(t, i=0) = i >= len(heater_profile)-2 ?
    heater_profile[i][1]+(heater_profile[i+1][1]-heater_profile[i][1])*
    (t-heater_profile[i][0])/(heater_profile[i+1][0]-heater_profile[i][0]) :
    t <= heater_profile[i+1][0] ?
    heater_profile[i][1]+(heater_profile[i+1][1]-heater_profile[i][1])*
    (t-heater_profile[i][0])/(heater_profile[i+1][0]-heater_profile[i][0]) : drop_radius(t,i+1);
function drop_point(t,a) = [(heater_width/2-heater_wire/2)*drop_radius(t)*cos(a),
    (heater_depth/2-heater_wire/2)*drop_radius(t)*sin(a),
    heater_wire/2+t*(heater_height-heater_wire)];
module heater_placement(){
    translate([heater_x,heater_back_y,heater_bottom])
        rotate([0,0,heater_rotation])
            translate([0,-heater_depth/2,0]) children();
}
module drop_ring(t){
    p=drop_point(t,0);
    translate([0,0,p[2]]) scale([1,(heater_depth-heater_wire)/(heater_width-heater_wire),1])
        rotate_extrude($fn=64) translate([p[0],0,0]) circle(d=heater_wire,$fn=8);
}
module drop_cage(){
    for(i=[0:14])drop_ring(i/14);
    for(a=[0:45:359])for(i=[0:13])hull(){
        translate(drop_point(i/14,a))sphere(d=heater_wire,$fn=8);
        translate(drop_point((i+1)/14,a))sphere(d=heater_wire,$fn=8);
    }
}
module drop_mount(){
    // Simplified bracket within the product envelope; not a drilling template.
    for(x=[-70,70])translate([x-12,130,190])cube([24,37.5,250]);
}
module drop_stones(){
    // Deterministic individual rounded stones, all inside the basket envelope.
    for(k=[0:8])let(t=(k+0.5)/9, r=drop_radius(t),
        rx=(heater_width/2-12)*r, ry=(heater_depth/2-12)*r)
        for(ix=[-3:3])for(iy=[-2:2])let(
            x=ix*53+(k%2)*20, y=iy*53,
            seed=1000+k*100+(ix+3)*10+iy+2,
            s=rands(0.88,1.08,3,seed))
            if(pow((abs(x)+27)/rx,2)+pow((abs(y)+27)/ry,2)<1)
                translate([x,y,30+k*62])rotate([13*ix,17*iy,seed%180])
                    scale([25*s[0],24*s[1],27*s[2]])sphere(r=1,$fn=12);
}
module heater_part(name){heater_placement(){
    if(name=="heater_cage")drop_cage();
    if(name=="heater_mount")drop_mount();
    if(name=="heater_stones")drop_stones();
}}

