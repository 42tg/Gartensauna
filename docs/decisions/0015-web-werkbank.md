# ADR 0015 – Interaktive Web-Werkbank

Datum: 14.11.2026. Status: umgesetzt auf Nutzerwunsch.

Zeichnungen, Explosionsmodell und Umgebungsscan werden in drei Tabs bereitgestellt.
OpenSCAD bleibt geometrische Quelle. Blender-Szenen werden als GLB exportiert;
Browsermaterialien sind eine vereinfachte Darstellung. Der Viewer verändert keine
Konstruktionsmaße. Die Scanregistrierung bleibt vorläufig und getrennt vom Neubau.

Der Quellcode liegt direkt auf main. Private Scandaten bleiben außerhalb des
öffentlichen GitHub-Repositories und werden nur mit der privaten Site bereitgestellt.
Der Renderworkflow liefert einen reproduzierbaren CAD-Viewer als zusätzliches
Artefakt; die private Veröffentlichung erfolgt separat.
