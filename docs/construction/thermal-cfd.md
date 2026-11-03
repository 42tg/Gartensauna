# Thermische Sauna-CFD: Wärmeauftrieb, Strahlung und Luftwechsel

Stand: 03.11.2026. **Implementierte numerische Untersuchung mit angenommenen Betriebsbedingungen; keine Messung oder Bau-/Ofenfreigabe.** Der neue Workflow ergänzt den bisherigen isothermen Potentialvergleich. Seine Werte dürfen nicht ungeprüft mit dessen Faktoren gleichgesetzt werden.

## Tatsächlich gekoppelte Physik

OpenCFD **OpenFOAM v1912.200626**, `buoyantSimpleFoam`, löst stationär die Kontinuitäts-, Impuls- und Enthalpiegleichungen. Die Luftdichte folgt dem idealen Gasgesetz `rho = p/(R T)`. Die Schwerkraft wirkt damit auf die temperaturabhängige Dichte; warme Luft steigt aus der berechneten Lösung auf. Es werden keine vorgegebenen Auftriebsvektoren oder illustrierten Stromlinien addiert. Die große Temperaturspanne wird nicht auf eine Boussinesq-Näherung reduziert.

- Turbulenz: `buoyantKEpsilon`, einschließlich Produktion/Dämpfung durch Dichtegradienten, mit Wandfunktionen.
- Lufttransport: Sutherland-Viskosität und zugehörige Wärmeleitfähigkeit; Cp 1005 J/(kg K), Molmasse 28,97 kg/kmol.
- Oberflächenstrahlung: `fvDOM`, graue diffus emittierende/reflektierende Oberflächen, 16 Strahlrichtungen im Basisfall; 36 im Winkel-Sensitivitätsfall. Luft ist als nicht absorbierend/emittierend angenommen. Fenster sind für diese langwellige Wärmestrahlung als undurchlässige Oberfläche modelliert, nicht als offenes Loch.
- Ofen: vorgeschriebene **gesamte mittlere Wärmeleistung** an seiner CAD-Außenhülle. Sie teilt sich in berechnete Konvektion und Strahlung auf.
- Wand, Glas, Dach und Boden: Wärmeabgabe an eine vorgegebene Umgebung über thermische Leitwerte; innere Konvektion wird vom Solver erfasst.
- Bänke: geschlossen angenäherte Oberflächen, außen adiabatisch; aufgenommene Strahlung und konvektiver Wärmeaustausch werden bilanziert.
- Ventilation: vorgegebene Zuluftmenge **bei Zulufttemperatur**, Druckauslass mit Rückströmungs-Randbedingung. Die mechanische Anlage wird als Randbedingung repräsentiert; der erforderliche Ventilator-/Kanalbetrieb wird nicht ausgelegt. Warme Abluft hat wegen ihrer geringeren Dichte einen anderen Volumenstrom als die kalte Zuluft.

Die tatsächlichen RANS-Geschwindigkeiten fließen anschließend in eine konservative Berechnung des mittleren Luftalters ein. Für skalare Durchmischung gilt `D = 2e-5 m²/s + nut/0,7`. Der turbulente Schmidt-Wert ist eine Modellannahme. Die zugehörige Quellgröße ist `rho * Zellvolumen`, die Flüsse sind Massenflüsse. Normierung: gesamte Luftmasse / einströmender Massenstrom.

## Geometrie und Rechengitter

`scripts/thermal_case.py` wertet dieselben OpenSCAD-Parameter aus wie das CAD. Die Gitterlinien liegen exakt auf Raum-, Ofen-, Bank- und Öffnungsgrenzen. Die daraus erzeugten Hexaeder sind orthogonal; `checkMesh` muss bestehen. Zu-/Abluftflächen und Raumvolumen werden gegen die analytische CAD-Hüllgeometrie getestet, außerdem die geschlossene orientierte Flächenbilanz jeder Zelle.

Im Gegensatz zur alten Voxelapproximation werden die Hüllgrenzen bei dieser Vernetzung nicht auf grobe Zellmittelpunkte verschoben. Die thermische Geometrie enthält aber weiterhin **vereinfachte geschlossene Ofen- und Bankhüllen**, keine Strömung durch einzelne Steine, Heizstäbe oder Holzlamellen. Bankfüße und Personen fehlen. Gitterweiten 16/11 cm sind maximale Teilungslängen; kleine CAD-Abstände erzeugen lokal feinere Zellen. Tür zur Umkleide und Trocknungsklappe sind im Grundfall geschlossen. Die Öffnungen sind homogenisierte volle Querschnitte, keine aufgelösten Lamellenstrahlen. Der freie Gitterquerschnitt aus dem CAD ist daher relevant für die spätere reale Auslegung, wird aber nicht als erfundene Druckverlustkennlinie benutzt.

## Basisszenario – Annahmen, keine Messwerte

Zentral: `simulation/thermal/config.json`.

