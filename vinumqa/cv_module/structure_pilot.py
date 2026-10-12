"""Run the same pixel-reference pilot with a new, independently reviewed store."""
import argparse
import json
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
    store = ChartStructureStore(args.output_dir/'chart_structures.json', args.model,
                                load_in_4bit=args.four_bit, read_mode='reviewed')
    records = {}
    try:
        for i, name in enumerate(refs['images'], 1):
            path = args.images/name
            print(f'[Reviewed pilot {i}/{len(refs["images"])}] {name}', flush=True)
            try: store.get(path, retry_failed=True)
            except SavedVisionFailure as error: print('Saved failure:', error, flush=True)
            records[name] = store.record(path)
    finally:
        store.close()
    report = score(records, refs['images'])
    report['scope'] = refs['scope']
    write_json(args.output_dir/'ocr_accuracy_pilot.json', report)
    print(json.dumps({k:v for k,v in report.items() if k!='images'}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
