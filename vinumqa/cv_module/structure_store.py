"""Durable per-image records shared by preparation, requests and lookup execution."""
import hashlib
import json
from pathlib import Path
from vinumqa.cv_module.structure import (
    STORE_VERSION, STRUCTURE_PROMPT, STRUCTURE_RETRY_PROMPT, LEGACY_STRUCTURE_PROMPT_SHA256, validate_structure, merge_observation,
)
from vinumqa.nlp_module.data_prep.incremental import write_json
from vinumqa.cv_module.pipeline import CVInitializationError


class SavedVisionFailure(RuntimeError):
    pass


INSPECTION_VERSION = "legend-axis-review-v3-separated-fields"


class ChartStructureStore:
    @classmethod
    def from_saved(cls, path):
        """Reopen a store with its recorded vision model/read mode, never guess 2B."""
        path = Path(path)
        if not path.is_file(): return cls(path)
        identity = json.loads(path.read_text(encoding='utf-8')).get('identity', {})
        return cls(path, model_id=identity.get('model', 'Qwen/Qwen2-VL-2B-Instruct'),
                   load_in_4bit=identity.get('load_in_4bit', False), read_mode=identity.get('read_mode', 'joint'))

    def __init__(self, path="prepared/chart_structures.json", model_id="Qwen/Qwen2-VL-2B-Instruct", reader=None, reader_factory=None,
                 load_in_4bit=False, read_mode='joint'):
        if read_mode not in {'joint', 'parts'}: raise ValueError('Unknown structure read mode')
        self.path, self.model_id, self.reader = Path(path), model_id, reader
        self.load_in_4bit, self.read_mode = load_in_4bit, read_mode
        self.reader_factory = reader_factory
        self._initialization_error = None
        self.identity = {"version": STORE_VERSION, "model": model_id,
                         "prompt_sha256": hashlib.sha256((STRUCTURE_PROMPT + "\n" + STRUCTURE_RETRY_PROMPT).encode()).hexdigest(), "max_pixels": 1400000}
        if load_in_4bit: self.identity['load_in_4bit'] = True
        if read_mode != 'joint': self.identity['read_mode'] = read_mode
        self.data = {"identity": self.identity, "images": {}}
        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))
            if self.data.get("identity") != self.identity:
                previous = self.data.get("identity", {})
                expected_legacy = {**self.identity, "prompt_sha256": LEGACY_STRUCTURE_PROMPT_SHA256}
                if previous != expected_legacy:
                    raise ValueError("Chart store contract changed; use a new store filename")
                # This prompt-only upgrade keeps the same schema, model and pixels.
                # Retain successful reads and sticky failures, with original provenance.
                for record in self.data["images"].values():
                    record.setdefault("prompt_sha256", previous["prompt_sha256"])
                self.data.setdefault("migrations", []).append({"from": previous, "to": self.identity})
                self.data["identity"] = self.identity
                self.save()
        self._keys = {}

    def _key(self, path):
        path = Path(path).resolve()
        stat = path.stat()
        stamp = (str(path), stat.st_size, stat.st_mtime_ns)
        if stamp not in self._keys: self._keys[stamp] = hashlib.sha256(path.read_bytes()).hexdigest()
        return self._keys[stamp]

    def _reader(self):
        if self._initialization_error is not None:
            raise CVInitializationError(self._initialization_error)
        if self.reader is None:
            try:
                if self.reader_factory is not None:
                    self.reader = self.reader_factory()
                else:
                    from vinumqa.cv_module.structure_reader import ChartStructureReader
                    self.reader = ChartStructureReader(self.model_id, load_in_4bit=self.load_in_4bit, read_mode=self.read_mode)
            except Exception as error:
                self._initialization_error = f"Cannot load CV model: {error}"
                raise CVInitializationError(self._initialization_error) from error
        return self.reader

    def save(self):
        write_json(self.path, self.data)

    def record(self, path):
        return self.data["images"].get(self._key(path))

    def has_request(self, path, kind, payload):
        payload = {k: v for k, v in payload.items() if k != "image_id"}
        key = hashlib.sha256(json.dumps([kind, payload, self.identity["prompt_sha256"], INSPECTION_VERSION], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        return key in (self.record(path) or {}).get("requests", {})

    def get(self, path, retry_failed=False):
        key = self._key(path)
        record = self.data["images"].get(key)
        if record:
            if record["status"] == "ok":
                try:
                    return validate_structure(record["structure"])
                except ValueError as error:
                    record.update(status="error", error="Saved structure failed validation: " + str(error))
                    self.save()
            if not retry_failed: raise SavedVisionFailure(record["error"])
        reader = self._reader()  # Initialization failure must not blacklist the image.
        previous_generation = record.get("generation") if record else None
        record = {"image": Path(path).name, "sha256": key, "requests": {},
                  "prompt_sha256": self.identity["prompt_sha256"]}
        if previous_generation is not None: record["previous_generation"] = previous_generation
        try:
            structure = validate_structure(reader.read_structure(str(path)))
            record.update(status="ok", structure=structure)
        except Exception as error:
            record.update(status="error", error=str(error))
        record["generation"] = getattr(reader, "last_generation", {})
        self.data["images"][key] = record
        self.save()
        if record["status"] != "ok": raise SavedVisionFailure(record["error"])
        return structure

    def _request(self, path, kind, payload, run):
        structure = self.get(path)
        record = self.data["images"][self._key(path)]
        # Image IDs are sample-local; they must not prevent reuse across questions.
        payload = {k: v for k, v in payload.items() if k != "image_id"}
        key = hashlib.sha256(json.dumps([kind, payload, self.identity["prompt_sha256"], INSPECTION_VERSION], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        saved = record["requests"].get(key)
        if saved is not None:
            if saved["status"] != "ok": raise SavedVisionFailure(saved["error"])
            return saved["result"]
        reader = self._reader()
        try:
            result = run(reader, structure)
            saved = {"status": "ok", "result": result}
        except Exception as error:
            saved = {"status": "error", "error": str(error)}
        saved.update(kind=kind, request=payload, generation=getattr(reader, "last_generation", {}),
                     prompt_sha256=self.identity["prompt_sha256"])
        record["requests"][key] = saved
        self.save()
        if saved["status"] != "ok": raise SavedVisionFailure(saved["error"])
        return saved["result"]

    def inspect(self, path, request, retry_failed=False):
        def read(reader, original):
            observed = reader.inspect(str(path), request, original)
            observed["structure"] = validate_structure(observed["structure"])
            return observed
        if retry_failed:
            record = self.record(path)
            payload = {k: v for k, v in request.items() if k != 'image_id'}
            if record:
                record['requests'] = {k: v for k, v in record.get('requests', {}).items()
                    if not (v.get('kind') == 'inspect' and v.get('request') == payload and v.get('status') == 'error')}
        cached = self.has_request(path, "inspect", request)
        result = self._request(path, "inspect", request, read)
        record = self.data["images"][self._key(path)]
        if cached:
            # A repeated old request must not roll back a newer full-image review.
            return validate_structure(record["structure"])
        if result.get('replace_fields'):
            allowed = {'title', 'kind', 'series', 'series_complete', 'x_labels', 'x_labels_complete', 'x_order_known', 'y_labels'}
            updated = {**record['structure'], **{k: result['structure'][k] for k in result['replace_fields'] if k in allowed}}
            updated['uncertain'] = list(dict.fromkeys(record['structure'].get('uncertain', []) + result['structure'].get('uncertain', [])))
        else:
            updated = merge_observation(record["structure"], result["structure"], result.get("full_image", False))
        # Preserve fields transcribed from these exact image bytes by a human reviewer.
        # A new automated read must not reintroduce an already corrected OCR error.
        updated.update(record.get('reviewed_fields', {}))
        updated = validate_structure(updated)
        if updated != record["structure"]:
            record.setdefault("structure_history", []).append(record["structure"])
        record["structure"] = updated
        self.save()
        return record["structure"]

    def read_values(self, path, lookup):
        return self._request(path, "values", lookup,
                             lambda reader, structure: reader.read_values(str(path), lookup, structure))

    def close(self):
        if self.reader is not None:
            close = getattr(self.reader, "close", None)
            if close: close()
            self.reader = None
