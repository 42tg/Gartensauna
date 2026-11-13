# ADR 0014 – Bündige Trennwand und tatsächliche Türbewegung

Datum: 13.11.2026. Status: umgesetzt als überprüfbarer Vorentwurf, keine Ausführungsfreigabe.

Die bisherige Trennwand war 307,5 mm stark, weil sie als Rest zwischen zwei Raumsubtraktionen entstand. Das war kein begründeter Wandaufbau. Ihre Vorraumseite lag 102,5 mm vor dem Flügelbeginn. Beides wird korrigiert.

- Separate Trennwand: 19 + 70 + 0,1 + 20 + 19 = 128,1 mm; Vorraumseite und Flügelbeginn bei x=1605 mm.
- Vorraum lichte Breite 1400 mm bleibt provisorisch; Außenwand 205 mm. Gesamtbreite 205 + 1400 + 2000 = 3605 mm. Dachüberstand je 80 mm kommt hinzu.
- Zwei nach außen aus dem jeweiligen Raum öffnende Türen. Saunatür hinten angeschlagen, öffnet in den Vorraum; Außentür öffnet ins Freie. Zargen 800 × 2000 mm licht, Rohöffnungen 880 × 2040 mm als **Planungsproxies**, nicht Produktbestellmaße.
- Saunatür: 8 mm Glas, Blatt 794 × 1977 mm, Unterkante 20 mm. Außentür: 60-mm-Blatt, 794 × 1987 mm, Unterkante 10 mm. Griffe beidseitig; Saunatür ohne Verriegelung. Beschlag-/Falzdetails nicht ausgeführt.
- Beide Liegen um 30 mm nach vorn: y=-1280..820 mm. Maße 600 × 2100 unverändert; hinten 675 mm Standfläche.
- Frontwand schließt am Glasrahmen an; vorherige geometrische 160-mm-Ecklücke geschlossen. Dichtungs- und Tragwerksdetails bleiben offen.

`audit_layout.py` vergleicht unabhängig gebildete Wände mit einem OpenSCAD-Schnitt, prüft beide Türschwenks einschließlich Griffen und eine 600-mm-Kreisroute. `verify_render.py` prüft echte STL-Bauteilmaße. CAD und Blender zeigen geschlossene Türen in der Gesamtansicht, offene Türen in Cutaway und Grundriss.

Nicht gelöst: Bankaufstieg, unterdimensionierter DROP, reale Türprodukte, Gründung/Tragwerk, Feuchte-/Glasanschlüsse und Aufmaß. [Rechnung und Befunde](../reality-check-2026-11-13.md). Historische Scan-Skalierung auf 3200 mm bleibt unverändert.
