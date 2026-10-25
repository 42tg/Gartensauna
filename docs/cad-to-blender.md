# CAD → Blender

Die **CAD-Geometrie** ist die Quelle für Abmessungen. Blender dient nur der Visualisierung.

## Voraussetzungen
- OpenSCAD (CLI `openscad`)
- Python 3.10+
- Blender 4.0+ (`blender`)

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

## GitHub Actions
Der Workflow `Render CAD to Blender` läuft bei Änderungen an CAD, Skripten oder Workflow auf `main` sowie manuell. Im Run steht das Artefakt `gartensauna-cad-blender` zum Download bereit:
- `blender/gartensauna_assembled.blend` und `.png`
- `blender/gartensauna_exploded.blend` und `.png`
- JSON-Berichte mit Bauteilmaßen in Metern und Herkunft der Meshes
- `meshes/`: 16 STL-Dateien und Manifest

Alle acht Bauteile werden aus OpenSCAD importiert; Blender skaliert Millimeter mit Faktor 0,001 zu Metern. Die Kamera passt den Ausschnitt an alle Bauteile an, ohne ihre Geometrie zu verändern. CPU-Rendering ohne Denoising unterstützt das Ubuntu-Blender-Paket. Fehlende Meshes und unvollständige Ausgaben lassen den Workflow fehlschlagen.

Das Dach verwendet denselben XY-Grundriss wie die Wände, mit 80 mm Überstand; nur in der Explosionsansicht wird es in Z angehoben. Die Modellannahme `wing_extension = 2000` bedeutet weiterhin **2 m zusätzlichen Vorsprung** und damit 3,70 m Gesamttiefe; diese Interpretation ist noch zu bestätigen.
