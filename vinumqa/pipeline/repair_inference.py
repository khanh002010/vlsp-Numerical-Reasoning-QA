"""Resumable CV/NLP rounds, one resident model, durable per-question outputs.

Run on raw question JSON plus an image store, not a store pretending to be samples.
No training labels are read, and no chart operation is replaced by a numeric answer.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path

from vinumqa.cv_module.pipeline import CVInitializationError
from vinumqa.cv_module.structure import validate_structure, validate_request
from vinumqa.cv_module.structure_store import ChartStructureStore, INSPECTION_VERSION
from vinumqa.data.context import build_inline_context
from vinumqa.nlp_module.contracts import build_prompt, INSTRUCTION
from vinumqa.nlp_module.data_prep.incremental import write_json
from vinumqa.nlp_module.inference.evidence_validation import validate_evidence
from vinumqa.nlp_module.inference.semantic_validation import REVIEW_GUIDANCE, REVIEW_VERSION, structure_concerns


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def file_digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def source_view(sample, image_dir, store):
    charts, missing = {}, {}
    images = {k: str(Path(image_dir) / v) for k, v in sample.get("images", {}).items()}
    for key, path in images.items():
        try:
            record = store.record(path)
            if not record or record.get("status") != "ok":
                missing[key] = (record or {}).get("error", "Image has no saved structure")
            else:
                charts[key] = validate_structure(record["structure"])
        except (ValueError, OSError) as error:
            missing[key] = str(error)
    context = build_inline_context(sample.get("text", []), sample.get("tables", {}), images,
                                   None, chart_structures=charts, allow_unavailable_images=True)
    return charts, images, missing, context


def check_prediction(prediction, sample, charts):
    request = prediction.get("cv_request")
    if request:
        try:
            request = validate_request(request, sample.get("images", {}))
            return {"valid": False, "errors": ["CV inspection requested"], "cv_requests": [request]}
        except ValueError as error:
            return {"valid": False, "errors": [str(error)], "cv_requests": []}
    check = validate_evidence(prediction.get("program", ""), charts,
                              set(sample.get("images", {})) | set(sample.get("tables", {})),
                              prediction.get("extracted_values", ""), tables=sample.get("tables", {}),
                              text_segments=sample.get("text", []), question=sample["qa"]["question"])
    if prediction.get("termination") != "eos" or prediction.get("error"):
        check["errors"].append(prediction.get("error") or "Generation did not finish at EOS")
    check["valid"] = not check["errors"]
    return check


def export_outputs(output_dir, data, state, phase):
    records = state["records"]
    programs = [{"qid": s["qid"], "program": records.get(s["qid"], {}).get("program", "")
                 if records.get(s["qid"], {}).get("valid") else ""} for s in data]
    ready = sum(bool(r["program"]) for r in programs)
    # Save state first. Reruns rebuild all exports from state if interrupted mid-export.
    write_json(output_dir / "state.json", state)
    write_json(output_dir / "results.json", [{"qid": r["qid"], "predicted": r["program"]} for r in programs])
    write_json(output_dir / "results_program.json", programs)
    write_json(output_dir / "diagnostics.json", [{"qid": s["qid"], **records.get(s["qid"], {"valid": False, "status": "pending"})} for s in data])
    summary = {"total": len(data), "accepted_by_checks": ready, "unresolved": len(data) - ready,
               "complete": ready == len(data), "phase": phase, "accuracy": None,
               "note": "Accepted is not official accuracy; inspect diagnostics before submission"}
    write_json(output_dir / "summary.json", summary)
    return summary


def apply_reviewed_structures(store, image_paths, corrections_path):
    if not corrections_path:
        return
    corrections = read_json(corrections_path)
    for path in image_paths:
        key = file_digest(path) if path.is_file() else None
        correction = corrections.get(key)
        if not correction:
            continue
        structure = validate_structure(correction["structure"])
        old = store.record(path)
        if old and old.get("structure") == structure:
            continue
        history = (old or {}).get("structure_history", [])
        if old and old.get("structure"):
            history = history + [old["structure"]]
        store.data["images"][key] = {"image": path.name, "sha256": key, "status": "ok",
            "structure": structure, "structure_history": history, "requests": {},
            "review": correction["provenance"], "prompt_sha256": store.identity["prompt_sha256"]}
        store.save()
        print(f"[CV reviewed] {path.name}: applied pixel-verified labels, SHA256 matched", flush=True)


def inspect_queue(store, queue, image_dir, state, expired):
    """Group sample-local requests by image bytes; NLP must already be closed."""
    grouped = {}
    for sample, requests in queue:
        for raw in requests:
            try:
                request = validate_request(raw, sample.get("images", {}))
                path = Path(image_dir) / sample["images"][request["image_id"]]
                key = file_digest(path)
                entry = grouped.setdefault(key, {"path": path, "hints": set()})
                if request["series"]:
                    entry["hints"].add(request["series"])
            except (ValueError, OSError) as error:
                print(f"[CV request rejected] {sample['qid']}: {error}", flush=True)
    changed = False
    try:
        for index, (key, entry) in enumerate(grouped.items(), 1):
            if expired():
                break
            path = entry["path"]
            # One full-image review addresses all labels requested by all questions.
            request = {"image_id": "Image 1", "kind": "inspect", "region": "full",
                       "series": "; ".join(sorted(entry["hints"]))[:200]}
            signature = digest([key, request, INSPECTION_VERSION])
            if signature in state["inspections"]:
                continue
            before = digest((store.record(path) or {}).get("structure"))
            print(f"[CV review {index}/{len(grouped)}] {path.name}: START", flush=True)
            try:
                record = store.record(path)
                if record and record.get("review"):
                    status = "pixel_verified_structure_retained"
                elif not record or record.get("status") != "ok":
                    store.get(path, retry_failed=True)
                    status = "read"
                else:
                    store.inspect(path, request)
                    status = "inspected"
                state["inspections"][signature] = {"image": path.name, "status": status}
            except CVInitializationError:
                raise
            except (ValueError, RuntimeError, OSError) as error:
                state["inspections"][signature] = {"image": path.name, "status": "error", "error": str(error)}
            changed |= before != digest((store.record(path) or {}).get("structure"))
            print(f"[CV review {index}/{len(grouped)}] {path.name}: {state['inspections'][signature]}", flush=True)
    finally:
        store.close()
    return changed


def run_repair(input_path, image_dir, adapter, store_path, output_dir, *, previous_diagnostics=None,
               reviewed_structures=None, max_rounds=3, max_hours=10.5, generator_factory=None, store=None):
    if max_rounds < 1 or max_hours <= 0:
        raise ValueError("max_rounds and max_hours must be positive")
    data = read_json(input_path)
    if not isinstance(data, list) or len({s["qid"] for s in data}) != len(data):
        raise ValueError("Input must be raw question records with unique qid, not an image store")
    # Exclude all training labels from run state, context, prompts and identity.
    data = [{"qid": s["qid"], "text": s.get("text", []), "tables": s.get("tables", {}),
             "images": s.get("images", {}), "qa": {"question": s["qa"]["question"]}} for s in data]
    output_dir = Path(output_dir)
    names = list(dict.fromkeys(v for s in data for v in s["images"].values()))
    paths = [Path(image_dir) / name for name in names]
    adapter = Path(adapter)
    adapter_files = sorted(p for p in adapter.iterdir() if p.is_file() and
                           (p.suffix in {".json", ".safetensors", ".jinja"} or p.name == "adapter_model.bin")) if adapter.exists() else []
    if generator_factory is None and not adapter_files:
        raise FileNotFoundError(f"Adapter files missing: {adapter}")
    identity = digest({"data": data, "adapter": [(p.name, file_digest(p)) for p in adapter_files],
        "images": [(p.name, file_digest(p) if p.is_file() else None) for p in paths],
        "policy": REVIEW_VERSION, "instruction": INSTRUCTION, "review_guidance": REVIEW_GUIDANCE,
        "inspection": INSPECTION_VERSION,
        "corrections": file_digest(reviewed_structures) if reviewed_structures else None})
    state_path = output_dir / "state.json"
    if not state_path.exists() and any((output_dir / name).exists() for name in
                                       ("results.json", "results_program.json", "diagnostics.json")):
        raise ValueError("Output directory already contains results without repair state; choose a new --output-dir")
    state = read_json(state_path) if state_path.exists() else {"run_id": identity, "records": {}, "inspections": {}}
    if state["run_id"] != identity:
        raise ValueError("Data/adapter/images/review policy changed. Choose a new --output-dir.")
    previous = {}
    if previous_diagnostics:
        old = read_json(previous_diagnostics)
        previous = old.get("records", {}) if isinstance(old, dict) else {r["qid"]: r for r in old}
    if store is None:
        store = ChartStructureStore(store_path)
    if generator_factory is None:
        def generator_factory():
            from vinumqa.nlp_module.inference.generate_program import ProgramGenerator
            return ProgramGenerator(lora_weights=str(adapter))
    started = time.monotonic()
    expired = lambda: time.monotonic() - started >= max(0, max_hours * 3600 - min(300, max_hours * 3600 / 10))
    generator = None
    try:
        apply_reviewed_structures(store, paths, reviewed_structures)
        # Read missing/failed images ONCE per unique file in this invocation.
        for index, path in enumerate(paths, 1):
            if expired(): break
            try:
                record = store.record(path)
                if record and record.get("status") == "ok":
                    print(f"[CV prepare {index}/{len(paths)}] {path.name}: SAVED", flush=True)
                    continue
                print(f"[CV prepare {index}/{len(paths)}] {path.name}: READ/RETRY", flush=True)
                store.get(path, retry_failed=True)
            except CVInitializationError:
                raise
            except (ValueError, RuntimeError, OSError) as error:
                print(f"[CV prepare {index}/{len(paths)}] {path.name}: {error}", flush=True)
        store.close()
        queue = []
        for sample in data:
            charts, _, _, _ = source_view(sample, image_dir, store)
            requests = list(previous.get(sample["qid"], {}).get("evidence_validation", {}).get("cv_requests", []))
            requests.extend({"image_id": k, "kind": "inspect", "region": "full", "series": ""}
                            for k, c in charts.items() if structure_concerns(c))
            queue.append((sample, requests))
        inspect_queue(store, queue, image_dir, state, expired)
        # Any changed structure invalidates previous outputs of every dependent question.
        def invalidate_stale():
            for sample in data:
                row = state["records"].get(sample["qid"])
                if not row:
                    continue
                charts, _, missing, context = source_view(sample, image_dir, store)
                if row.get("source_digest") != digest([context, charts, missing]):
                    row.update(valid=False, status="source_changed")
        invalidate_stale()
        export_outputs(output_dir, data, state, "prepared")
        for round_index in range(max_rounds):
            queue, cache = [], {}
            if expired(): break
            for index, sample in enumerate(data, 1):
                if expired(): break
                qid = sample["qid"]
                charts, images, missing, context = source_view(sample, image_dir, store)
                context_digest = digest([context, charts, missing])
                old = state["records"].get(qid, {})
                if old.get("valid") and old.get("source_digest") == context_digest:
                    continue
                prior = old or previous.get(qid, {})
                prior_check = check_prediction(prior, sample, charts) if prior.get("program") else {}
                feedback = ""
                if prior_check.get("errors"):
                    feedback = "\n\n### Validation feedback\n" + json.dumps({
                        "previous_program": prior.get("program", ""), "errors": prior_check["errors"]}, ensure_ascii=False)
                prompt = build_prompt(context + "\n\n### Source review\n" + REVIEW_GUIDANCE + feedback,
                                      sample["qa"]["question"], ", ".join(images))
                print(f"[NLP round {round_index+1}/{max_rounds} {index}/{len(data)}] {qid}: START", flush=True)
                cached = prompt in cache
                if not cached and generator is None:
                    store.close()
                    generator = generator_factory()
                try:
                    prediction = dict(cache[prompt]) if cached else generator.generate_with_prompt(prompt)
                    check = check_prediction(prediction, sample, charts)
                    if check["valid"]:
                        cache[prompt] = dict(prediction)
                except Exception as error:
                    prediction = {"program": "", "error": str(error)}
                    check = {"valid": False, "errors": [str(error)], "cv_requests": []}
                history = list(old.get("repair_history", []))
                history.append({"program": prediction.get("program", ""), "errors": check["errors"],
                                "source_digest": context_digest})
                state["records"][qid] = {**prediction, "valid": check["valid"], "cache_hit": cached,
                    "source_digest": context_digest, "evidence_validation": check, "unavailable_images": missing,
                    "repair_history": history, "status": "accepted" if check["valid"] else "needs_review"}
                queue.append((sample, check["cv_requests"]))
                summary = export_outputs(output_dir, data, state, f"nlp_round_{round_index+1}")
                print(f"  valid={check['valid']}; accepted={summary['accepted_by_checks']}/{len(data)}; errors={check['errors'][:2]}", flush=True)
            if generator is not None:
                generator.close()
                generator = None
            # Never update structures on the final round without revalidating dependent outputs.
            if round_index + 1 < max_rounds and not expired():
                inspect_queue(store, queue, image_dir, state, expired)
                invalidate_stale()
                export_outputs(output_dir, data, state, "cv_reviewed")
            if all(state["records"].get(s["qid"], {}).get("valid") for s in data):
                break
    finally:
        if generator is not None: generator.close()
        store.close()
        # On interruption, do not leave results accepted against an obsolete structure.
        for sample in data:
            row = state["records"].get(sample["qid"])
            if not row: continue
            try:
                charts, _, missing, context = source_view(sample, image_dir, store)
                if row.get("source_digest") != digest([context, charts, missing]):
                    row.update(valid=False, status="source_changed")
            except (ValueError, OSError):
                row.update(valid=False, status="source_unavailable")
        summary = export_outputs(output_dir, data, state, "paused_time_budget" if expired() else "finished_or_interrupted")
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--images", required=True)
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--structure-store", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--previous-diagnostics")
    parser.add_argument("--reviewed-structures")
    parser.add_argument("--max-rounds", type=int, default=3)
    parser.add_argument("--max-hours", type=float, default=10.5)
    args = parser.parse_args()
    result = run_repair(args.input, args.images, args.adapter, args.structure_store, args.output_dir,
                        previous_diagnostics=args.previous_diagnostics, reviewed_structures=args.reviewed_structures,
                        max_rounds=args.max_rounds, max_hours=args.max_hours)
    if not result["complete"]:
        print("Unresolved predictions remain; rerun the same command to resume, inspect diagnostics before submitting.", flush=True)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
