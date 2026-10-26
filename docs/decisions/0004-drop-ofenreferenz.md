# 0004 – HUUM DROP als visuelle Ofenreferenz

Datum: 2026-10-25. Status: Gestaltungsreferenz akzeptiert, keine Kauf-/Montageentscheidung.

Nutzerwunsch: Ofen ungefähr wie das verlinkte Produkt in den CAD-/Blender-Ansichten darstellen.

## Belegte Produktangaben
- HUUM DROP, wandhängend, offener Edelstahlkorb mit sichtbaren Steinen.
- Breite 390 mm, Tiefe 335 mm, Höhe 590 mm; Steinfüllung laut Hersteller 55 kg.
- Quelle: https://huum.eu/product/drop-electric-sauna-heater/
- Nutzerreferenz: https://www.iot-pool.com/en/products/aquecedor-para-sauna-huum-drop?variant=53968447766868

## Modellentscheidung und Annahmen
Eigenes parametrisches Näherungsmodell in `cad/heater-drop.scad`, kein Hersteller-CAD und keine Fertigungszeichnung. Korbprofil, Stababstände, Halterung und Steinanordnung sind visuell angenähert. Alle drei Gruppen werden über OpenSCAD → STL nach Blender übernommen, einschließlich Cutaway und Explosion; keine nachträglich erfundene Blender-Geometrie.

Die ursprüngliche Position an der hinteren Innenwand wurde am 2026-10-26 durch die fensternahe Position aus [ADR 0005](0005-ofen-am-fenster.md) ersetzt. Dort stehen aktuelle Maße und Abstandsprüfung. Der Ofen bleibt bei der Gebäude-Explosion unzerlegt an seiner Position. Die zusätzliche Ansicht `heater_detail` zeigt dieselben CAD-Meshes aus der Nähe.

## Offen
Leistungsvariante, Eignung für Raumvolumen inklusive großer Glasfläche, vorgeschriebene Sicherheitsabstände, Berührungsschutz, tragfähige Wandbefestigung und Elektroplanung sind noch zu prüfen. Die gerenderte Lage ist keine bestätigte sichere Montage. Keine Behauptung einer exakt 55 kg schweren modellierten Steinfüllung. Alte V1-/V3-Konzeptmodelle bleiben historische Layoutstände; das aktive Detailmodell enthält den neuen Ofen.
