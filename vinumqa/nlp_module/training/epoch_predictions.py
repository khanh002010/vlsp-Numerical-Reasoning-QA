"""Export validation results incrementally without loading CV during training."""
import json
from pathlib import Path
from vinumqa.nlp_module.contracts import RESPONSE_PREFIX, parse_response, source_ids
from vinumqa.utils.dsl_parser import validate_program
from vinumqa.nlp_module.data_prep.incremental import write_json
from vinumqa.nlp_module.training.session_control import SessionBudgetExceeded


def validation_prompt(sample):
    # Never read sample['output'] here: it contains the ground truth.
    return sample["instruction"] + "\n\n" + sample["input"] + "\n\n" + RESPONSE_PREFIX


def export_epoch_predictions(samples, generate, directory, epoch, step, session_budget=None):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    stem = f"epoch_{epoch:g}_step_{step}"
    predictions = [{"qid": s["qid"], "predicted": ""} for s in samples]
    diagnostics, requests = [], []
    def save():
        write_json(directory / (stem + ".json"), predictions)
        write_json(directory / (stem + ".diagnostics.json"), diagnostics)
        request_path = directory / (stem + ".cv_requests.json")
        if requests or request_path.exists(): write_json(request_path, requests)
    save()
    for index, sample in enumerate(samples):
        if session_budget is not None and session_budget.expired():
            diagnostics.extend({"qid": s["qid"], "valid": False, "status": "pending_time_budget"}
                               for s in samples[index:])
            save()
            break
        prompt = validation_prompt(sample)
        try:
            result = parse_response(generate(prompt))
            valid, reason = validate_program(result["program"], sources=source_ids(sample["input"]))
            if "charts" in sample and "cv_request" not in result:
                from vinumqa.nlp_module.inference.evidence_validation import validate_evidence
                check = validate_evidence(result["program"], sample["charts"], source_ids(sample["input"]),
                                          result.get("extracted_values", ""))
                valid, reason = check["valid"], "; ".join(check["errors"])
                requests.extend({"qid": sample["qid"], "request": r} for r in check["cv_requests"])
            if "cv_request" in result:
                requests.append({"qid": sample["qid"], "request": result["cv_request"]})
                valid, reason = False, "CV inspection deferred; run batch_inference after training"
            diagnostics.append({"qid": sample["qid"], **result, "valid": valid, "validation_error": reason})
            predictions[index]["predicted"] = result["program"] if valid else ""
        except SessionBudgetExceeded:
            diagnostics.extend({"qid": s["qid"], "valid": False, "status": "pending_time_budget"}
                               for s in samples[index:])
            save()
            break
        except Exception as error:
            diagnostics.append({"qid": sample["qid"], "valid": False, "error": str(error)})
        save()  # Completed QIDs survive an interrupted validation pass.
    return predictions


def make_epoch_callback(samples, tokenizer, max_new_tokens=1536, session_budget=None):
    import torch
    from transformers import TrainerCallback
    from vinumqa.nlp_module.inference.constrained_decode import DSLLogitsProcessor

    class EpochPredictions(TrainerCallback):
        def on_evaluate(self, args, state, control, model=None, **kwargs):
            if not state.is_world_process_zero: return control
            if args.world_size != 1: raise ValueError("Epoch generation requires single-process training")
            training, use_cache = model.training, model.config.use_cache
            checkpointing = getattr(model, "is_gradient_checkpointing", False)
            processor = DSLLogitsProcessor(tokenizer)
            try:
                model.eval()
                if checkpointing: model.gradient_checkpointing_disable()
                model.config.use_cache = True
                def generate(prompt):
                    if session_budget is not None and session_budget.expired(): raise SessionBudgetExceeded()
                    inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to(model.get_input_embeddings().weight.device)
                    length = inputs.input_ids.shape[1]
                    if length + max_new_tokens > getattr(model.config, "max_position_embeddings", 32768):
                        raise ValueError("Validation prompt exceeds generation context budget")
                    processor.reset(length)
                    with torch.inference_mode():
                        outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False,
                            pad_token_id=tokenizer.pad_token_id, logits_processor=[processor], use_cache=True,
                            max_time=120)
                    if int(outputs[0, -1]) != tokenizer.eos_token_id:
                        raise ValueError("Validation generation stopped before EOS")
                    return tokenizer.decode(outputs[0, length:], skip_special_tokens=True)
                export_epoch_predictions(samples, generate, Path(args.output_dir) / "validation_predictions",
                                         state.epoch or 0, state.global_step, session_budget)
            finally:
                model.config.use_cache = use_cache
                if checkpointing: model.gradient_checkpointing_enable()
                model.train(training)
            if session_budget is not None and session_budget.expired():
                control.should_training_stop = True
                control.should_save = True
            return control
    return EpochPredictions()
