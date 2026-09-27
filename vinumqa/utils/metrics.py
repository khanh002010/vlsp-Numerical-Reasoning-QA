"""
Evaluation metrics for ViNumQA Reasoning Programs.

Metrics:
1. Program Accuracy: Exact match of the normalized program structure
2. Execution Accuracy: Whether the executed result matches the gold answer
3. Operator F1: F1 score on operator prediction
"""

import re
from typing import List, Dict, Tuple, Optional
from collections import Counter

from vinumqa.utils.dsl_parser import (
    parse_program,
    normalize_program,
    programs_equivalent,
    ALL_OPS,
)


def program_accuracy(pred_programs: List[str], gold_programs: List[str]) -> float:
    """
    Compute exact-match program accuracy.
    A prediction is correct if it is semantically equivalent to the gold program.
    """
    assert len(pred_programs) == len(gold_programs), \
        f"Length mismatch: {len(pred_programs)} vs {len(gold_programs)}"
    
    correct = 0
    for pred, gold in zip(pred_programs, gold_programs):
        if programs_equivalent(pred, gold):
            correct += 1
    
    return correct / len(gold_programs) if gold_programs else 0.0


def execution_accuracy(pred_answers: List[Optional[float]],
                       gold_answers: List[Optional[float]],
                       tolerance: float = 0.01) -> float:
    """
    Compute execution accuracy with relative tolerance.
    An answer is correct if |pred - gold| / |gold| <= tolerance.
    """
    assert len(pred_answers) == len(gold_answers)
    
    correct = 0
    total = 0
    
    for pred, gold in zip(pred_answers, gold_answers):
        if pred is None or gold is None:
            continue
        total += 1
        
        if gold == 0:
            if pred == 0:
                correct += 1
        else:
            relative_error = abs(pred - gold) / abs(gold)
            if relative_error <= tolerance:
                correct += 1
    
    return correct / total if total > 0 else 0.0


def operator_f1(pred_programs: List[str], gold_programs: List[str]) -> Dict[str, float]:
    """
    Compute per-operator precision, recall, and F1.
    Returns a dict with per-operator and macro-averaged metrics.
    """
    pred_ops_total = Counter()
    gold_ops_total = Counter()
    correct_ops = Counter()
    
    for pred, gold in zip(pred_programs, gold_programs):
        pred_steps = parse_program(pred)
        gold_steps = parse_program(gold)
        
        pred_op_list = [s.operator for s in pred_steps]
        gold_op_list = [s.operator for s in gold_steps]
        
        pred_op_counter = Counter(pred_op_list)
        gold_op_counter = Counter(gold_op_list)
        
        for op in ALL_OPS:
            pred_ops_total[op] += pred_op_counter.get(op, 0)
            gold_ops_total[op] += gold_op_counter.get(op, 0)
            correct_ops[op] += min(pred_op_counter.get(op, 0), gold_op_counter.get(op, 0))
    
    results = {}
    f1_scores = []
    
    for op in sorted(ALL_OPS):
        p = correct_ops[op] / pred_ops_total[op] if pred_ops_total[op] > 0 else 0.0
        r = correct_ops[op] / gold_ops_total[op] if gold_ops_total[op] > 0 else 0.0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
        
        if gold_ops_total[op] > 0:  # Only include ops that appear in gold
            results[op] = {"precision": p, "recall": r, "f1": f1, "support": gold_ops_total[op]}
            f1_scores.append(f1)
    
    # Macro average
    results["macro_avg"] = {
        "precision": sum(r["precision"] for r in results.values() if isinstance(r, dict)) / max(len(f1_scores), 1),
        "recall": sum(r["recall"] for r in results.values() if isinstance(r, dict)) / max(len(f1_scores), 1),
        "f1": sum(f1_scores) / max(len(f1_scores), 1),
    }
    
    return results


def step_count_accuracy(pred_programs: List[str], gold_programs: List[str]) -> float:
    """
    Compute the accuracy of predicting the correct number of steps.
    """
    correct = 0
    for pred, gold in zip(pred_programs, gold_programs):
        pred_steps = parse_program(pred)
        gold_steps = parse_program(gold)
        if len(pred_steps) == len(gold_steps):
            correct += 1
    
    return correct / len(gold_programs) if gold_programs else 0.0


def compute_all_metrics(pred_programs: List[str],
                        gold_programs: List[str],
                        pred_answers: Optional[List[float]] = None,
                        gold_answers: Optional[List[float]] = None) -> Dict:
    """
    Compute all evaluation metrics at once.
    """
    results = {
        "program_accuracy": program_accuracy(pred_programs, gold_programs),
        "step_count_accuracy": step_count_accuracy(pred_programs, gold_programs),
        "num_samples": len(gold_programs),
    }
    
    if pred_answers is not None and gold_answers is not None:
        results["execution_accuracy"] = execution_accuracy(pred_answers, gold_answers)
    
    op_f1 = operator_f1(pred_programs, gold_programs)
    results["operator_f1"] = op_f1
    results["macro_f1"] = op_f1.get("macro_avg", {}).get("f1", 0.0)
    
    return results


def print_metrics(metrics: Dict, verbose: bool = True):
    """Pretty print evaluation metrics."""
    print("=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    print(f"  Samples:             {metrics['num_samples']}")
    print(f"  Program Accuracy:    {metrics['program_accuracy']:.4f}")
    print(f"  Step Count Accuracy: {metrics['step_count_accuracy']:.4f}")
    
    if "execution_accuracy" in metrics:
        print(f"  Execution Accuracy:  {metrics['execution_accuracy']:.4f}")
    
    print(f"  Macro Operator F1:   {metrics['macro_f1']:.4f}")
    
    if verbose and "operator_f1" in metrics:
        print("\n  Per-Operator F1:")
        for op, scores in sorted(metrics["operator_f1"].items()):
            if isinstance(scores, dict) and "support" in scores:
                print(f"    {op:20s}  P={scores['precision']:.3f}  R={scores['recall']:.3f}  F1={scores['f1']:.3f}  (n={scores['support']})")
    
    print("=" * 60)
