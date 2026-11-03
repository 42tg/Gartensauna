#!/usr/bin/env python3
"""Explicit freshness ranking, finalist-only robustness, and missing-run accounting."""
import argparse,json,math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from study_cases import settings,case,implementation_hash
from simulate_ventilation import ROOT

def qualified(r):
    try:
        return bool(r and r.get('thermal_window_pass') and r.get('age_quality_pass') and r.get('window_end_s',0)>=settings()['end_time_s'] and r.get('window_start_s')==settings()['mean_start_s'] and all(math.isfinite(r['regions'][k]['age_factor']) and r['regions'][k]['age_factor']>0 for k in ('upper','lower')))
    except (KeyError,TypeError,ValueError):return False

def score(r):return max(r['regions'][k]['age_factor'] for k in ('upper','lower'))

def collect(root):
    found={}
    for p in root.rglob('study_case.json'):
        info=json.loads(p.read_text());key=(info['variant']['name'],info['scenario'])
        if key in found:raise ValueError('Duplicate study result: '+str(key))
        if info['study_id']!=settings()['id'] or info.get('smoke'):continue
        if info.get('implementation_sha256')!=implementation_hash():raise ValueError('Result generated with different solver/study sources: '+str(p))
        file=p.parent/'transient_results.json'
        if file.exists():found[key]=json.loads(file.read_text())
    return found

def select(found):
    valid=[v['name'] for v in settings()['variants'] if qualified(found.get((v['name'],'nominal')))]
    return sorted(valid,key=lambda name:score(found[(name,'nominal')]))[:settings()['max_finalists']]

def evaluate(found):
    s=settings();names=[v['name'] for v in s['variants']];finalists=select(found)
    expected=[(n,'nominal') for n in names]+[(n,x['name']) for n in finalists for x in s['validation_scenarios']]
    missing=[list(k) for k in expected if k not in found];unqualified=[list(k) for k in expected if k in found and not qualified(found[k])]
    nominal=sorted([n for n in names if qualified(found.get((n,'nominal')))],key=lambda n:score(found[(n,'nominal')]))
    # Relative separation threshold is declared before seeing any results.
    bands={n:s['ranking_margin_relative'] for n in nominal}
    for n in finalists:
        for scenario in ('fine_mesh','half_step'):
            r=found.get((n,scenario))
            if qualified(r):bands[n]=max(bands[n],abs(score(r)/score(found[(n,'nominal')])-1))
    tiers=[]
    for n in nominal:
        value=score(found[(n,'nominal')]);lo=value*(1-bands[n]);hi=value*(1+bands[n])
        if tiers and lo<=tiers[-1]['upper']:
            tiers[-1]['variants'].append(n);tiers[-1]['upper']=max(tiers[-1]['upper'],hi)
        else:tiers.append({'variants':[n],'lower':lo,'upper':hi})
    winner=None;checks=[]
    if len(finalists)==2 and not missing and not unqualified:
        a,b=finalists
        def better(x,y,scenario):
            rx,ry=found[(x,scenario)],found[(y,scenario)]
            margin=max(bands[x],bands[y]);fresh=score(rx)*(1+margin)<score(ry)*(1-margin)
            cold=lambda r:min(r['regions'][k]['mean_temperature_C'] for k in ('upper','lower'))
            temp=cold(rx)>=cold(ry)-s['temperature_tradeoff_K']
            speed=rx['occupied_p95_mean_speed_m_s']<=ry['occupied_p95_mean_speed_m_s']+s['speed_tradeoff_m_s']
            tail=rx['occupied_p95_mean_age_min']<=ry['occupied_p95_mean_age_min']*(1+margin)
            return fresh and temp and speed and tail
        scenarios=['nominal']+[x['name'] for x in s['validation_scenarios']]
        for x,y in [(a,b),(b,a)]:
            passed=[better(x,y,z) for z in scenarios];checks.append({'candidate':x,'other':y,'scenarios':dict(zip(scenarios,passed))})
            if all(passed):winner=x
    return {'study_id':s['id'],'nominal_freshness_order':nominal,'nominal_tiers':tiers,'relative_comparison_bands':bands,'finalists':finalists,'missing':missing,'unqualified':unqualified,
        'complete':len(nominal)==len(names) and not missing and not unqualified,'robust_finalist_winner':winner,'finalist_checks':checks,
        'scope':s['ranking_scope'],'uncertainty_note':'Comparison bands are engineering separation thresholds plus observed grid/time sensitivity, not statistical confidence intervals.',
        'physical_validation':False,'implementation_sha256':implementation_hash(),'results':{n+'__'+c:r for (n,c),r in found.items()}}

