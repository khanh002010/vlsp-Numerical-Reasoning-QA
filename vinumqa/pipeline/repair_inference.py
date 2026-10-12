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
from vinumqa.nlp_module.prompting import reviewed_context as add_source_review


DEFAULT_REVIEWED = Path(__file__).resolve().parents[1] / 'data' / 'reviewed_private_structures.json'


def fatal_runtime_error(error):
    message = str(error).lower()
    return any(x in message for x in ('out of memory', 'device-side assert', 'cuda error',
                                      'context budget', 'model not loaded', 'initialization failed'))


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


def needs_cv_before_retry(prediction, check, charts):
    """Only defer pure missing-evidence errors; wrong known labels still get NLP repair."""
    if prediction.get('cv_request') and check.get('cv_requests'):
        return True
    if not check.get('cv_requests') or not check.get('errors'):
        return False
    # Don't suppress repair of DSL, source choice, Step-1 or numerical reasoning.
    for error in check['errors']:
        if error.startswith('Missing chart structure for '):
            continue
        if not any(f'unverified {field} label' in error for field in ('x_labels', 'y_labels')):
            return False
    for request in check['cv_requests']:
        chart = charts.get(request['image_id'])
        if chart is None:
            continue
        field = {'x_axis': 'x_labels', 'y_axis': 'y_labels'}.get(request['region'])
        if field is None or chart.get(field + '_complete', False):
            return False
    return True


