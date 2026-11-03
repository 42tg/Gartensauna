# 0008 – Lüftungsöffnungen und vergleichende Strömungsprüfung
Datum: 03.11.2026. Nutzerauftrag: Öffnungen ins CAD integrieren und eine vergleichbare Strömungsprüfung einrichten.

Umgesetzt als **vorläufige mechanische Lüftungsvariante**: Zuluft über dem Ofen, Abluft unter dem entfernten Bankbereich, separate geschlossene Trocknungsklappe. Positionen/Größen zentral in `cad/ventilation.scad`. CAD-Kollisionsprüfung gegen Ständer und Lattung. Glasfront unverändert.

Der erste Solver ist bewusst als isothermes Potentialströmungs-/Luftaltermodell gekennzeichnet; keine thermische Navier-Stokes-CFD und kein Baunachweis. Kennzahl: normiertes mittleres Luftalter über den Bänken, ergänzt durch P95 und Sensitivität. Keine automatische Verlegung nach dem besten Einzelwert. Varianten, Rechenannahmen, Grenzen und Ergebnisse siehe [Lüftung](../construction/ventilation.md).

Noch offen: Ofenauswahl/Leistung, Steuerungsfühler, reale Ventilatorkennlinie, Geräusch, Wetterschutz, Kondensatführung und dampfdichte Durchführungen. Vor Ausführung fachlich prüfen. Die numerischen Prüfungen belegen Reproduzierbarkeit und Erhaltung, nicht physikalische Validierung im Saunabetrieb.
