#!/usr/bin/env python3
"""Export each named OpenSCAD part as an STL, using a single CAD source.
Requires: openscad. Run from repository root: python3 scripts/export_meshes.py
"""
from pathlib import Path
import subprocess
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "cad" / "sauna-v3.scad"
DEST = ROOT / "build" / "meshes"
PARTS = ["foundation", "floor", "walls", "roof", "upper_bench", "lower_bench", "chair", "glazing"]
VARIANTS = ["assembled", "exploded"]

def main():
    if not SOURCE.is_file():
        raise SystemExit(f"Missing source: {SOURCE}")
    DEST.mkdir(parents=True, exist_ok=True)
    manifest = {"source": str(SOURCE.relative_to(ROOT)), "units": "mm", "variants": {}}
    for view in VARIANTS:
        manifest["variants"][view] = {}
        for part in PARTS:
            target = DEST / f"{view}_{part}.stl"
            command = ["openscad", "-o", str(target), "-D", f'part="{part}"',
                       "-D", f'view="{view}"', str(SOURCE)]
            subprocess.run(command, check=True)
            manifest["variants"][view][part] = str(target.relative_to(ROOT))
    (DEST / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("Wrote", DEST / "manifest.json")

if __name__ == "__main__":
    main()
