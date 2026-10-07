"""Chart-to-table OCR with bounded retries and early repetition detection."""
import copy
import time
from pathlib import Path

import torch
from PIL import Image
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration, StoppingCriteria, StoppingCriteriaList
from qwen_vl_utils import process_vision_info

from vinumqa.cv_module.chart_to_table.backend import select_attention_backend
from vinumqa.cv_module.chart_to_table.model_files import resolve_model_directory
from vinumqa.cv_module.chart_to_table.token_budget import initial_token_budget, budget_schedule, reached_eos, MAX_NEW_TOKENS
from vinumqa.cv_module.chart_to_table.quality import OCR_PROMPT, FALLBACK_PROMPT, OCR_VERSION, repetition_reason, extract_with_retries

MAX_PIXELS = 750_000


def preprocess_image(image):
    w, h = image.size
    if w * h > MAX_PIXELS:
        scale = (MAX_PIXELS / (w * h)) ** 0.5
        return image.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)
    return image


class RepetitionStop(StoppingCriteria):
    """Check a short decoded suffix periodically, ignoring the input prompt."""
    def __init__(self, processor, input_length):
        self.processor = processor
        self.input_length = input_length
        self.reason = None

    def __call__(self, input_ids, scores, **kwargs):
        count = input_ids.shape[1] - self.input_length
        if count >= 128 and count % 32 == 0:
            tail = input_ids[:, max(self.input_length, input_ids.shape[1] - 512):]
            text = self.processor.batch_decode(tail, skip_special_tokens=True,
                                                clean_up_tokenization_spaces=False)[0]
            self.reason = repetition_reason(text)
        return torch.full((input_ids.shape[0],), self.reason is not None,
                          device=input_ids.device, dtype=torch.bool)


class ChartToTableExtractor:
    def __init__(self, model_id="Qwen/Qwen2-VL-2B-Instruct", device="cuda"):
        self.device = device if torch.cuda.is_available() else "cpu"
        print(f"Loading {model_id} on {self.device}...", flush=True)
        from transformers.utils import is_flash_attn_2_available
        capabilities = ([torch.cuda.get_device_capability(i) for i in range(torch.cuda.device_count())]
                        if self.device == "cuda" else [])
        attention = select_attention_backend(capabilities, is_flash_attn_2_available())
        print(f"OCR attention backend: {attention}; GPU capabilities: {capabilities}", flush=True)
        model_directory = resolve_model_directory(model_id)
        self.processor = AutoProcessor.from_pretrained(
            model_directory, max_pixels=MAX_PIXELS, local_files_only=True)
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_directory, local_files_only=True,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None,
            attn_implementation=attention)
        self.model.eval()
        self.base_prompt = OCR_PROMPT
        # Normalize irrelevant sampling settings without mutating model defaults.
        self.generation_config = copy.deepcopy(self.model.generation_config)
        self.generation_config.do_sample = False
        self.generation_config.temperature = 1.0
        self.generation_config.top_p = 1.0
        self.generation_config.top_k = 50
        self.generation_config.num_beams = 1
        self.generation_config.num_return_sequences = 1
        self.last_generation = {}

    def prepare_inputs(self, image, prompt=None):
        messages = [{"role": "user", "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": prompt or self.base_prompt}]}]
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        images, videos = process_vision_info(messages)
        inputs = self.processor(text=[text], images=images, videos=videos, padding=True,
                                return_tensors="pt").to(self.device)
        return inputs, text

    def generate_once(self, inputs, budget):
        started = time.monotonic()
        guard = RepetitionStop(self.processor, inputs.input_ids.shape[1])
        with torch.inference_mode():
            output = self.model.generate(
                **inputs, max_new_tokens=budget, generation_config=self.generation_config,
                stopping_criteria=StoppingCriteriaList([guard]))
        ids = output[0, inputs.input_ids.shape[1]:].detach().cpu().tolist()
        eos = bool(ids) and reached_eos(ids[-1], self.generation_config.eos_token_id)
        text = self.processor.batch_decode([ids], skip_special_tokens=True,
                                          clean_up_tokenization_spaces=False)[0].strip()
        reason = guard.reason or repetition_reason(text)
        return {"text": text,
                "raw_text": self.processor.batch_decode([ids], skip_special_tokens=False,
                                                         clean_up_tokenization_spaces=False)[0],
                "token_ids": ids, "tokens": len(ids), "eos": eos,
                "stop_reason": "repetition" if reason else "eos" if eos else "token_limit",
                "seconds": round(time.monotonic() - started, 2)}

    def extract(self, image_path):
        self.last_generation = {"version": OCR_VERSION, "attempts": []}
        try:
            with Image.open(image_path) as source:
                image = preprocess_image(source.convert("RGB"))
            initial = initial_token_budget(image)
            self.last_generation["initial_budget"] = initial
            inputs, _ = self.prepare_inputs(image)
            fallback_inputs = None

            def generate(budget, fallback):
                nonlocal fallback_inputs
                if fallback and fallback_inputs is None:
                    fallback_inputs, _ = self.prepare_inputs(image, FALLBACK_PROMPT)
                print(f"[OCR] {Path(image_path).name}: generating, budget={budget}/{MAX_NEW_TOKENS}, "
                      f"prompt={'fallback' if fallback else 'primary'}", flush=True)
                result = self.generate_once(fallback_inputs if fallback else inputs, budget)
                print(f"[OCR] {Path(image_path).name}: tokens={result['tokens']}, "
                      f"stop={result['stop_reason']}, seconds={result['seconds']}", flush=True)
                return result

            return extract_with_retries(generate, budget_schedule(initial), self.last_generation["attempts"])
        except Exception as error:
            raise RuntimeError(f"CV extraction failed: {image_path}: {error}") from error

    def extract_batch(self, image_paths):
        return [self.extract(path) for path in image_paths]