def export_outputs(output_dir, data, state, phase):
    records = state["records"]
    programs = [{"qid": s["qid"], "program": records.get(s["qid"], {}).get("program", "")
                 if records.get(s["qid"], {}).get("valid") else ""} for s in data]
    ready = sum(bool(r["program"]) for r in programs)
    # Save state first. Reruns rebuild all exports from state if interrupted mid-export.
    write_json(output_dir / "state.json", state)
    # Never publish empty programs as a submission. Progress and failures have separate files.
    accepted = [r for r in programs if r['program']]
    write_json(output_dir / "accepted.partial.json", [{"qid": r["qid"], "predicted": r["program"]} for r in accepted])
    write_json(output_dir / "unresolved.json", [
        {'qid': s['qid'], 'question': s['qa']['question'],
         'candidate': records.get(s['qid'], {}).get('program') or None,
         'errors': records.get(s['qid'], {}).get('evidence_validation', {}).get('errors', ['Not processed'])}
        for s in data if not records.get(s['qid'], {}).get('valid') or not records.get(s['qid'], {}).get('program')])
    if ready == len(data):
        write_json(output_dir / "results.json", [{"qid": r["qid"], "predicted": r["program"]} for r in programs])
        write_json(output_dir / "results_program.json", programs)
    else:
        for name in ('results.json', 'results_program.json'):
            path = output_dir / name
            if path.exists():
                path.replace(output_dir / f'{name}.{time.time_ns()}.superseded')
    write_json(output_dir / "diagnostics.json", [{"qid": s["qid"], **records.get(s["qid"], {"valid": False, "status": "pending"})} for s in data])
    summary = {"total": len(data), "accepted_by_checks": ready, "unresolved": len(data) - ready,
               "complete": ready == len(data), "submission_written": ready == len(data), "phase": phase, "accuracy": None,
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
        old = store.record(path)
        if 'patch' in correction:
            if not old or not old.get('structure'):
                continue
            structure = validate_structure({**old['structure'], **correction['patch']})
            reviewed_fields = correction['patch']
        else:
            structure = validate_structure(correction["structure"])
            reviewed_fields = structure
        if old and old.get("structure") == structure and old.get('reviewed_fields') == reviewed_fields:
            continue
        history = (old or {}).get("structure_history", [])
        if old and old.get("structure"):
            history = history + [old["structure"]]
        store.data["images"][key] = {"image": path.name, "sha256": key, "status": "ok",
            "structure": structure, "structure_history": history, "requests": {},
            "review": correction["provenance"], 'reviewed_fields': reviewed_fields,
            "prompt_sha256": store.identity["prompt_sha256"]}
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
                entry = grouped.setdefault(key, {"path": path, "hints": set(), "regions": set()})
                entry['regions'].add(request['region'])
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
            regions = entry['regions']
            request = {"image_id": "Image 1", "kind": "inspect", "region": next(iter(regions)) if len(regions) == 1 else 'full',
                       "series": "; ".join(sorted(entry["hints"]))[:200]}
            signature = digest([key, request, INSPECTION_VERSION])
            previous = state['inspections'].get(signature, {})
            if previous and (previous.get('status') != 'error' or previous.get('attempts', 1) >= 2):
                continue
            before = digest((store.record(path) or {}).get("structure"))
            print(f"[CV review {index}/{len(grouped)}] {path.name}: START", flush=True)
            try:
                record = store.record(path)
                reviewed = (record or {}).get('reviewed_fields', {})
                legend_verified = request['region'] == 'legend' and 'series' in reviewed and record['structure'].get('series_complete')
                if record and record.get("review") and (record['review'].get('scope', 'full') == 'full' or legend_verified):
                    status = "pixel_verified_structure_retained"
                elif not record or record.get("status") != "ok":
                    store.get(path, retry_failed=True)
                    status = "read"
                else:
                    store.inspect(path, request, retry_failed=True)
                    status = "inspected"
                state["inspections"][signature] = {"image": path.name, "status": status, 'attempts': previous.get('attempts', 0)+1}
            except CVInitializationError:
                raise
            except (ValueError, RuntimeError, OSError) as error:
                if fatal_runtime_error(error):
                    raise
                state["inspections"][signature] = {"image": path.name, "status": "error", "error": str(error), 'attempts': previous.get('attempts', 0)+1}
            changed |= before != digest((store.record(path) or {}).get("structure"))
            print(f"[CV review {index}/{len(grouped)}] {path.name}: {state['inspections'][signature]}", flush=True)
    finally:
        store.close()
    return changed


def run_repair(input_path, image_dir, adapter, store_path, output_dir, *, previous_diagnostics=None,
               reviewed_structures=None, max_rounds=3, max_hours=10.5, generator_factory=None, store=None,
               nlp_attempts=2, nlp_device='cuda:0', max_generation_seconds=120, progress_seconds=30):
    if max_rounds < 1 or max_hours <= 0 or nlp_attempts < 1:
        raise ValueError("max_rounds and max_hours must be positive")
    if reviewed_structures is None and DEFAULT_REVIEWED.is_file():
        reviewed_structures = DEFAULT_REVIEWED
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
        store = ChartStructureStore.from_saved(store_path)
    if generator_factory is None:
        def generator_factory():
            from vinumqa.nlp_module.inference.generate_program import ProgramGenerator
            return ProgramGenerator(lora_weights=str(adapter), device=nlp_device,
                                    max_generation_seconds=max_generation_seconds,
                                    progress_seconds=progress_seconds)
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
                if fatal_runtime_error(error):
                    raise
                print(f"[CV prepare {index}/{len(paths)}] {path.name}: {error}", flush=True)
        store.close()
        # Partial reviewed patches need a base structure. Newly prepared images
        # did not have one during the first application above.
        apply_reviewed_structures(store, paths, reviewed_structures)
        queue = []
        for sample in data:
            charts, _, _, _ = source_view(sample, image_dir, store)
            previous_row = previous.get(sample['qid'], {})
            # Saved requests refer to the old OCR snapshot. Recheck after reviewed
            # corrections, rather than paying to reread labels that are already fixed.
            requests = list(check_prediction(previous_row, sample, charts).get('cv_requests', [])) if previous_row.get('program') else []
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
                reviewed_context = add_source_review(context, sample.get('tables', {}))
                prompt = build_prompt(reviewed_context + feedback,
                                      sample["qa"]["question"], ", ".join(images))
                print(f"[NLP round {round_index+1}/{max_rounds} {index}/{len(data)}] {qid}: START", flush=True)
                cached = prompt in cache
                if not cached and generator is None:
                    store.close()
                    generator = generator_factory()
                history = list(old.get("repair_history", []))
                initial_prompt = prompt
                attempt_signatures = set()
                for attempt in range(nlp_attempts):
                    try:
                        prediction = dict(cache[initial_prompt]) if cached else generator.generate_with_prompt(prompt)
                        if fatal_runtime_error(prediction.get('error', '')):
                            raise RuntimeError(prediction['error'])
                        check = check_prediction(prediction, sample, charts)
                    except Exception as error:
                        if fatal_runtime_error(error):
                            raise
                        prediction = {"program": "", "error": str(error)}
                        check = {"valid": False, "errors": [str(error)], "cv_requests": []}
                    history.append({"program": prediction.get("program", ""), "errors": check["errors"],
                                    "source_digest": context_digest, 'prompt_sha256': digest(prompt),
                                    'cv_requests': check['cv_requests']})
                    if check['valid']:
                        cache[initial_prompt] = dict(prediction)
                        break
                    signature = digest([prediction.get('program'), prediction.get('cv_request'), check['errors']])
                    if signature in attempt_signatures:
                        print('  [NLP retry stopped] Same candidate/errors; saved for CV review or next round.', flush=True)
                        break
                    attempt_signatures.add(signature)
                    if round_index + 1 < max_rounds and needs_cv_before_retry(prediction, check, charts):
                        print('  [NLP -> CV queue] Missing evidence in incomplete structure; defer NLP retry until CV review.', flush=True)
                        break
                    if expired() or attempt + 1 == nlp_attempts:
                        break
                    feedback = '\n\n### Repair attempt\n' + json.dumps({
                        'attempt': len(history), 'previous_program': prediction.get('program'),
                        'errors': check['errors'], 'instruction':
                        'Rebuild the complete program from source facts. Fix all errors, connect every branch to the final result, and emit both aligned Steps 1 and 2. Use exact existing labels when you picked the wrong source/name. If the required label truly is absent, return a CV request; never invent labels or change the question to pass validation. Do not repeat the rejected program.'}, ensure_ascii=False)
                    prompt = build_prompt(reviewed_context + feedback, sample['qa']['question'], ', '.join(images))
                    print(f"  [NLP repair {attempt+1}/{nlp_attempts}] {check['errors'][:2]}", flush=True)
                state["records"][qid] = {**prediction, "valid": check["valid"], "cache_hit": cached,
                    "source_digest": context_digest, "evidence_validation": check, "unavailable_images": missing,
                    "repair_history": history, "status": "accepted" if check["valid"] else "needs_review"}
                queue.append((sample, check["cv_requests"]))
                print(f'  [SAVE] {qid}: writing state and diagnostics', flush=True)
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
    parser.add_argument('--nlp-attempts', type=int, default=2)
    parser.add_argument('--nlp-device', default='cuda:0', help='cuda:0 (one GPU), cuda:1, auto (dispatch), or cpu')
    parser.add_argument('--max-generation-seconds', type=float, default=120, help='Soft limit per generation; cannot interrupt a blocked CUDA forward')
    parser.add_argument('--progress-seconds', type=float, default=30, help='CPU heartbeat interval during generation')
    args = parser.parse_args()
    result = run_repair(args.input, args.images, args.adapter, args.structure_store, args.output_dir,
                        previous_diagnostics=args.previous_diagnostics, reviewed_structures=args.reviewed_structures,
                        max_rounds=args.max_rounds, max_hours=args.max_hours, nlp_attempts=args.nlp_attempts,
                        nlp_device=args.nlp_device, max_generation_seconds=args.max_generation_seconds,
                        progress_seconds=args.progress_seconds)
    if not result["complete"]:
        print("Unresolved predictions remain; rerun the same command to resume, inspect diagnostics before submitting.", flush=True)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
