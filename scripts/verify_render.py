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
assert len(report['parts']) == (8 if variant == 'wall_detail' else 26)
if variant == 'cutaway':
    assert report['source_variant'] == 'assembled'
    assert sum(p['hidden_in_render'] for p in report['parts'].values()) == 8
    assert sum(p['cutaway_modifiers'] for p in report['parts'].values()) == 24
    for name in ('bench_upper', 'bench_lower', 'changing_chair', 'floor_boards'):
        assert not report['parts'][name]['hidden_in_render']
print(variant, 'verified:', len(report['parts']), 'CAD groups, Blender file, 1600x1100 PNG')
