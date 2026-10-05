"""Full operator-name restriction, not a claim of full argument grammar."""
import torch
from transformers import LogitsProcessor
from vinumqa.nlp_module.dsl_operators import OPERATOR_NAMES
from vinumqa.nlp_module.inference.operator_constraint import operator_prefix, allows_operator_piece

VALID_DSL_OPERATORS = OPERATOR_NAMES

class DSLLogitsProcessor(LogitsProcessor):
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.start = 0
        self.pieces = None
        self.cache = {}

    def reset(self, prompt_length):
        self.start = prompt_length

    def __call__(self, input_ids, scores):
        # Per-row state also supports beam-expanded batches. Never scan the prompt.
        for row in range(input_ids.shape[0]):
            generated = self.tokenizer.decode(input_ids[row, self.start:], skip_special_tokens=True)
            prefix = operator_prefix(generated)
            if prefix is None: continue
            if self.pieces is None:
                self.pieces = self.tokenizer.batch_decode([[i] for i in range(len(self.tokenizer))], skip_special_tokens=False)
            key = (prefix, scores.shape[-1])
            if key not in self.cache:
                special = set(self.tokenizer.all_special_ids)
                self.cache[key] = [i for i, piece in enumerate(self.pieces) if i < scores.shape[-1]
                                   and i not in special and piece and allows_operator_piece(prefix, piece)]
            allowed = self.cache[key]
            if not allowed: raise ValueError(f"No token can complete DSL operator prefix {prefix!r}")
            mask = torch.full_like(scores[row], float("-inf"))
            mask[allowed] = 0
            scores[row] += mask
        return scores
