#!/usr/bin/env python3
"""Apply an externally supplied, uniform scan calibration to a PLY point cloud.

The JSON must contain world_to_metres_4x4. No dimensions or private scan data
are embedded in this utility. Requires numpy and plyfile.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from plyfile import PlyData, PlyElement


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('calibration', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--millimetres', action='store_true', help='Export CAD millimetres instead of metres')
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f'Output already exists: {args.output}')
    transform = np.asarray(json.loads(args.calibration.read_text())['world_to_metres_4x4'], dtype=float)
    if transform.shape != (4, 4) or not np.isfinite(transform).all():
        parser.error('Calibration must be a finite 4×4 matrix')
    if not np.allclose(transform[3], [0, 0, 0, 1], atol=1e-10):
        parser.error('Calibration must be affine')
    linear = transform[:3, :3]
    scale = np.linalg.norm(linear, axis=0).mean()
    if scale <= 0:
        parser.error('Calibration must have a positive scale')
    rotation = linear / scale
    if not np.allclose(rotation.T @ rotation, np.eye(3), rtol=1e-6, atol=1e-8):
        parser.error('Calibration must use one uniform scale and an orthogonal rotation')
    if not np.isclose(np.linalg.det(rotation), 1, atol=1e-6):
        parser.error('Calibration must preserve handedness')
    cloud = PlyData.read(args.input)
    source = cloud['vertex'].data
    if not all(k in source.dtype.names for k in ('x', 'y', 'z')):
        parser.error('Input has no x/y/z vertex coordinates')
    if any(source.dtype[k].kind != 'f' for k in ('x', 'y', 'z')):
        parser.error('Input coordinates must be floating point to avoid truncation')
    if all(k in source.dtype.names for k in ('nx', 'ny', 'nz')) and any(source.dtype[k].kind != 'f' for k in ('nx', 'ny', 'nz')):
        parser.error('Input normals must be floating point to avoid truncation')
    vertices = source.copy()
    factor = 1000 if args.millimetres else 1
    for start in range(0, len(vertices), 1_000_000):
        chunk = vertices[start:start + 1_000_000]
        points = np.column_stack([chunk[k] for k in ('x', 'y', 'z')]).astype(float)
        points = (points @ linear.T + transform[:3, 3]) * factor
        chunk['x'], chunk['y'], chunk['z'] = points.T
        if all(k in vertices.dtype.names for k in ('nx', 'ny', 'nz')):
            normals = np.column_stack([chunk[k] for k in ('nx', 'ny', 'nz')]).astype(float) @ rotation.T
            chunk['nx'], chunk['ny'], chunk['nz'] = normals.T
    elements = [PlyElement.describe(vertices, 'vertex') if e.name == 'vertex' else e for e in cloud.elements]
    unit = 'millimetres' if args.millimetres else 'metres'
    comments = list(cloud.comments) + [f'Calibrated coordinates: {unit}. Uniform similarity transform.',
                                      'Calibration validity and measurement accuracy require external verification.']
    args.output.parent.mkdir(parents=True, exist_ok=True)
    PlyData(elements, text=False, byte_order='<', comments=comments).write(args.output)
    print(f'{len(vertices):,} vertices written in {unit}: {args.output}')


if __name__ == '__main__':
    main()
