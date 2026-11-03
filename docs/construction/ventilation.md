# Lüftung und vergleichende Strömungsprüfung

Stand: 03.11.2026. **Planungsvariante, keine Montage- oder bauphysikalische Freigabe.**

## Eingebautes Konzept
Mechanische Abluft, passive Zuluft, separate geschlossene Trocknungsklappe. Die Luftführung ist unabhängig von der Fassadenhinterlüftung. Die Glasfront bleibt erhalten. Alle Maße werden in `cad/ventilation.scad` definiert und über OpenSCAD für die Simulation ausgewertet.

| Bauteil | Position im CAD (mm) | Freie Rohöffnung vor Lamellen |
|---|---|---|
| Zuluft | Stirnwand am Ofen: x 1550–1700, z 1080–1160 | 150 × 80 mm |
| Betriebsabluft | Rechte Außenwand: y 500–800, z 220–380 | 300 × 160 mm |
| Trocknung | Rechte Außenwand: y 500–800, z 2180–2340 | 300 × 160 mm, während Nutzung geschlossen |

Wanddurchführungen enthalten 2-mm-Hülsen, innen/außen Lamellen und einen 8-mm-Rand. Die Trocknungsöffnung hat eine geschlossene Platte. Farben zur Orientierung: Zuluft blau, Abluft kupferfarben, Trocknung dunkelgrau. Mechanik, Wetterschutz, Insektenschutz, Befestigung und Ventilator sind nicht konstruiert. Abdichtung der Hülse an die Dampfsperre, Kondensatableitung/Gefälle und Wärmebrücken sind vor Bau zu detaillieren; der CAD-Kontakt ersetzt keinen Dichtheitsnachweis.

Die Lamellen lassen geometrisch 65 % frei: ca. 78 cm² Zuluft und 312 cm² Abluft, flächengleich etwa Ø100/200 mm. Das ist **keine hydraulische Gleichwertigkeit** zu Rundrohren. Bei 80 m³/h ergibt sich an der freien Zuluftfläche etwa 2,85 m/s. Geräusch, Druckverlust und Zug am Auslass müssen durch passende Ventile/Verteiler und Ventilatorauslegung geprüft werden. Angegeben sind tatsächliche Volumenströme am Raum, keine unbelastete Ventilator-Nennleistung.

