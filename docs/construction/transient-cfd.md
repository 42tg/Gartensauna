# Zeitabhängige Strömung mit zeitlicher Mittelung

Die stationäre Auftriebsrechnung erfüllte die Geschwindigkeitsprüfung nicht. Diese Erweiterung verwendet OpenCFD v1912 `buoyantPimpleFoam` mit physikalischer Zeit: ideale Gasdichte, `buoyantKEpsilon`-URANS, Oberflächenstrahlung und dieselben Wärme-/Lüftungsrandbedingungen wie die [thermische Rechnung](thermal-cfd.md). Das CAD und das ursprüngliche orthogonale Rechengitter bleiben unverändert.

## Versuch und Mittelung

- Ein endliches, vorgewärmtes Feld aus der stationären Rechnung dient ausschließlich als Initialisierung. Es wird nicht als konvergiert vorausgesetzt. Die physischen Zeitskalen beginnen wieder bei 0 s; die alte numerische Leistungsrampe wird deaktiviert, sodass tatsächlich konstant 3000 W anliegen.
- Geplanter Zeitraum: 0–300 s. Mittelung: 100–300 s. Die ersten 100 s sind eine anfänglich gewählte Einschwingphase; die Prüfung der beiden Fensterhälften entscheidet, ob die Mittelwerte bereits ausreichend stabil sind.
- Implizite Euler-Zeitdiskretisierung, PISO als Sonderfall von PIMPLE mit einem äußeren und zwei Druckkorrekturschritten; keine künstliche stationäre Unterrelaxation der Gleichungen.
- Basis: adaptive Schritte mit `maxCo=5`, `maxDeltaT=0.05 s`. Kontrolllauf: **beide** Grenzen halbiert. Der hohe lokale Courant-Wert liegt in sehr dünnen Zellen; seine Eignung wird ausdrücklich durch den kleineren Zeitschritt geprüft, nicht aus impliziter Stabilität abgeleitet. Die tatsächlichen Schritte und Courant-Werte stehen im Solverlog.
- Ausgabefelder alle 5 s; die Zeitintegration der Strömung erfolgt wesentlich feiner. Die Mittelung verwendet Trapezgewichte der tatsächlichen Ausgabezeiten und interpoliert Fenstergrenzen. Ein arithmetischer Mittelwert über ungleich große Zeitschritte wäre falsch.
- Mittelwerte der ersten und zweiten Fensterhälfte werden räumlich verglichen. Die gleiche Auswertung aus jedem zweiten gespeicherten Feld prüft die Empfindlichkeit gegenüber dem Ausgabeabstand.

Die Feldpfeile zeigen den zeitlichen Mittelwert des Geschwindigkeitsvektors. Der mittlere Geschwindigkeitsbetrag in der Tabelle wird **vor** der Mittelung gebildet; gegenläufige Bewegungen heben sich dort nicht auf. Räumliche Temperatur-P10/P90 beziehen sich auf das zeitgemittelte Feld. URANS löst nicht alle turbulenten Wirbel auf.

## Bilanzen und Freigaben

Für einen instationären Kontrollraum gelten:

- Masse: Netto-Massenausfluss plus zeitliche Änderung der Luftmasse muss null ergeben. Lokal wird dieselbe Bilanz je Zelle geprüft.
- Energie: Ofenwärme minus Wärmeabgabe minus Änderung der im Luftvolumen gespeicherten inneren, kinetischen und potentiellen Energie muss null ergeben. An Öffnungen werden Enthalpie, kinetische/potentielle Energie, Strahlung und Wärmeleitung bilanziert.

Die Mittelungsprüfung verwendet die bestehenden Bilanzgrenzen (globale Masse 0,5 %, lokale Masse 2 %, Wärme 5 %, Oberflächenbilanz 5 %, Strahlung 2 %). Hinzu kommen maximal 0,5 K bzw. 0,01 m/s Unterschied zwischen den gemittelten Feldhälften, maximal 0,1 K Einfluss des verdoppelten Ausgabeabstands und mindestens 100 s Mittelungsdauer. Der geplante Endzeitpunkt muss erreicht sein.

`transient_compare.py` verlangt gleiche Geometrie, physische Parameter, Anfangsfelder und Zeitfenster sowie halbierte Schrittgrenzen. Beide Fenster müssen die Prüfungen bestehen; die mittleren Felder dürfen sich höchstens um 0,5 K und 0,01 m/s unterscheiden. Das ist eine begrenzte numerische Prüfung, **keine Messvalidierung, räumliche Gitterunabhängigkeit oder statistische Konfidenzgarantie**.

## Luftalter separat prüfen

Der Luftaltertransport wird nachträglich aus den gespeicherten Massenflüssen implizit zeitabhängig gelöst, einschließlich der veränderlichen Luftmasse pro Zelle. Zwei Anfangsfelder laufen mit: ein aus dem Startströmungsfeld berechnetes stationäres Luftalter und null. Ihr verbleibender Unterschied zeigt den Einfluss der Initialisierung. Bei mehr als 5 % Unterschied wird das Luftalter nicht als freigegebener Vergleichswert verwendet – auch wenn Temperatur und Strömungsmittel bereits stabil sind. Für eine Sauna mit mehreren Minuten Masseverweilzeit kann diese Prüfung deutlich mehr physikalische Zeit benötigen.

## Ausführen

Voraussetzungen und Bau der Randbedingungsbibliothek: [thermische CFD](thermal-cfd.md#reproduzieren).

```sh
python scripts/run_transient.py --seed build/thermal/thermal_planned --dest build/transient/planned --end 300 --sample 5 --max-co 5 --max-dt .05 --outer 1
python scripts/run_transient.py --seed build/thermal/thermal_planned --dest build/transient/half-step --end 300 --sample 5 --max-co 2.5 --max-dt .025 --outer 1
python scripts/transient_results.py build/transient/planned --start 100
python scripts/transient_results.py build/transient/half-step --start 100
python scripts/transient_compare.py build/transient/planned build/transient/half-step --require-quality
```

Ausgaben: `transient_mean.png`, `transient_history.png`, `mean_fields.npz`, `transient_results.json`, `time_series.json` und gemeinsamer Vergleichsbericht. Mit installiertem `openmpi-bin` verteilt `--ranks 4` die Rechnung auf vier Prozesse und rekonstruiert danach die vollständigen Felder. Die ursprünglichen Einzelfelder bleiben lokal erhalten. `transient.json` dokumentiert Anfangsfeld-Hashes und Rechenparameter.

Der manuell startbare Workflow **Transient sauna CFD** erzeugt ein gemeinsames warmes Anfangsfeld und rechnet beide Zeitauflösungen. Wegen Rechenzeit und Speicherbedarf läuft er nicht bei jedem Push. Seed-Artefakte bleiben einen Tag, verdichtete Einzelergebnisse drei Tage und der Vergleich sieben Tage erhalten. Die zahlreichen Roh-Zeitschrittordner werden nicht zusätzlich als Actions-Artefakt gespeichert.

Die Simulation bleibt ein trockenes Luftmodell mit vereinfachter Ofenhülle und vorgewärmtem Anfangsfeld. Sie sagt weder die reale Aufheizzeit von Holz/Steinen noch Aufguss-/Feuchteverhalten voraus. Die Annahmen zur Wärmeleistung und zu den Hüllverlusten gelten unverändert.

Primärquelle: [OpenCFD buoyantPimpleFoam](https://doc.openfoam.com/2212/tools/processing/solvers/rtm/heat-transfer/buoyantPimpleFoam/); für das tatsächliche Verhalten maßgeblich ist der im Projekt gepinnte v1912-Quellcode.
