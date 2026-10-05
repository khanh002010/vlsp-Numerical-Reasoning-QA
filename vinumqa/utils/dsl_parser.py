"""Public compatibility imports for the strict DSL implementation."""
from vinumqa.utils.dsl_core import (
    ProgramStep, MATH_OPS, TABLE_OPS, CHART_OPS, ALL_OPS,
    parse_program, resolve_arg, execute_math_op, execute_program,
    validate_program, normalize_program, programs_equivalent, compile_plan, _is_number,
)
