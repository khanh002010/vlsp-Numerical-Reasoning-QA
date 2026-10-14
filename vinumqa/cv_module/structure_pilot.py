"""Run the same pixel-reference pilot with a new, independently reviewed store."""
import argparse
import json
import hashlib
import time
import statistics
from pathlib import Path
from vinumqa.cv_module.structure_store import ChartStructureStore, SavedVisionFailure
from vinumqa.evaluation.score_ocr_labels import score
from vinumqa.nlp_module.data_prep.incremental import write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--images', type=Path, default=Path('data/public_test/public_test_images'))
    parser.add_argument('--reference', type=Path, default=Path('reports/public_accuracy_v2/pixel_references.json'))
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--model', default='Qwen/Qwen2.5-VL-7B-Instruct')
    parser.add_argument('--four-bit', action='store_true')
    args = parser.parse_args()
    refs = json.loads(args.reference.read_text(encoding='utf-8'))
    for name in refs['images']:
        path = args.images/name
        if not path.is_file(): raise FileNotFoundError(path)
        expected = refs.get('sha256', {}).get(name)
        if expected and hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Pilot image changed: {path}')
    store = ChartStructureStore(args.output_dir/'chart_structures.json', args.model,
                                load_in_4bit=args.four_bit, read_mode='reviewed')
    records = {}
    timings = {}
    try:
        # Load once before timing; cache hits must not appear as fast OCR runs.
        pending = [name for name in refs['images']
                   if (store.record(args.images/name) or {}).get('status') != 'ok']
        import torch
        if pending: store._reader()
        for i, name in enumerate(refs['images'], 1):
            path = args.images/name
            cached = (store.record(path) or {}).get('status') == 'ok'
            if torch.cuda.is_available():
                for device in range(torch.cuda.device_count()):
                    torch.cuda.synchronize(device)
                    torch.cuda.reset_peak_memory_stats(device)
            started = time.monotonic()
            print(f'[Reviewed pilot {i}/{len(refs["images"])}] {name}', flush=True)
            try: store.get(path, retry_failed=True)
            except SavedVisionFailure as error: print('Saved failure:', error, flush=True)
            records[name] = store.record(path)
            if torch.cuda.is_available():
                for device in range(torch.cuda.device_count()): torch.cuda.synchronize(device)
            timings[name] = {'cache_hit': cached, 'seconds': round(time.monotonic()-started, 3),
                             'peak_allocated_bytes_per_gpu': [torch.cuda.max_memory_allocated(d)
                                 for d in range(torch.cuda.device_count())]}
            write_json(args.output_dir/'timings.json', timings)
    finally:
        store.close()
    report = score(records, refs['images'])
    report['scope'] = refs['scope']
    report['model'] = args.model
    report['four_bit'] = args.four_bit
    report['reference_sha256'] = hashlib.sha256(args.reference.read_bytes()).hexdigest()
    report['status_counts'] = {s: sum(r.get('status') == s for r in records.values()) for s in ('ok', 'error')}
    report['stage_progress'] = {name: {
        'completed': list(record.get('generation', {}).get('completed_stages', {})),
        'failed': record.get('generation', {}).get('failed_stages', {}),
        'note': 'Stage completion is cross-view validation, not measured OCR accuracy.'}
        for name, record in records.items()}
    measured = [t['seconds'] for t in timings.values() if not t['cache_hit']]
    report['runtime'] = {'uncached_images': len(measured),
                         'median_seconds_excluding_model_load': statistics.median(measured) if measured else None,
                         'total_seconds_excluding_model_load': sum(measured),
                         'note': 'Cache hits excluded. Includes validation and retries. GPU memory is allocated tensor memory, not total process VRAM.'}
    if 'selection' in refs:
        report['subsets'] = {group: score(records, {n: refs['images'][n] for n in refs['selection'][group]})
                             for group in ('fixed_difficult', 'random_extra')}
    write_json(args.output_dir/'ocr_accuracy_pilot.json', report)
    print(json.dumps({k:v for k,v in report.items() if k!='images'}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
