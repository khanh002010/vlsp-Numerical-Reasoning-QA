"""
Inference script to generate reasoning programs from text and tables using the fine-tuned NLP module.
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from vinumqa.nlp_module.inference.symbolic_executor import SymbolicExecutor
from vinumqa.nlp_module.inference.constrained_decode import DSLLogitsProcessor
from vinumqa.nlp_module.data_prep.format_training_data import DSL_HINT_SHORT
import re


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

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(base_model_id)
            self.model = AutoModelForCausalLM.from_pretrained(
                base_model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
            )

            if lora_weights:
                print(f"Loading LoRA weights from {lora_weights}...")
                self.model = PeftModel.from_pretrained(self.model, lora_weights)

            self.model.eval()
            self.executor = SymbolicExecutor()

            # DSL Constrained Decoder (Problem 2 fix)
            if self.use_constrained_decoding:
                self.dsl_processor = DSLLogitsProcessor(self.tokenizer)
                print("DSL Constrained Decoder: ACTIVE")
            else:
                self.dsl_processor = None
                print("DSL Constrained Decoder: DISABLED")

            # DSL short hint (same as val data format — consistent train/val/inference)
            self.dsl_hint = DSL_HINT_SHORT

            print("NLP Module loaded successfully.")
        except Exception as e:
            print(f"Failed to load NLP module: {e}")
            self.model = None

    def generate(
        self,
        context_text: str,
        markdown_table: str,
        images_available_str: str,
        question: str,
    ) -> dict:
        """
        Generate a reasoning program and execute it.
        Returns a dict with 'extracted_values', 'program', and 'answer'.
        """
        if self.model is None:
            return {"error": "Model not loaded"}

        prompt = self._build_prompt(context_text, markdown_table, images_available_str, question)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        # Build logits_processor list (empty list = unconstrained)
        logits_processor = []
        if self.use_constrained_decoding and self.dsl_processor is not None:
            logits_processor.append(self.dsl_processor)

        try:
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=256,
                    temperature=0.0,    # Greedy decoding for deterministic reasoning
                    do_sample=False,
                    logits_processor=logits_processor,
                )

            response_text = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:],
                skip_special_tokens=True,
            )
            return self._parse_response(response_text)

        except Exception as e:
            return {"error": str(e)}

    def _build_prompt(
        self,
        context_text: str,
        markdown_table: str,
        images_available_str: str,
        question: str,
    ) -> str:
        """
        Build the prompt following the Step-wise Pipeline format.
        DSL operator definitions from dsl_operators.py are injected into the
        instruction so the model always has the authoritative DSL reference.
        """
        instruction = (
            "### Instruction\n"
            "Step 1 - Extractor: Tu bang va van ban duoi day, hay trich xuat cac gia tri so "
            "va thong tin lien quan de tra loi cau hoi.\n"
            "Step 2 - Reasoner: Dua tren cac gia tri da trich xuat, hay sinh ra cong thuc "
            f"tinh toan duoi dang reasoning program.\n{self.dsl_hint}\n"
            "Dung #0, #1, ... de tham chieu ket qua buoc truoc."
        )

        context = ""
        if markdown_table:
            context += f"\n\n### Table\n{markdown_table}"
        if context_text:
            context += f"\n\n### Text\n{context_text}"
        if images_available_str:
            context += f"\n\n### Images Available\n{images_available_str}"

        context += f"\n\n### Question\n{question}\n\n### Response\n| Step | Output |\n|---|---|\n"

        return instruction + context

    def _parse_response(self, response_text: str) -> dict:
        """
        Parse the markdown table generated by the LLM to extract values and program.
        """
        result = {
            "extracted_values": "",
            "program": "",
            "answer": "",
        }

        lines = response_text.strip().split("\n")
        for line in lines:
            if line.startswith("| 1 |"):
                parts = line.split("|")
                if len(parts) >= 3:
                    result["extracted_values"] = parts[2].strip()
            elif line.startswith("| 2 |"):
                parts = line.split("|")
                if len(parts) >= 3:
                    result["program"] = parts[2].strip()

        # Execute the program via Symbolic Executor
        if result["program"]:
            result["answer"] = self.executor.execute(result["program"])

        return result


if __name__ == "__main__":
    print("ProgramGenerator module is ready.")
    print("NOTE: Run train_qlora.py first to produce LoRA weights before inference.")
