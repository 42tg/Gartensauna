"""Verify one render artifact in CI."""
import json
import struct
import sys
from pathlib import Path

variant = sys.argv[1]
stem = Path('build/blender') / f'gartensauna_{variant}'
assert stem.with_suffix('.blend').read_bytes().startswith(b'BLENDER')
png = stem.with_suffix('.png').read_bytes()
assert png[:8] == b'\x89PNG\r\n\x1a\n'
assert struct.unpack('>II', png[16:24]) == (1600, 1100)
report = json.loads(stem.with_suffix('.json').read_text())
assert len(report['parts']) == (8 if variant == 'wall_detail' else 29)
if variant == 'cutaway':
    assert report['source_variant'] == 'assembled'
    assert sum(p['hidden_in_render'] for p in report['parts'].values()) == 8
    assert sum(p['cutaway_modifiers'] for p in report['parts'].values()) == 24
    for name in ('bench_upper', 'bench_lower', 'changing_chair', 'floor_boards'):
        assert not report['parts'][name]['hidden_in_render']
if variant != 'wall_detail':
    for name in ('heater_cage', 'heater_mount', 'heater_stones'):
        assert name in report['parts']
        assert not report['parts'][name]['hidden_in_render']
    dims = report['parts']['heater_cage']['dimensions']
    assert all(abs(a-b) < 0.002 for a,b in zip(dims, (0.390, 0.335, 0.590)))
if variant == 'heater_detail':
    assert sum(not p['hidden_in_render'] for p in report['parts'].values()) == 3
if variant == 'assembled':
    parts = report['parts']
    lo, hi = parts['heater_cage']['bounds_min'], parts['heater_cage']['bounds_max']
    clearances = {
        'glass': (lo[0] - parts['glass_front']['bounds_max'][0]) * 1000,
        'window_frame': (lo[0] - parts['glass_frame']['bounds_max'][0]) * 1000,
        'lower_bench': (parts['bench_lower']['bounds_min'][0] - hi[0]) * 1000,
        'upper_bench': (parts['bench_upper']['bounds_min'][0] - hi[0]) * 1000,
        'floor': (lo[2] - parts['floor_boards']['bounds_max'][2]) * 1000,
        'ceiling': (parts['ceiling_boards']['bounds_min'][2] - hi[2]) * 1000,
    }
    for name, gap in clearances.items():
        minimum = 1200 if name == 'ceiling' else 100 if name == 'floor' else 150
        assert gap >= minimum - 0.5, (name, gap, minimum)
    # Bracket faces the window-side end wall; no accidental mirror/old placement.
    mount_lo = parts['heater_mount']['bounds_min']
    assert abs(mount_lo[1] - (-1.820)) < 0.001
    assert -1.821 < lo[1] < -1.819 and -1.486 < hi[1] < -1.484
    assert abs((lo[0] + hi[0]) / 2 - 1.700) < 0.001
    report['heater_clearances_mm'] = clearances
    stem.with_suffix('.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Heater clearances (mm):', clearances)
print(variant, 'verified:', len(report['parts']), 'CAD groups, Blender file, 1600x1100 PNG')
