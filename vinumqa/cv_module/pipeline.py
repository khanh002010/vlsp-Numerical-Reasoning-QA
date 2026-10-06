"""Persistent content-addressed CV cache; extraction failures never become evidence."""
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

class SkippedImageError(RuntimeError):
    """An image failed OCR and must not be retried automatically."""

class CVInitializationError(RuntimeError):
    """Fatal environment/model error; do not retry for every dataset row."""

class CVPipeline:
    # Keep successful v5 cache entries when increasing the generation cap.
    CACHE_VERSION = "chart-markdown-v5-adaptive-750k"

    def __init__(self, model_id="Qwen/Qwen2-VL-2B-Instruct", cache_dir="outputs/cv_cache", extractor=None, total_images=None):
        self.model_id = model_id
        self.cache_dir = Path(cache_dir)
        self.extractor = extractor
        self.total_images = total_images
        self._image_numbers = {}
        self._requests = 0
        self._initialization_error = None

    def _log(self, image_path, status, **details):
        identity = str(Path(image_path).resolve())
        number = self._image_numbers.setdefault(identity, len(self._image_numbers) + 1)
        event = {"time": datetime.now(timezone.utc).isoformat(), "image": Path(image_path).name,
                 "image_number": number, "seen_images": len(self._image_numbers),
                 "total_images": self.total_images, "request": self._requests,
                 "status": status, **details}
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        with (self.cache_dir / "progress.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + "\n")
        total = self.total_images if self.total_images is not None else "?"
        print(f"[OCR image {number}/{total}; seen={len(self._image_numbers)}] "
              f"{Path(image_path).name}: {status} "
              + json.dumps(details, ensure_ascii=False), flush=True)

    @staticmethod
    def _write_json(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        temp.replace(path)

    def process_image(self, image_path):
        self._requests += 1
        payload = Path(image_path).read_bytes()
        key = hashlib.sha256(payload + (self.CACHE_VERSION + self.model_id).encode()).hexdigest()
        target = self.cache_dir / (key + ".json")
        failure = self.cache_dir / "failures" / (key + ".json")
        if target.exists():
            table = json.loads(target.read_text(encoding="utf-8"))["table"]
            self._log(image_path, "CACHE_HIT")
        else:
            if failure.exists():
                record = json.loads(failure.read_text(encoding="utf-8"))
                self._log(image_path, "SKIP_FAILED", error=record["error"])
                raise SkippedImageError(f"Skipping previously failed image {image_path}: {record['error']}")
            self._log(image_path, "START")
            # A model initialization error must not blacklist an image.
            if self.extractor is None:
                if self._initialization_error is not None:
                    raise CVInitializationError(self._initialization_error)
                try:
                    from vinumqa.cv_module.chart_to_table.extract_table import ChartToTableExtractor
                    self.extractor = ChartToTableExtractor(model_id=self.model_id)
                except Exception as error:
                    self._initialization_error = f"Cannot initialize OCR model: {error}"
                    self._log(image_path, "INITIALIZATION_FAILED", error=str(error))
                    raise CVInitializationError(self._initialization_error) from error
            started = time.monotonic()
            try:
                table = self.extractor.extract(image_path)
                self._validate(table, image_path)
            except Exception as error:
                record = {"image": Path(image_path).name, "model": self.model_id, "error": str(error),
                          "time": datetime.now(timezone.utc).isoformat(),
                          "generation": getattr(self.extractor, "last_generation", None)}
                self._write_json(failure, record)
                self._log(image_path, "FAILED", error=str(error), seconds=round(time.monotonic() - started, 2),
                          generation=record["generation"])
                raise SkippedImageError(f"OCR failed; future occurrences will be skipped: {image_path}: {error}") from error
            self._write_json(target, {"table": table, "model": self.model_id, "version": self.CACHE_VERSION})
            self._log(image_path, "DONE", seconds=round(time.monotonic() - started, 2),
                      generation=getattr(self.extractor, "last_generation", None))
        self._validate(table, image_path)
        return table

    @staticmethod
    def _validate(table, image_path):
        if not isinstance(table, str) or len(table.strip().splitlines()) < 3 or "| Lỗi |" in table or "extracted by CV Module" in table:
            raise ValueError(f"Invalid CV extraction: {image_path}")

    def process_batch(self, image_paths):
        return {p: self.process_image(p) for p in image_paths}
