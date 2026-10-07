"""Read every source image; compare pixel caps without changing source images or OCR."""
import hashlib
import json
import math
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
CAPS = (500000, 750000, 1000000, 1003520, 1250000, 1400000)


def resized_size(width, height, cap):
    if width * height <= cap:
        return width, height
    scale = math.sqrt(cap / (width * height))
    return max(1, int(width * scale)), max(1, int(height * scale))


def describe(rows):
    pixels = sorted(r['pixels'] for r in rows)
    return {
        'count': len(rows), 'referenced_images': sum(r['references'] > 0 for r in rows),
        'minimum_pixels': min(pixels), 'median_pixels': statistics.median(pixels),
        'mean_pixels': round(statistics.mean(pixels)), 'maximum_pixels': max(pixels),
        'percentiles_nearest_rank': {str(p): pixels[math.ceil(p / 100 * len(pixels))-1]
                                     for p in (50, 75, 90, 95, 99, 100)},
        'minimum_width': min(r['width'] for r in rows), 'maximum_width': max(r['width'] for r in rows),
        'minimum_height': min(r['height'] for r in rows), 'maximum_height': max(r['height'] for r in rows),
        'unique_dimensions': len({(r['width'], r['height']) for r in rows}),
        'caps': {str(cap): {
            'at_or_below_cap': sum(p <= cap for p in pixels),
            'resized_images': sum(p > cap for p in pixels),
            'coverage_percent': round(100 * sum(p <= cap for p in pixels) / len(rows), 2),
            'processed_pixels_total_before_processor_rounding': sum(
                math.prod(resized_size(r['width'], r['height'], cap)) for r in rows),
            'worst_linear_scale': round(min(1, math.sqrt(cap / max(pixels))), 4),
        } for cap in CAPS},
    }


def main():
    rows, errors, missing = [], [], []
    for split in ('train', 'public_test'):
        source = ROOT / 'data' / split
        data = json.loads((source / f'{split}.json').read_text(encoding='utf-8'))
        refs = Counter(name for sample in data for name in sample.get('images', {}).values())
        folder = source / f'{split}_images'
        missing.extend({'split': split, 'file': name} for name in refs if not (folder / name).is_file())
        for path in sorted(folder.rglob('*')):
            if not path.is_file():
                continue
            try:
                with Image.open(path) as image:
                    image.load()  # Full decode, not only the PNG header.
                    width, height = image.size
                    row = {'split': split, 'file': path.name, 'path': path.relative_to(ROOT).as_posix(),
                           'width': width, 'height': height, 'pixels': width * height,
                           'megapixels': round(width * height / 1000000, 6),
                           'mode': image.mode, 'format': image.format, 'dpi': image.info.get('dpi'),
                           'file_bytes': path.stat().st_size, 'references': refs[path.name],
                           'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                           'resize_at_caps': {str(c): dict(zip(('width', 'height'), resized_size(width, height, c)))
                                              for c in CAPS}}
                rows.append(row)
            except Exception as error:
                errors.append({'path': path.relative_to(ROOT).as_posix(), 'error': str(error)})
    summary = {'generated_at_local': datetime.now().astimezone().isoformat(),
               'image_count': len(rows), 'errors': errors, 'missing_referenced_images': missing,
               'unique_file_contents': len({r['sha256'] for r in rows}),
               'groups': {s: describe([r for r in rows if s == 'all' or r['split'] == s])
                          for s in ('train', 'public_test', 'all')},
               'largest_images': sorted(rows, key=lambda r: r['pixels'], reverse=True)[:10],
               'note': 'Measured source dimensions; simulated area cap follows local preprocess_image. '
                       'Qwen processor may additionally round dimensions. No GPU OCR/quality or timing benchmark.'}
    (OUT / 'inventory.json').write_text(json.dumps({'summary': summary, 'images': rows},
                                                  ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in summary.items() if k != 'largest_images'}, indent=2))
    print('Largest images:', [(r['file'], r['width'], r['height'], r['pixels'])
                              for r in summary['largest_images'][:5]])


if __name__ == '__main__':
    main()
