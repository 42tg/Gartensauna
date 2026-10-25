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
print(variant, 'verified:', len(report['parts']), 'CAD groups, Blender file, 1600x1100 PNG')
