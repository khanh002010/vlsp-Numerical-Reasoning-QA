"""
Inference script to generate reasoning programs from text and tables using the fine-tuned NLP module.
"""

import torch
import re
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
from vinumqa.nlp_module.inference.constrained_decode import DSLLogitsProcessor
from vinumqa.nlp_module.data_prep.format_training_data import DSL_HINT_SHORT


class ProgramGenerator:
    def __init__(
        self,
        base_model_id: str = "Qwen/Qwen2.5-7B-Instruct",
        lora_weights: str = None,
        device: str = "cuda",
        use_constrained_decoding: bool = True,
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
        self.device = device if torch.cuda.is_available() else "cpu"
        self.use_constrained_decoding = use_constrained_decoding
        print(f"Loading {base_model_id} on {self.device}...")

        self.tokenizer = None
        self.model = None
        self.dsl_processor = None
        self.dsl_hint = DSL_HINT_SHORT

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(base_model_id)

            # Load in 4-bit QLoRA — SAME as training setup.
            # Fixes 2 problems:
            #   1. OOM: FP16 7B model takes ~14GB but T4 only has 14.56GB total.
            #           4-bit reduces to ~4GB, leaving room for CV model (~4.5GB).
            #   2. torchao incompatibility: BnB 4-bit bypasses the torchao
            #      dispatch path in PEFT's inject_adapter.
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                base_model_id,
                quantization_config=bnb_config,
                device_map="auto",
            )

            if lora_weights:
                print(f"Loading LoRA weights from {lora_weights}...")
                self.model = PeftModel.from_pretrained(self.model, lora_weights)

            self.model.eval()

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

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        # Build logits_processor list
        logits_processor = []
        if self.use_constrained_decoding and self.dsl_processor is not None:
            logits_processor.append(self.dsl_processor)

        try:
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=768,
                    temperature=0.0,    # Greedy decoding — deterministic
                    do_sample=False,
                    logits_processor=logits_processor,
                )

            response_text = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:],
                skip_special_tokens=True,
            )

            # Always log raw output for diagnosis
            print(f"[DEBUG] Raw model output: {repr(response_text[:300])}")

            return self._parse_response(response_text)

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
        # DSL hint formatting exactly as in val data
        dsl_line = f"\n{self.dsl_hint}\n"
        
        instruction = (
            "### Instruction\n"
            "Step 1 - Extractor: Tu bang va van ban duoi day, hay trich xuat cac gia tri so "
            "va thong tin lien quan de tra loi cau hoi.\n"
            "Step 2 - Reasoner: Dua tren cac gia tri da trich xuat, hay sinh ra cong thuc "
            f"tinh toan duoi dang reasoning program.{dsl_line}\n"
            "Dung #0, #1, ... de tham chieu ket qua buoc truoc."
        )

        # Build inline context similar to training
        inline_context = context_text
        if markdown_table:
            # If a separate table is provided, append it
            inline_context += f"\n\n{markdown_table}"
            
        if images_available_str:
            inline_context += f"\n\n### Images Available\n{images_available_str}"

        # EXACT match with train format: "### Context\n..."
        context = f"### Context\n{inline_context.strip()}\n\n### Question\n{question}"

        # In qlora, the prompt given to the model includes the response prefix
        prompt = f"{instruction}\n\n{context}\n\n### Response\n| Step | Output |\n|---|---|\n"
        return prompt

    def _parse_response(self, response_text: str) -> dict:
        """
        Parse the markdown table generated by the LLM.
        Uses regex to be robust against minor whitespace variations.
        Returns: {extracted_values, program}. No answer field (executor removed).
        """
        result = {
            "extracted_values": "",
            "program": "",
        }

        # Robust regex: handles | 1 |, |1|, | 1|, etc.
        step1_match = re.search(r'\|\s*1\s*\|\s*(.+?)\s*\|', response_text)
        step2_match = re.search(r'\|\s*2\s*\|\s*(.+?)\s*\|', response_text)

        if step1_match:
            result["extracted_values"] = step1_match.group(1).strip()
        if step2_match:
            result["program"] = step2_match.group(1).strip()

        if not result["program"]:
            print(f"[WARNING] Could not parse program from response. Full text: {repr(response_text[:500])}")

        return result


if __name__ == "__main__":
    print("ProgramGenerator module is ready.")
    print("NOTE: Run train_qlora.py first to produce LoRA weights before inference.")