| Parameter | Basis |
|---|---:|
| Zuluftmenge bei Zulufttemperatur | 80 m³/h |
| Zuluft / Umgebung | 10 / 10 °C |
| Numerischer Startwert Lufttemperatur | 65 °C |
| Mittlere gesamte Wärmeabgabe Ofen | 3000 W |
| Wand / Dach / Boden Leitwert | 0,35 / 0,22 / 0,50 W/(m² K) |
| Glas-Leitwert | 2,5 W/(m² K) |
| Emissions-/Absorptionsgrad Oberflächen | 0,9 |
| Schwerkraft | 9,81 m/s² |

Die 3000 W sind ein **mittlerer Dauerbetriebsszenario-Wert**, nicht die gewählte elektrische Ofen-Nennleistung. Die bereits offene Ofenleistungsfrage wird dadurch nicht gelöst. Ein zweiter Fall nutzt 6000 W. Die Hüll-Leitwerte repräsentieren Wärmeleitung und äußeren Wärmeübergang ohne den bereits im CFD berechneten inneren Luftfilm. Sie sind noch nicht aus endgültigen Bauteil-/Glasdaten abgeleitet.

## Vergleichsfälle

1. Geplante Lüftung.
2. Identische Bedingungen ohne Schwerkraft: kausaler Kontrollfall für den Einfluss des Auftriebs.
3. Abluft näher am Ofen.
4. Hohe Abluft an der Trocknungsöffnung, untere Abluft geschlossen; virtuelle Alternative.
5. Feineres räumliches Gitter.
6. Höherer Glas-Leitwert 5,8 W/(m² K).
7. Mittlere Wärmeabgabe 6000 W.
8. Feinere Winkelauflösung der Strahlung.

Nur die geplante Öffnungsanordnung ist im CAD gebaut; die Alternativen ändern lediglich den Rechenfall. Zwei räumliche Gitter und zwei Strahlauflösungen erlauben eine erste Sensitivitätsbeurteilung, keinen vollständigen Nachweis der Gitterunabhängigkeit. Unterschiede kleiner als die beobachtete Sensitivität nicht als belastbare Optimierung ausgeben.

## Warum eine eigene thermische Randbedingung enthalten ist

Der Ubuntu-24.04-OpenFOAM-Build nutzt v1912. Dessen `externalWallHeatFluxTemperature` dämpft bei `relaxation < 1` Referenzwert und Mischungsanteil so, dass der physikalische Fixpunkt verändert wird. Besonders bei vorgeschriebenem Wärmefluss erzeugt dies eine künstliche Wärmesenke. Die Wärmebilanzprüfung hat diesen Effekt sichtbar gemacht.

Das Projekt liefert deshalb die **separat benannte** `saunaHeatFluxTemperature` als kleine dynamische Bibliothek. Sie ändert keine Systembibliotheken. Der vollständige gemischte Randwert wird konvex gedämpft, sodass am Fixpunkt weiterhin genau der vorgegebene Wärmefluss gilt. Der Produktions-Rechenbaustein wird mit einem eigenständigen C++-Test für Dirichlet-, Neumann- und gemischte Grenzfälle geprüft. Relaxation wird in allen Modi gespeichert, damit Neustarts dieselben Einstellungen verwenden.

Zusätzlich wird die Ofenleistung über die ersten 500 **SIMPLE-Iterationen** linear von null auf den Zielwert erhöht. Das stabilisiert die nichtlineare Initialisierung; es ist **keine Aufheizkurve in Sekunden**. Ausgewertet wird erst nach der Rampe bei vollständiger Zielwärmeleistung.

Herkunft, Quellcodeänderung und GPL-3.0-or-later-Lizenz: [Boundary README](../../simulation/thermal/boundary/README.md). Der Build lädt ausschließlich den hashgeprüften v1912-Quellstand als Header-/Buildgrundlage; Solver und Bibliotheken kommen aus dem gepinnten Ubuntu-Paket. Ein weiterer v1912-Laufzeitfehler betrifft Function-Object-Hashes. Daher werden Function Objects deaktiviert und die Bilanzen unabhängig aus den gespeicherten Feldern berechnet.

## Welche Prüfungen einen Vergleich freigeben

Ein Solver-Ende allein ist kein Erfolgskriterium. `results.json` enthält `quality_pass` und konkrete Fehlergründe. Die GitHub-Rechenjobs schlagen bei nicht erfüllten Kriterien fehl; der Abschlussbericht erscheint trotzdem und kennzeichnet diese Fälle. Ihr Luftalterfaktor wird nicht als freigegebener Vergleichswert dargestellt.

