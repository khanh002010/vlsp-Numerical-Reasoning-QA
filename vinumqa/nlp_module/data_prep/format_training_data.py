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

def format_sample(sample, include_dsl_prompt=True, cv_pipeline=None, image_dir=None, image_tables=None, image_structures=None,
                  prompt_profile='legacy'):
    # include_dsl_prompt retained for callers; the contract is always identical.
    images = {k: str(Path(image_dir or ".") / v) for k, v in sample.get("images", {}).items()}
    context = build_inline_context(sample.get("text", []), sample.get("tables", {}), images, cv_pipeline,
                                   prepared_images=image_tables, chart_structures=image_structures)
    from vinumqa.nlp_module.prompting import apply_prompt_profile
    context = apply_prompt_profile(context, sample.get('tables', {}), prompt_profile)
    program = normalize_program(sample["qa"]["program"], allow_newline_separators=True)
    evidence = evidence_from_program(program)
    result = {"qid": sample["qid"], "format_version": FORMAT_VERSION,
        "group_keys": ["image:" + v for v in sample.get("images", {}).values()] + ["doc:" + hashlib.sha256(
            json.dumps({k: sample.get(k) for k in ["text", "tables"]}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()],
        "instruction": INSTRUCTION,
        "input": input_text(context, sample["qa"]["question"], ", ".join(images)),
        "output": "| Step | Output |\n|---|---|\n| 1 | " + evidence + " |\n| 2 | " + program + " |"}
    if image_structures is not None: result["charts"] = image_structures
    if prompt_profile != 'legacy': result['prompt_profile'] = prompt_profile
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--images", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--start-image", type=int, default=1, help="Start OCR at this 1-based unique image ordinal")
    parser.add_argument("--retry-failed", action="store_true", help="Retry saved failed images at or after --start-image")
    parser.add_argument("--skip-invalid", action="store_true", help="Compatibility flag; invalid samples are now always saved with error status")
    parser.add_argument("--image-mode", choices=["structure", "legacy-markdown"], default="structure")
    parser.add_argument("--structure-store", default="prepared/chart_structures.json", help="Durable image records shared across datasets")
    parser.add_argument("--max-minutes", type=float, help="Stop between images after this preparation time budget")
    parser.add_argument('--prompt-profile', choices=['legacy', 'source-review-v1'], default='legacy')
    parser.add_argument('--cv-model', default='Qwen/Qwen2-VL-2B-Instruct')
    parser.add_argument('--cv-4bit', action='store_true', help='4-bit CUDA vision model; use a new store')
    parser.add_argument('--cv-read-mode', choices=['joint', 'parts', 'reviewed'], default='joint')
    args = parser.parse_args()
    from vinumqa.nlp_module.data_prep.incremental import prepare_incrementally
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if args.image_mode == "structure":
        from vinumqa.nlp_module.data_prep.prepare_structures import prepare_structured
        from vinumqa.cv_module.structure_store import ChartStructureStore
        store = ChartStructureStore(args.structure_store, args.cv_model,
                                    load_in_4bit=args.cv_4bit, read_mode=args.cv_read_mode)
        prepare_structured(data, args.images, args.output, args.structure_store, args.start_image,
                           args.retry_failed, args.max_minutes, store=store, prompt_profile=args.prompt_profile)
    else:
        prepare_incrementally(data, args.images, args.output, args.start_image, retry_failed=args.retry_failed)

if __name__ == "__main__": main()