def layout(out):
    s=settings();fig,axes=plt.subplots(1,5,figsize=(16,4),sharey=True,constrained_layout=True)
    details=[]
    for ax,v in zip(axes,s['variants']):
        g,c,info=case(v['name']);y0,y1=g['room'][0][1]/1000,g['room'][1][1]/1000;h=g['room'][1][2]/1000
        ax.add_patch(Rectangle((y0,0),y1-y0,h,fill=False,color='black'))
        for name,col in [('heater','#c16b35'),('upper','#998272'),('lower','#c5b5a5')]:
            p,d=np.array(g[name][0])/1000,np.array(g[name][1])/1000;ax.add_patch(Rectangle((p[1],p[2]),d[1],d[2],color=col,alpha=.6))
        sp,ss=np.array(g['supply'][0])/1000,np.array(g['supply'][1])/1000;ep,es=np.array(g['exhaust'][0])/1000,np.array(g['exhaust'][1])/1000
        ax.plot([y0,y0],[sp[2],sp[2]+ss[2]],color='#167ac6',lw=6)
        ax.add_patch(Rectangle((ep[1],ep[2]),es[1],es[2],color='#df582c'))
        ax.set_title(v['label'].replace(' · ','\n'));ax.set_aspect('equal');ax.set_xlabel('Längsrichtung y [m]');ax.set_xlim(y0-.15,y1+.1);ax.set_ylim(-.05,h+.1)
        details.append({'variant':v['name'],'supply_mm':g['supply'],'exhaust_mm':g['exhaust']})
    axes[0].set_ylabel('Höhe über Boden [m]');fig.suptitle('Virtuelle Lüftungsvarianten aus den CAD-Maßen\nBlau: Zuluft an Stirnwand · Orange: Abluft an rechter Seitenwand · Projektion, keine Konstruktionsänderung')
    out.mkdir(parents=True,exist_ok=True);fig.savefig(out/'ventilation-study-positions.png',dpi=150);plt.close(fig);(out/'positions.json').write_text(json.dumps(details,indent=2)+'\n')

