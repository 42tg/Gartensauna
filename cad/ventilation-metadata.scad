// Evaluated by OpenSCAD: simulation consumes the same parameters as the CAD.
include <sauna-detailed.scad>
echo(["room", [main_width-wing_width+45,-wing_extension+wall,0], [main_width-wall,main_depth-wall,height], wing_start_x+partition_t]);
echo(["supply", [vent_supply_x,-wing_extension+wall,vent_supply_z], [vent_supply_w,0,vent_supply_h]]);
echo(["exhaust", [main_width-wall,vent_exhaust_y,vent_exhaust_z], [0,vent_exhaust_w,vent_exhaust_h]]);
echo(["drying", [main_width-wall,vent_exhaust_y,vent_drying_z], [0,vent_exhaust_w,vent_exhaust_h]]);
echo(["upper", [bench_upper_x,bench_start_y,bench_upper_z-50], [bench_depth,bench_length,78]]);
echo(["lower", [bench_lower_x,bench_start_y,bench_lower_z-50], [bench_depth,bench_length,78]]);
echo(["heater", [heater_x-heater_width/2,heater_back_y,heater_bottom], [heater_width,heater_depth,heater_height]]);
echo(["grille", vent_blade, vent_pitch]);
