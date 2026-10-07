"""Resumable batch generation. Invalid candidates stay in diagnostics, not submissions."""
import argparse
import hashlib
import json
from pathlib import Path
from vinumqa.pipeline.full_pipeline import ViNumQAPipeline
from vinumqa.utils.dsl_parser import validate_program
from vinumqa.nlp_module.contracts import FORMAT_VERSION, INSTRUCTION
from vinumqa.cv_module.structure import STRUCTURE_PROMPT, STORE_VERSION

def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)

def run_batch_inference(test_json_path, output_path, img_dir, lora_path=None, pipeline=None,
                        structure_store="prepared/chart_structures.json", max_cv_requests=2):
    data = json.loads(Path(test_json_path).read_text(encoding="utf-8"))
    if len({s["qid"] for s in data}) != len(data): raise ValueError("Duplicate QIDs")
    output = Path(output_path)
    diagnostics = output.with_suffix(".diagnostics.json")
    lora_path = lora_path or "outputs/nlp_module/final"
    manifest = Path(lora_path) / "pipeline_manifest.json"
    identity = hashlib.sha256(Path(test_json_path).read_bytes() + str(Path(lora_path).resolve()).encode()
                              + (manifest.read_bytes() if manifest.exists() else b"") + FORMAT_VERSION.encode() + INSTRUCTION.encode()
                              + STORE_VERSION.encode() + STRUCTURE_PROMPT.encode()).hexdigest()
    records = {}
    if diagnostics.exists():
        previous = json.loads(diagnostics.read_text(encoding="utf-8"))
        if previous.get("run_id") != identity: raise ValueError("Output belongs to another dataset/adapter; choose another output path")
        records = previous["records"]
    owns_pipeline = pipeline is None
    if owns_pipeline:
        pipeline = ViNumQAPipeline(nlp_lora_weights=lora_path, structure_store=structure_store, max_cv_requests=max_cv_requests)
    try:
        for sample in data:
            qid = sample["qid"]
            if records.get(qid, {}).get("valid"): continue
            try:
                result = pipeline.run(sample.get("text", []), sample.get("tables", {}),
                    {k: str(Path(img_dir) / v) for k, v in sample.get("images", {}).items()}, sample["qa"]["question"])
                reasoning = result["reasoning_result"]
                valid, reason = validate_program(reasoning.get("program", ""), sources=set(sample.get("tables", {})) | set(sample.get("images", {})))
                records[qid] = {**reasoning, "valid": valid and not reasoning.get("error") and reasoning.get("valid", True), "validation_error": reason if not valid else reasoning.get("validation_error", "")}
            except Exception as e: records[qid] = {"valid": False, "error": str(e), "program": ""}
            save_json(diagnostics, {"run_id": identity, "format_version": FORMAT_VERSION, "records": records})
    finally:
        if owns_pipeline: pipeline.close()
    failures = [s["qid"] for s in data if not records.get(s["qid"], {}).get("valid")]
    if failures: raise RuntimeError(f"{len(failures)} invalid/failed predictions. See {diagnostics}; rerun to retry. Submission was not overwritten.")
    results = [{"qid": s["qid"], "predicted": records[s["qid"]]["program"]} for s in data]
    save_json(output, results)
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/public_test/public_test.json")
    parser.add_argument("--images", default="data/public_test/public_test_images")
    parser.add_argument("--adapter", default="outputs/nlp_module/final")
    parser.add_argument("--output", default="submission.json")
    parser.add_argument("--structure-store", default="prepared/chart_structures.json")
    parser.add_argument("--max-cv-requests", type=int, default=2)
    args = parser.parse_args()
    run_batch_inference(args.input, args.output, args.images, args.adapter,
                        structure_store=args.structure_store, max_cv_requests=args.max_cv_requests)
