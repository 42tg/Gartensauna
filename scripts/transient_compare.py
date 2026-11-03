#!/usr/bin/env python3
"""Compare matching physical-time windows at two actual solver step limits."""
import argparse,json
from pathlib import Path
import numpy as np

def compare(base,ref,out):
    a=json.loads((base/'transient_results.json').read_text());b=json.loads((ref/'transient_results.json').read_text())
    ac=json.loads((base/'transient.json').read_text());bc=json.loads((ref/'transient.json').read_text())
    am=json.loads((base/'case.json').read_text());bm=json.loads((ref/'case.json').read_text())
    if am!=bm:raise ValueError('Different geometry or physical configuration')
    for key in ('window_start_s','window_end_s'):
        if a[key]!=b[key]:raise ValueError('Time windows must match')
    for key in ('seed_T_sha256','seed_U_sha256'):
        if ac[key]!=bc[key]:raise ValueError('Time-step test requires identical initial fields')
    if bc['max_Co']>ac['max_Co']/2+1e-12 or bc['max_delta_t_s']>ac['max_delta_t_s']/2+1e-12:raise ValueError('Reference does not halve both time-step constraints')
    af=np.load(base/'mean_fields.npz');bf=np.load(ref/'mean_fields.npz');v=af['volumes']
    dT=float(np.average(abs(af['T_C']-bf['T_C']),weights=v));dU=float(np.average(np.linalg.norm(af['U']-bf['U'],axis=1),weights=v))
    failures=[]
    if not a['thermal_window_pass']:failures.append('base window: '+ '; '.join(a['quality_failures']))
    if not b['thermal_window_pass']:failures.append('half-step window: '+ '; '.join(b['quality_failures']))
    if dT>.5:failures.append('mean temperature step sensitivity >0.5 K')
    if dU>.01:failures.append('mean velocity step sensitivity >0.01 m/s')
    r={'thermal_time_step_check_pass':not failures,'failures':failures,'mean_field_temperature_difference_K':dT,'mean_field_velocity_difference_m_s':dU,
       'base':a,'half_step':b,'physical_validation':False,'air_age_qualified':a['age_initialization_pass'] and b['age_initialization_pass'] and not failures}
    out.mkdir(parents=True,exist_ok=True);(out/'comparison.json').write_text(json.dumps(r,indent=2)+'\n')
    lines=['# Zeitabhängige Sauna-CFD','',f"Zeitmittel von {a['window_start_s']:g} bis {a['window_end_s']:g} Sekunden nach warmem numerischem Start.",
        '**Numerische Fenster- und Zeitschrittprüfungen bestanden.**' if not failures else '**Noch keine numerische Freigabe der Mittelwerte.**','',
        '| Größe | Basis | Halbierte Zeitschrittgrenze |','|---|---:|---:|']
    for k,label in [('upper','Obere Bank'),('lower','Untere Bank')]:
        lines.append(f"| {label}: Temperatur °C | {a['regions'][k]['mean_temperature_C']:.2f} | {b['regions'][k]['mean_temperature_C']:.2f} |")
        lines.append(f"| {label}: mittlerer Geschwindigkeitsbetrag m/s | {a['regions'][k]['mean_speed_m_s']:.4f} | {b['regions'][k]['mean_speed_m_s']:.4f} |")
    for k,label,scale in [('energy_balance_relative','Betrag Wärmebilanzfehler %',100),('split_window_temperature_difference_K','Unterschied der Fensterhälften K',1),('split_window_velocity_difference_m_s','Unterschied der mittleren Geschwindigkeit der Fensterhälften m/s',1)]:
        lines.append(f'| {label} | {abs(a[k])*scale:.5f} | {abs(b[k])*scale:.5f} |')
    lines+=['',f'Mittlere absolute Feldabweichung beim Halbieren der Zeitschrittgrenzen: **{dT:.4f} K**, **{dU:.5f} m/s**.','',
        'Die Energiebilanz enthält die Änderung der im Luftvolumen gespeicherten Energie; die Massenbilanz enthält die Änderung der Luftmasse. Das ist keine stationäre Bilanz.','',
        f"Luftalter: {'Initialisierungsprüfung bestanden' if r['air_age_qualified'] else 'noch nicht als Vergleichswert freigegeben'}. Empfindlichkeit gegenüber den zwei Startfeldern: {100*a['age_initial_condition_sensitivity_relative']:.1f} % / {100*b['age_initial_condition_sensitivity_relative']:.1f} %.",
        'Der Luftaltertransport wird aus gespeicherten Strömungsfeldern implizit nachgerechnet; er ist keine direkt mit jedem CFD-Schritt gekoppelte Messgröße.','',
        'Annahmen: 3000 W mittlere Ofenwärme, 80 m³/h Zuluft bei 10 °C; vereinfachte geschlossene Ofen-/Bankhüllen. Trockenes URANS-Modell mit Oberflächenstrahlung. Keine Aufheizzeit realer Steine/Hölzer, kein Aufguss, keine Messvalidierung. Ein Zeitschrittvergleich ersetzt keine räumliche Gitterstudie und keinen Nachweis statistischer Unabhängigkeit.']
    if failures:lines+=['','Fehler:']+['- '+f for f in failures]
    (out/'comparison.md').write_text('\n'.join(lines)+'\n');return r
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('base',type=Path);p.add_argument('reference',type=Path);p.add_argument('--out',type=Path,default=Path('build/transient-comparison'));p.add_argument('--require-quality',action='store_true');a=p.parse_args();r=compare(a.base,a.reference,a.out);print(json.dumps({k:v for k,v in r.items() if k not in ('base','half_step')},indent=2))
    if a.require_quality and not r['thermal_time_step_check_pass']:raise SystemExit('Transient numerical checks failed')
