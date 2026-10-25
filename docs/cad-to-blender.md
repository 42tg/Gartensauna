# CAD → Blender

Die **CAD-Geometrie** ist die Quelle für Abmessungen. Blender dient nur der Visualisierung.

## Voraussetzungen
- OpenSCAD (CLI `openscad`)
- Python 3.10+
- Blender 4.1+ (`blender`)

## Erzeugen
```bash
python3 scripts/export_meshes.py
blender -b -P scripts/create_blender.py -- assembled
blender -b -P scripts/create_blender.py -- exploded
```

Ergebnisse: `build/meshes/` (STL je Bauteil), `build/blender/*.blend` und `*.png`.

**Wichtig:** Die STL-Dateien sind Triangulations-Exports und keine parametrischen CAD-Dateien. Die editierbare Quelle bleibt `cad/sauna-v3.scad`. Explosionsabstände stammen aus dem CAD-Parameter `view`.

## Grenzen
V3 ist eine schematische Raumstudie. Die Grundstücksausrichtung, Durchgänge, Dämmung, Glasanschlüsse, Dachneigung und alle bauphysikalischen Details sind noch nicht fertig konstruiert. Dieses Verfahren prüft keine Statik oder Baurecht. Vor der Verwendung als Bauunterlage sind Geometrie und Details zu überarbeiten.