def report(found,out,run_url=''):
    s=settings();r=evaluate(found);r['run_url']=run_url
    out.mkdir(parents=True,exist_ok=True);(out/'ventilation-study-results.json').write_text(json.dumps(r,indent=2)+'\n')
    lines=['# Vergleich von fünf Lüftungspositionen','',f'Studie `{s["id"]}`. 60 simulierte Minuten pro Lauf, Zeitmittel Minuten 50–60.','',
           '**Vollständiger numerisch qualifizierter Vergleich.**' if r['complete'] else '**Vergleich noch unvollständig oder nicht ausreichend konvergiert. Keine vollständige Rangfolge freigegeben.**','',
           '| Variante | Zustand | ungünstigere Bank: Luftalterfaktor ↓ | P95 mittleres Luftalter min | obere / untere Bank °C | P95 mittlere Geschwindigkeit m/s |','|---|---|---:|---:|---:|---:|']
    for v in s['variants']:
        x=found.get((v['name'],'nominal'))
        if not x:lines.append(f'| {v["label"]} | fehlt / abgebrochen | — | — | — | — |');continue
        ok=qualified(x);f=f'{score(x):.3f}' if ok else 'nicht freigegeben'
        temps=' / '.join(f'{x["regions"][k]["mean_temperature_C"]:.1f}' for k in ('upper','lower'))
        lines.append(f'| {v["label"]} | {"bestanden" if ok else "nicht qualifiziert"} | {f} | {x.get("occupied_p95_mean_age_min",float("nan")):.2f} | {temps} | {x.get("occupied_p95_mean_speed_m_s",float("nan")):.3f} |')
    lines+=['','## Aussage zur Rangfolge','',
        'Primärkriterium ist der Luftalterfaktor der schlechter versorgten Bank. Es wird kein willkürlich gewichteter Gesamtscore aus Temperatur, Frische und Geschwindigkeit gebildet.',
        'Vorläufige nominale Frischegruppen der qualifizierten Teilmenge (überlappende Vergleichsbänder werden zusammengefasst): '+(' → '.join(' / '.join(t['variants']) for t in r['nominal_tiers']) or 'noch nicht verfügbar')+'.',
        'Die Reihenfolge gilt nur unter den nominalen Modellannahmen. Die Robustheitsprüfung umfasst ausschließlich die ausgewählten Finalisten; ausgeschiedene Varianten wurden nicht in allen Betriebsfällen geprüft.']
    if r['robust_finalist_winner']:lines.append('Unter den geprüften Finalisten robust günstiger: **'+r['robust_finalist_winner']+'**. Keine globale oder experimentell validierte Siegerbehauptung.')
    else:lines.append('**Kein belastbar getrennter Sieger der Finalisten nachgewiesen.** Das kann an Gleichwertigkeit, Zielkonflikten, Rangwechseln oder fehlenden Prüfungen liegen.')
    lines+=['','## Prüfungen der Finalisten','', '| Variante | Fall | Qualität | ungünstigerer Luftalterfaktor |','|---|---|---|---:|']
    for n in r['finalists']:
        for scenario in s['validation_scenarios']:
            x=found.get((n,scenario['name']));ok=qualified(x);lines.append(f'| {n} | {scenario["name"]} | {"bestanden" if ok else "fehlt / nicht qualifiziert"} | '+(f'{score(x):.3f}' if ok else '—')+' |')
    lines+=['','## Grenzen','',
        '3 kW mittlere Wärmeabgabe; nominal 80 m³/h Zuluft bei 10 °C. Vereinfachte geschlossene Ofen- und Bankhüllen, keine Personen oder Aufgüsse. Der Emissivitätsfall verändert nur die Ofenoberfläche von 0,9 auf 0,5 und prüft eine angenommene Wärmeverteilung; er ersetzt keinen durchströmten Steinkorb und keine Messvalidierung.',
        'Die Vergleichsbänder sind Mindestabstände für eine vorsichtige Ingenieurentscheidung und beobachtete Gitter-/Zeitschrittempfindlichkeit, keine statistischen Konfidenzintervalle. Die thermischen Zielkonfliktgrenzen (2 K und 0,02 m/s) sind gewählte Vergleichsregeln, keine Komfort- oder Sicherheitsnormen.',
        'Der Durchsatz ist vorgeschrieben. Ventilator-, Kanal- und Gitterdruckverluste werden nicht ausgelegt. Eine spätere Bauentscheidung erfordert auch deren Prüfung.','',
        f'[Rechenlauf und ausführliche Artefakte]({run_url})' if run_url else 'Lokaler Bericht; kein GitHub-Lauf angegeben.', '',
        '![CAD-basierte Positionsübersicht](assets/ventilation-study-positions.png)']
    (out/'ventilation-study-results.md').write_text('\n'.join(lines)+'\n')
    return r

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT/'build/study-artifacts');p.add_argument('--out',type=Path,default=ROOT/'build/study-report');p.add_argument('--select',action='store_true');p.add_argument('--layout',action='store_true');p.add_argument('--run-url',default='');a=p.parse_args()
    if a.layout:layout(a.out)
    else:
        data=collect(a.root)
        if a.select:print(json.dumps({'include':[{'variant':n,'scenario':s['name']} for n in select(data) for s in settings()['validation_scenarios']]}))
        else:print(json.dumps({k:v for k,v in report(data,a.out,a.run_url).items() if k!='results'},indent=2))
