"""Strict DSL validation. Literal numbers use a dot decimal, never locale guessing."""
import math
import re
from dataclasses import dataclass
from vinumqa.nlp_module.dsl_operators import DSL_OPERATORS

MATH_OPS = {k for k, v in DSL_OPERATORS.items() if "impl" in v}
TABLE_OPS = {k for k in DSL_OPERATORS if k.startswith("table_")}
CHART_OPS = {k for k in DSL_OPERATORS if k.startswith("chart_")}
ALL_OPS = set(DSL_OPERATORS)
NUMBER = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\Z")

@dataclass
class ProgramStep:
    step_id: int
    operator: str
    args: list

    def __repr__(self):
        return f"#{self.step_id}: {self.operator}({'; '.join(self.args)})"

def _split(text):
    parts, start, depth = [], 0, 0
    for i, ch in enumerate(text):
        if ch == "(": depth += 1
        elif ch == ")": depth -= 1
        if depth < 0: raise ValueError("Unbalanced parentheses")
        if ch == ";" and depth == 0:
            parts.append(text[start:i].strip())
            start = i + 1
    if depth: raise ValueError("Unbalanced parentheses")
    parts.append(text[start:].strip())
    return parts

def parse_program(program_str):
    if not program_str.strip(): return []
    steps = []
    try:
        for i, part in enumerate(_split(program_str.strip())):
            match = re.fullmatch(r"([a-z_]+)\((.*)\)", part, re.S)
            if not match: raise ValueError("Malformed operation")
            depth = 0
            for j, ch in enumerate(part):
                depth += (ch == "(") - (ch == ")")
                if ch == ")" and depth == 0 and j != len(part) - 1:
                    raise ValueError("Missing step separator")
            steps.append(ProgramStep(i, match[1], _split(match[2])))
    except ValueError:
        return [ProgramStep(0, "INVALID", [program_str])]
    return steps

def _is_number(s):
    return bool(NUMBER.fullmatch(s.strip())) and math.isfinite(float(s))

def resolve_arg(arg, results):
    if re.fullmatch(r"#\d+", arg):
        if int(arg[1:]) not in results: raise ValueError(f"Unavailable reference {arg}")
        return results[int(arg[1:])]
    return float(arg) if _is_number(arg) else arg

def validate_program(program_str, sources=None):
    """Optional sources contains exact Image/Table IDs from the input."""
    steps = parse_program(program_str)
    if not steps: return False, "Empty program"
    known = {}
    for s in steps:
        if s.operator not in ALL_OPS: return False, f"Unknown/malformed operator: {s.operator}"
        arity = len(DSL_OPERATORS[s.operator]["args"])
        if len(s.args) != arity or any(not a for a in s.args):
            return False, f"Step {s.step_id}: {s.operator} requires {arity} nonempty arguments"
        if s.operator in MATH_OPS:
            for a in s.args:
                if a.startswith("#"):
                    if not re.fullmatch(r"#\d+", a) or int(a[1:]) >= s.step_id:
                        return False, f"Step {s.step_id}: invalid/forward reference {a}"
                elif not _is_number(a): return False, f"Step {s.step_id}: expected number/reference, got {a}"
            args = [resolve_arg(a, known) for a in s.args]
            if s.operator == "divide" and args[1] == 0:
                return False, f"Step {s.step_id}: division by zero"
            if all(a is not None for a in args):
                try: known[s.step_id] = execute_math_op(s.operator, args)
                except (ValueError, ArithmeticError, TypeError) as e: return False, str(e)
            else: known[s.step_id] = None
        else:
            prefix = "Table" if s.operator in TABLE_OPS else "Image"
            if not re.fullmatch(prefix + r" [1-9]\d*", s.args[0]):
                return False, f"Step {s.step_id}: expected {prefix} ID, got {s.args[0]}"
            if sources is not None and s.args[0] not in sources: return False, f"Source not found: {s.args[0]}"
            if any(a.startswith("#") for a in s.args): return False, "Lookup requires labels, not references"
            known[s.step_id] = None
    return True, "Valid"

def execute_math_op(operator, args):
    if len(args) != 2: raise ValueError("Math operation requires two arguments")
    if operator == "divide" and args[1] == 0: raise ValueError("Division by zero")
    value = DSL_OPERATORS[operator]["impl"](*args)
    if isinstance(value, complex) or value is None or not math.isfinite(value): raise ValueError("Non-finite arithmetic result")
    return value

def execute_program(steps, tables=None, charts=None):
    """Lookup sources map IDs to callables (operator, label, start, end) -> number.

    No guessed lookup semantics: missing resolvers fail explicitly.
    """
    valid, reason = validate_program("; ".join(f"{s.operator}({'; '.join(s.args)})" for s in steps))
    if not valid: raise ValueError(reason)
    results = {}
    for s in steps:
        if s.operator in MATH_OPS:
            value = execute_math_op(s.operator, [resolve_arg(a, results) for a in s.args])
        else:
            sources = tables if s.operator in TABLE_OPS else charts
            resolver = (sources or {}).get(s.args[0])
            if not callable(resolver): raise ValueError(f"No lookup resolver for {s.args[0]}")
            value = resolver(s.operator, *s.args[1:])
            if value is None or not math.isfinite(float(value)): raise ValueError("Missing/non-finite lookup result")
        results[s.step_id] = value
    return results

def normalize_program(program_str):
    """Syntax whitespace only; preserve labels and literal spelling."""
    valid, reason = validate_program(program_str)
    if not valid: raise ValueError(reason)
    return "; ".join(f"{s.operator}({'; '.join(s.args)})" for s in parse_program(program_str))

def programs_equivalent(prog1, prog2):
    """Conservative step-wise match allowing only add/multiply argument reversal."""
    if not validate_program(prog1)[0] or not validate_program(prog2)[0]: return False
    a, b = parse_program(prog1), parse_program(prog2)
    return len(a) == len(b) and all(x.operator == y.operator and
        (x.args == y.args or x.operator in {"add", "multiply"} and x.args == y.args[::-1]) for x, y in zip(a, b))

def compile_plan(nodes):
    """Ordered named nodes; references are {'ref': 'id'}, literals are strings."""
    ids, parts = {}, []
    for node in nodes:
        if node["id"] in ids: raise ValueError("Duplicate node ID")
        args = []
        for arg in node["args"]:
            if isinstance(arg, dict):
                if set(arg) != {"ref"} or arg["ref"] not in ids: raise ValueError("Unknown/forward node reference")
                args.append(f"#{ids[arg['ref']]}")
            else:
                if not isinstance(arg, str) or arg.startswith("#"): raise ValueError("Use explicit node references")
                args.append(arg)
        parts.append(f"{node['operator']}({'; '.join(args)})")
        ids[node["id"]] = len(ids)
    return normalize_program("; ".join(parts))
