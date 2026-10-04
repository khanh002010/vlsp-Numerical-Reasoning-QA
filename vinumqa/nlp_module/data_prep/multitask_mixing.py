"""
Multitask Mixing.
Mixes secondary tasks (like table summarization or coordinate perception) into the main QA dataset
to improve the model's structural understanding, inspired by ChartAssistant.
"""

import json
import os
import random

def create_summarization_task(sample: dict) -> dict:
    """
    Given a dataset sample, create a summarization task if it has text/tables.
    """
    tables = sample.get("input", "")
    if "**Table" not in tables:
        return None
        
    return {
        "instruction": "Hãy tóm tắt nội dung chính của bảng dữ liệu dưới đây trong 1-2 câu.",
        "input": tables,
        "output": "Bảng dữ liệu cung cấp thông tin chi tiết về các chỉ số được trích xuất." # Dummy generic response
    }

def mix_multitask_data(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        return
        
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    mixed_data = []
    for sample in data:
        mixed_data.append(sample)
        # Add summarization task 10% of the time
        if random.random() < 0.1:
            summary_task = create_summarization_task(sample)
            if summary_task:
                mixed_data.append(summary_task)
                
    random.shuffle(mixed_data)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mixed_data, f, ensure_ascii=False, indent=2)
        
    print(f"Mixed multitask data saved to {output_path} (Total: {len(mixed_data)})")

if __name__ == "__main__":
    print("Multitask mixing module ready.")
