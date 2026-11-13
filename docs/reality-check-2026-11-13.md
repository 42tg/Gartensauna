# Realitätscheck des Sauna-Neubaus – 13.11.2026

**Ergebnis: Geometrie korrigiert und nachgerechnet; noch kein baureifer Entwurf.** Beide Türen sind enthalten. Bankaufstieg, Ofenauswahl und bauliche Nachweise bleiben echte offene Punkte.

## Grundlage und Verlässlichkeit

- Bestandsaufmaß ungefähr 3200 × 1700 × 1930 mm; der alte Schuppen wird abgerissen. Video/Punktwolke liefern räumliche Orientierung, keinen unabhängigen Millimeternachweis. Die Scan-Skalierung wird nicht an den größeren Neubau angepasst.
- Nutzerfestlegung: lichte Innenhöhe 2200 mm; Vorraumbreite vorläufig 1400 mm bis Nachmessung. Zwei getrennte Liegen, Glasfront zum Garten.
- Planungsannahmen: rechter Flügel 2000 mm außen breit, 2000 mm zusätzliche Tiefe; Außenwand 205 mm, neue Trennwand 128,1 mm. Keine dieser Schichtannahmen ist statisch/hygrothermisch freigegeben.
- Rechenquelle: durch OpenSCAD ausgewertete Parameter und tatsächlicher CAD-Wandschnitt, `scripts/audit_layout.py`. STL-Bauteile und Ofenabstände zusätzlich durch `scripts/verify_render.py`. Reproduktion: `python scripts/audit_layout.py` (Shapely erforderlich).

## Korrigierte Maße

| Punkt | Ergebnis / Rechnung | Status |
|---|---|---|
| Trennwand | 19 + 70 + 0,1 + 20 + 19 = **128,1 mm**, vorher 307,5 mm | Planungsaufbau; kein dimensionsloser Restkörper mehr |
| Bündigkeit | Vorraumseite und Beginn Saunaflügel bei x=1605 mm | Im CAD bestätigt |
| Neubau außen | 205 + 1400 + 2000 = **3605 mm** breit, **3700 mm** Gesamttiefe | Aufstellfläche noch messen |
| Dachhülle | ca. **3765 × 3860 mm** mit 80-mm-Überstand | Noch ohne Gefälle/Entwässerung |
| Vorraum innen | **1400 × 1290 mm**, 1,806 m² | CAD; 1400 noch vorläufig |
| Saunabreite | vorn 1750 mm, hinten 1666,9 mm | Unterschied durch Glasrahmen/Trennwand |
| Innenhöhe | **2200 mm** | Fertigboden bis fertige Deckenunterkante |
| Dachoberkante | 2200 + 281 = **2481 mm** über Fertigboden | Keine Höhe über Gelände |
| Stehhöhenreserve bei 1870 mm Körpergröße | **330 mm** | Geometrisch |
| Liegen | zweimal **600 × 2100 mm**, Oberkanten 535 / 975 mm | Beide vollständig frei; 230 mm Längenreserve für 1870 mm |
| Abstand obere Liege–Decke | **1225 mm** | Liegt im HUUM-Orientierungsbereich 1100–1300 mm |
| Hinterer Zugang | **675 mm** bis Rückwand | Bänke um 30 mm nach vorn verschoben |
| Gang am Glas / neben Trennwand | **520 / 436,9 mm** | Eng; regulärer Einstieg erfolgt hinten |

Außerdem wurde eine **160-mm-Lücke an der vorderen Glas-/Wandecke** geschlossen. Das korrigiert den Modellumriss; ein fachgerechter Glasanschluss ist damit noch nicht konstruiert.

## Beide Türen einschließlich Bewegung

| Merkmal | Saunatür | Außentür |
|---|---|---|
| Öffnungsrichtung | Aus Sauna in Vorraum | Aus Vorraum ins Freie |
| Anschlag | Hinten, nahe Rückwand | Links, von außen in den Grundriss blickend; maßgebend CAD |
| Zargenöffnung nominal | 800 × 2000 mm | 800 × 2000 mm |
| Rohöffnung im Modell | 880 × 2040 mm | 880 × 2040 mm |
| Blatt | 794 × 1977 × 8 mm Glas | 794 × 1987 × 60 mm |
| Bodenspalt | 20 mm | 10 mm |
| Freie Breite mit Blatt bei 90° | **793 mm** | **767 mm** |
| Kopffreiheit bei 1870 mm Körpergröße | 130 mm | 130 mm |
| Griffe | Beidseitige Holzgriffe, keine Verriegelung | Beidseitiger Griffproxy |

