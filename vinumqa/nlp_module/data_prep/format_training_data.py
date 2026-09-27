"""
Format the ViNumQA data into the Step-wise Pipeline instruction format.
This prepares the data for QLoRA fine-tuning of the NLP module (Qwen2.5-7B).
"""

import json
import os
import re
from typing import List, Dict

def extract_values_from_program(program: str) -> str:
    """
    Extract the arguments from a reasoning program to act as the 'evidence' for Step 1.
    For example: 'chart_at(Image 1; P/B trượt; Jul-21; none); subtract(#0; 2.1)'
    Returns: 'Image 1#P/B trượt#Jul-21#none#2.1'
    """
    pattern = r'\(([^)]*)\)'
    matches = re.finditer(pattern, program)
    
    values = []
    for match in matches:
        args_str = match.group(1)
        args = [a.strip() for a in args_str.split(';')]
        for arg in args:
            # Skip references to previous steps
            if not arg.startswith('#'):
                values.append(arg)
                
    # Remove duplicates while preserving order
    seen = set()
    unique_values = []
    for v in values:
        if v not in seen:
            seen.add(v)
            unique_values.append(v)
            
    return "#".join(unique_values)

def dict_to_markdown_table(table_dict: Dict) -> str:
    """
    Convert the table HTML string in the dataset to Markdown.
    (Assuming the dictionary values are HTML strings, as seen in data analysis).
    """
    import pandas as pd
    from bs4 import BeautifulSoup

    md_tables = []
    for table_name, table_html in table_dict.items():
        try:
            # Parse HTML table
            soup = BeautifulSoup(table_html, 'html.parser')
            table_tag = soup.find('table')
            if not table_tag:
                continue
                
            # Convert to Pandas DataFrame
            # pandas read_html expects a string or file-like object containing HTML
            dfs = pd.read_html(str(table_tag))
            if dfs:
                df = dfs[0]
                # Convert DataFrame to Markdown
                md_table = df.to_markdown(index=False)
                md_tables.append(f"**{table_name}**\n{md_table}")
        except Exception as e:
            md_tables.append(f"**{table_name}**\n[Lỗi parsing HTML: {e}]")
            
    return "\n\n".join(md_tables)

def format_sample(sample: Dict) -> Dict:
    """
    Format a single sample into the Step-wise Pipeline instruction format.
    """
    question = sample['qa']['question']
    program = sample['qa']['program']
    
    # Process Texts
    texts = "\n".join(sample.get('text', []))
    
    # Process Tables
    tables_dict = sample.get('tables', {})
    tables_md = dict_to_markdown_table(tables_dict)
    
    # Process Images (list them for reference, actual extraction handled by CV module)
    images = ", ".join(list(sample.get('images', {}).keys()))
    
    # 1. Extractor Step
    extracted_values = extract_values_from_program(program)
    
    instruction = (
        "### Instruction\n"
        "Step 1 - Extractor: Từ bảng và văn bản dưới đây, hãy trích xuất các giá trị số và thông tin liên quan để trả lời câu hỏi.\n"
        "Step 2 - Reasoner: Dựa trên các giá trị đã trích xuất, hãy sinh ra công thức tính toán dưới dạng reasoning program.\n\n"
        "Các hàm được phép: add, subtract, multiply, divide, greater, exp, table_max, table_min, table_sum, table_average, chart_at, chart_max, chart_min, chart_sum, chart_average\n"
        "Dùng #0, #1, ... để tham chiếu kết quả bước trước."
    )
    
    context = ""
    if tables_md:
        context += f"### Table\n{tables_md}\n\n"
    if texts:
        context += f"### Text\n{texts}\n\n"
    if images:
        context += f"### Images Available\n{images}\n\n"
        
    context += f"### Question\n{question}"
    
    response = (
        "| Step | Output |\n"
        "|---|---|\n"
        f"| 1 | {extracted_values} |\n"
        f"| 2 | {program} |"
    )
    
    # Format for LLM fine-tuning (e.g., standard Alpaca or ChatML format)
    # Here we use a generic instruction/input/output format
    formatted = {
        "instruction": instruction,
        "input": context,
        "output": response
    }
    
    return formatted

def main():
    data_dir = r"d:\VS CODE\vlsp Numerical Reasoning QA\vinumqa\data"
    
    for split in ["train_split", "val_split"]:
        input_path = os.path.join(data_dir, f"{split}.json")
        output_path = os.path.join(data_dir, f"{split}_formatted.json")
        
        if not os.path.exists(input_path):
            print(f"Skipping {input_path} (not found)")
            continue
            
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Formatting {len(data)} samples from {split}...")
        
        formatted_data = []
        for sample in data:
            formatted_data.append(format_sample(sample))
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, ensure_ascii=False, indent=2)
            
        print(f"Saved formatted data to {output_path}")

if __name__ == "__main__":
    main()