Referenz: [HUUM DROP 2.0 EU v6, Lüftung S. 12–13](https://huum.eu/wp-content/uploads/2026/01/DROP_2_0_User_Manual_EU_v6_WEB.pdf), geprüft 03.11.2026. Mechanisch: Zuluft Ofenmitte oder höher, Abluft gegenüber ≤600 mm über Boden, Trocknung unter Decke; etwa sechs Luftwechsel/h. Endgültige Ofen-/Steuerungswahl und Fühlerabstände bleiben offen; insbesondere ist die bereits dokumentierte Leistungsfrage des DROP durch diese Lüftungsplanung nicht gelöst.

## Was berechnet wird
Ein **stationäres dreidimensionales isothermes Potentialströmungsmodell** mit anschließendem konservativem Luftaltertransport. Es löst keine Navier-Stokes-Impulsgleichung und ist keine thermische Sauna-CFD. Es eignet sich zum reproduzierbaren Screening der Luftwege bei vorgegebenem mechanischem Durchsatz.

1. Aus der CAD-Geometrie werden Innenraum, Glas-/Trennwandversatz, Ofenhülle, beide Bankhüllen und Öffnungen übernommen. Umkleidetür und Trocknungsklappe sind geschlossen. Die Saunatür selbst ist im bisherigen Darstellungsmodell nicht als Türblatt modelliert; ihre geschlossene Wirkung ist eine explizite Simulationsrandbedingung.
2. Kartesisches Finite-Volumen-Gitter; alle Wand- und Hindernisflächen undurchlässig. Die Bänke werden inklusive Unterzügen als geschlossene Hüllen voxelisiert; Lamellenspalten, Füße, Menschen und Ofenporosität fehlen. Randzellen werden nicht teilvolumetrisch aufgelöst. Gitterverfeinerung verändert deshalb auch leicht das Luftvolumen.
3. Diskrete Potentialgleichung: `L φ = q_in − q_out`, Fluss zwischen Nachbarzellen `F_ij = (A/d) (φ_i − φ_j)`. Eine Zelle setzt den Potentialnullpunkt. Zu-/Abluft werden über die exakte geometrische Überlappung der Öffnung mit den Randzellen verteilt. Die Lamellen werden hier homogenisiert; Düsenstrahlen sind nicht aufgelöst. Der Ventilator wird als vorgegebener Volumenstrom dargestellt.
4. Stationäres mittleres Luftalter `a`: `div(u a − D grad(a)) = 1`. Konservatives Upwind-Verfahren; Frischluft hat Luftalter null, konvektiver Austrag, kein diffusiver Transport durch die äußeren Grenzen (Danckwerts-Zufluss). `D = 0,003 m²/s` ist eine **unkalibrierte effektive Mischungsannahme**, keine Materialkonstante oder gemessene Turbulenz.
5. Numerische Prüfungen: lokale/global geschlossene Volumenbilanz, Gleichungsresiduen, nichtnegative endliche Luftalter, globaler Identitätstest `mittleres Abluftalter = Luftvolumen/Q`. Ein unabhängiger 1-D-Kanaltest prüft das exakte diskrete Luftalter; ein Skalierungstest prüft den Solver bei verdoppeltem Durchsatz und Mischungskoeffizienten.

**Nicht enthalten:** Wärmeauftrieb vom Ofen, Lufttemperaturen, Temperaturgradienten, thermische Behaglichkeit, Aufguss/Feuchte, CO₂-Produktion durch Personen, Turbulenz, Wandreibung, Wind, Leckagen, Rohrwiderstand, Ventilatorkennlinie oder Entfeuchtungsdauer. Gerade im heißen Saunabetrieb kann Wärmeauftrieb die reale Strömung wesentlich ändern. Aus den Zahlen folgt keine Gesundheits-/Komfortaussage oder Freigabe.

## Vergleichswert
**Luftalterfaktor im Aufenthaltsbereich = mittleres lokales Luftalter / (Luftvolumen / Q).** Kleiner bedeutet innerhalb identischer Modellannahmen frischere Luft an den betrachteten Orten. 1 entspricht dem mittleren Luftalter idealer vollständiger Durchmischung. Werte unter 1 sind möglich; dies ist kein auf 100 % begrenzter Wirkungsgrad und kein Sicherheitsgrenzwert.

Ausgewertet wird die Vereinigung der Bereiche über beiden Bankgrundflächen, von 0,10 bis 1,00 m über der Bankhülle (begrenzt durch die Decke). Zusätzlich: P95 des Luftalters, Anteil der Aufenthaltszellen über zweifachem nominalem Luftalter, Luftwechsel/h und numerische Residuen. Keine räumliche/personenbezogene Aufenthaltsgewichtung. Durchschnitt und P95 gemeinsam beurteilen.

## Varianten und Reproduzierbarkeit
`simulation/cases.json` steuert:
- geplante Position bei 80 m³/h;
- Abluft näher am Ofen (y −1100 mm), nur virtuell;
- hohe Abluft über die Trocknungsöffnung statt der unteren Abluft, nur virtuell;
- geplante Position bei 60 und 100 m³/h;
- Gitter 12 und 8 cm;
- Mischungskoeffizienten 0,001 / 0,003 / 0,01 m²/s.

Die virtuellen Varianten ändern das gebaute CAD nicht. Zwei Gitter sind ein Empfindlichkeitstest, kein vollständiger Konvergenznachweis. Die unterschiedlichen Mischungsannahmen zeigen Modellunsicherheit. Eine höhere Luftmenge muss nicht einen besseren normierten Faktor ergeben; deshalb stets auch Minutenwerte vergleichen.

```sh
pip install -r simulation/requirements.txt
python -m unittest discover -s tests -v
python scripts/check_ventilation_cad.py
python scripts/simulate_ventilation.py
```

OpenSCAD muss installiert sein. Ausgabe unter `build/ventilation/`: `comparison.md`, `results.json` (Parameter, Geometrie-Hash, Residuen und Kennzahlen), `geometry.json`, Schnittbilder mit projizierten berechneten Geschwindigkeitsvektoren und Vergleichsgrafik. Gittervektoren sind keine thermischen Auftriebs-/Aufgussbahnen. Farben zeigen Luftalter, keine Temperatur.

GitHub Action **Ventilation comparison** läuft bei relevanten CAD-/Solveränderungen und manuell, veröffentlicht eine Job-Zusammenfassung und das 14 Tage aufbewahrte Artefakt `ventilation-comparison`. Die bestehende CAD→Blender-Pipeline zeigt die tatsächlichen neuen Öffnungen.

## Erste Ergebnisse und nächste Validierung
Bei 80 m³/h: geplante Position Faktor ca. **0,758**, Ø **7,11 min**, P95 **10,47 min**; ofennahe Abluft **1,367**, Ø **12,83 min**, P95 **18,73 min**. Die geplante Position ist in diesem isothermen Vergleich günstiger. Hohe Abluft: **0,729**, aber P95 **10,66 min**; wegen fehlender Wärmeverluste/Auftrieb daraus ausdrücklich keine Empfehlung ableiten.

Gitterwechsel 12→8 cm: ca. **0,2 %** Faktoränderung. Mischungsvariation: Faktor **0,689–0,856**. Diese Modellunsicherheit ist deutlich größer als die beobachtete Gitterabweichung. Ausgangs-Luftvolumen ca. 12,52 m³ (voxelisierte freie Luft); 80 m³/h entsprechen ca. 6,39 Luftwechseln/h. Das Raumvolumen ohne Einbauten ist größer und darf für die Ofenauslegung nicht durch das simulierte Luftvolumen ersetzt werden.

Für eine thermische Optimierung: tatsächliche Heizleistung/Steintemperatur, Zulufttemperatur, Glas-/Wandwärmeverluste, Ventilatorbetrieb und Nutzung definieren; anschließend thermische CFD mit Auftrieb und Gitter-/Randbedingungssensitivität. Nach Bau reale Luftmenge, Temperaturverteilung und Luftqualität mit für die Bedingungen geeigneter Messtechnik überprüfen.

## Thermische Erweiterung

Seit 03.11.2026 ergänzt eine [gekoppelte OpenFOAM-CFD](thermal-cfd.md) dieses isotherme Screening. Sie berechnet temperaturabhängige Dichte, Wärmeauftrieb, Turbulenz, Hüllverluste und Oberflächenstrahlung. Die thermischen Szenarien haben eigene Bilanz- und Stabilitätsprüfungen. Die oben dokumentierten Potentialmodell-Zahlen bleiben Ergebnisse des alten vereinfachten Modells und werden nicht als thermische Ergebnisse umgedeutet.
