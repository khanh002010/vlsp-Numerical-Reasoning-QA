"""Recover successful chart reads into a new store, without loading a CV model."""
import argparse
import copy
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

from vinumqa.cv_module.structure import (
    STORE_VERSION, STRUCTURE_PROMPT, STRUCTURE_RETRY_PROMPT,
    LEGACY_STRUCTURE_PROMPT_SHA256, validate_structure,
)
from vinumqa.nlp_module.data_prep.incremental import write_json


def merge_stores(baseline, current):
    prompt_hash = hashlib.sha256((STRUCTURE_PROMPT + "\n" + STRUCTURE_RETRY_PROMPT).encode()).hexdigest()
    identity = {"version": STORE_VERSION, "model": "Qwen/Qwen2-VL-2B-Instruct",
                "max_pixels": 1400000, "prompt_sha256": prompt_hash}
    merged, ranks, selected = {}, {}, Counter()
    inputs = []
    for source, data in (("baseline", baseline), ("current", current)):
        source_identity = data.get("identity", {})
        if (any(source_identity.get(k) != identity[k] for k in ("version", "model", "max_pixels"))
                or source_identity.get("prompt_sha256") not in {prompt_hash, LEGACY_STRUCTURE_PROMPT_SHA256}):
            raise ValueError(f"{source}: incompatible store identity; refusing to mix models/pixels/contracts")
        if not isinstance(data.get("images"), dict): raise ValueError(f"{source}: missing images map")
        inputs.append({"source": source, "identity": copy.deepcopy(source_identity),
                       "images": len(data["images"])})
        for key, original in data["images"].items():
            if not re.fullmatch(r"[0-9a-f]{64}", key) or original.get("sha256") != key:
                raise ValueError(f"{source}: invalid image content hash")
            record = copy.deepcopy(original)
            record.setdefault("prompt_sha256", source_identity["prompt_sha256"])
            if record.get("status") == "ok":
                try:
                    validate_structure(record["structure"])
                    rank = 2
                except (ValueError, TypeError, KeyError) as error:
                    record.update(status="error", error="Recovery validation failed: " + str(error))
                    rank = 0
            elif record.get("status") == "error":
                rank = 1
            else:
                raise ValueError(f"{source}: unknown record status")
            # Prefer a valid success over every failure. On ties, keep the current
            # run, including any new successful reads. Preserve original evidence.
            if key not in merged or rank >= ranks[key]:
                merged[key], ranks[key] = record, rank
                record["recovery_source"] = source
    for record in merged.values(): selected[record["recovery_source"]] += 1
    return {"identity": identity, "images": merged,
            "recovery": {"inputs": inputs, "selected": dict(selected),
                         "summary": dict(Counter(r["status"] for r in merged.values()))}}


def recover(current_path, baseline, output_path):
    current_path, output_path = Path(current_path), Path(output_path)
    if output_path.exists() or output_path.resolve() == current_path.resolve():
        raise ValueError("Choose a new --output-store; existing progress will not be overwritten")
    current = json.loads(current_path.read_text(encoding="utf-8"))
    result = merge_stores(baseline, current)
    write_json(output_path, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current-store", required=True)
    parser.add_argument("--output-store", required=True)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--baseline-store", help="Optional baseline JSON file instead of Git")
    source.add_argument("--baseline-ref", default="origin/main", help="Local Git ref containing prepared/chart_structures.json")
    args = parser.parse_args()
    if args.baseline_store:
        baseline = json.loads(Path(args.baseline_store).read_text(encoding="utf-8"))
    else:
        repo = Path(__file__).resolve().parents[2]
        raw = subprocess.check_output(["git", "show", f"{args.baseline_ref}:prepared/chart_structures.json"], cwd=repo)
        baseline = json.loads(raw)
    result = recover(args.current_store, baseline, args.output_store)
    print(json.dumps(result["recovery"], ensure_ascii=False, indent=2), flush=True)
    print(f"Saved recovered store: {Path(args.output_store).resolve()}", flush=True)
    print("No CV was run. Rebuild prepared datasets using this store and the new output directory.", flush=True)


if __name__ == "__main__": main()
