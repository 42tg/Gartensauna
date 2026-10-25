// Gartensauna Konzept V2 – alle Maße in mm
// Visualisierungsmodell, keine Bau- oder Statikfreigabe.
// In OpenSCAD öffnen, F5 Vorschau, F6 Rendern. Ansicht umschalten.
variant = "planung"; // ["bestand","planung"]
view = "assembled"; // ["assembled","exploded","structure"]
W = 3200;
D = variant == "bestand" ? 1700 : 2000;
H_front = 2300; // Annahme
H_back = 2200;  // Annahme
wall = 145;     // Beispielgesamtwandstärke, NICHT festgelegt
floor_h = 120;  // Platzhalter
roof_h = 160;   // Platzhalter
explode = view == "exploded" ? 430 : 0;
show_cladding = view != "structure";
$fn = 24;
module panel(pos, size, rgb, a=1) { color(rgb,a) translate(pos) cube(size); }
module shell(){
    // Boden / Tragplatte (Platzhalter)
    panel([0,0,-floor_h-explode],[W,D,floor_h],[0.48,0.48,0.48]);
    // Ständer und Wandkörper (schematisch, ohne konstruktive Freigabe)
    if(show_cladding) {
      panel([0,0,0],[wall,D,H_front],[0.69,0.49,0.28],0.65);
      panel([W-wall,0,0],[wall,D,H_front],[0.69,0.49,0.28],0.65);
      panel([wall,D-wall,0],[W-2*wall,wall,H_back],[0.69,0.49,0.28],0.65);
      // Front geteilt, Türöffnung mittig rechts
      panel([wall,0,0],[W*0.53-wall,wall,H_front],[0.69,0.49,0.28],0.65);
      panel([W*0.53+850,0,0],[W-(W*0.53+850)-wall,wall,H_front],[0.69,0.49,0.28],0.65);
      panel([W*0.53,0,2050],[850,wall,H_front-2050],[0.69,0.49,0.28],0.65);
    }
    // Ständer schematisch
    for(x=[80,W-160]) for(y=[80,D-160])
      panel([x,y,0],[80,80,H_back],[0.56,0.31,0.13]);
    // Dach als Pultdach-Scheibe, Neigung nur schematisch
    translate([0,-80,H_front+explode])
      rotate([atan((H_back-H_front)/D),0,0])
      panel([-90,0,0],[W+180,D+160,roof_h],[0.27,0.31,0.34],0.85);
}
module interior(){
    // Bänke an Rückwand – Positionen nur zur Veranschaulichung
    panel([wall+70,D-wall-680,900],[W-2*wall-140,600,55],[0.86,0.66,0.39]);
    panel([wall+70,D-wall-420,450],[W-2*wall-140,340,55],[0.79,0.58,0.32]);
    // Ofenplatzhalter links vorne
    panel([wall+120,wall+150,0],[380,420,700],[0.33,0.36,0.39]);
}
shell();
if(view != "structure") interior();
