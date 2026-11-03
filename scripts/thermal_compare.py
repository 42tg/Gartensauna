#!/usr/bin/env python3
"""Publish explicit quality gates; never silently rank unconverged runs."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',default='build/thermal');args=p.parse_args()
    cfg=json.loads((ROOT/'simulation/thermal/config.json').read_text());wanted=[c['name'] for c in cfg['cases']]
    reports={}
    for path in (ROOT/args.root).glob('*/results.json'):
        r=json.loads(path.read_text())
        if r['case'] in wanted:reports[r['case']]=r
    out=ROOT/'build/thermal-comparison';out.mkdir(parents=True,exist_ok=True)
    lines=['# Thermische Sauna-CFD','',
        'Idealgas-RANS, Wärmeauftrieb und Oberflächenstrahlung. Szenarien, keine gemessenen Betriebswerte. Nur Fälle mit erfüllten Qualitätskriterien vergleichen.','',
        '| Fall | Numerik | obere / untere Bank °C | Luftalterfaktor ↓ | P95 Luftalter min | Aufwärtsgeschwindigkeit am Ofen m/s | Energiebilanzfehler % |',
        '|---|---|---:|---:|---:|---:|---:|']
    for name in wanted:
        if name not in reports:lines.append(f'| {name} | FEHLT / ABGEBROCHEN | — | — | — | — | — |');continue
        r=reports[name];quality='bestanden' if r['quality_pass'] else '**NICHT KONVERGIERT**'
        temps=f"{r['regions']['upper']['temperature_mean_C']:.1f} / {r['regions']['lower']['temperature_mean_C']:.1f}"
        factor=f"{r['occupied_age_factor']:.3f}" if r['quality_pass'] else 'nicht freigegeben'
        lines.append(f"| {name} | {quality} | {temps} | {factor} | {r['occupied_p95_age_min']:.1f} | {r['plume_mean_vertical_velocity_m_s']:.3f} | {100*r['energy_balance_relative']:.2f} |")
    checks={}
    baseline=reports.get('thermal_planned')
    if baseline and baseline['quality_pass']:
        for name in ('thermal_no_gravity','thermal_fine','thermal_radiation_fine','thermal_near_heater','thermal_high_exhaust'):
            r=reports.get(name)
            if r and r['quality_pass']:
                checks[name]={'upper_temperature_difference_K':r['regions']['upper']['temperature_mean_C']-baseline['regions']['upper']['temperature_mean_C'],
                    'air_age_factor_relative_change':r['occupied_age_factor']/baseline['occupied_age_factor']-1,
                    'plume_vertical_velocity_difference_m_s':r['plume_mean_vertical_velocity_m_s']-baseline['plume_mean_vertical_velocity_m_s']}
        lines+=['','## Empfindlichkeit gegenüber Gitter und Strahlungsauflösung','']
        for name in ('thermal_fine','thermal_radiation_fine'):
            if name in checks:
                v=checks[name];lines.append(f"- {name}: obere Bank {v['upper_temperature_difference_K']:+.2f} K; Luftalterfaktor {100*v['air_age_factor_relative_change']:+.1f} % gegenüber Basis.")
            else:lines.append(f'- {name}: noch kein qualifizierter Vergleich verfügbar.')
    lines+=['','## Grenzen','',
        'Stationäre Rechnung, keine Aufheizzeit, kein Aufguss/Feuchtetransport und keine thermische Speicherung in Holz/Steinen. Ofen und Bänke sind vereinfachte geschlossene CAD-Hüllen. Wärmeverluste, mittlere Heizleistung und Oberflächenemissivität sind Annahmen. Zwei Gitter und zwei Winkelauflösungen sind Sensitivitätstests, kein vollständiger Konvergenz-/Validierungsnachweis.','',
        'Die Prozentabweichung einer Energiebilanz ist kein Fehlerband für Temperaturen. Der Faktor verwendet die Masseverweilzeit (Luftmasse/Massenstrom) und ist nicht direkt mit dem alten isothermen Potentialmodell gleichzusetzen.']
    failures={name:r['quality_failures'] for name,r in reports.items() if not r['quality_pass']}
    if failures:lines+=['','## Fehlgeschlagene Qualitätskriterien','',json.dumps(failures,ensure_ascii=False,indent=2)]
    summary={'cases':reports,'missing':[n for n in wanted if n not in reports],'qualified_differences':checks,'all_quality_pass':len(reports)==len(wanted) and all(r['quality_pass'] for r in reports.values())}
    (out/'comparison.md').write_text('\n'.join(lines)+'\n');(out/'comparison.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('\n'.join(lines))
if __name__=='__main__':main()
