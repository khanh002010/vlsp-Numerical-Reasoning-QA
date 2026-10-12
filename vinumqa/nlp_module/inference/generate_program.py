"""
Inference script to generate reasoning programs from text and tables using the fine-tuned NLP module.
"""

import torch
import re
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, StoppingCriteriaList
from vinumqa.nlp_module.inference.constrained_decode import DSLLogitsProcessor
from vinumqa.nlp_module.contracts import DSL_HINT_SHORT, build_prompt, parse_response, FORMAT_VERSION, INSTRUCTION
from vinumqa.utils.dsl_parser import validate_program
from pathlib import Path
import json
import hashlib
from contextlib import nullcontext
import time
from vinumqa.nlp_module.inference.generation_runtime import GenerationProgress, placement, eos_ids


class ProgramGenerator:
    def __init__(
        self,
        base_model_id: str = "Qwen/Qwen2.5-7B-Instruct",
        lora_weights: str = None,
        device: str = "cuda",
        use_constrained_decoding: bool = True,
        allow_legacy_adapter: bool = False,
        max_generation_seconds: float = 120,
        progress_seconds: float = 30,
    ):
        """
        Initialize the Program Generator (NLP Module).

        Args:
            base_model_id:              HuggingFace model ID (must be fine-tuned via train_qlora.py).
            lora_weights:               Path to QLoRA adapter directory (output of train_qlora.py).
            device:                     'cuda' or 'cpu'.
            use_constrained_decoding:   If True, activates DSLLogitsProcessor to prevent
                                        the model from generating unknown operators.
        """
        if max_generation_seconds <= 0 or progress_seconds <= 0:
            raise ValueError('Generation time and progress interval must be positive')
        self.device, device_map = placement(device, torch.cuda.is_available())
        self.max_generation_seconds = max_generation_seconds
        self.progress_seconds = progress_seconds
        cuda = self.device.startswith('cuda')
        self.use_constrained_decoding = use_constrained_decoding
        print(f"Loading {base_model_id} on {self.device}...")

        self.tokenizer = None
        self.model = None
        self.dsl_processor = None
        self.dsl_hint = DSL_HINT_SHORT

        if lora_weights and not allow_legacy_adapter:
            manifest = Path(lora_weights) / "pipeline_manifest.json"
            info = json.loads(manifest.read_text(encoding="utf-8")) if manifest.is_file() else {}
            if (info.get("format_version") != FORMAT_VERSION
                or info.get("base_model") != base_model_id
                or info.get("prompt_sha256") != hashlib.sha256(INSTRUCTION.encode()).hexdigest()):
                raise ValueError("Adapter contract mismatch. Retrain with chart structures or explicitly allow a legacy comparison.")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(lora_weights if lora_weights and not allow_legacy_adapter else base_model_id)
            self.tokenizer.pad_token = self.tokenizer.eos_token

            # Match the 4-bit training setup. The orchestrator releases CV before loading NLP.
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
            ) if cuda else None
            self.model = AutoModelForCausalLM.from_pretrained(
                base_model_id,
                quantization_config=bnb_config,
                device_map=device_map,
                dtype=torch.float16 if cuda else torch.float32,
                attn_implementation="sdpa",
            )

            if lora_weights:
                from peft import PeftModel
                print(f"Loading LoRA weights from {lora_weights}...")
                self.model = PeftModel.from_pretrained(self.model, lora_weights)

            self.model.eval()
            if cuda:
                from vinumqa.nlp_module.training.memory_attention import register_memory_attention
                self.model.set_attn_implementation(register_memory_attention())
            self.model.config.use_cache = True
            print(f'[NLP placement] device_map={getattr(self.model, "hf_device_map", device_map)}; '
                  f'compute_dtype={"float16" if cuda else "float32"}', flush=True)

            # DSL Constrained Decoder
            if self.use_constrained_decoding:
                self.dsl_processor = DSLLogitsProcessor(self.tokenizer)
                print("DSL Constrained Decoder: ACTIVE")
            else:
                print("DSL Constrained Decoder: DISABLED")

            print("NLP Module loaded successfully.")
        except Exception as e:
            # Print full error so it's visible in logs — do NOT swallow silently
            import traceback
            print(f"[ERROR] Failed to load NLP module: {e}")
            traceback.print_exc()
            self.model = None
            raise RuntimeError("NLP model/adapter initialization failed") from e

    def generate(
        self,
        context_text: str,
        markdown_table: str,
        images_available_str: str,
        question: str,
    ) -> dict:
        """
        Generate a reasoning program.
        Returns a dict with 'extracted_values' and 'program'. No answer execution.
        """
        if self.model is None:
            print("[ERROR] Model not loaded. Cannot generate.")
            return {"error": "Model not loaded", "extracted_values": "", "program": ""}

        prompt = self._build_prompt(context_text, markdown_table, images_available_str, question)
        return self.generate_with_prompt(prompt)

    def generate_with_prompt(self, prompt: str) -> dict:
        """
        Generate a reasoning program directly from a raw prompt string.
        """
        if self.model is None:
            print("[ERROR] Model not loaded. Cannot generate.")
            return {"error": "Model not loaded", "extracted_values": "", "program": ""}

        inputs = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to(self.model.get_input_embeddings().weight.device)
        limit = getattr(self.model.config, "max_position_embeddings", 32768)
        if inputs.input_ids.shape[1] + 1536 > limit:
            return {"error": "Prompt exceeds model context budget", "program": "", "extracted_values": ""}

        # Build logits_processor list
        logits_processor = []
        if self.use_constrained_decoding and self.dsl_processor is not None:
            self.dsl_processor.reset(inputs.input_ids.shape[1])
            logits_processor.append(self.dsl_processor)

        started = time.monotonic()
        prompt_tokens = inputs.input_ids.shape[1]
        print(f'[NLP generate] prompt_tokens={prompt_tokens}; max_new_tokens=1536; '
              f'soft_time_limit={self.max_generation_seconds}s; device={self.device}', flush=True)
        try:
            precision = torch.autocast("cuda", dtype=torch.float16) if self.device.startswith('cuda') else nullcontext()
            progress = GenerationProgress(prompt_tokens, self.progress_seconds)
            with progress, torch.inference_mode(), precision:
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=1536,
                    pad_token_id=self.tokenizer.pad_token_id,
                    do_sample=False,
                    logits_processor=logits_processor,
                    max_time=self.max_generation_seconds,
                    stopping_criteria=StoppingCriteriaList([progress]),
                )

            response_text = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:],
                skip_special_tokens=True,
            )

            # Always log raw output for diagnosis
            print(f"[DEBUG] Raw model output (first 300 chars): {repr(response_text[:300])}", flush=True)

            result = self._parse_response(response_text)
            result["prompt_sha256"] = hashlib.sha256(prompt.encode()).hexdigest()
            result["generated_tokens"] = outputs.shape[1] - inputs.input_ids.shape[1]
            result['prompt_tokens'] = prompt_tokens
            result['generation_seconds'] = round(time.monotonic() - started, 2)
            result["termination"] = "eos" if int(outputs[0][-1]) in eos_ids(self.model.generation_config, self.tokenizer) else "length_or_stop"
            if result["termination"] != "eos":
                result.update(valid=False, error="Generation stopped before EOS")
            print(f'[NLP generated] tokens={result["generated_tokens"]}; '
                  f'seconds={result["generation_seconds"]}; termination={result["termination"]}', flush=True)
            return result

        except Exception as e:
            import traceback
            print(f"[ERROR] Generation failed: {e}")
            traceback.print_exc()
            return {"error": str(e), "extracted_values": "", "program": ""}

    def _build_prompt(
        self,
        context_text: str,
        markdown_table: str,
        images_available_str: str,
        question: str,
    ) -> str:
        """
        Build the prompt exactly matching the training data format.
        """
        context = context_text + ("\n\n" + markdown_table if markdown_table else "")
        return build_prompt(context, question, images_available_str)

    def _parse_response(self, response_text: str) -> dict:
        """
        Parse the markdown table generated by the LLM.
        Uses regex to be robust against minor whitespace variations.
        Returns: {extracted_values, program}. No answer field (executor removed).
        """
        return parse_response(response_text)

    def close(self):
        import gc
        self.model = None
        self.tokenizer = None
        self.dsl_processor = None
        gc.collect()
        if torch.cuda.is_available(): torch.cuda.empty_cache()