**Dies sind noch keine bestellbaren Türspezifikationen.** Beispiel: Harvia DA92104 hat als reales 9×21-Element 890 × 2090 × 60 mm und 8-mm-Sicherheitsglas. Es passt nicht unverändert in unsere 880 × 2040-mm-Rohöffnung. Vor Bestellung Produkt wählen, Rohöffnung/Zarge/Falz/Spalte/Bänder/Glas und Schwelle danach anpassen und Prüfung erneut laufen lassen. Die aktuelle tiefe Zarge ist eine vereinfachte Laibungsdarstellung, kein Nachbau dieses Produkts.

Prüfung: 0–90° in 0,05°-Schritten, einschließlich beidseitiger Griffe. Von jedem Stichprobenabstand wird eine konservative maximale Bewegung zwischen zwei Schritten abgezogen (r·Δwinkel/2, rund 0,35 mm). Kein Kontakt mit Wänden, Zargen, Glasrahmen, Stuhl oder Liegen. Kleinster bestätigter Abstand zum Stuhl beim Saunatürschwenk etwa **85,6 mm**. Beide Türbewegungsräume sind voneinander getrennt.

Direkt an den Zargen bleiben im vereinfachten Schwenkmodell nur ca. **2,8 mm** (Sauna) bzw. **0,6 mm** (außen) garantierter Abstand. Das ist **kein Einbautoleranznachweis**: konkrete Beschlagkinematik, Dichtungen und Falz fehlen. Die Bänder sind schematische Drehachsen, ihre Verschraubung ist nicht modelliert.

Bei beiden auf 90° geöffneten Türen lässt sich ein **600-mm-Kreisprüfkörper** ohne Überschneidung von außen durch den Vorraum bis hinter die Bänke führen. Die engste Stelle wird exakt erreicht, ohne zusätzliche Toleranzreserve. Dieser Test ist weder Barrierefreiheitsnachweis noch Zusicherung bequemen Umziehens. Er gilt nicht für den 520-mm-Gang an der Glasfront. Die Außenbewegung bis etwa 0,83 m vor die Fassade muss am Standort frei bleiben.

## Ofen und Raumvolumen

Lichte Grundfläche ohne Türnische:

`1,750 × 1,795 + 1,6669 × 1,495 = 5,6332655 m²`

`5,6332655 × 2,200 = 12,3931841 m³`

Zusätzlicher geometrischer Türnischenansatz bis zur geschlossenen Glasscheibe:

`0,1291 × 0,800 × 2,000 = 0,20656 m³`

Raumansatz insgesamt **12,5997 m³**. Möbel werden für die Ofenauswahl nicht vom Raumvolumen abgezogen. Kleine Falz-/Beschlagvolumina werden vernachlässigt.

Glasfront `1,930 × 2,130 = 4,1109 m²`; Saunatür `0,794 × 1,977 = 1,569738 m²`; zusammen **5,680638 m²**. Nach HUUMs pauschalem Zuschlag von 1 m³ je m² ungedämmter Glasfläche:

`12,5997441 + 5,680638 = 18,2803821 m³`

**Auslegungsorientierung rund 18,3 m³.** Der Zuschlag wird mangels spezifiziertem Glasaufbau konservativ auf beide Glasflächen angewandt; kein Ersatz für eine Wärmeverlustrechnung. DROP 9 ist im geprüften EU-Handbuch nur für **8–13 m³** angegeben (Nennleistung dort 8,5 kW). Er bleibt **zu klein und nur Formreferenz**. Ein stärkerer Ofen kann andere Abstände und Abmessungen benötigen; die jetzige Platzierung darf nicht ungeprüft übernommen werden.

Für die jetzige DROP-Hülle: Rahmen 260 mm, Glas 274 mm, untere Bank 180 mm, obere Bank rund 522 mm, Boden 310 mm, Decke 1300 mm. Geprüft gegen konservativ 150 mm horizontal, 310 mm Boden und 1200 mm Decke. Die Wandmontagefläche ist bestimmungsgemäß angrenzend; Befestigung, Sensor, Berührungsschutz und Elektroinstallation bleiben offen.

## Lüftung und Hülle

