# 0012 – Abriss des Altbestands und 2,20 m lichte Neubauhöhe

Status: beschlossen. Datum: 13.11.2026.

Der alte Schuppen wird abgerissen. Es entsteht ein Neubau am Standort. Die gemessenen ca. 1930 mm Altbestandshöhe sind keine Begrenzung für den Neubau. Scan und Bestandsmaße beschreiben den alten Zustand; alte Pfosten, Dach und Lagergut sind keine dauerhaft verbleibenden Hindernisse.

## Verbindliche Definition

**2200 mm lichte Innenhöhe = Abstand von Oberkante fertigem Boden (z=0) bis Unterkante fertiger Deckenbekleidung (z=2200).** Gilt im aktuellen horizontalen Modell für Sauna und Umkleide. Kein Rohbaumaß, keine Außenhöhe und kein Maß ab Gelände.

| Bezug | Höhe im aktuellen CAD |
|---|---:|
| Fertigboden | 0 mm |
| Fertige Deckenunterseite | +2200 mm |
| Dachaufbau einschließlich Deckenbekleidung | 281 mm |
| Dachoberkante | +2481 mm |
| Bodenunterseite | −120 mm |
| Bodenunterseite bis Dachoberkante | 2601 mm |
| Schematische Auflagerunterkante | −300 mm |

Dachgefälle, Entwässerung, Gelände-/Fundamentbezug und örtlich zulässige Gebäudehöhe sind offen. Die Außenhöhe ab Gelände ist deshalb noch nicht festgelegt. Aufbauwerte sind Planungsannahmen, keine Ausführungsfreigabe.

## Umsetzung und Folgen

`clear_internal_height` in `cad/sauna-v3.scad` ist die zentrale Höhenvorgabe. `height` übernimmt diesen Wert für Wände, Glasfront und Deckenbeginn; der Dachaufbau kommt nach oben hinzu. Die bisherigen 2400 mm im CAD waren bereits Innenhöhe, nicht Außenhöhe. Diese frühere Annahme wird hiermit ersetzt.

Die Glasfront folgt mit 2000 × 2200 mm der Öffnung; sichtbares Glas im Detailmodell 1930 × 2130 mm. Die Trocknungsöffnung folgt der Decke mit 60 mm Abstand über der freien Öffnung. Türen bleiben 2050 mm hoch. Grundriss und Bankpositionen bleiben bestehen.

Alte CFD-Ergebnisse bleiben historische Resultate und müssen vor Aussagen zum neuen Modell neu berechnet werden. Ofenauswahl bleibt offen: Der niedrigere Raum allein löst die bereits dokumentierte Leistungsfrage nicht. Referenzraum nach aktuellem Hüllaufbau ca. 1,75 × 3,29 × 2,20 = 12,67 m³, sichtbares Glas ca. 4,11 m²; mit bisher angesetztem Glaszuschlag ca. 16,78 m³. Keine Beschaffungsfreigabe.
