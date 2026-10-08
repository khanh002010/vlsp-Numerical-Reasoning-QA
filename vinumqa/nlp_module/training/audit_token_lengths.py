"""Measure the exact training sequences without allocating model weights or CUDA."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from vinumqa.nlp_module.contracts import RESPONSE_PREFIX
from vinumqa.nlp_module.training.supervision import load_prepared_pair, encode_supervised
from vinumqa.cv_module.structure import render_structure


def summarize(rows):
    lengths = sorted(r['total_tokens'] for r in rows)
    return {
        'samples': len(rows), 'min': lengths[0],
        'mean': round(sum(lengths) / len(lengths), 2),
        **{f'p{p}': lengths[math.ceil(len(lengths)*p/100)-1] for p in (50,90,95,99)},
        'max': lengths[-1], 'max_padded_to_8': (lengths[-1]+7)//8*8,
        'over_budget': {str(n): sum(v > n for v in lengths)
                        for n in (4096,4608,5120,5632,6144,7168,7680,8182,8192)},
        'longest': sorted(rows, key=lambda r:r['total_tokens'], reverse=True)[:10],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared-dir', type=Path, default=Path('prepared'))
    parser.add_argument('--data-root', type=Path, default=Path('data'))
    parser.add_argument('--output-dir', type=Path, default=Path('reports/token_length_audit'))
    parser.add_argument('--model', default='Qwen/Qwen2.5-7B-Instruct')
    args = parser.parse_args()
    from transformers import AutoTokenizer, __version__
    from huggingface_hub import HfApi
    from PIL import Image
    revision = HfApi().model_info(args.model).sha
    tokenizer = AutoTokenizer.from_pretrained(args.model, revision=revision)
    print(f'Tokenizer: {args.model}@{revision}; no model weights loaded', flush=True)
    paths = [args.prepared_dir / f'{s}_structured.json' for s in ('train','public_test')]
    datasets = load_prepared_pair(*paths)
    all_rows, image_rows = [], []
    report = {'model': args.model, 'revision': revision, 'transformers': __version__,
              'tokenizer_class': type(tokenizer).__name__, 'eos_token_id': tokenizer.eos_token_id,
              'method': 'prompt and completion encoded separately, add_special_tokens=False; append one EOS; padding multiple=8',
              'component_note': 'Chart token counts are standalone diagnostics, not additive to total.',
              'splits': {}}
    for split, rows, path in zip(('train','public_test'), datasets, paths):
        measured = []
        artifact = json.loads(path.read_text(encoding='utf-8'))
        for sample in rows:
            header = '| Step | Output |\n|---|---|\n'
            if not sample['output'].startswith(header): raise ValueError('Invalid completion header')
            prompt = sample['instruction'] + '\n\n' + sample['input'] + '\n\n' + RESPONSE_PREFIX
            completion = sample['output'][len(header):]
            # Use the real encoder, including its target masking and EOS behavior.
            encoded = encode_supervised(tokenizer, prompt, completion, 10**9)
            prompt_count = encoded['labels'].count(-100)
            charts = sample.get('charts', {})
            chart_text = '\n'.join(render_structure(k,v) for k,v in charts.items())
            measured.append(dict(split=split, qid=sample['qid'], prompt_tokens=prompt_count,
                target_tokens=len(encoded['input_ids'])-prompt_count,
                total_tokens=len(encoded['input_ids']), padded_tokens=(len(encoded['input_ids'])+7)//8*8,
                image_count=len(charts), chart_text_tokens=len(tokenizer.encode(chart_text, add_special_tokens=False))))
        for record in artifact.get('images', []):
            image_path = args.data_root / split / f'{split}_images' / record['image']
            info = dict(split=split, image=record['image'], status=record['status'], exists=image_path.is_file())
            if image_path.is_file():
                with Image.open(image_path) as im:
                    info.update(width=im.width, height=im.height, pixels=im.width*im.height)
                    im.verify()
                actual_hash = hashlib.sha256(image_path.read_bytes()).hexdigest()
                info['sha256_matches_prepared'] = actual_hash == record.get('sha256') if record.get('sha256') else None
            image_rows.append(info)
        report['splits'][split] = {**summarize(measured), 'artifact_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        all_rows.extend(measured)
        print(split, json.dumps({k:v for k,v in report['splits'][split].items() if k!='longest'}), flush=True)
    report['combined'] = summarize(all_rows)
    report['images'] = {'referenced':len(image_rows), 'missing':sum(not r['exists'] for r in image_rows),
                        'hash_mismatch':sum(r.get('sha256_matches_prepared') is False for r in image_rows)}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir/'summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    for name, records in [('samples.csv', all_rows), ('images.csv', image_rows)]:
        keys = list(dict.fromkeys(k for row in records for k in row))
        with (args.output_dir/name).open('w', encoding='utf-8-sig', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=keys)
            writer.writeheader()
            writer.writerows(records)
    print('Saved', args.output_dir, 'required padded budget:', report['combined']['max_padded_to_8'], flush=True)


if __name__ == '__main__': main()
