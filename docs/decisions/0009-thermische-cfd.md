# 0009 – Gekoppelte thermische Strömungssimulation

03.11.2026. Nutzerauftrag: Wärmeauftrieb und weitere thermische Effekte tatsächlich implementieren.

- OpenCFD OpenFOAM v1912.200626 mit idealgasbasierter Dichte, `buoyantSimpleFoam`, `buoyantKEpsilon` und fvDOM-Oberflächenstrahlung.
- CAD-parameterbasiertes orthogonales Gitter mit exakten Hüll-/Öffnungsgrenzen; vereinfachte Ofen-/Bankhüllen bleiben explizite Annahmen.
- Vorgeschriebene mittlere gesamte Ofenwärmeleistung, Hüllverluste und kalte mechanische Zuluft. Basisszenario 3 kW, 80 m³/h Zuluft bei 10 °C, keine gemessenen Betriebswerte.
- Eigene konservativ gedämpfte thermische Randbedingung behebt einen bei der Wärmebilanzprüfung nachgewiesenen Fehler im v1912-Referenzmodell. Getrennter Typ, keine Systemänderung; GPL-Quellcode und Regressionstest im Repository.
- Automatische Massen-/Wärme-/Strahlungs-/Feldstabilitätsprüfung; fehlgeschlagene Fälle werden nicht für Rankings freigegeben.
- Kontrollfall ohne Schwerkraft und Sensitivitäten für Gitter, Strahlung, Wärmeleistung und Glasverluste.

Details und Grenzen: [Thermische CFD](../construction/thermal-cfd.md). Diese Entscheidung ist eine Simulationsimplementierung, keine Änderung der Baugeometrie und keine Bau-/Ofenfreigabe. Offene physikalische Eingaben und spätere Messvalidierung bleiben in Issue #8.
