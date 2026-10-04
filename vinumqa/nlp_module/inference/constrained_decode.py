"""
Constraint Decoding for ViNumQA Reasoning Program Synthesis.
Uses a LogitsProcessor to restrict the LLM to generate only valid DSL operators.

Implementation: Token-level hard constraint.
  - At every decoding step, the processor checks if the current position is the
    start of a new operator (i.e., right after "; " or at step beginning).
  - If so, it sets logits of all tokens that are NOT a valid operator's first
    token to -inf, forcing the model to begin with a known operator name.
  - All other positions (inside parentheses: args, numbers, strings) are unconstrained.

Note: For production-grade constrained decoding with full grammar enforcement,
      consider using the `outlines` library (pip install outlines) which builds
      a complete FSM from a regex/grammar.
"""

import torch
from transformers import LogitsProcessor


VALID_DSL_OPERATORS = [
    "subtract", "divide", "multiply", "add", "greater", "exp",
    "chart_at", "chart_max", "chart_min", "chart_average", "chart_sum", "chart_total",
    "table_max", "table_min", "table_average", "table_sum",
]


class DSLLogitsProcessor(LogitsProcessor):
    """
    Hard-constrains the model to start each new operator with a valid DSL name.
    """

    def __init__(self, tokenizer):
        """
        Args:
            tokenizer: The tokenizer of the model (Qwen2.5-7B).
        """
        self.tokenizer = tokenizer

        # Pre-compute: first-token IDs for each valid operator name
        self.operator_first_token_ids: set[int] = set()
        for op in VALID_DSL_OPERATORS:
            # Tokenize WITHOUT space prefix (Qwen tokenizer behaviour)
            ids = tokenizer.encode(op, add_special_tokens=False)
            if ids:
                self.operator_first_token_ids.add(ids[0])
            # Also with space prefix (some tokenizers split differently)
            ids_space = tokenizer.encode(" " + op, add_special_tokens=False)
            if ids_space:
                self.operator_first_token_ids.add(ids_space[0])

        # Always allow structural tokens: ( ) ; # digits space . - newline
        structural_chars = [
            "(", ")", ";", "#", " ", ".", "-", "\n",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        ]
        self.structural_token_ids: set[int] = set()
        for ch in structural_chars:
            ids = tokenizer.encode(ch, add_special_tokens=False)
            if ids:
                self.structural_token_ids.add(ids[0])

        # Combine: allowed at the START of a new operator step
        self.allowed_at_op_start = (
            self.operator_first_token_ids | self.structural_token_ids
        )

        # Decode trigger: "; " signals the start of a new operator
        self._semi_ids = tokenizer.encode("; ", add_special_tokens=False)
        self._pipe_ids = tokenizer.encode("| 2 |", add_special_tokens=False)

    def _is_at_operator_start(self, input_ids: torch.LongTensor) -> bool:
        """
        Heuristic: if the last N tokens form "; " or "| 2 |", we're at
        the beginning of a new operator call.
        """
        ids = input_ids[0].tolist()
        # Check for "; " suffix
        if len(ids) >= len(self._semi_ids):
            if ids[-len(self._semi_ids):] == self._semi_ids:
                return True
        # Check for "| 2 |" suffix (table row start → operator position)
        if len(ids) >= len(self._pipe_ids):
            if ids[-len(self._pipe_ids):] == self._pipe_ids:
                return True
        return False

    def __call__(
        self,
        input_ids: torch.LongTensor,
        scores: torch.FloatTensor,
    ) -> torch.FloatTensor:
        """
        At operator-start positions: mask out all tokens NOT in allowed set.
        At all other positions: return scores unchanged (args, strings, numbers).
        """
        if self._is_at_operator_start(input_ids):
            # Create a mask: -inf for disallowed tokens
            mask = torch.full_like(scores, float("-inf"))
            allowed = list(self.allowed_at_op_start)
            # Clip to vocab size
            allowed = [t for t in allowed if t < scores.shape[-1]]
            mask[:, allowed] = 0.0
            scores = scores + mask

        return scores


if __name__ == "__main__":
    print("DSLLogitsProcessor is ACTIVE.")
    print(f"Constraining to {len(VALID_DSL_OPERATORS)} operators: {VALID_DSL_OPERATORS}")
    print("Recommendation: for full grammar enforcement, also use 'outlines' library.")
