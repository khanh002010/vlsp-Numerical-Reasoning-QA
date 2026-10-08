import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from vinumqa.cv_module.recover_store import merge_stores, recover
from vinumqa.cv_module.structure import STORE_VERSION, LEGACY_STRUCTURE_PROMPT_SHA256


def store(statuses):
    data = {"identity": {"version": STORE_VERSION, "model": "Qwen/Qwen2-VL-2B-Instruct",
                         "max_pixels": 1400000, "prompt_sha256": LEGACY_STRUCTURE_PROMPT_SHA256}, "images": {}}
    for image, status in statuses.items():
        key = hashlib.sha256(image.encode()).hexdigest()
        data["images"][key] = {"image": image, "sha256": key, "status": status, "requests": {}}
        if status == "ok":
            data["images"][key]["structure"] = {
                "title": image, "kind": "line", "series": [{"name": "TCB"}],
                "x_labels": ["2020"], "y_labels": [], "series_complete": True, "x_labels_complete": True,
            }
        else:
            data["images"][key]["error"] = "CV failed"
    return data


class RecoveryTests(unittest.TestCase):
    def test_recovers_baseline_success_preserves_new_success_and_does_not_mutate_inputs(self):
        baseline = store({"a": "ok", "b": "error", "c": "ok", "d": "error"})
        current = store({"a": "error", "b": "ok", "c": "ok", "e": "ok"})
        c_key = hashlib.sha256(b"c").hexdigest()
        current["images"][c_key]["structure"]["title"] = "new reading"
        original = copy.deepcopy([baseline, current])
        merged = merge_stores(baseline, current)
        self.assertEqual([baseline, current], original)
        self.assertEqual(merged["recovery"]["summary"], {"ok": 4, "error": 1})
        self.assertEqual(merged["images"][c_key]["structure"]["title"], "new reading")
        self.assertEqual(merged["images"][hashlib.sha256(b"a").hexdigest()]["recovery_source"], "baseline")

    def test_invalid_current_success_cannot_replace_valid_baseline(self):
        baseline, current = store({"a": "ok"}), store({"a": "ok"})
        key = next(iter(current["images"]))
        current["images"][key]["structure"]["series"] *= 2
        merged = merge_stores(baseline, current)
        self.assertEqual(merged["images"][key]["status"], "ok")
        self.assertEqual(merged["images"][key]["recovery_source"], "baseline")

    def test_mismatched_model_pixels_prompt_or_hash_rejected(self):
        baseline = store({"a": "ok"})
        for field, value in [("model", "another/model"), ("max_pixels", 750000), ("prompt_sha256", "unknown")]:
            current = copy.deepcopy(baseline)
            current["identity"][field] = value
            with self.assertRaisesRegex(ValueError, "incompatible"): merge_stores(baseline, current)
        current = copy.deepcopy(baseline)
        next(iter(current["images"].values()))["sha256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "hash"): merge_stores(baseline, current)

    def test_recovery_refuses_overwrite_and_is_loadable_without_cv(self):
        from vinumqa.cv_module.structure_store import ChartStructureStore
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / "image.png"
            image.write_bytes(b"a")
            current_path, out = root / "current.json", root / "new/store.json"
            current_path.write_text(json.dumps(store({"a": "error"})), encoding="utf-8")
            before = current_path.read_bytes()
            recover(current_path, store({"a": "ok"}), out)
            self.assertEqual(current_path.read_bytes(), before)
            cv_store = ChartStructureStore(out)
            self.assertEqual(cv_store.get(image)["series"][0]["name"], "TCB")
            self.assertIsNone(cv_store.reader)
            for target in (out, current_path):
                with self.assertRaisesRegex(ValueError, "overwritten"):
                    recover(current_path, store({"a": "ok"}), target)


if __name__ == "__main__": unittest.main()
