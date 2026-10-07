"""Inventory and visual contact sheets; does not perform OCR or estimate exact tokens."""
import hashlib
import json
from collections import Counter
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
rows = []
for split in ("train", "public_test"):
    source = ROOT / "data" / split
    samples = json.loads((source / f"{split}.json").read_text(encoding="utf-8"))
    refs = Counter(name for sample in samples for name in sample.get("images", {}).values())
    for path in sorted((source / f"{split}_images").glob("*")):
        if not path.is_file(): continue
        row = {"split": split, "file": path.name, "path": str(path), "references": refs[path.name]}
        try:
            with Image.open(path) as opened:
                image = opened.convert("RGB")
            width, height = image.size
            processed = image
            if width * height > 750000:
                scale = (750000 / (width * height)) ** .5
                processed = image.resize((int(width * scale), int(height * scale)), Image.Resampling.LANCZOS)
            gray = processed.convert("L")
            gray.thumbnail((512, 512))
            hist = gray.filter(ImageFilter.FIND_EDGES).histogram()
            density = sum(hist[40:]) / (gray.width * gray.height)
            row.update(width=width, height=height, pixels=width*height,
                       edge_density=round(density, 5),
                       initial_budget=4096 if density > .20 else 2048 if density > .09 else 1024,
                       sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        except Exception as error:
            row["error"] = str(error)
        row["index"] = len(rows) + 1
        rows.append(row)

summary = {"files": len(rows), "errors": [r for r in rows if "error" in r]}
good = [r for r in rows if "error" not in r]
summary["unique_contents"] = len({r["sha256"] for r in good})
for split in ("train", "public_test", "all"):
    subset = [r for r in good if split == "all" or r["split"] == split]
    pixels = sorted(r["pixels"] for r in subset)
    summary[split] = {"count": len(subset), "referenced": sum(r["references"] > 0 for r in subset),
                      "over_750k": sum(p > 750000 for p in pixels),
                      "pixels_min": min(pixels), "pixels_max": max(pixels),
                      "pixels_median": pixels[len(pixels)//2],
                      "budgets": dict(Counter(r["initial_budget"] for r in subset))}
summary["densest_indices"] = [r["index"] for r in sorted(good, key=lambda r: r["edge_density"], reverse=True)[:20]]
(OUT / "inventory.json").write_text(json.dumps({"summary": summary, "images": rows}, indent=2), encoding="utf-8")
for page in range(0, len(good), 32):
    canvas = Image.new("RGB", (1600, 2240), "#eeeeee")
    draw = ImageDraw.Draw(canvas)
    for cell, row in enumerate(good[page:page+32]):
        x, y = (cell % 4)*400, (cell//4)*280
        with Image.open(row["path"]) as opened:
            thumb = ImageOps.contain(opened.convert("RGB"), (390, 250))
        canvas.paste(thumb, (x+(400-thumb.width)//2, y+25+(250-thumb.height)//2))
        draw.text((x+5, y+4), f"{row['index']:03} {row['split']} {row['width']}x{row['height']} cap={row['initial_budget']}", fill="black")
    canvas.save(OUT / f"sheet_{page//32+1:02}.jpg", quality=90)
print(json.dumps(summary, indent=2))
