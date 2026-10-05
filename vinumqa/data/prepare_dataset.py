"""
Prepare ViNumQA dataset: parse train.json, split train/val, analyze statistics.
"""

import json
import random
import os
import sys
import io
from collections import Counter, defaultdict
from pathlib import Path



# Add project root to path (Dynamic for Kaggle/Local)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from vinumqa.utils.dsl_parser import parse_program, validate_program, ALL_OPS, MATH_OPS, TABLE_OPS, CHART_OPS


def load_data(data_path: str) -> list:
    """Load train.json."""
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} samples from {data_path}")
    return data


def analyze_dataset(data: list):
    """Print comprehensive statistics about the dataset."""
    print("\n" + "=" * 60)
    print("DATASET ANALYSIS")
    print("=" * 60)
    
    # --- Operator distribution ---
    ops_counter = Counter()
    op_per_sample = []
    step_counts = Counter()
    
    for s in data:
        prog = s["qa"]["program"]
        steps = parse_program(prog)
        step_counts[len(steps)] += 1
        op_per_sample.append(len(steps))
        for step in steps:
            ops_counter[step.operator] += 1
    
    print(f"\nTotal samples: {len(data)}")
    print(f"\n--- Step count distribution ---")
    for n_steps, count in sorted(step_counts.items()):
        pct = count / len(data) * 100
        print(f"  {n_steps} steps: {count:5d} ({pct:5.1f}%)")
    
    print(f"\n--- Operator frequency ---")
    for op, count in ops_counter.most_common():
        if op in ALL_OPS:
            category = "MATH" if op in MATH_OPS else "TABLE" if op in TABLE_OPS else "CHART"
            print(f"  [{category:5s}] {op:20s}: {count:5d}")
    
    # --- Operator category distribution ---
    math_count = sum(ops_counter[op] for op in MATH_OPS if op in ops_counter)
    table_count = sum(ops_counter[op] for op in TABLE_OPS if op in ops_counter)
    chart_count = sum(ops_counter[op] for op in CHART_OPS if op in ops_counter)
    total_ops = math_count + table_count + chart_count
    
    print(f"\n--- Operator category breakdown ---")
    print(f"  MATH  ops: {math_count:5d} ({math_count/total_ops*100:5.1f}%)")
    print(f"  TABLE ops: {table_count:5d} ({table_count/total_ops*100:5.1f}%)")
    print(f"  CHART ops: {chart_count:5d} ({chart_count/total_ops*100:5.1f}%)")
    
    # --- Samples using charts vs tables ---
    uses_chart = 0
    uses_table_op = 0
    uses_both = 0
    
    for s in data:
        prog = s["qa"]["program"]
        steps = parse_program(prog)
        ops_in_prog = {step.operator for step in steps}
        has_chart = bool(ops_in_prog & CHART_OPS)
        has_table = bool(ops_in_prog & TABLE_OPS)
        if has_chart: uses_chart += 1
        if has_table: uses_table_op += 1
        if has_chart and has_table: uses_both += 1
    
    print(f"\n--- Sample modality (by program operators) ---")
    print(f"  Uses chart_* ops: {uses_chart:5d} ({uses_chart/len(data)*100:5.1f}%)")
    print(f"  Uses table_* ops: {uses_table_op:5d} ({uses_table_op/len(data)*100:5.1f}%)")
    print(f"  Uses both:        {uses_both:5d} ({uses_both/len(data)*100:5.1f}%)")
    print(f"  Math only:        {len(data)-uses_chart-uses_table_op+uses_both:5d}")
    
    # --- Validation ---
    valid_count = 0
    invalid_samples = []
    for s in data:
        is_valid, msg = validate_program(s["qa"]["program"])
        if is_valid:
            valid_count += 1
        else:
            invalid_samples.append((s["qid"], msg))
    
    print(f"\n--- Program validation ---")
    print(f"  Valid:   {valid_count}/{len(data)}")
    print(f"  Invalid: {len(data)-valid_count}/{len(data)}")
    if invalid_samples[:5]:
        print(f"  First 5 invalid:")
        for qid, msg in invalid_samples[:5]:
            print(f"    QID {qid}: {msg}")
    
    print("=" * 60)
    return ops_counter


def split_dataset(data: list, val_ratio: float = 0.2, seed: int = 42) -> tuple:
    """
    Split data into train and validation sets.
    Stratified by number of steps in the program.
    """
    # Connected components prevent a shared document/image crossing splits.
    import hashlib
    parents = list(range(len(data)))
    def root(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i
    owners = {}
    for i, sample in enumerate(data):
        fingerprint = hashlib.sha256(json.dumps({k: sample.get(k) for k in ["text", "tables"]}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        keys = ["doc:" + fingerprint] + ["image:" + x for x in sample.get("images", {}).values()]
        for key in keys:
            if key in owners: parents[root(i)] = root(owners[key])
            else: owners[key] = i
    groups = defaultdict(list)
    for i, sample in enumerate(data): groups[root(i)].append(sample)
    groups = list(groups.values())
    if len(groups) < 2: raise ValueError("At least two independent document groups are required")
    random.Random(seed).shuffle(groups)
    train_data, val_data = [], []
    target = max(1, round(len(data) * val_ratio))
    for group in groups[:-1]:
        (val_data if len(val_data) < target else train_data).extend(group)
    train_data.extend(groups[-1])
    return train_data, val_data


def save_splits(train_data: list, val_data: list, output_dir: str):
    """Save train/val splits to JSON files."""
    os.makedirs(output_dir, exist_ok=True)
    
    train_path = os.path.join(output_dir, "train_split.json")
    val_path = os.path.join(output_dir, "val_split.json")
    
    with open(train_path, 'w', encoding='utf-8') as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)
    
    with open(val_path, 'w', encoding='utf-8') as f:
        json.dump(val_data, f, ensure_ascii=False, indent=2)
    
    print(f"Saved: {train_path} ({len(train_data)} samples)")
    print(f"Saved: {val_path} ({len(val_data)} samples)")


def main():
    # Relative paths based on project root
    project_root = Path(__file__).resolve().parent.parent.parent
    data_path = project_root / "data" / "train" / "train.json"
    output_dir = project_root / "vinumqa" / "data"
    
    # Load and analyze
    data = load_data(str(data_path))
    analyze_dataset(data)
    
    # Split
    train_data, val_data = split_dataset(data, val_ratio=0.2)
    
    # Save
    save_splits(train_data, val_data, output_dir)
    
    print("\n✅ Phase 0 - Data preparation complete!")


if __name__ == "__main__":
    main()
