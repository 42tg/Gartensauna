# Gartensauna Werkbank

Interaktiver Viewer für den aktuellen CAD-Entwurf: bemaßte SVG-Zeichnungen,
GLB aus den Blender-Szenen, stufenlose Explosion, Cutaway, Bauteil-Hüllmaße,
Zwei-Punkt-Abstand und Punktwolke mit einblendbarem Entwurf.

## Reproduzieren

Im Repository-Root, nach dem vorhandenen CAD-/Blender-Renderlauf:

```sh
blender -b --python-exit-code 1 -P scripts/export_web.py -- build/blender web/assets
python3 scripts/web_drawings.py
cd web
npm ci
npm test
npm run build
python3 -m http.server 8000 --directory dist
```

Optional den absoluten Pfad zu `Saunaecke_Punktwolke.blend` als drittes Argument
an `export_web.py` übergeben. Die Kalibrierung dieser externen Datei bleibt
unverändert. Alle 974.627 enthaltenen Punkte und ihre Farben werden übernommen.
Scan und erzeugte Assets werden **nicht in das öffentliche GitHub-Repository**
committed. Die private Site enthält den ausgewählten Scan; die Build-Ausgabe
aus GitHub enthält nur CAD und kann lokale PLY-Dateien öffnen.

`web/assets/`, `web/dist/` und `node_modules/` sind ignoriert. Ein neuer CAD-Lauf
erzeugt ein `gartensauna-web`-Artefakt. Die private Site wird getrennt aktualisiert;
ein GitHub-Push veröffentlicht nicht automatisch den Umgebungsscan.

## Bedienung und Grenzen

- Zeichnungen: verschieben/zoomen, Drauf-/Vorder-/Seitenansicht, SVG-Download.
- Modell: Drehen, Zoomen, Blickrichtungen, Explosion 0–100 %, Innenansicht,
  Dach ausblenden, Drahtgitter und Bauteilwahl.
- Messen: zwei Oberflächenpunkte antippen. Messwerte in mm. Kein Kantensnapping;
  angezeigt wird die Distanz der angeklickten Punkte. Bei Explosion zählt die
  verschobene Darstellung, nicht der Zusammenbau.
- Umgebung: Scan/Modell/Bestandsrahmen getrennt schalten, Punktgröße/Deckkraft,
  temporäre XYZ-Verschiebung und Z-Drehung, lokaler PLY-Import bis 200 MB.
- PLY muss bereits im metrischen Z-up-System vorliegen. Kein automatisches
  Registrieren, Umkalibrieren oder Speichern lokaler Dateien.
- GLB erhält CAD-Geometrie und ausgewertete Cutaway-Modifikatoren; prozedurale
  Blender-Materialien werden auf portable Grundfarben reduziert.
- WebGL ist bevorzugt. Ohne WebGL läuft eine langsamere Canvas-CPU-Darstellung
  mit Tiefenpuffer, vereinfachter Beleuchtung und höchstens etwa 100.000 sichtbaren
  Scanpunkten. Die geladenen Daten und Messpunkte bleiben unverändert.
- Transparenz im CPU-Modus ist eine Annäherung, kein verlässlicher Sichtbarkeitstest.
- Scan: vorläufig auf 3,20 m Bestandsbreite kalibriert, kein vermessenes Gelände.
  Grundrissbreite 3.605 mm und lichte Höhe 2.200 mm betreffen den Neubau.

## Verifikation am 14.11.2026

Geometrie unverändert gegenüber Renderlauf 43502154437 / Commit 7143537.
GLB-Bauteilgrenzen werden gegen die Blender-Prüfberichte kontrolliert.
Vier Unit-Tests prüfen Messumrechnung, Explosion, Scanvalidierung und Dachgruppen.
Browser-QA: SVG-Umschaltung, GLB-Laden, Explosion, Cutaway, Umgebungsschalter und
Messfunktion. Die Testumgebung bietet kein WebGL; GPU-Ausgabe hier nicht visuell
geprüft. CPU-Fallback wird im Browser sichtbar gekennzeichnet.
