// Planning allowances, mm. Not a structural/moisture approval.
cladding_t=20;
vent_t=30;
sheathing_t=15;
wind_t=0.9; // visual allowance; product not selected
stud_t=100;
vapour_t=0.1;
service_t=20;
lining_t=19;
wall=cladding_t+vent_t+sheathing_t+wind_t+stud_t+vapour_t+service_t+lining_t;
ceiling_t=15;
ceiling_gap=20;
roof_insulation_t=160;
roof_vent_t=60; // reserved ventilation zone, inlet/outlet design pending
roof_deck_t=22;
roof_cover_t=3;
roof_thickness=ceiling_t+ceiling_gap+vapour_t+roof_insulation_t+wind_t+roof_vent_t+roof_deck_t+roof_cover_t;