- Globale Massenbilanz: Fehler ≤0,5 % des einströmenden Massenstroms.
- Lokale Massenbilanz: Summe absoluter Zell-Divergenzfehler ≤2 % des einströmenden Massenstroms.
- Gesamtwärmebilanz: Fehler ≤5 % der vorgeschriebenen Ofenleistung. Berücksichtigt werden Hüllverluste, Enthalpie-/kinetische-/potentielle Energie an den Öffnungen und dort entweichende Strahlung.
- Geschlossene Strahlungsbilanz: Fehler ≤2 % der Ofenleistung.
- Änderung zwischen den letzten gespeicherten Feldständen: volumenmittlerer Betrag der Temperaturänderung ≤0,5 K und der Geschwindigkeitsänderung ≤0,01 m/s. Der Vergleichsabstand wird ausgewiesen.
- Endliche, plausible Temperaturwerte; nichtnegative endliche Luftalter und numerisches Luftalter-Gleichungsresiduum ≤1e-7.

Das sind **numerische Qualitätskriterien**, keine Unsicherheitsgrenzen für reale Temperaturen. Insbesondere prüfen sie weder die Richtigkeit der angenommenen Wärmeverluste noch die Eignung der Wandfunktionen für alle lokalen Grenzschichten. Nicht stationär konvergierende Fälle brauchen gegebenenfalls eine instationäre URANS-Rechnung mit zeitlicher Mittelung; die Kriterien dürfen dafür nicht still gelockert werden.

## Ausgaben

Pro Fall:
- Temperatur und Luftgeschwindigkeit über beiden Bänken; Temperatur P10/P90 und Geschwindigkeit P95.
- Mittleres Luftalter, P95 und normierter Luftalterfaktor im definierten Aufenthaltsbereich über den Bänken.
- Gemittelte vertikale Luftgeschwindigkeit über der Ofenhülle als zusätzliche Diagnose; eine Einzelzahl beschreibt nicht die gesamte Zirkulation.
- Wärme-/Massenbilanzen, Feldänderungen, Strahlungsbilanz und Solverlogs.
- Temperatur-Schnittbilder mit den **berechneten** projizierten Geschwindigkeiten, Rohfelder, Netz und `sauna.foam` zum Öffnen in ParaView.

Die Pfeile sind Schnittprojektionen, keine vollständigen 3-D-Stromlinien. Farben geben Temperatur an. Der Vergleichsbericht enthält außerdem die Empfindlichkeit gegenüber Gitter und Strahlungsauflösung; fehlgeschlagene/fehlende Fälle bleiben sichtbar.

## Reproduzieren

Auf Ubuntu 24.04:

```sh
sudo apt-get install openfoam=1912.200626-2build3 libopenfoam=1912.200626-2build3 openscad build-essential flex bison curl
pip install -r simulation/requirements.txt
bash scripts/build_thermal_boundary.sh
g++ -std=c++11 tests/test_thermal_relaxation.cpp -o build/test-thermal-relaxation
build/test-thermal-relaxation
python -m unittest discover -s tests -v
python scripts/run_thermal.py thermal_planned --require-quality
python scripts/thermal_compare.py
```

Vorhandene Ergebnisordner werden nicht automatisch überschrieben. Für einen neuen Lauf den alten Fallordner umbenennen/archivieren. Der Workflow **Thermal sauna CFD** baut die Randbedingung einmal und rechnet die acht Fälle mit maximal vier parallelen Jobs. Er läuft bei Änderungen an relevanter CAD-Geometrie, Solver, Tests oder Konfiguration sowie manuell. Artefakte werden 14 Tage aufbewahrt; ein neuer Lauf derselben Branch ersetzt eine noch laufende ältere Rechnung.

## Noch nicht enthalten

Aufguss, Wasserdampf, Kondensation, CO₂-Produktion, Personenwärme, realer Thermostat-/Sensorbetrieb, Wärmeaufnahme von Holz und Steinen beim Aufheizen, poröse Durchströmung des Steinkorbs, detaillierte Lamellen-/Düsenströmung, Wind und Ventilatorkennlinie. Für diese Aspekte darf aus der trockenen stationären Rechnung keine Aussage abgeleitet werden. Experimentelle Validierung steht aus; die offenen Punkte werden in [Issue #8](https://github.com/42tg/Gartensauna/issues/8) weitergeführt.

## Primärquellen

- [OpenCFD: buoyantSimpleFoam](https://doc.openfoam.com/2306/tools/processing/solvers/rtm/heat-transfer/buoyantSimpleFoam/)
- [OpenCFD: thermische Wandrandbedingung](https://doc.openfoam.com/2306/tools/processing/boundary-conditions/rtm/derived/thermal/externalWallHeatFluxTemperature/)
- [OpenCFD: greyDiffusiveRadiation](https://doc.openfoam.com/2306/tools/processing/boundary-conditions/rtm/derived/thermal/greyDiffusiveRadiation/)
- Maßgeblich für die verwendete Implementierung ist der v1912.200626-Quellcode, dessen Archiv und Hash im Buildskript fixiert sind, einschließlich `buoyantKEpsilon` und der thermischen Randbedingung. Neuere Online-Dokumentation kann sich in Details unterscheiden.
