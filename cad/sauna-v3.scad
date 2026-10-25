// V3 L-Form Konzept, Millimeter. Geometrie vorläufig, nicht baufreigegeben.
main_width=3200; main_depth=1700; wing_width=2000; wing_extension=2000;
wall=180; height=2400; floor_thickness=100; roof_thickness=160;
view="assembled"; // ["assembled","exploded"]
explode=view=="exploded"?450:0;
module block(x,y,z,w,d,h,c){color(c)translate([x,y,z])cube([w,d,h]);}
module outline(x,y,w,d){difference(){cube([w,d,height]);translate([wall,wall,-1])cube([w-2*wall,d-2*wall,height+2]);}}
color([.68,.49,.31,.65]) union(){
 // Umkleide links: Grundrechteck bis zur inneren Trennwand
 difference(){cube([main_width,main_depth,height]);translate([wall,wall,-1])cube([main_width-2*wall,main_depth-2*wall,height+2]);}
 // Flügel ragt um 2 m nach vorne (negative y-Richtung)
 translate([main_width-wing_width,-wing_extension,0]) difference(){
 cube([wing_width,wing_extension,height]);
 translate([wall,-1,-1])cube([wing_width-2*wall,wing_extension+2,height+2]);
 }
}
block(0,-wing_extension,-floor_thickness-explode,main_width,main_depth+wing_extension,floor_thickness,[.48,.49,.50]);
block(-100,-wing_extension-100,height+explode,main_width+200,main_depth+wing_extension+200,roof_thickness,[.26,.30,.33]);
// Benches in sauna wing, along extension, illustrative only
block(main_width-650,-wing_extension+180,850,470,1850,55,[.82,.62,.39]);
block(main_width-1050,-wing_extension+180,450,380,1850,55,[.73,.53,.31]);
