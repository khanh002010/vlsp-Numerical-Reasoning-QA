"""Persistent content-addressed CV cache; extraction failures never become evidence."""
import hashlib
import json
from pathlib import Path

class CVPipeline:
    CACHE_VERSION = "chart-markdown-v4"

    def __init__(self, model_id="Qwen/Qwen2-VL-2B-Instruct", cache_dir="outputs/cv_cache", extractor=None):
        self.model_id = model_id
        self.cache_dir = Path(cache_dir)
        self.extractor = extractor

    def process_image(self, image_path):
        payload = Path(image_path).read_bytes()
        key = hashlib.sha256(payload + (self.CACHE_VERSION + self.model_id).encode()).hexdigest()
        target = self.cache_dir / (key + ".json")
        if target.exists():
            table = json.loads(target.read_text(encoding="utf-8"))["table"]
        else:
            if self.extractor is None:
                from vinumqa.cv_module.chart_to_table.extract_table import ChartToTableExtractor
                self.extractor = ChartToTableExtractor(model_id=self.model_id)
            table = self.extractor.extract(image_path)
        if not isinstance(table, str) or len(table.strip().splitlines()) < 3 or "| Lỗi |" in table or "extracted by CV Module" in table:
            raise ValueError(f"Invalid CV extraction: {image_path}")
        if not target.exists():
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            temp = target.with_suffix(".tmp")
            temp.write_text(json.dumps({"table": table, "model": self.model_id, "version": self.CACHE_VERSION}, ensure_ascii=False), encoding="utf-8")
            temp.replace(target)
        return table

    def process_batch(self, image_paths):
        return {p: self.process_image(p) for p in image_paths}
