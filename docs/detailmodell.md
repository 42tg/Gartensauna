# Bauteilmodell und Materialansichten

Stand: 26.10.2026. Visualisierter Konstruktionsentwurf, keine Ausführungsplanung.

`cad/sauna-detailed.scad` verwendet Grundriss und Öffnungen des V3-Modells. Alle Bretter, Latten, Ständer und Dämmfelder sind CAD-Geometrie. Blender ergänzt ausschließlich prozedurale Holzmaserung, raue Dämmstoff- und Betonoberflächen, Metall, transparentes Glas, Beleuchtung und Beschriftung. Keine KI-Bilder und keine Bildtexturen erforderlich.

## Vier Ansichten

- `assembled`: zusammengebautes Gebäude mit Holzfassade und vollständiger Glasfront.
- `exploded`: Dach- und Bodenbauteile in Z auseinandergezogen; gleiche Bauteilgeometrie.
- `wall_detail`: eigenständiges 1.200 × 2.400-mm-Wandmuster, dessen acht Materialgruppen seitlich versetzt und beschriftet sind. Dieses Muster ist keine zusätzliche Gebäudewand.

## Wandaufbau – neue, unbestätigte Modellannahmen

Von außen nach innen, Gesamtdicke 180 mm:

| Schicht | Modellmaß | Darstellung |
|---|---:|---|
| Holzfassade | 18 mm | einzelne vertikale Bretter, 120-mm-Raster |
| Hinterlüftung / Lattung | 20 mm | horizontale Latten, übriger Raum bleibt offen |
| Winddichtung | 2 mm | dunkle Bahn, Dicke zur Sichtbarkeit überhöht |
| Holzständer und Dämmung | 100 mm | 45-mm-Ständer im 600-mm-Raster; Dämmfelder dazwischen |
| Alu-Dampfsperre | 1 mm | silberne Bahn, Dicke zur Sichtbarkeit überhöht |
| Innenlattung | 19 mm | horizontale Latten |
| Innenverkleidung | 20 mm | einzelne Bretter im 95-mm-Raster |

Ständerwerk und Dämmung teilen sich dieselbe Schicht. Bahndicken sind schematische Volumina, keine Produktspezifikation. Eckanschlüsse, Dichtung, Lüftungswege und Tragwerk sind noch nicht gelöst. Die horizontale Fassadenlattung allein ist insbesondere noch kein Nachweis einer durchgängigen Hinterlüftung.

## Boden und Dach – Modellannahmen

Boden: 12-mm-Unterplatte, 88-mm-Balken-/Dämmzone, 20-mm-Bodendielen; insgesamt 120 mm. Sichtbare Betonauflager ersetzen den alten massiven Fundamentplatzhalter, ohne einen Fundamentnachweis darzustellen.

Dach: 15-mm-Untersicht, 120-mm-Balken-/Dämmzone, 22-mm-Schalung, 3-mm-dunkle Dachhaut; insgesamt 160 mm. Umlaufende Blende. Die bisherige flache Geometrie bleibt erhalten; Dachgefälle und Entwässerung sind weiterhin offen.

Die 2.000 × 2.400-mm-Glasfront besitzt nun einen schmalen 35-mm-Rahmen als Visualisierungsannahme. Der Glasaufbau ist nicht spezifiziert. Bänke bestehen aus einzelnen Latten mit sichtbaren Unterzügen und Beinen.

Die automatisch erzeugten JSON-Berichte dokumentieren CAD-Gruppen und Abmessungen in Metern. Sie sind keine bestellfähige Stückliste.

## Cutaway – zusätzliche Innenansicht
`cutaway` importiert dieselben 29 CAD-Gruppen wie `assembled`. Dach einschließlich Untersicht und die Glasfront werden für Render und Viewport ausgeblendet. Drei zur Kamera gerichtete Außenwandbereiche (Front Umkleide, Stirnseite Saunaflügel, linke Außenseite Umkleide) werden mit nicht angewendeten Boolean-Modifikatoren ausgeblendet. Boden, Bänke, Stuhl, rückwärtige Wände und Trennwand bleiben sichtbar. Die Original-Meshdaten bleiben erhalten. Dach-/Glasobjekte wieder einblenden und die Cutaway-Modifikatoren deaktivieren, um die vollständige Geometrie zu sehen.

Die vier Ansichten laufen parallel auf GitHub. Einzelansichten sind als `render-<Ansicht>` verfügbar; das vollständige Paket bleibt `gartensauna-cad-blender`.

## Zwei gleich breite Liegebänke
Beide Ebenen haben 600 mm vollständig freie Liegebreite und 2100 mm Länge. Die untere Fläche liegt nicht unter der oberen. Zwischen beiden liegen 20 mm; rechts zur Wand 10 mm Modellfuge. Acht gleich breite Lamellen je Ebene mit 5-mm-Fugen vermeiden schmale Reststreifen. Alle Layoutparameter stehen in `cad/bench-layout.scad` und werden von V3 und Detailmodell verwendet.

Die Bänke beginnen bei y=-1250 und enden bei y=850 mm. Vorne bleibt Abstand zum Ofen, hinten 670 mm Standfläche. Der Umkleide-Durchgang wurde auf y=650..1450 mm verschoben; davon führen 600 mm unmittelbar in die freie hintere Standfläche. Der Gang an der Glasfront ist 545 mm breit; die Engstelle neben der Trennwand bleibt 410 mm, wird durch den rückwärtigen Zugang umgangen und ist nicht der geplante Ein-/Ausstieg. Kein barrierefreier Entwurf. Höhen unverändert: Oberkante unten 535 mm, oben 975 mm; Aufstiegshilfe und Tragwerk bleiben zu planen.

Der CAD-projizierte aktuelle Grundriss liegt unter `docs/visuals/grundriss-v3.svg`. Details und Quellen: ADR 0006.
