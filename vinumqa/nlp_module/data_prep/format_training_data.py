"""
Format the ViNumQA data into the Step-wise Pipeline instruction format.
This prepares the data for QLoRA fine-tuning of the NLP module (Qwen2.5-7B).
"""

import json
import os
import re
from typing import List, Dict

from vinumqa.nlp_module.dsl_operators import get_dsl_system_prompt

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
    from io import StringIO

    md_tables = []
    for table_name, table_html in table_dict.items():
        try:
            # Parse HTML table
            soup = BeautifulSoup(table_html, 'html.parser')
            table_tag = soup.find('table')
            if not table_tag:
                continue
                
            # Convert to Pandas DataFrame
            # wrap in StringIO to avoid pandas FutureWarning
            dfs = pd.read_html(StringIO(str(table_tag)))
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
    Uses inline placeholder injection (same logic as full_pipeline.py)
    to replace ### Image N ### and ### Table N ### with actual content.
    """
    question = sample['qa']['question']
    program = sample['qa']['program']

    # --- Build inline context (placeholders replaced inline) ---
    placeholder_re = re.compile(
        r'^###\s*(Image|Table)\s+(\d+)\s*###$', re.IGNORECASE
    )
    tables_md_map = {}
    if sample.get('tables'):
        for k, v in sample['tables'].items():
            tables_md_map[k] = dict_to_markdown_table({k: v})

    # Images: during training we reference them by name only (CV output used at inference)
    image_keys = list(sample.get('images', {}).keys())
    image_placeholder_map = {
        k: f"[Chart: {k} - extracted by CV Module]" for k in image_keys
    }

    result_segs = []
    for seg in sample.get('text', []):
        m = placeholder_re.match(seg.strip())
        if m:
            kind = m.group(1).capitalize()
            num  = m.group(2)
            key  = f"{kind} {num}"
            if kind == 'Table' and key in tables_md_map:
                result_segs.append(tables_md_map[key])
            elif kind == 'Image' and key in image_placeholder_map:
                result_segs.append(image_placeholder_map[key])
            # silently drop unmatched placeholders
        else:
            result_segs.append(seg)

    inline_context = "\n\n".join(result_segs)
    if image_keys:
        inline_context += f"\n\n### Images Available\n{', '.join(image_keys)}"

    # 1. Extractor Step
    extracted_values = extract_values_from_program(program)

    # DSL System Prompt (identical to inference prompt)
    dsl_prompt = get_dsl_system_prompt()

    instruction = (
        "### Instruction\n"
        "Step 1 - Extractor: Tu bang va van ban duoi day, hay trich xuat cac gia tri so "
        "va thong tin lien quan de tra loi cau hoi.\n"
        "Step 2 - Reasoner: Dua tren cac gia tri da trich xuat, hay sinh ra cong thuc "
        "tinh toan duoi dang reasoning program.\n\n"
        f"{dsl_prompt}\n\n"
        "Dung #0, #1, ... de tham chieu ket qua buoc truoc."
    )

    context = f"### Context\n{inline_context}\n\n### Question\n{question}"

    response = (
        "| Step | Output |\n"
        "|---|---|\n"
        f"| 1 | {extracted_values} |\n"
        f"| 2 | {program} |"
    )

    return {
        "instruction": instruction,
        "input": context,
        "output": response,
    }

def main():
    TRAIN_JSON = r"d:\VS CODE\vlsp Numerical Reasoning QA\data\train\train.json"
    TEST_JSON  = r"d:\VS CODE\vlsp Numerical Reasoning QA\data\public_test\public_test.json"
    OUT_DIR = r"d:\VS CODE\vlsp Numerical Reasoning QA\vinumqa\data"
    os.makedirs(OUT_DIR, exist_ok=True)

    with open(TRAIN_JSON, 'r', encoding='utf-8') as f:
        train_data = json.load(f)

    with open(TEST_JSON, 'r', encoding='utf-8') as f:
        val_data = json.load(f)

    for name, data in [("train_split", train_data), ("val_split", val_data)]:
        out_path = os.path.join(OUT_DIR, f"{name}_formatted.json")
        print(f"Formatting {len(data)} samples -> {out_path}")
        formatted = [format_sample(s) for s in data]
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(formatted, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(formatted)} samples to {out_path}")


if __name__ == "__main__":
    main()
