# Hinweise für Coding Agents

- Dieses Repository dokumentiert ein reales DIY-Saunabauprojekt. Keine ungeprüften Bauanweisungen als sicher darstellen.
- Zwischen **gemessenen Fakten**, **Annahmen**, **Optionen** und **beschlossenen Entscheidungen** unterscheiden.
- Geometrie nach Möglichkeit parametrisch in Millimetern definieren; Eingabeparameter zentral pflegen.
- Bei Maßänderungen Grundriss, 3D-Modell, Dokumentation und Stückliste konsistent halten.
- CAD-Ausgaben (z. B. STEP) zusätzlich zur editierbaren Quelle versionieren, sofern verfügbar.
- Konstruktionen auf Feuchteschutz, Austrocknung, Hitze, Ofen-Sicherheitsabstände und Brandschutz prüfen lassen.
- Elektroanschlüsse und tragende Änderungen müssen durch geeignete Fachleute beurteilt bzw. ausgeführt werden.
- Neue Entscheidungen als kurze ADR unter docs/decisions/ dokumentieren; Ungeklärtes als Issue erfassen.
- Keine Maße aus Fotos ableiten, als seien sie vermessen worden.

## Plausible Platzierung und Abstände
- Bei Änderungen an Ofen, Bänken, Öffnungen oder Einbauten selbstständig die zugänglichen Herstellerunterlagen prüfen, Maße am aktuellen CAD kontrollieren und eine sinnvolle Position wählen.
- Wärmeabstände zu brennbaren Bauteilen, Glas/Rahmen, Boden und Decke sowie Kollisionen, Montageorientierung und Laufwege berücksichtigen. Bei ungewählter Variante konservative verfügbare Herstellerwerte verwenden und Annahmen benennen.
- Wesentliche geometrisch prüfbare Abstände automatisiert absichern. Nicht prüfbare Punkte konkret dokumentieren; geometrisches Bestehen nicht als umfassende Montagefreigabe darstellen.
- Bei Ofenplanung auch Raumvolumen und Glaszuschlag auf Plausibilität prüfen. Nutzer nicht für routinemäßige sinnvolle Platzierungen um Bestätigung bitten.

## Verbindliche visuelle Präsentation

- Bei Änderungen an CAD-Geometrie, Raumaufteilung, Bauteilen, Materialien oder der Darstellung die aktualisierten Ansichten erzeugen und dem Nutzer **direkt als eingebettete Bilder** präsentieren. Ein bloßer Hinweis auf einen erfolgreichen Workflow oder ein Download-Link genügt nicht.
- Immer die **Gesamtansicht**, die **Explosionsansicht** und die **Cutaway-Innenansicht** zeigen. Bei Änderungen am Wandaufbau zusätzlich die beschriftete **Wandlagenansicht** zeigen; auf Wunsch alle vier Ansichten.
- Ausschließlich Bilder aus der tatsächlichen CAD-Geometrie verwenden: OpenSCAD → STL-Bauteile → Blender → PNG. Keine KI-generierten Ersatzbilder. Materialien, Licht und Kamera dürfen die Darstellung verbessern, aber keine falschen Maße oder Bauteile suggerieren.
- Einzelne Bretter, Latten, Ständer, Dämmung und weitere Materiallagen erkennbar darstellen. Explosionsansichten verschieben Bauteile ohne Skalierung; die Cutaway-Ansicht blendet Dach und kameraseitige Fassaden für die Innenansicht reversibel aus.
- Den Workflow `Render CAD to Blender` in `.github/workflows/render-cad.yml` für den aktuellen Modellstand erfolgreich durchlaufen lassen. Danach die PNGs aus den zugehörigen Artefakten herunterladen, selbst visuell prüfen und im Ergebnis zeigen. Keine veralteten Bilder als aktuellen Stand ausgeben.
- Die vier Ausgaben heißen `gartensauna_assembled`, `gartensauna_exploded`, `gartensauna_wall_detail` und `gartensauna_cutaway` (jeweils `.blend`, `.png` und Prüfbericht). Das gemeinsame Download-Paket heißt `gartensauna-cad-blender`.
- Zusätzlich zu den Bildern den passenden GitHub-Lauf bzw. das Download-Paket mit den Blender-Dateien verlinken. Noch offene Maße, Schichtdicken und Konstruktionsannahmen knapp benennen, soweit sie für die gezeigte Änderung relevant sind.
- Falls Rendering oder Bildanzeige technisch scheitern, den konkreten Fehler transparent nennen; keine erfolgreiche Bildprüfung behaupten.
- Reine Dokumentationsänderungen ohne Einfluss auf Modell oder Darstellung erfordern keinen erneuten Renderlauf.

## Verbindlicher Neubau- und Höhenbezug
- Der alte Schuppen wird abgerissen. Seine 1930 mm Höhe sind ausschließlich Bestandsdaten und keine Neubaugrenze.
- Entscheidung 0012 gilt: 2200 mm lichte Innenhöhe, Oberkante Fertigboden bis Unterkante fertige Decke. Dach- und Bodenaufbau kommen außen hinzu.
- `clear_internal_height` ist die zentrale CAD-Vorgabe. Innenhöhe, Dachoberkante und Gelände-/Fundamentbezug ausdrücklich unterscheiden. Historische V1/V2-Maße und ältere ADR-Höhen nicht als aktuellen Stand übernehmen.
