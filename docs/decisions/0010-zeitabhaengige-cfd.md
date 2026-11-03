# ADR 0010: Zeitabhängige Auftriebsrechnung und getrennte Mittelungsprüfung

Status: implementiert, numerische Resultate gesondert prüfen. Datum: 03.11.2026.

## Anlass

Der stationäre Auftriebsfall blieb nach 8000 SIMPLE-Iterationen schwankend. Weitere Iterationen allein ergaben keinen freigegebenen Vergleichswert.

## Entscheidung

Zusätzlicher physikalisch zeitabhängiger `buoyantPimpleFoam`-Lauf auf unveränderter CAD-Hüllgeometrie. Zeitgewichtete Feldmittel, Massen-/Energiebilanzen einschließlich Speicherung und identischer Kontrolllauf mit halbierten Zeitschrittgrenzen. Temperatur-/Strömungsmittel und das langsamer einschwingende Luftalter erhalten getrennte Prüfungen.

## Konsequenzen

Höhere Rechenkosten; der neue GitHub-Workflow wird nur manuell gestartet. Ein numerisch bestandenes Zeitfenster ist keine Bau- oder physische Modellfreigabe. Reproduzierbarkeit, Rechenparameter und Initialisierung werden mit den Ergebnissen gespeichert. Details: [zeitabhängige CFD](../construction/transient-cfd.md).
