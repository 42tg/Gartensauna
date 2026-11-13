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

Die Bahndicken sind CAD-Reserven, keine Produktspezifikation. Ständer und Dämmung teilen sich eine Zone. Horizontale Bretter auf vertikalen Latten ermöglichen durchgehende vertikale Luftwege. Lüftungsöffnungen, Insektenschutz und Fenster-/Sockelanschlüsse müssen noch konstruiert werden. Außenplatte nicht pauschal durch OSB ersetzen; Material und Feuchteverhalten des Gesamtaufbaus prüfen. Die Trennwand erhält einen gesonderten Planungsaufbau von **128,1 mm**: 19 mm Vorraumholz + 70 mm Ständer/Dämmung + 0,1 mm Dampfsperre auf der heißen Seite + 20 mm Lattung/Luft + 19 mm Saunaholz. Keine Tragwerks- oder Feuchteschutzfreigabe. Vorraumseite x=1605 mm bündig mit Flügel-/Glasrahmenbeginn.

## Decke / Dach, unten nach oben

15 mm Holz + 20 mm Luft/Lattung + 0,1 mm Alu + 160 mm Balken/Dämmung + 0,9 mm diffusionsoffene Windlage + 60 mm reservierte Dachlüftung + 22 mm Dachschalung + 3 mm Dachhaut = **281 mm**.

Die 160 mm Dämmung sind ein Planungsansatz, kein statisch bemessener Balkenquerschnitt. Das CAD zeigt weiterhin eine horizontale Hülle. Dachgefälle, Entwässerung, Belüftungsöffnungen und Anschluss an die L-Ecke sind offen; die 60-mm-Zone ist noch kein funktionierender Lüftungsnachweis. Der Dachrand ist schematisch geschlossen. Lichte Innenhöhe ist seit Entscheidung 0012 auf 2200 mm festgelegt; Dachoberkante liegt auf 2481 mm über Fertigboden, zuzüglich späterem Gefälle. Bodenunterseite bei -120 mm, Auflagerunterkante bei -300 mm; Gelände-/Fundamentbezug offen.

## Aktuelle Maßfolgen (ADR 0012 und 0013; vorläufig bis Aufmaß)

| Merkmal | V3.1 |
|---|---:|
| Umriss | 3605 × 3700 mm, L-Form |
| Saunaflügel außen | 2000 mm breit |
| Saunabreite hinten / vor Glasrahmen | 1666,9 / 1750 mm |
| Saunalänge zwischen Stirnwänden | 3290 mm |
| Liegeflächen | 2 × 600 × 2100 mm |
| Gang zwischen Fensterrahmen und unterer Bank | 520 mm |
| Rückwärtige Standfläche | 675 mm |
| Freier Zugang hinter Bankende innerhalb Türöffnung | 600 mm |
| Engstelle neben Trennwand, nicht regulärer Zugang | 436,9 mm |
| Umkleide lichte Rechteckfläche | 1400 × 1290 mm |

Bänke y=-1280..820 mm, obere Bank x=2790..3390, untere x=2170..2770. Zugang hinter den Bänken; 675 mm bis zur Rückwand. Vorraum 1400 × 1290 mm. Trennwand 128,1 mm, lichte Zargenöffnungen 800 × 2000 mm. Mit um 90° geöffneten Türblättern bleiben 793 mm (Sauna) und 767 mm (außen). Öffnung und 600-mm-Prüfkörperroute werden gegen einen tatsächlichen CAD-Wandschnitt geprüft. Türprodukte, Fälze, Dichtungen und Beschläge bleiben unbestimmt.

Ofenmitte x=2105, Montageebene y=-1795, Unterkante=310 mm. Konservative Modellhüllen: Rahmen 260, Glas 274, untere Bank 180, obere Bank rund 522, Decke 1300, Boden 310 mm. Der Render-Prüfer berechnet diese aus den tatsächlichen exportierten STL-Hüllen. Ofenschutz und Befestigung fehlen.

Saunagrundfläche ohne Türnische 5,6333 m²; bei 2200 mm Höhe 12,3932 m³. Mit 0,2066 m³ Türnischenzuschlag und 5,6806 m² sichtbarem Glas (Front **und Tür**) ergeben sich nach HUUMs 1-m³/m²-Ansatz **18,28 m³ Auslegungsvolumen**. DROP bis 13 m³ ist dafür zu klein; nur Formreferenz. Vollständige Rechnung: [Realitätscheck](../reality-check-2026-11-13.md).

## Boden und offene Nachweise

Der Boden bleibt ein 120-mm-Platzhalter: 12 mm Unterplatte, 88 mm Balken/Dämmung und 20 mm Dielen. Feuchteabdichtung, wasserbeständiger Oberbelag, Wandanschluss und Gründung sind noch zu planen. Ebenfalls offen: Bestätigung des Trennwandaufbaus, geschlossene Dampfsperrenanschlüsse an Wand/Decke/Glas, Tragwerk über der Glasfront, Bankaufstieg und Lüftung. Siehe Issues #3, #4 und #6.

## Quellen

- HUUM, Hüllaufbau und mindestens 20 mm Luft hinter Innenholz, geprüft 26.10.2026: https://huum.eu/sauna-building-envelope-structures-how-to-build-a-durable-and-moisture-resistant-sauna-room/
- HUUM DROP, Maße und Gerätebereich: https://huum.eu/product/drop-electric-sauna-heater/
- Montageabstände: https://huum.eu/wp-content/uploads/2026/01/DROP_2_0_User_Manual_EU_v6_WEB.pdf

Die angegebenen Wand-/Dachdicken sind unsere Planungswahl und keine vollständige Herstellervorgabe.
