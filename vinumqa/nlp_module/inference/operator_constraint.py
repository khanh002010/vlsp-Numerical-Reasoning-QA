"""Pure operator-prefix checks; final structural validation remains mandatory."""
import re
from vinumqa.nlp_module.dsl_operators import OPERATOR_NAMES

def operator_prefix(generated):
    matches = list(re.finditer(r"\|\s*2\s*\|", generated))
    if not matches: return None
    program = generated[matches[-1].end():]
    depth, start = 0, 0
    for i, ch in enumerate(program):
        if ch == "(": depth += 1
        elif ch == ")": depth -= 1
        elif ch == ";" and depth == 0: start = i + 1
    tail = program[start:].lstrip()
    return tail if re.fullmatch(r"[a-z_]*", tail) else None

def allows_operator_piece(prefix, piece):
    value = prefix + piece
    value = value.lstrip()
    if "(" in value:
        return value.split("(", 1)[0] in OPERATOR_NAMES
    return any(op.startswith(value) for op in OPERATOR_NAMES)
