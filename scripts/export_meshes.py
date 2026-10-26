#!/usr/bin/env python3
"""Export each named OpenSCAD part as an STL, using a single CAD source.
Requires: openscad. Run from repository root: python3 scripts/export_meshes.py
"""
from pathlib import Path
import subprocess
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "cad" / "sauna-detailed.scad"
DEST = ROOT / "build" / "meshes"
PARTS = ["concrete_piers", "floor_underside", "floor_joists", "floor_insulation", "floor_boards",
         "wall_cladding", "wall_battens", "wall_sheathing", "wind_barrier", "wall_studs", "wall_insulation",
         "vapour_barrier", "service_battens", "interior_boards", "partition_frame", "partition_boards",
         "ceiling_boards", "ceiling_battens", "ceiling_vapour", "roof_wind", "roof_vent_battens", "roof_joists", "roof_insulation", "roof_deck", "roof_covering", "roof_fascia",
         "bench_upper", "bench_lower", "changing_chair", "glass_front", "glass_frame",
         "heater_cage", "heater_mount", "heater_stones"]
WALL_PARTS = PARTS[5:14]
VARIANTS = ["assembled", "exploded", "wall_detail"]

def main():
    if not SOURCE.is_file():
        raise SystemExit(f"Missing source: {SOURCE}")
    DEST.mkdir(parents=True, exist_ok=True)
    manifest = {"source": str(SOURCE.relative_to(ROOT)), "units": "mm", "variants": {}}
    for view in VARIANTS:
        manifest["variants"][view] = {}
        for part in (WALL_PARTS if view == "wall_detail" else PARTS):
            target = DEST / f"{view}_{part}.stl"
            command = ["openscad", "-o", str(target), "-D", f'part="{part}"',
                       "-D", f'view="{view}"', str(SOURCE)]
            subprocess.run(command, check=True)
            manifest["variants"][view][part] = str(target.relative_to(ROOT))
    (DEST / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("Wrote", DEST / "manifest.json")

if __name__ == "__main__":
    main()


