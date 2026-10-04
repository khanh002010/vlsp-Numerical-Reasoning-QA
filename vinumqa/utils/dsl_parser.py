"""
DSL Parser & Executor for ViNumQA Reasoning Programs.

Format: op(args); op(args); ...
- Arguments separated by "; " within parentheses
- #N references result of step N (0-indexed)
- Operators: add, subtract, multiply, divide, greater, exp,
             table_max, table_min, table_sum, table_average,
             chart_at, chart_max, chart_min, chart_sum, chart_average
"""

import re
from typing import List, Dict, Tuple, Optional, Any


MATH_OPS = {"add", "subtract", "multiply", "divide", "greater", "exp"}
TABLE_OPS = {"table_max", "table_min", "table_sum", "table_average"}
CHART_OPS = {"chart_at", "chart_max", "chart_min", "chart_sum", "chart_average", "chart_total"}
ALL_OPS = MATH_OPS | TABLE_OPS | CHART_OPS


class ProgramStep:
    """Represents a single step in a reasoning program."""

    def __init__(self, step_id: int, operator: str, args: List[str]):
        self.step_id = step_id
        self.operator = operator
        self.args = args

    def __repr__(self):
        args_str = "; ".join(self.args)
        return f"#{self.step_id}: {self.operator}({args_str})"


def parse_program(program_str: str) -> List[ProgramStep]:
    """
    Parse a reasoning program string into a list of ProgramStep objects.
    
    Example input: "chart_at(Image 1; P/B trượt; Jul-21; none); subtract(#0; 2.1)"
    """
    steps = []
    
    # Split by top-level "; " that separates steps (not inside parentheses)
    # Strategy: find each op(...) pattern
    pattern = r'([a-z_]+)\(([^)]*)\)'
    matches = re.finditer(pattern, program_str)
    
    for i, match in enumerate(matches):
        operator = match.group(1)
        args_str = match.group(2)
        args = [a.strip() for a in args_str.split(";")]
        steps.append(ProgramStep(step_id=i, operator=operator, args=args))
    
    return steps


def resolve_arg(arg: str, results: Dict[int, Any]) -> Any:
    """
    Resolve an argument to its value.
    - If it starts with '#', look up the result of the referenced step.
    - If it's a number, convert to float.
    - Otherwise, return as string (for table/chart lookups).
    """
    arg = arg.strip()
    
    # Reference to previous step result
    if arg.startswith("#"):
        ref_id = int(arg[1:])
        if ref_id not in results:
            raise ValueError(f"Reference #{ref_id} not found in results")
        return results[ref_id]
    
    # Try to parse as number
    try:
        # Handle Vietnamese number formats (e.g., "1.234,56" or "1,234.56")
        cleaned = arg.replace(",", "")
        return float(cleaned)
    except (ValueError, TypeError):
        pass
    
    # Return as string (for table/chart column/row names)
    return arg


def execute_math_op(operator: str, args: List[Any]) -> float:
    """Execute a mathematical operator on resolved arguments."""
    if operator == "add":
        return float(args[0]) + float(args[1])
    elif operator == "subtract":
        return float(args[0]) - float(args[1])
    elif operator == "multiply":
        return float(args[0]) * float(args[1])
    elif operator == "divide":
        if float(args[1]) == 0:
            raise ValueError("Division by zero")
        return float(args[0]) / float(args[1])
    elif operator == "greater":
        return 1.0 if float(args[0]) > float(args[1]) else 0.0
    elif operator == "exp":
        return float(args[0]) ** float(args[1])
    else:
        raise ValueError(f"Unknown math operator: {operator}")


