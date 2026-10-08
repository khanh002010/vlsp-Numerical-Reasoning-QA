"""Full-context causal LM training without logits for masked prompt prefixes.

Qwen applies logits_to_keep only between the decoder and lm_head. Keeping one
position before the first supervised label preserves the causal label shift.
The original model loss and Trainer normalization/AMP/accumulation stay in use.
"""
import inspect
from transformers import Trainer


def completion_loss_inputs(inputs):
    labels = inputs.get("labels")
    if labels is None or labels.ndim != 2 or labels.shape[1] < 2:
        raise ValueError("Completion loss requires [batch, sequence] causal LM labels")
    if inputs.get("input_ids") is None or inputs["input_ids"].shape != labels.shape:
        raise ValueError("Input IDs and labels must cover the same full sequence")
    # Label column j is predicted by logit column j-1. Column zero is never a
    # target. Union across the batch supports unequal prompt/completion lengths.
    supervised_columns = (labels[:, 1:] != -100).any(dim=0).nonzero(as_tuple=True)[0]
    if supervised_columns.numel() == 0:
        raise ValueError("No supervised next-token targets in this batch")
    start = int(supervised_columns[0].item())
    keep = labels.shape[1] - start
    result = dict(inputs)
    # Do not touch input_ids, attention_mask or position_ids: all context remains.
    result["labels"] = labels[:, start:].contiguous()
    result["logits_to_keep"] = keep
    return result


class CompletionLogitsTrainer(Trainer):
    """Keep stock loss handling and limit only the LM-head sequence dimension."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model = self.model
        if hasattr(model, "get_base_model"):
            model = model.get_base_model()
        if getattr(model.config, "model_type", None) != "qwen2":
            raise ValueError("Completion logits optimization is verified for Qwen2/Qwen2.5 only")
        if "logits_to_keep" not in inspect.signature(model.forward).parameters:
            raise ValueError("Installed Qwen2 forward lacks logits_to_keep; update transformers or use --loss-mode full")
        if not self.args.prediction_loss_only or self.compute_metrics is not None:
            raise ValueError("Completion logits requires loss-only Trainer evaluation; use separate generation exports")
        self._logged_completion_window = False

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        reduced = completion_loss_inputs(inputs)
        if not self._logged_completion_window:
            full, kept = inputs["labels"].shape[1], reduced["logits_to_keep"]
            print(f"[Loss] context={full} tokens unchanged; LM-head logits={kept}/{full} positions "
                  f"({100 * (1 - kept / full):.1f}% fewer); original causal loss retained", flush=True)
            self._logged_completion_window = True
        return super().compute_loss(model, reduced, return_outputs=return_outputs,
                                    num_items_in_batch=num_items_in_batch)
