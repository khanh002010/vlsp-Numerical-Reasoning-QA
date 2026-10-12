"""Experimental PaddleOCR-VL native-task pilot; outputs are NOT training structures.

Use OCR:/Chart Recognition:/Spotting: as documented by the model author. Do not
send Qwen JSON instructions to this specialized model or execute chart values.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path
from vinumqa.nlp_module.data_prep.incremental import write_json
from vinumqa.cv_module.chart_to_table.image_preprocessing import preprocess_image, MAX_PIXELS

MODEL = 'PaddlePaddle/PaddleOCR-VL-1.6'
PROMPTS = {'ocr': 'OCR:', 'chart': 'Chart Recognition:', 'spotting': 'Spotting:'}


class PaddleRecognizer:
    def __init__(self, model_id=MODEL, device='cuda:0'):
        import torch
        from transformers import AutoProcessor, AutoModelForImageTextToText
        if device.startswith('cuda') and not torch.cuda.is_available():
            raise RuntimeError('Paddle pilot needs CUDA; explicitly choose --device cpu only for diagnostics')
        self.torch, self.device = torch, device
        dtype = torch.float16 if device.startswith('cuda') else torch.float32
        print(f'Loading {model_id}: {device}, dtype={dtype}; native OCR tasks', flush=True)
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = AutoModelForImageTextToText.from_pretrained(
            model_id, dtype=dtype, device_map={'': device}, attn_implementation='sdpa').eval()

    def recognize(self, path, task, max_new_tokens, max_seconds):
        from PIL import Image
        with Image.open(path) as source:
            original_size = list(source.size)
            image = preprocess_image(source.convert('RGB'), MAX_PIXELS)
        messages = [{'role': 'user', 'content': [
            {'type': 'image', 'image': image}, {'type': 'text', 'text': PROMPTS[task]}]}]
        started = time.monotonic()
        inputs = self.processor.apply_chat_template(messages, add_generation_prompt=True,
            tokenize=True, return_dict=True, return_tensors='pt',
            images_kwargs={'size': {'shortest_edge': self.processor.image_processor.min_pixels,
                                   'longest_edge': MAX_PIXELS}}).to(self.device)
        length = inputs['input_ids'].shape[-1]
        with self.torch.inference_mode():
            output = self.model.generate(**inputs, max_new_tokens=max_new_tokens,
                                         do_sample=False, max_time=max_seconds)
        ids = output[0, length:].detach().cpu().tolist()
        eos_ids = self.model.generation_config.eos_token_id
        eos_ids = [eos_ids] if isinstance(eos_ids, int) else eos_ids or []
        complete = bool(ids) and ids[-1] in eos_ids
        # Decode all generated tokens, removing only actual special tokens, never
        # arbitrarily dropping the last character/token of a truncated response.
        return {'text': self.processor.decode(ids, skip_special_tokens=True),
                'tokens': len(ids), 'complete': complete,
                'stop_reason': 'eos' if complete else 'token_limit' if len(ids) >= max_new_tokens else 'time_or_other_stop',
                'seconds': round(time.monotonic()-started, 2), 'original_size': original_size,
                'input_image_size': list(image.size), 'max_pixels': MAX_PIXELS, 'prompt': PROMPTS[task]}

    def close(self):
        import gc
        self.model = None; self.processor = None
        gc.collect()
        if self.torch.cuda.is_available(): self.torch.cuda.empty_cache()


def run_pilot(images, output_dir, recognizer, tasks, identity):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / 'paddle_pilot.json'
    data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'identity': identity, 'images': {}}
    if data['identity'] != identity: raise ValueError('Pilot configuration changed; use a new output directory')
    for index, image in enumerate(images, 1):
        image = Path(image)
        sha = hashlib.sha256(image.read_bytes()).hexdigest()
        row = data['images'].setdefault(image.name, {'image': image.name, 'sha256': sha, 'tasks': {}})
        if row['sha256'] != sha: raise ValueError('Image bytes changed; choose a new pilot directory')
        for task in tasks:
            if row['tasks'].get(task, {}).get('complete'): continue
            print(f'[Paddle {index}/{len(images)}] {image.name}: {task}', flush=True)
            try:
                result = recognizer.recognize(image, task, identity['max_new_tokens'], identity['max_seconds'])
                row['tasks'][task] = result
                print(f'  {result["stop_reason"]}; tokens={result["tokens"]}; seconds={result["seconds"]}', flush=True)
            except Exception as error:
                row['tasks'][task] = {'complete': False, 'error': str(error)}
                raise
            finally:
                write_json(path, data)  # Completed tasks survive an interrupt/error.
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--images', type=Path, default=Path('data/public_test/public_test_images'))
    parser.add_argument('--reference', type=Path, default=Path('reports/public_accuracy_v2/pixel_references.json'))
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--tasks', nargs='+', choices=list(PROMPTS), default=list(PROMPTS))
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--max-new-tokens', type=int, default=4096)
    parser.add_argument('--max-seconds', type=float, default=240)
    args = parser.parse_args()
    if args.max_new_tokens < 1 or args.max_seconds <= 0: parser.error('Budgets must be positive')
    # Reference NAMES choose images. Reference labels never enter the recognizer.
    names = json.loads(args.reference.read_text(encoding='utf-8'))['images']
    images = [args.images/name for name in names]
    for path in images:
        if not path.is_file(): raise FileNotFoundError(path)
    identity = {'model': MODEL, 'recipe': 'native-paddle-v1', 'tasks': args.tasks,
                'max_pixels': MAX_PIXELS, 'max_new_tokens': args.max_new_tokens, 'max_seconds': args.max_seconds,
                'dtype': 'float16' if args.device.startswith('cuda') else 'float32'}
    recognizer = PaddleRecognizer(device=args.device)
    try:
        run_pilot(images, args.output_dir, recognizer, args.tasks, identity)
    finally:
        recognizer.close()
    print('Saved', args.output_dir / 'paddle_pilot.json', flush=True)
    print('Experimental native OCR output; compare against pixels before choosing the production reader.', flush=True)


if __name__ == '__main__': main()
