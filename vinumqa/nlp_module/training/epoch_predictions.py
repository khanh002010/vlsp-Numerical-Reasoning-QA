"""Generate public-validation submissions from input-only prompts after evaluation."""
import json
from pathlib import Path
from vinumqa.nlp_module.contracts import RESPONSE_PREFIX, parse_response, source_ids
from vinumqa.utils.dsl_parser import validate_program

def validation_prompt(sample):
    # Deliberately never read sample['output'] here (contains the ground truth).
    return sample["instruction"] + "\n\n" + sample["input"] + "\n\n" + RESPONSE_PREFIX

def export_epoch_predictions(samples, generate, directory, epoch, step):
    predictions, diagnostics = [], []
    for sample in samples:
        prompt = validation_prompt(sample)
        try:
            result = parse_response(generate(prompt))
            valid, reason = validate_program(result["program"], sources=source_ids(sample["input"]))
            diagnostics.append({"qid": sample["qid"], **result, "valid": valid, "validation_error": reason})
            predictions.append({"qid": sample["qid"], "predicted": result["program"]})
        except Exception as e:
            predictions.append({"qid": sample["qid"], "predicted": ""})
            diagnostics.append({"qid": sample["qid"], "valid": False, "error": str(e)})
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    stem = f"epoch_{epoch:g}_step_{step}"
    for suffix, rows in [(".json", predictions), (".diagnostics.json", diagnostics)]:
        path = directory / (stem + suffix)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)
    return predictions

def make_epoch_callback(samples, tokenizer, max_new_tokens=1536):
    import torch
    from transformers import TrainerCallback
    from vinumqa.nlp_module.inference.constrained_decode import DSLLogitsProcessor

    class EpochPredictions(TrainerCallback):
        def on_evaluate(self, args, state, control, model=None, **kwargs):
            if not state.is_world_process_zero: return control
            # This callback targets the single-GPU QLoRA configuration in this repo.
            if args.world_size != 1: raise ValueError("Epoch generation currently requires single-process training")
            training = model.training
            use_cache = model.config.use_cache
            checkpointing = getattr(model, "is_gradient_checkpointing", False)
            processor = DSLLogitsProcessor(tokenizer)
            try:
                model.eval()
                if checkpointing: model.gradient_checkpointing_disable()
                model.config.use_cache = True
                def generate(prompt):
                    inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to(model.get_input_embeddings().weight.device)
                    length = inputs.input_ids.shape[1]
                    if length + max_new_tokens > getattr(model.config, "max_position_embeddings", 32768):
                        raise ValueError("Validation prompt exceeds generation context budget")
                    processor.reset(length)
                    with torch.inference_mode():
                        outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False,
                            pad_token_id=tokenizer.pad_token_id, logits_processor=[processor], use_cache=True)
                    return tokenizer.decode(outputs[0, length:], skip_special_tokens=True)
                export_epoch_predictions(samples, generate, Path(args.output_dir) / "validation_predictions",
                                         state.epoch or 0, state.global_step)
            finally:
                model.config.use_cache = use_cache
                if checkpointing: model.gradient_checkpointing_enable()
                model.train(training)
            return control
    return EpochPredictions()
