"""Format real multimodal inputs using the same contract as inference."""
import argparse
import json
import hashlib
from pathlib import Path
from vinumqa.data.context import build_inline_context, dict_to_markdown_table
from vinumqa.nlp_module.contracts import (
    FORMAT_VERSION, INSTRUCTION, DSL_HINT_SHORT, input_text, evidence_from_program,
)
from vinumqa.utils.dsl_parser import normalize_program

extract_values_from_program = evidence_from_program

def format_sample(sample, include_dsl_prompt=True, cv_pipeline=None, image_dir=None):
    # include_dsl_prompt retained for callers; the contract is always identical.
    images = {k: str(Path(image_dir or ".") / v) for k, v in sample.get("images", {}).items()}
    context = build_inline_context(sample.get("text", []), sample.get("tables", {}), images, cv_pipeline)
    program = normalize_program(sample["qa"]["program"])
    evidence = evidence_from_program(program)
    return {"qid": sample["qid"], "format_version": FORMAT_VERSION,
        "group_keys": ["image:" + v for v in sample.get("images", {}).values()] + ["doc:" + hashlib.sha256(
            json.dumps({k: sample.get(k) for k in ["text", "tables"]}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()],
        "instruction": INSTRUCTION,
        "input": input_text(context, sample["qa"]["question"], ", ".join(images)),
        "output": "| Step | Output |\n|---|---|\n| 1 | " + evidence + " |\n| 2 | " + program + " |"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--images", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--skip-invalid", action="store_true", help="Quarantine invalid gold programs; CV failures always stop formatting")
    args = parser.parse_args()
    from vinumqa.cv_module.pipeline import CVPipeline, CVInitializationError
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    total_images = len({str((Path(args.images) / name).resolve())
                        for sample in data for name in sample.get("images", {}).values()})
    cv = CVPipeline(total_images=total_images)
    print(f"Preparing {len(data)} samples, {total_images} unique image paths. OCR log: {cv.cache_dir / 'progress.jsonl'}", flush=True)
    formatted, rejected, failures = [], [], []
    for sample in data:
        try: normalize_program(sample["qa"]["program"])
        except ValueError as e:
            rejected.append({"qid": sample["qid"], "error": str(e), "stage": "gold_validation"})
            continue
        try: formatted.append(format_sample(sample, cv_pipeline=cv, image_dir=args.images))
        except CVInitializationError:
            raise
        except Exception as e: failures.append({"qid": sample["qid"], "error": str(e), "stage": "context"})
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.with_suffix(".rejected.json").write_text(json.dumps(rejected + failures, ensure_ascii=False, indent=2), encoding="utf-8")
    if failures or (rejected and not args.skip_invalid) or not formatted:
        raise ValueError(f"{len(rejected)} invalid golds, {len(failures)} context failures; inspect {path.with_suffix('.rejected.json')}. Existing dataset was not overwritten.")
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(formatted, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)
    print(f"Saved {len(formatted)} prepared samples to {path.resolve()}. "
          "OCR Markdown is embedded: copy this JSON to the training machine; "
          "original images and OCR cache are not required for training.", flush=True)

if __name__ == "__main__": main()
