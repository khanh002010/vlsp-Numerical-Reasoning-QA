"""
Chart-to-Table extraction using a Vision Language Model (VLM).
This module uses Qwen2-VL-2B-Instruct to convert chart images into Markdown tables.
Includes Aspect Ratio classification and Smart Image Resizing (MAX_PIXELS).
"""

import torch
from typing import Union, List, Dict
from PIL import Image
import io
import sys
from vinumqa.cv_module.chart_to_table.token_budget import initial_token_budget, budget_schedule, reached_eos


try:
    from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
    from qwen_vl_utils import process_vision_info
except ImportError:
    print("Please install transformers and qwen_vl_utils: pip install transformers qwen-vl-utils")

# ==============================================================
# HELPER FUNCTIONS
# ==============================================================

MAX_PIXELS = 750_000
LANDSCAPE_RATIO_THRESHOLD = 1.2
SQUARE_RATIO_THRESHOLD = 0.8

def classify_chart_type(image: Image.Image) -> dict:
    """
    Phân loại loại biểu đồ dựa trên Aspect Ratio (Tỷ lệ khung hình).
    """
    w, h = image.size
    ratio = w / h if h > 0 else 1.0
    
    if ratio > LANDSCAPE_RATIO_THRESHOLD:
        return {
            'shape': 'Landscape',
            'prompt_hint': (
                "[CHART TYPE HINT - Landscape Chart]: Đây là biểu đồ nằm ngang (Cột / Đường / Vùng). "
                "Hãy đọc kỹ: (1) TRỤC X - thường là mốc thời gian (Tháng/Quý/Năm) hoặc danh mục; "
                "(2) TRỤC Y - thường là đơn vị số (Tỷ VNĐ, Tr. USD, %, điểm...); "
                "(3) LEGEND (Chú thích màu sắc) - xác định tên của từng series dữ liệu."
            )
        }
    elif SQUARE_RATIO_THRESHOLD <= ratio <= LANDSCAPE_RATIO_THRESHOLD:
        return {
            'shape': 'Square',
            'prompt_hint': (
                "[CHART TYPE HINT - Square Chart]: Có thể là biểu đồ tròn (Pie) hoặc biểu đồ cột/đường dạng vuông. "
                "Hãy đọc kỹ: (1) TÊN CÁC LÁT CẮT / TRỤC - nhãn tên của từng phần; "
                "(2) TỶ LỆ % HOẶC SỐ - con số ghi bên trong hoặc bên ngoài; "
                "(3) LEGEND - bảng chú thích màu nếu nhãn không hiển thị trực tiếp."
            )
        }
    else:
        return {
            'shape': 'Portrait',
            'prompt_hint': (
                "[CHART TYPE HINT - Portrait Chart]: Đây là biểu đồ dạng dọc. "
                "Hãy đọc kỹ các trục, nhãn dữ liệu và chú thích màu (nếu có)."
            )
        }

def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Chuẩn hóa ảnh: giữ nguyên Aspect Ratio, nhưng giới hạn pixel tối đa = MAX_PIXELS.
    Tránh OOM khi đi thi với ảnh độ phân giải quá cao.
    """
    w, h = image.size
    current_pixels = w * h
    
    if current_pixels > MAX_PIXELS:
        scale = (MAX_PIXELS / current_pixels) ** 0.5
        new_w = int(w * scale)
        new_h = int(h * scale)
        return image.resize((new_w, new_h), Image.LANCZOS)
    return image


# ==============================================================
# EXTRACTOR CLASS
# ==============================================================

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
                device_map="auto" if self.device == "cuda" else None,
                attn_implementation="flash_attention_2" if self.device == "cuda" else None
            )
            self.processor = AutoProcessor.from_pretrained(model_id, max_pixels=MAX_PIXELS)
            self.model.eval()
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.model = None
            self.processor = None
            raise RuntimeError("CV initialization failed") from e
            
        self.base_prompt = (
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
            raise RuntimeError("CV model not loaded")
            
        try:
            raw_image = Image.open(image_path).convert("RGB")
            
            # 1. Image Preprocessing (MAX_PIXELS)
            image = preprocess_image(raw_image)
            
            # 2. Chart Type Classification
            chart_info = classify_chart_type(image)
            prompt_hint = chart_info['prompt_hint']
            
            # 3. Combine prompt
            full_prompt = f"{prompt_hint}\n\n{self.base_prompt}"
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": full_prompt},
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

            # Retry only truncated outputs, never cache a partial table.
            self.last_generation = {"initial_budget": initial_token_budget(image), "attempts": []}
            for budget in budget_schedule(self.last_generation["initial_budget"]):
                with torch.inference_mode():
                    generated_ids = self.model.generate(**inputs, max_new_tokens=budget, do_sample=False)
                count = generated_ids.shape[1] - inputs.input_ids.shape[1]
                eos = reached_eos(generated_ids[0, -1], self.model.generation_config.eos_token_id)
                self.last_generation["attempts"].append({"budget": budget, "tokens": count, "eos": eos})
                if eos or count < budget:
                    break
            else:
                raise ValueError("CV output reached maximum 8192 tokens; incomplete table")
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = self.processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )
            
            return output_text[0].strip()
            
        except Exception as e:
            print(f"Error extracting table from {image_path}: {e}")
            raise RuntimeError(f"CV extraction failed: {image_path}") from e

    def extract_batch(self, image_paths: List[str]) -> List[str]:
        """
        Extract Markdown tables from a batch of chart images.
        (Simplified sequential implementation for now; can be optimized for actual batching)
        """
        return [self.extract(path) for path in image_paths]


if __name__ == "__main__":
    # Test script
    extractor = ChartToTableExtractor()
    print("ChartToTableExtractor module is ready.")
