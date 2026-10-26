# Bauteilmodell V3.1

Stand 26.10.2026. CAD ist Geometriequelle; Blender ergänzt Materialien, Licht, Kamera und Beschriftung. Keine KI-Bilder.

Der aktuelle [Hüllaufbau](construction/insulation.md) ersetzt die bisherigen 180-mm-Wand- und 160-mm-Dachannahmen: Wand 205 mm, Dach 281 mm, Boden weiterhin 120 mm. Parameter stehen in `cad/envelope.scad`. 34 CAD-Gruppen, davon neun Wandgruppen. Ständer und Dämmung belegen dieselbe Schicht.

## Ansichten

- Gesamtansicht: vollständiges Bauteilmodell.
- Explosion: identische Geometrie, Dach-/Bodenlagen in Z versetzt.
- Wandlagen: neun Gruppen eines 1200 × 2400-mm-Musters, mit Beschriftung. Horizontale Bretter und vertikale Luftwege.
- Cutaway: dieselben 34 Gruppen; zehn Dachgruppen und zwei Glasgruppen ausgeblendet. Neun Wandgruppen mit je drei reversiblen Schnittmasken. Bänke, Stuhl und Boden bleiben sichtbar.

Zusätzlich bleibt die Ofendetailansicht verfügbar. Ausgabe: `gartensauna_<Ansicht>.blend/.png/.json`; gemeinsames Paket `gartensauna-cad-blender`.

Zwei freie Liegeflächen je 600 × 2100 mm; Oberkante unten 535, oben 975 mm. Acht Lamellen je Bank, 5-mm-Fugen. Gang an Glasfront 520 mm, rückwärtige Standfläche 645 mm, freier Türzugang hinter dem Bankende 600 mm. Umkleide nur 892,5 × 1290 mm. Bankaufstieg, Türflügel und konstruktive Anschlüsse bleiben offen.

Die Berichte prüfen Modellmaße und geometrische Ofenabstände; sie sind keine Fertigungs- oder Montagefreigabe. Das Dach ist ein flaches Schichtmodell mit reservierter Lüftungszone; Gefälle und offene Lüftungsanschlüsse sind noch nicht konstruiert.
