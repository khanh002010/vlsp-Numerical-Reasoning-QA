"""Diagnose one image at independent token budgets; save even truncated outputs.

python -m vinumqa.cv_module.ocr_token_probe --image path/to/image.png
"""
import argparse
import hashlib
import json
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def write_json(path, value):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def run_probe(generate, budgets, output_dir, metadata=None):
    """generate(budget) returns text, raw_text, token_ids, eos, seconds."""
    budgets = list(dict.fromkeys(budgets))
    if not budgets or any(b <= 0 for b in budgets):
        raise ValueError("Token budgets must be positive integers")
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    summary = {"metadata": metadata or {}, "budgets": budgets, "results": []}
    write_json(directory / "summary.json", summary)
    for budget in budgets:
        print(f"[PROBE] budget={budget}: START", flush=True)
        started = time.perf_counter()
        try:
            result = generate(budget)
        except Exception as error:
            row = {"budget": budget, "status": "error", "error": str(error),
                   "seconds": round(time.perf_counter() - started, 2)}
            write_json(directory / f"tokens_{budget}.error.json", row)
        else:
            # Diagnostic output is deliberately kept even without EOS.
            (directory / f"tokens_{budget}.md").write_text(result["text"], encoding="utf-8")
            (directory / f"tokens_{budget}.raw.txt").write_text(result["raw_text"], encoding="utf-8")
            write_json(directory / f"tokens_{budget}.ids.json", result["token_ids"])
            counts = Counter(line.strip() for line in result["text"].splitlines() if line.strip())
            repeated = [{"line": line, "count": count} for line, count in counts.most_common(10) if count > 1]
            count = len(result["token_ids"])
            row = {"budget": budget, "generated_tokens": count, "eos": result["eos"],
                   "status": "eos" if result["eos"] else "limit_reached" if count >= budget else "stopped_without_eos",
                   "seconds": result["seconds"], "markdown": f"tokens_{budget}.md",
                   "repeated_lines": repeated}
            write_json(directory / f"tokens_{budget}.meta.json", row)
        summary["results"].append(row)
        write_json(directory / "summary.json", summary)
        print(f"[PROBE] budget={budget}: {row['status']}, seconds={row['seconds']}; saved to {directory}", flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True)
    parser.add_argument("--budgets", nargs="+", type=int, default=[1024, 2048, 4096, 8192, 16384])
    parser.add_argument("--output-dir", default="outputs/ocr_probe", help="Parent directory; each run creates a new subfolder")
    parser.add_argument("--model", default="Qwen/Qwen2-VL-2B-Instruct")
    parser.add_argument("--device", choices=["cuda", "cpu"], default="cuda")
    args = parser.parse_args()
    path = Path(args.image)
    if not path.is_file(): parser.error(f"Image not found: {path}")
    if any(b <= 0 for b in args.budgets): parser.error("Budgets must be positive")

    import torch
    from PIL import Image
    from qwen_vl_utils import process_vision_info
    from vinumqa.cv_module.chart_to_table.extract_table import ChartToTableExtractor, preprocess_image, classify_chart_type, MAX_PIXELS
    from vinumqa.cv_module.chart_to_table.token_budget import reached_eos

    extractor = ChartToTableExtractor(model_id=args.model, device=args.device)
    with Image.open(path) as opened:
        original_size = opened.size
        image = preprocess_image(opened.convert("RGB"))
    prompt = classify_chart_type(image)["prompt_hint"] + "\n\n" + extractor.base_prompt
    messages = [{"role": "user", "content": [{"type": "image", "image": image}, {"type": "text", "text": prompt}]}]
    text = extractor.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    images, videos = process_vision_info(messages)
    inputs = extractor.processor(text=[text], images=images, videos=videos, padding=True,
                                 return_tensors="pt").to(extractor.device)
    directory = Path(args.output_dir) / f"{path.stem}_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}_{uuid4().hex[:8]}"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "prompt.txt").write_text(text, encoding="utf-8")
    metadata = {"image": str(path.resolve()), "image_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "model": args.model, "device": extractor.device, "original_size": original_size,
                "processed_size": image.size, "max_pixels": MAX_PIXELS,
                "input_tokens": inputs.input_ids.shape[1], "do_sample": False,
                "generation_config": extractor.model.generation_config.to_dict(),
                "note": "Independent generations from the same input. EOS does not prove OCR correctness. Repeated lines are a diagnostic only."}

    def generate(budget):
        started = time.perf_counter()
        with torch.inference_mode():
            output = extractor.model.generate(**inputs, max_new_tokens=budget, do_sample=False)
        ids = output[0, inputs.input_ids.shape[1]:].detach().cpu().tolist()
        seconds = round(time.perf_counter() - started, 2)
        return {"text": extractor.processor.batch_decode([ids], skip_special_tokens=True, clean_up_tokenization_spaces=False)[0],
                "raw_text": extractor.processor.batch_decode([ids], skip_special_tokens=False, clean_up_tokenization_spaces=False)[0],
                "token_ids": ids, "eos": bool(ids) and reached_eos(ids[-1], extractor.model.generation_config.eos_token_id),
                "seconds": seconds}

    summary = run_probe(generate, args.budgets, directory, metadata)
    print(f"Results: {directory.resolve()}", flush=True)
    if any(row["status"] == "error" for row in summary["results"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
