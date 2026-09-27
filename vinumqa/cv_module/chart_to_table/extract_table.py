"""
Chart-to-Table extraction using a Vision Language Model (VLM).
This module uses Qwen2-VL-2B-Instruct to convert chart images into Markdown tables.
"""

import torch
from typing import Union, List, Dict
from PIL import Image
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
    from qwen_vl_utils import process_vision_info
except ImportError:
    print("Please install transformers and qwen_vl_utils: pip install transformers qwen-vl-utils")


class ChartToTableExtractor:
    def __init__(self, model_id: str = "Qwen/Qwen2-VL-2B-Instruct", device: str = "cuda"):
        """
        Initialize the Chart-to-Table extractor.
        Uses Qwen2-VL-2B-Instruct by default as it fits on T4 (16GB) and supports Vietnamese.
        """
        self.device = device if torch.cuda.is_available() else "cpu"
        print(f"Loading {model_id} on {self.device}...")
        
        try:
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                model_id, 
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            self.processor = AutoProcessor.from_pretrained(model_id)
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.model = None
            self.processor = None
            
        self.system_prompt = (
            "You are an expert data analyst. Convert the following chart image into a well-structured "
            "Markdown table. Extract all text, labels, and numerical values accurately. "
            "Preserve the original language (Vietnamese) and formatting of the numbers. "
            "Output ONLY the markdown table, without any conversational text or explanation."
        )

    def extract(self, image_path: str) -> str:
        """
        Extract a Markdown table from a chart image.
        """
        if self.model is None or self.processor is None:
            return "| Lỗi | Model chưa được load |\n|---|---|\n| N/A | N/A |"
            
        try:
            image = Image.open(image_path).convert("RGB")
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": self.system_prompt},
                    ],
                }
            ]
            
            # Preparation for inference
            text = self.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            image_inputs, video_inputs = process_vision_info(messages)
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            inputs = inputs.to(self.device)

            # Inference
            generated_ids = self.model.generate(**inputs, max_new_tokens=1024)
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = self.processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )
            
            return output_text[0].strip()
            
        except Exception as e:
            print(f"Error extracting table from {image_path}: {e}")
            return f"| Lỗi | {str(e)} |\n|---|---|"

    def extract_batch(self, image_paths: List[str]) -> List[str]:
        """
        Extract Markdown tables from a batch of chart images.
        (Simplified sequential implementation for now; can be optimized for actual batching)
        """
        return [self.extract(path) for path in image_paths]


if __name__ == "__main__":
    # Test script
    extractor = ChartToTableExtractor()
    
    # Example usage:
    # table_md = extractor.extract("path/to/chart.png")
    # print(table_md)
    print("ChartToTableExtractor module is ready.")
