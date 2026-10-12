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
    totals = {f: Counter() for f in ('series', 'x_labels')}
    images = {}
    for name, reference in references.items():
        if name not in records: raise ValueError(f'Missing image record: {name}')
        chart = records[name].get('structure', {})
        result = {}
        for field in totals:
            expected = reference[field]
            actual = [s['name'] for s in chart.get('series', [])] if field == 'series' else chart.get(field, [])
            a, b = Counter(map(key, actual)), Counter(map(key, expected))
            counts = {'correct': sum((a & b).values()), 'predicted': len(actual), 'reference': len(expected)}
            totals[field].update(counts)
            result[field] = {**counts, 'ordered_exact': list(map(key, actual)) == list(map(key, expected)),
                             'missing': list((b-a).elements()), 'extra': list((a-b).elements())}
        images[name] = result
    summary = {f: {**c, 'precision': c['correct']/c['predicted'] if c['predicted'] else 0.,
                   'recall': c['correct']/c['reference'] if c['reference'] else 0.} for f,c in totals.items()}
    return {'reviewed_images': len(images), 'normalization': 'NFC, whitespace and case only; no fuzzy matching or date inference',
            'fields': summary, 'images': images}


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
