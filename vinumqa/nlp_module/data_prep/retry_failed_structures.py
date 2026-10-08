"""Retry only failed image records, saving into original artifacts after each image."""
import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from vinumqa.nlp_module.data_prep.prepare_structures import prepare_structured


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared-dir", type=Path, default=Path("prepared"))
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    parser.add_argument("--splits", nargs="+", choices=("train", "public_test"),
                        default=["train", "public_test"])
    parser.add_argument("--max-minutes", type=float, default=90,
                        help="Soft time budget per split; checked between images")
    args = parser.parse_args()
    if args.max_minutes <= 0:
        parser.error("--max-minutes must be positive")
    prepared = args.prepared_dir.resolve()
    store = prepared / "chart_structures.json"
    if not store.is_file():
        parser.error(f"Missing existing store: {store}")
    # Preflight every split before creating backups or mutating any artifact.
    jobs = []
    for split in dict.fromkeys(args.splits):
        output = prepared / f"{split}_structured.json"
        artifact = json.loads(output.read_text(encoding="utf-8"))
        if artifact.get("artifact_version") != "vinumqa-prepared-structures-v1":
            parser.error(f"Not a structure artifact: {output}")
        data = json.loads((args.data_root / split / f"{split}.json").read_text(encoding="utf-8"))
        image_dir = args.data_root / split / f"{split}_images"
        failed = [r for r in artifact["images"] if r["status"] == "error"]
        for row in failed:
            if not (image_dir / row["image"]).is_file():
                parser.error(f"Missing failed image: {image_dir / row['image']}")
        print(f"{split}: retry {len(failed)}/{len(artifact['images'])} images; "
              "successful/pending images are not selected", flush=True)
        jobs.append((split, output, data, image_dir, len(failed)))
    if not any(job[-1] for job in jobs):
        print("No failed images. Nothing changed.", flush=True)
        return
    backup = prepared / "backups" / datetime.now(timezone.utc).strftime("retry_%Y%m%dT%H%M%S_%fZ")
    backup.mkdir(parents=True, exist_ok=False)
    for source in [store] + [p for _, out, _, _, _ in jobs for p in (
            out, out.with_suffix(".ocr_errors.json"), out.with_suffix(".rejected.json")) if p.exists()]:
        shutil.copy2(source, backup / source.name)
    print(f"Backup: {backup}", flush=True)
    for split, output, data, image_dir, count in jobs:
        if not count: continue
        result = prepare_structured(data, image_dir, output, store_path=store,
                                    only_failed=True, max_minutes=args.max_minutes)
        print(f"{split}: {result['summary']}", flush=True)


if __name__ == "__main__":
    main()