def execute_program(steps: List[ProgramStep],
                    tables: Optional[Dict] = None,
                    charts: Optional[Dict] = None) -> Dict[int, Any]:
    """
    Execute a parsed program and return results for each step.
    
    For table/chart operations, if the actual data is not provided,
    the result will be None (useful for program structure validation).
    """
    results = {}
    
    for step in steps:
        resolved_args = []
        for arg in step.args:
            resolved_args.append(resolve_arg(arg, results))
        
        if step.operator in MATH_OPS:
            try:
                results[step.step_id] = execute_math_op(step.operator, resolved_args)
            except (ValueError, TypeError) as e:
                results[step.step_id] = None
        elif step.operator in TABLE_OPS or step.operator in CHART_OPS:
            # Table/chart ops need actual data to execute
            # For now, return None if no data provided
            results[step.step_id] = None
        else:
            results[step.step_id] = None
    
    return results


def validate_program(program_str: str) -> Tuple[bool, str]:
    """
    Validate a reasoning program string.
    Returns (is_valid, error_message).
    """
    try:
        steps = parse_program(program_str)
        
        if len(steps) == 0:
            return False, "Empty program"
        
        for step in steps:
            # Check operator is valid
            if step.operator not in ALL_OPS:
                return False, f"Unknown operator: {step.operator}"
            
            # Check references are valid
            for arg in step.args:
                if arg.startswith("#"):
                    ref_id = int(arg[1:])
                    if ref_id >= step.step_id:
                        return False, f"Forward reference #{ref_id} in step {step.step_id}"
                    if ref_id < 0:
                        return False, f"Negative reference #{ref_id}"
            
            # Check argument count
            if step.operator in MATH_OPS:
                if len(step.args) != 2:
                    return False, f"Toán tử {step.operator} yêu cầu đúng 2 tham số, nhưng nhận được {len(step.args)}"
            elif step.operator in TABLE_OPS or step.operator in CHART_OPS:
                if len(step.args) != 4:
                    return False, f"Toán tử {step.operator} yêu cầu đúng 4 tham số, nhưng nhận được {len(step.args)}"
                    
        return True, "Valid"
    
    except Exception as e:
        return False, str(e)


def _is_number(s: str) -> bool:
    """Check if a string is a number."""
    try:
        float(s.replace(",", ""))
        return True
    except (ValueError, TypeError):
        return False


def normalize_program(program_str: str) -> str:
    """
    Normalize a program string for comparison.
    - Lowercase operators
    - Strip whitespace
    - Standardize number format
    """
    steps = parse_program(program_str)
    parts = []
    for step in steps:
        args_str = "; ".join(step.args)
        parts.append(f"{step.operator}({args_str})")
    return "; ".join(parts)


def programs_equivalent(prog1: str, prog2: str) -> bool:
    """
    Check if two programs are semantically equivalent.
    Handles commutative operations (add, multiply).
    """
    steps1 = parse_program(prog1)
    steps2 = parse_program(prog2)
    
    if len(steps1) != len(steps2):
        return False
    
    for s1, s2 in zip(steps1, steps2):
        if s1.operator != s2.operator:
            return False
        
        # For commutative ops, check both orderings
        if s1.operator in {"add", "multiply"}:
            if not (s1.args == s2.args or s1.args == s2.args[::-1]):
                return False
        else:
            if s1.args != s2.args:
                return False
    
    return True


if __name__ == "__main__":
    # Test parsing
    test_programs = [
        "table_max(Table 1; Đầu tư công (%); 2021; 2025F)",
        "chart_at(Image 1; P/B trượt; Jul-21; none); subtract(#0; 2.1)",
        "chart_at(Image 2; Doanh thu thuần; 2021; none); chart_at(Image 2; Doanh thu thuần; 2022; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)",
    ]
    
    for prog_str in test_programs:
        print(f"\nProgram: {prog_str}")
        steps = parse_program(prog_str)
        for step in steps:
            print(f"  {step}")
        
        is_valid, msg = validate_program(prog_str)
        print(f"  Valid: {is_valid} ({msg})")
        
        results = execute_program(steps)
        print(f"  Results: {results}")
