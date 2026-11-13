#!/usr/bin/env python3
"""Experimental sparse SfM; no metric scale or invented surface geometry.

Dependencies: ffmpeg, pycolmap==4.2.1. The input video remains local.
Run: python scripts/reconstruct_video.py VIDEO --output OUTPUT
"""
import argparse
import json
from pathlib import Path
import subprocess
import pycolmap


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    video = args.video.resolve()
    if not video.is_file():
        parser.error('Input video does not exist')
    root = args.output.resolve()
    if root.exists():
        parser.error('Output must be a new directory (avoids stale matches)')
    images = root / 'images'
    images.mkdir(parents=True)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(video),
                    '-vf', 'fps=2,scale=720:-2', '-q:v', '2',
                    str(images / 'frame_%04d.jpg')], check=True)
    db = root / 'database.db'
    extraction = pycolmap.FeatureExtractionOptions()
    extraction.num_threads = 4
    extraction.sift.max_num_features = 5000
    pycolmap.extract_features(db, images, camera_mode=pycolmap.CameraMode.SINGLE,
        reader_options=pycolmap.ImageReaderOptions(camera_model='SIMPLE_RADIAL'),
        extraction_options=extraction, device=pycolmap.Device.cpu)
    matching = pycolmap.FeatureMatchingOptions()
    matching.num_threads = 4
    pycolmap.match_sequential(db, matching_options=matching, device=pycolmap.Device.cpu)
    options = pycolmap.IncrementalPipelineOptions()
    options.num_threads = 4
    options.random_seed = 42
    models = pycolmap.incremental_mapping(db, images, root / 'sparse', options=options)
    results = []
    for index, model in models.items():
        model.export_PLY(root / f'cloud_{index}.ply')
        model.write_text(root / 'sparse' / str(index))
        results.append({'model': index, 'summary': model.summary()})
    (root / 'summary.json').write_text(json.dumps({
        'input_frames': len(list(images.glob('*.jpg'))),
        'scale': 'arbitrary; not metres or millimetres',
        'camera_assumption': 'shared SIMPLE_RADIAL; stabilization not modeled',
        'models': results}, indent=2))
    if not models:
        raise SystemExit('No reconstruction succeeded; inspect logs and capture overlap')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
