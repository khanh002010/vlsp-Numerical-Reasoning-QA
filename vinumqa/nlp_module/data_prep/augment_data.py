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
    
    # We want num_samples distributed across rare operators
    rare_ops = ["exp", "chart_total", "chart_sum", "table_sum"]
    samples_per_op = num_samples // len(rare_ops)
    
    for _ in range(samples_per_op):
        # exp
        val1 = round(random.uniform(1.0, 5.0), 2)
        val2 = random.randint(2, 5)
        question = f"Tính {val1} mũ {val2}."
        program = f"exp({val1}; {val2})"
        samples.append({
            "instruction": "Step 1 - Extractor: Tu bang va van ban duoi day, hay trich xuat cac gia tri so va thong tin lien quan de tra loi cau hoi.\nStep 2 - Reasoner: Dua tren cac gia tri da trich xuat, hay sinh ra cong thuc tinh toan duoi dang reasoning program.",
            "input": f"### Context\n\n### Question\n{question}",
            "output": f"| Step | Output |\n|---|---|\n| 1 | {val1}#{val2} |\n| 2 | {program} |"
        })
        
        # chart_total
        img = f"Image {random.randint(1, 5)}"
        lbl = f"Thang {random.randint(1, 12)}"
        question = f"Tổng giá trị trong {img} tại {lbl} là bao nhiêu?"
        program = f"chart_total({img}; {lbl}; none; none)"
        samples.append({
            "instruction": "Step 1 - Extractor: Tu bang va van ban duoi day, hay trich xuat cac gia tri so va thong tin lien quan de tra loi cau hoi.\nStep 2 - Reasoner: Dua tren cac gia tri da trich xuat, hay sinh ra cong thuc tinh toan duoi dang reasoning program.",
            "input": f"### Context\n\n### Question\n{question}",
            "output": f"| Step | Output |\n|---|---|\n| 1 | {img}#{lbl}#none |\n| 2 | {program} |"
        })

        # chart_sum
        img = f"Image {random.randint(1, 5)}"
        series = f"Series {random.randint(1, 5)}"
        question = f"Tổng của {series} trong {img} là bao nhiêu?"
        program = f"chart_sum({img}; {series}; none; none)"
        samples.append({
            "instruction": "Step 1 - Extractor: Tu bang va van ban duoi day, hay trich xuat cac gia tri so va thong tin lien quan de tra loi cau hoi.\nStep 2 - Reasoner: Dua tren cac gia tri da trich xuat, hay sinh ra cong thuc tinh toan duoi dang reasoning program.",
            "input": f"### Context\n\n### Question\n{question}",
            "output": f"| Step | Output |\n|---|---|\n| 1 | {img}#{series}#none |\n| 2 | {program} |"
        })

        # table_sum
        tbl = f"Table {random.randint(1, 5)}"
        col = f"Column {random.randint(1, 5)}"
        r1 = f"Row {random.randint(1, 5)}"
        r2 = f"Row {random.randint(6, 10)}"
        question = f"Tổng của {col} trong {tbl} từ {r1} đến {r2} là bao nhiêu?"
        program = f"table_sum({tbl}; {col}; {r1}; {r2})"
        samples.append({
            "instruction": "Step 1 - Extractor: Tu bang va van ban duoi day, hay trich xuat cac gia tri so va thong tin lien quan de tra loi cau hoi.\nStep 2 - Reasoner: Dua tren cac gia tri da trich xuat, hay sinh ra cong thuc tinh toan duoi dang reasoning program.",
            "input": f"### Context\n\n### Question\n{question}",
            "output": f"| Step | Output |\n|---|---|\n| 1 | {tbl}#{col}#{r1}#{r2} |\n| 2 | {program} |"
        })
        
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
