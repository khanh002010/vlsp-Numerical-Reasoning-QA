"""Score a human pixel transcription; never derive an OCR reference from gold DSL."""
import argparse
import hashlib
import json
import unicodedata
from collections import Counter
from pathlib import Path


def key(value):
    return ' '.join(unicodedata.normalize('NFC', value).split()).casefold()


def score(records, references):
    totals = {f: Counter() for f in ('series', 'x_labels', 'y_labels')
              if any(f in ref for ref in references.values())}
    metadata = {f: Counter() for f in ('title', 'units') if any(f in ref for ref in references.values())}
    images = {}
    for name, reference in references.items():
        if name not in records: raise ValueError(f'Missing image record: {name}')
        record = records[name] or {}
        chart = record.get('structure', {}) if record.get('status', 'ok') == 'ok' else {}
        result = {}
        for field in totals:
            if field not in reference: continue
            expected = reference[field]
            actual = [s['name'] for s in chart.get('series', [])] if field == 'series' else chart.get(field, [])
            a, b = Counter(map(key, actual)), Counter(map(key, expected))
            counts = {'correct': sum((a & b).values()), 'predicted': len(actual), 'reference': len(expected)}
            totals[field].update(counts)
            totals[field]['evaluated_images'] += 1
            exact = bool(chart) and list(map(key, actual)) == list(map(key, expected))
            totals[field]['exact_images'] += int(exact)
            result[field] = {**counts, 'ordered_exact': exact,
                             'missing': list((b-a).elements()), 'extra': list((a-b).elements())}
        if 'title' in reference:
            actual_title = chart.get('title', '')
            same = key(actual_title) == key(reference['title']) and bool(chart)
            metadata['title'].update(correct=int(same), total=1)
            result['title'] = {'expected': reference['title'], 'actual': actual_title, 'exact': same}
        if 'units' in reference:
            actual_units = {key(s['name']): s.get('unit', '') for s in chart.get('series', [])}
            result['units'] = {}
            for series, unit in reference['units'].items():
                actual_unit = actual_units.get(key(series))
                same = actual_unit is not None and key(actual_unit) == key(unit)
                metadata['units'].update(correct=int(same), total=1)
                result['units'][series] = {'expected': unit, 'actual': actual_unit, 'exact': same}
        images[name] = result
    # Empty Y references are meaningful: expose exact-image rate and false positives,
    # not an undefined 0/0 recall disguised as a measured accuracy.
    summary = {f: {**c, 'precision': c['correct']/c['predicted'] if c['predicted'] else None,
                   'recall': c['correct']/c['reference'] if c['reference'] else None,
                   'exact_image_rate': c['exact_images']/c['evaluated_images']} for f,c in totals.items()}
    scalar_summary = {f: {**c, 'accuracy': c['correct']/c['total'] if c['total'] else None} for f,c in metadata.items()}
    return {'reviewed_images': len(images), 'normalization': 'NFC, whitespace and case only; no fuzzy matching or date inference',
            'fields': summary, 'metadata': scalar_summary, 'images': images}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared', required=True, help='Structured artifact or chart store')
    parser.add_argument('--reference', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    artifact = json.loads(Path(args.prepared).read_text(encoding='utf-8'))
    records = artifact['images']
    records = list(records.values()) if isinstance(records, dict) else records
    refs = json.loads(Path(args.reference).read_text(encoding='utf-8'))
    result = score({r['image']:r for r in records}, refs['images'])
    result['scope'] = refs['scope']
    result['artifact_sha256'] = hashlib.sha256(Path(args.prepared).read_bytes()).hexdigest()
    path = Path(args.output); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'images'}, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
