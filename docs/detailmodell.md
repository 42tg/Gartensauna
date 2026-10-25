# Bauteilmodell und Materialansichten

Stand: 25.10.2026. Visualisierter Konstruktionsentwurf, keine Ausführungsplanung.

`cad/sauna-detailed.scad` verwendet Grundriss und Öffnungen des V3-Modells. Alle Bretter, Latten, Ständer und Dämmfelder sind CAD-Geometrie. Blender ergänzt ausschließlich prozedurale Holzmaserung, raue Dämmstoff- und Betonoberflächen, Metall, transparentes Glas, Beleuchtung und Beschriftung. Keine KI-Bilder und keine Bildtexturen erforderlich.

## Drei Ansichten

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
