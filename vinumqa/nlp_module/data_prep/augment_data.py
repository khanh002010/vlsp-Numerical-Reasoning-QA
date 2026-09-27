"""
Data Augmentation for ViNumQA.
Generates synthetic reasoning programs based on simple templates to augment the dataset.
"""

import json
import random
import os

def generate_synthetic_samples(num_samples: int = 500) -> list:
    """
    Generate synthetic samples for basic arithmetic operations.
    """
    samples = []
    
    # Template 1: Add two numbers
    for _ in range(num_samples // 4):
        val1 = random.randint(10, 1000)
        val2 = random.randint(10, 1000)
        question = f"Tổng của {val1} và {val2} là bao nhiêu?"
        program = f"add({val1}; {val2})"
        samples.append({
            "instruction": "Step 1 - Extractor: Từ bảng và văn bản dưới đây, hãy trích xuất các giá trị số và thông tin liên quan để trả lời câu hỏi.\nStep 2 - Reasoner: Dựa trên các giá trị đã trích xuất, hãy sinh ra công thức tính toán dưới dạng reasoning program.",
            "input": f"### Question\n{question}",
            "output": f"| Step | Output |\n|---|---|\n| 1 | {val1}#{val2} |\n| 2 | {program} |"
        })
        
    # Add more templates as needed...
    
    return samples

def augment_dataset(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        return
        
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    synthetic = generate_synthetic_samples(100)
    data.extend(synthetic)
    
    random.shuffle(data)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Augmented data saved to {output_path} (Total: {len(data)})")

if __name__ == "__main__":
    print("Data augmentation module ready.")
