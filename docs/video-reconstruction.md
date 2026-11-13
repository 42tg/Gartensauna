# Videorekonstruktion und Punktwolken-Ausrichtung

Die Werkzeuge in diesem Repository enthalten keine Videoaufnahmen, Bildmarkierungen,
Punktwolken oder projektspezifischen Kalibrierungsmatrizen. Eingaben und Ausgaben
werden lokal als separate Dateien verarbeitet. Die vorhandene Sauna-CAD-Geometrie
wird dadurch nicht verändert.

## Dünne Rekonstruktion als Einstieg

Voraussetzungen: FFmpeg, Python, `pycolmap==4.2.1`; für die Vorschau zusätzlich
NumPy und Matplotlib. Das Ausgabeverzeichnis darf noch nicht existieren.

```sh
python scripts/reconstruct_video.py /pfad/video.mp4 --output /tmp/scan
python scripts/preview_reconstruction.py /tmp/scan/sparse/0 /tmp/vorschau.png
```

Der einfache Einstieg extrahiert zwei Bilder pro Sekunde mit 720 Pixeln Breite
und verwendet SIFT, sequenzielles Matching und inkrementelles Structure-from-Motion
auf der CPU. Eine gemeinsame SIMPLE_RADIAL-Kamera ist eine Modellannahme;
digitale Stabilisierung und Rolling Shutter werden nicht explizit modelliert.
Mehrere entstandene Teilmodelle sind nicht automatisch miteinander ausgerichtet.

Die Vorschau zeigt Punkte mit mindestens drei Beobachtungen und weniger als
zwei Pixeln Reprojektionsfehler. Die äußeren 1-%-Quantile je Achse werden nur in
der Vorschau ausgeblendet. Mit `--reference BILDNAME` lässt sich ein registriertes
Referenzbild wählen; andernfalls wird das mittlere Bild nach Dateiname verwendet.
Der PLY-Export bleibt unskaliert und wird nicht durch die Vorschau verändert.

## Dichte Auswertung

Der einfache CLI oben ist keine vollständige Dense-MVS-Pipeline. Eine weitergehende
Auswertung kann schärfeorientierte Auswahl nativer Videobilder, einen gemeinsamen
Kameraverbund, Bildentzerrung, Multi-View-Stereo und geometrische Konsistenzprüfungen
verwenden. Die dabei tatsächlich ausgeführten Parameter, Qualitätsdaten und
projektbezogenen Referenzmarkierungen gehören in ein separates Reproduktionspaket.

Lücken dürfen nicht als beobachtete Oberflächen ausgegeben werden. Eine größere
Punktzahl allein belegt keine höhere Genauigkeit. Eine strengere Auswahl nach
Mehransichtskonsistenz sollte neben der möglichst vollständigen Wolke verfügbar
bleiben. Reprojektionsfehler beschreiben die interne Anpassung, keine externe
Messgenauigkeit.

## Extern bestimmte Kalibrierung anwenden

`align_point_cloud.py` überträgt eine bereits bestimmte Transformation auf eine
unskalierte PLY-Datei. Es ermittelt weder die Referenzkanten noch den Maßstab.
Die externe JSON-Datei muss `world_to_metres_4x4` enthalten: eine affine 4×4-Matrix
mit Rotation, Translation und genau einem gleichmäßigen Maßstab. Getrennte
Streckungen der Achsen und Spiegelungen werden abgewiesen.

```sh
python scripts/align_point_cloud.py unskaliert.ply calibration.json scan_m.ply
python scripts/align_point_cloud.py unskaliert.ply calibration.json scan_mm.ply --millimetres
```

Abhängigkeiten: NumPy und `plyfile`. Farben und weitere Punktattribute bleiben
erhalten; vorhandene Normalen werden nur rotiert. Bestehende Ausgabedateien werden
nicht überschrieben. Bereits kalibrierte Punktwolken nicht erneut transformieren.

Die Sauna-CAD-Quellen arbeiten in Millimetern. Die vorhandene Blender-Pipeline
importiert STL mit Faktor 0,001 und arbeitet in Metern. Für eine Überlagerung
müssen auch Ursprung und Achsen bewusst zugeordnet werden; eine bloße
Maßstabsänderung stellt noch keine räumliche Registrierung her.

Bekannte Maße benötigen eindeutig zugeordnete sichtbare Endpunkte. Eine weitere
Messstrecke sollte zur Kontrolle dienen. Zwischen gemessenen Angaben, angenommenen
Zuordnungen und Entwurfsoptionen ist zu unterscheiden. Ein 2-mm-Punktraster sagt
nichts über eine erreichbare 2-mm-Messgenauigkeit aus.

Die Transformation wurde auf rekonstruierten Punkten gegen COLMAPs `Sim3d`
geprüft; die Ergebnisse stimmen innerhalb der Float32-Exportpräzision überein.
Das prüft die Implementierung, nicht die externe Referenzmessung.
