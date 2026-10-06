"""Save OCR directly into a resumable prepared dataset, without a separate CV cache."""
import hashlib
import json
import os
import time
from pathlib import Path

ARTIFACT_VERSION = "vinumqa-prepared-v1"


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(path)


def prepare_incrementally(data, image_dir, output, start_image=1, extractor=None, retry_failed=False):
    from vinumqa.cv_module.pipeline import CVPipeline, CVInitializationError
    from vinumqa.nlp_module.data_prep.format_training_data import format_sample
    from vinumqa.nlp_module.contracts import FORMAT_VERSION, INSTRUCTION

    output = Path(output)
    # First occurrence in dataset order; repeated image IDs have only one ordinal.
    names = list(dict.fromkeys(name for sample in data for name in sample.get("images", {}).values()))
    if not 1 <= start_image <= max(1, len(names) + 1):
        raise ValueError(f"start-image must be between 1 and {max(1, len(names) + 1)}")
    fingerprint = hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    prompt_hash = hashlib.sha256(INSTRUCTION.encode()).hexdigest()
    if output.exists():
        artifact = json.loads(output.read_text(encoding="utf-8"))
        if not isinstance(artifact, dict) or artifact.get("artifact_version") != ARTIFACT_VERSION:
            raise ValueError("Output already contains a legacy dataset. Use a new --output filename to preserve it.")
        if (artifact.get("source_sha256") != fingerprint or artifact.get("format_version") != FORMAT_VERSION
                or artifact.get("prompt_sha256") != prompt_hash):
            raise ValueError("Source data or formatting contract changed. Use a new --output filename.")
        if [r["image"] for r in artifact["images"]] != names:
            raise ValueError("Saved image order does not match source dataset")
    else:
        artifact = {"artifact_version": ARTIFACT_VERSION, "source_sha256": fingerprint,
                    "format_version": FORMAT_VERSION, "prompt_sha256": prompt_hash,
                    "images": [{"image": name, "index": i, "status": "pending", "markdown": None}
                               for i, name in enumerate(names, 1)], "samples": []}
    records = {r["image"]: r for r in artifact["images"]}

    def rebuild_samples():
        rows = []
        previous = artifact["samples"]
        for position, sample in enumerate(data):
            related = [records[name] for name in sample.get("images", {}).values()]
            errors = [r for r in related if r["status"] == "error"]
            pending = [r for r in related if r["status"] == "pending"]
            if errors or pending:
                rows.append({"qid": sample["qid"], "status": "error" if errors else "pending",
                             "error": "Images not ready: " + ", ".join(r["image"] for r in errors + pending),
                             "source": sample})
                continue
            if (position < len(previous) and previous[position]["qid"] == sample["qid"]
                    and previous[position]["status"] == "ready"):
                rows.append(previous[position])
                continue
            try:
                tables = {key: records[name]["markdown"] for key, name in sample.get("images", {}).items()}
                prepared = format_sample(sample, image_tables=tables)
                rows.append({"qid": sample["qid"], "status": "ready", "data": prepared})
            except Exception as error:
                rows.append({"qid": sample["qid"], "status": "error", "error": str(error), "source": sample})
        artifact["samples"] = rows
        artifact["summary"] = {status: sum(r["status"] == status for r in rows)
                               for status in ("ready", "error", "pending")}

    def save():
        write_json(output, artifact)
        write_json(output.with_suffix(".ocr_errors.json"),
                   [r for r in artifact["images"] if r["status"] == "error"])
        write_json(output.with_suffix(".rejected.json"),
                   [{"qid": r["qid"], "status": r["status"], "error": r["error"]}
                    for r in artifact["samples"] if r["status"] != "ready"])

    rebuild_samples()
    save()
    for record in artifact["images"]:
        index, name = record["index"], record["image"]
        if index < start_image:
            continue
        if record["status"] == "ok" or (record["status"] == "error" and not retry_failed):
            print(f"[OCR image {index}/{len(names)}] {name}: SAVED_{record['status'].upper()}", flush=True)
            continue
        print(f"[OCR image {index}/{len(names)}] {name}: START (writing directly to {output})", flush=True)
        image_path = Path(image_dir) / name
        if image_path.is_file() and extractor is None:
            try:
                from vinumqa.cv_module.chart_to_table.extract_table import ChartToTableExtractor
                extractor = ChartToTableExtractor()
            except Exception as error:
                raise CVInitializationError(f"Cannot initialize OCR model: {error}. Progress saved to {output}") from error
        started = time.monotonic()
        try:
            if not image_path.is_file(): raise FileNotFoundError(image_path)
            table = extractor.extract(str(image_path))
            CVPipeline._validate(table, image_path)
            record.update(status="ok", markdown=table)
            record.pop("error", None)
        except Exception as error:
            record.update(status="error", markdown=None, error=str(error))
        record["seconds"] = round(time.monotonic() - started, 2)
        # Persist the image before rebuilding dependent samples; a restart can rebuild them.
        write_json(output, artifact)
        rebuild_samples()
        save()
        print(f"[OCR image {index}/{len(names)}] {name}: SAVED_{record['status'].upper()} "
              f"({record['seconds']}s); samples={artifact['summary']}", flush=True)
    print(f"Saved prepared dataset: {output.resolve()}; samples={artifact['summary']}", flush=True)
    return artifact
