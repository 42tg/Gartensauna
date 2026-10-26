# Konkretisierter Hüllaufbau V3.1

Stand 26.10.2026. Planungsannahmen auf Nutzerwunsch konkretisiert, keine Ausführungsfreigabe. Gemeinsame Parameter: `cad/envelope.scad`.

## Außenwand, innen nach außen

| Lage | Dicke mm |
|---|---:|
| Saunaholz, horizontal | 19 |
| Luftzwischenraum / vertikale Lattung | 20 |
| Saunageeignete Alu-Dampfsperre | 0,1 |
| Holzständer und geeignete Mineralwolle gemeinsam | 100 |
| Diffusionsoffene Winddichtung, Modellreserve | 0,9 |
| Diffusionsoffene Außenplatte, Produkt/Aussteifung offen | 15 |
| Vertikale Hinterlüftung / Lattung | 30 |
| Horizontale Holzfassade | 20 |
| **Summe** | **205** |

Die Bahndicken sind CAD-Reserven, keine Produktspezifikation. Ständer und Dämmung teilen sich eine Zone. Horizontale Bretter auf vertikalen Latten ermöglichen durchgehende vertikale Luftwege. Lüftungsöffnungen, Insektenschutz und Fenster-/Sockelanschlüsse müssen noch konstruiert werden. Außenplatte nicht pauschal durch OSB ersetzen; Material und Feuchteverhalten des Gesamtaufbaus prüfen. Die Trennwand bleibt ein gesonderter geometrischer Platzhalter (307,5 mm), nicht dieser Außenwandaufbau.

## Decke / Dach, unten nach oben

15 mm Holz + 20 mm Luft/Lattung + 0,1 mm Alu + 160 mm Balken/Dämmung + 0,9 mm diffusionsoffene Windlage + 60 mm reservierte Dachlüftung + 22 mm Dachschalung + 3 mm Dachhaut = **281 mm**.

Die 160 mm Dämmung sind ein Planungsansatz, kein statisch bemessener Balkenquerschnitt. Das CAD zeigt weiterhin eine horizontale Hülle. Dachgefälle, Entwässerung, Belüftungsöffnungen und Anschluss an die L-Ecke sind offen; die 60-mm-Zone ist noch kein funktionierender Lüftungsnachweis. Der Dachrand ist schematisch geschlossen. Innenhöhe bleibt 2400 mm; Dachoberkante steigt auf 2681 mm über Fertigboden, zuzüglich späterem Gefälle. Bodenunterseite bei -120 mm, Auflagerunterkante bei -300 mm; Gelände-/Fundamentbezug offen.

## Maßfolgen bei unverändertem Außenumriss

| Merkmal | V3.1 |
|---|---:|
| Umriss | 3200 × 3700 mm, L-Form |
| Saunaflügel außen | 2000 mm breit |
| Saunabreite zwischen geschlossenen Innenwänden | 1590 mm |
| Saunalänge zwischen Stirnwänden | 3290 mm |
| Liegeflächen | 2 × 600 × 2100 mm |
| Gang zwischen Fensterrahmen und unterer Bank | 520 mm |
| Rückwärtige Standfläche | 645 mm |
| Freier Zugang hinter Bankende innerhalb Türöffnung | 600 mm |
| Engstelle neben Trennwand, nicht regulärer Zugang | 360 mm |
| Umkleide lichte Rechteckfläche | 892,5 × 1290 mm |

Bänke y=-1250..850 mm, obere Bank x=2385..2985, untere x=1765..2365. Der reguläre Zugang erfolgt hinter den Bänken. Umkleide bleibt eng; Türrahmen, Anschlag und Bewegungsfläche sind noch nicht vollständig modelliert. Außenöffnung 850 mm auf x=225..1075 verschoben, damit sie nicht mehr in die Trennwand schneidet; verbleibende Pfostenbreiten sind statisch ungeprüft.

Ofen wandert mit der Stirnwand 25 mm nach innen: Montageebene y=-1795, x-Mitte=1700, Unterkante=310 mm. Konservative Abstände: Rahmen 260 mm, Glas 274 mm, untere Bank 210 mm, obere Bank 490 mm, Decke 1500 mm, Boden 310 mm. Diese Modellhüllen werden in CI geprüft. Ofenschutz und Befestigung fehlen weiterhin.

Das geschlossene innere Rechteck hat ca. 12,55 m³; die zusätzliche Nische an der dünneren Glasfront bringt den Raum auf ca. 13,24 m³ (ohne Türnische). Mit dem bisherigen Glaszuschlag von ca. 4,50 m³ liegt der Auslegungswert näherungsweise bei 17,74 m³. DROP 9 bleibt deshalb nur Formreferenz, nicht ausgewähltes Heizgerät (Herstellerbereich bis 13 m³).

## Boden und offene Nachweise

Der Boden bleibt ein 120-mm-Platzhalter: 12 mm Unterplatte, 88 mm Balken/Dämmung und 20 mm Dielen. Feuchteabdichtung, wasserbeständiger Oberbelag, Wandanschluss und Gründung sind noch zu planen. Ebenfalls offen: Trennwandaufbau, geschlossene Dampfsperrenanschlüsse an Wand/Decke/Glas, Tragwerk über der Glasfront, Bankaufstieg und Lüftung. Siehe Issues #3, #4 und #6.

## Quellen

- HUUM, Hüllaufbau und mindestens 20 mm Luft hinter Innenholz, geprüft 26.10.2026: https://huum.eu/sauna-building-envelope-structures-how-to-build-a-durable-and-moisture-resistant-sauna-room/
- HUUM DROP, Maße und Gerätebereich: https://huum.eu/product/drop-electric-sauna-heater/
- Montageabstände: https://huum.eu/wp-content/uploads/2026/01/DROP_2_0_User_Manual_EU_v6_WEB.pdf

Die angegebenen Wand-/Dachdicken sind unsere Planungswahl und keine vollständige Herstellervorgabe.
