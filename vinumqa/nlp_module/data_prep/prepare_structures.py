"""Save chart structures and portable training rows after every unique image."""
import hashlib
import json
import time
from pathlib import Path
from vinumqa.nlp_module.data_prep.incremental import write_json
from vinumqa.cv_module.structure_store import ChartStructureStore
from vinumqa.cv_module.pipeline import CVInitializationError

ARTIFACT_VERSION = "vinumqa-prepared-structures-v1"


def prepare_structured(data, image_dir, output, store_path="prepared/chart_structures.json",
                       start_image=1, retry_failed=False, max_minutes=None, store=None):
    from vinumqa.nlp_module.data_prep.format_training_data import format_sample
    from vinumqa.nlp_module.contracts import FORMAT_VERSION, INSTRUCTION
    output = Path(output)
    names = list(dict.fromkeys(name for sample in data for name in sample.get("images", {}).values()))
    if not 1 <= start_image <= max(1, len(names) + 1): raise ValueError("Invalid start-image")
    if max_minutes is not None and max_minutes <= 0: raise ValueError("max-minutes must be positive")
    fingerprint = hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    identity = {"artifact_version": ARTIFACT_VERSION, "format_version": FORMAT_VERSION,
                "source_sha256": fingerprint, "prompt_sha256": hashlib.sha256(INSTRUCTION.encode()).hexdigest()}
    artifact = {**identity, "images": [{"image": name, "index": i, "status": "pending"}
                                      for i, name in enumerate(names, 1)], "samples": []}
    if output.exists():
        artifact = json.loads(output.read_text(encoding="utf-8"))
        if not isinstance(artifact, dict) or any(artifact.get(k) != v for k, v in identity.items()):
            raise ValueError("Output uses different data/contract; choose a new --output for structure preparation")
        if [r["image"] for r in artifact["images"]] != names: raise ValueError("Image order changed")
    store = store if store is not None else ChartStructureStore(store_path)
    records = {r["image"]: r for r in artifact["images"]}

    def save():
        rows = []
        for sample in data:
            pending = [records[name] for name in sample.get("images", {}).values() if records[name]["status"] != "ok"]
            if pending:
                rows.append({"qid": sample["qid"], "status": "error" if any(r["status"] == "error" for r in pending) else "pending",
                             "source": sample, "error": "Image structure unavailable: " + ", ".join(r["image"] for r in pending)})
                continue
            try:
                structures = {key: records[name]["structure"] for key, name in sample.get("images", {}).items()}
                row = format_sample(sample, image_structures=structures)
                rows.append({"qid": sample["qid"], "status": "ready", "data": row})
            except Exception as error:
                rows.append({"qid": sample["qid"], "status": "error", "source": sample, "error": str(error)})
        artifact["samples"] = rows
        artifact["summary"] = {s: sum(r["status"] == s for r in rows) for s in ("ready", "pending", "error")}
        write_json(output, artifact)
        write_json(output.with_suffix(".ocr_errors.json"), [r for r in artifact["images"] if r["status"] == "error"])
        write_json(output.with_suffix(".rejected.json"), [{"qid": r["qid"], "status": r["status"], "error": r["error"]}
                                                       for r in rows if r["status"] != "ready"])

    started = time.monotonic()
    save()
    try:
        for record in artifact["images"]:
            if record["index"] < start_image: continue
            if max_minutes is not None and time.monotonic() - started >= max_minutes * 60:
                print("Preparation time budget reached; progress is saved. Resume using the same paths.", flush=True)
                break
            path = Path(image_dir) / record["image"]
            print(f"[Structure {record['index']}/{len(names)}] {record['image']}", flush=True)
            try:
                record.update(structure=store.get(path, retry_failed), status="ok")
                record["sha256"] = store.record(path)["sha256"]
                record.pop("error", None)
            except CVInitializationError:
                raise  # Environment failure is not an image failure.
            except Exception as error:
                record.update(status="error", error=str(error))
                record.pop("structure", None)
            saved = store.record(path) if path.is_file() else None
            if saved is not None: record["generation"] = saved.get("generation", {})
            save()
            print(f"Saved {record['status']}: {artifact['summary']}", flush=True)
    finally:
        store.close()
    return artifact
