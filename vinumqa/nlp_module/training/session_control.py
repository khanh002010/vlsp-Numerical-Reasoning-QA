"""Single-session budget and checkpoint manifests; no GPU imports at module load."""
import time
from pathlib import Path
from vinumqa.nlp_module.data_prep.incremental import write_json


class SessionBudgetExceeded(RuntimeError):
    pass


class SessionBudget:
    def __init__(self, hours=None, reserve_minutes=10, clock=time.monotonic):
        if hours is not None and hours <= 0: raise ValueError("Session hours must be positive")
        if reserve_minutes < 0: raise ValueError("Save reserve must be nonnegative")
        self.clock, self.started = clock, clock()
        self.limit = None if hours is None else hours * 3600
        self.reserve = reserve_minutes * 60
        if self.limit is not None and self.reserve >= self.limit: raise ValueError("Session budget must exceed save reserve")

    def expired(self):
        return self.limit is not None and self.clock() - self.started >= self.limit - self.reserve


def make_session_callback(budget, manifest, tokenizer):
    from transformers import TrainerCallback

    class SessionControl(TrainerCallback):
        def on_step_end(self, args, state, control, **kwargs):
            if budget.expired():
                control.should_save = True
                control.should_training_stop = True
                control.should_evaluate = False
            return control

        def on_epoch_end(self, args, state, control, **kwargs):
            control.should_save = True
            return self.on_step_end(args, state, control)

        def on_save(self, args, state, control, **kwargs):
            checkpoint = Path(args.output_dir) / f"checkpoint-{state.global_step}"
            tokenizer.save_pretrained(checkpoint)
            write_json(checkpoint / "pipeline_manifest.json", manifest)
            return control
    return SessionControl()
