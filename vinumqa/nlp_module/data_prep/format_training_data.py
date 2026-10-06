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

def format_sample(sample, include_dsl_prompt=True, cv_pipeline=None, image_dir=None, image_tables=None):
    # include_dsl_prompt retained for callers; the contract is always identical.
    images = {k: str(Path(image_dir or ".") / v) for k, v in sample.get("images", {}).items()}
    context = build_inline_context(sample.get("text", []), sample.get("tables", {}), images, cv_pipeline,
                                   prepared_images=image_tables)
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
    parser.add_argument("--start-image", type=int, default=1, help="Start OCR at this 1-based unique image ordinal")
    parser.add_argument("--retry-failed", action="store_true", help="Retry saved failed images at or after --start-image")
    parser.add_argument("--skip-invalid", action="store_true", help="Compatibility flag; invalid samples are now always saved with error status")
    args = parser.parse_args()
    from vinumqa.nlp_module.data_prep.incremental import prepare_incrementally
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    prepare_incrementally(data, args.images, args.output, args.start_image, retry_failed=args.retry_failed)

if __name__ == "__main__": main()