- Sechs Luftwechsel pro Stunde auf dem obigen Raumansatz ergeben **75,6 m³/h**; der bisherige Ansatz 80 m³/h entspricht rechnerisch **6,35/h**. Das ist ein Sollvolumenstrom, kein Nachweis des realen Ventilators.
- Versorgungsgitter 150 × 80 mm mit 7-mm-Lamellen bei 20-mm-Teilung: vereinfachte freie Fläche 7800 mm²; bei 80 m³/h mittlere Geschwindigkeit etwa 2,85 m/s. Abluft 300 × 160 mm entsprechend 31200 mm² und 0,71 m/s. Gitterdruckverlust, Geräusch, Leitungen und Ventilatorkennlinie fehlen.
- Zuluftöffnung z=1080..1160 mm über dem 900-mm-Ofenoberende; Abluft z=220..380 mm gegenüber, Trocknungsöffnung unter der Decke. Holzständer-/Lattenkollisionen werden gegen CAD geprüft. Hersteller-Sensorposition und konkrete Lüftungsanlage noch abgleichen.
- Frühere thermische CFD- und Aufheizergebnisse sind **kein Nachweis für diesen geänderten Entwurf**. Der automatisierte isotherme Vergleich wird mit der aktuellen Geometrie wiederholt; Ofenauswahl und neue thermische Randbedingungen sind Voraussetzung für eine belastbare Heizsimulation.
- Außenwand 205 mm, Trennwand 128,1 mm, Dach 281 mm und Boden 120 mm sind plausible geometrische Schichtansätze, aber ohne Produktkennwerte kein U-Wert-/Tauwasser-/Trocknungsnachweis.
- Bodenabdichtung/Sockel fehlen. Das Holz ist noch bis zum Boden gezeichnet; der im DROP-Handbuch beschriebene Feuchteschutzabstand und Deckenanschluss sind nicht als fertiges Baudetail umgesetzt. Dachgefälle, Lüftungsöffnungen und Entwässerung fehlen ebenfalls.

## Bankaufstieg: weiterhin nicht gelöst

535 mm vom Boden auf die untere Liege und weitere 440 mm nach oben sind keine vernünftige ausgearbeitete Treppe. Ein zusätzliches 300-mm-Trittbrett in der hinteren 675-mm-Standfläche ließe nur 375 mm Durchgang; ein 260-mm-Tritt im 520-mm-Seitengang halbierte diesen. Deshalb wurde kein zufälliger Hocker als scheinbare Lösung eingezeichnet. Hier muss die Bank-/Treppengeometrie konkret überarbeitet werden, ohne Türweg, zwei Liegeflächen oder Ofenabstand zu opfern.

## Vorläufige Mengengrundlage

| Position | Geometrischer Ansatz, ohne Verschnitt/Bestellung |
|---|---:|
| Boden-/Deckengrundriss | 3605×1700 + 2000×2000 = **10,1285 m²** |
| Außenumfang | **14,61 m** |
| Dachfläche einschließlich 80-mm-Überstand | etwa **11,32 m²**, horizontaler Ansatz |
| Brutto-Außenwandflächen | 14,61×2,2 = **32,142 m²** |
| Außenwand nach nominaler Glasöffnung, Außentür und 3 Lüftungsöffnungen | ca. **25,84 m²**; Anschlussdetails/Ecküberdeckungen nicht abgezogen |
| Trennwand je Seite, ohne Rohöffnung | 1,495×2,2 − 0,880×2,040 = **1,4938 m²** |
| Liegeoberflächen | **2,52 m²** vor Lamellenfugen |

Keine Stückliste zum Einkauf: Pfostenraster, Stürze, Lastabtragung über Glas, Befestigungen, Zuschnitt und Verschnitt müssen erst bemessen werden. Der schematische 900-mm-Fundamentraster ist kein Tragfähigkeitsnachweis.

## Quellen und offene Entscheidungen

Herstellerunterlagen am 13.11.2026 eingesehen:

- [HUUM DROP EU-Handbuch](https://huum.eu/wp-content/uploads/2026/01/DROP_2_0_User_Manual_EU_v6_WEB.pdf), Tabelle 1, Abstandsskizze und Abschnitte Sauna Room / Ventilation: Gerätebereich, Glaszuschlag, Abstände und Höhenorientierung.
- [Harvia DA92104](https://www.harvia.com/en/products/DA92104/glass-door-clear-9x21-aluminum-frame): tatsächliche Außenmaße 890 × 2090 × 60 mm, 8-mm-Sicherheitsglas; ausdrücklich nur Produktvergleich.
- [Tylö Kiruna Montagehandbuch](https://tylo.com/hubfs/TYLO%20US/Tylo-US%20Manuals/71-0185_Tylo_Kiruna_1_2_IG%20S-810_820_Manual_Rev_C_09-26-2024.pdf): nach außen öffnende Saunatür ohne mechanische Verriegelung als Gestaltungsgrundsatz; kein deutscher Normnachweis.

Offen bleiben Aufmaß einschließlich Außentürbewegung, Tür-/Glasprodukte, Bankaufstieg, größerer Ofen, Statik/Gründung, Feuchteschutz und Elektro. Geometrisch bestandene Tests dürfen nicht als Bau- oder Montagefreigabe bezeichnet werden.
