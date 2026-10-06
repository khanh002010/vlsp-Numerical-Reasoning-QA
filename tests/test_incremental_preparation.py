import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vinumqa.nlp_module.data_prep.incremental import prepare_incrementally
from vinumqa.nlp_module.training.supervision import load_prepared_pair


class IncrementalPreparationTests(unittest.TestCase):
    def data(self):
        return [{"qid": str(i), "images": {"Image 1": name}, "text": ["### Image 1 ###"],
                 "qa": {"question": "?", "program": "add(1; 2)"}}
                for i, name in enumerate(["a.png", "b.png", "a.png", "c.png"])]

    def images(self, root):
        for name in ["a.png", "b.png", "c.png"]:
            (root / name).write_bytes(b"test-image")

    def test_errors_and_successes_saved_immediately_without_cv_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.images(root)
            output = root / "prepared.json"
            case = self
            class Extractor:
                calls = []
                def extract(self, path):
                    name = Path(path).name
                    self.calls.append(name)
                    if name == "b.png":
                        saved = json.loads(output.read_text(encoding="utf-8"))
                        case.assertEqual(saved["images"][0]["status"], "ok")
                        case.assertEqual(saved["samples"][0]["status"], "ready")
                        raise ValueError("OCR failed")
                    if name == "c.png":
                        errors = json.loads(output.with_suffix(".ocr_errors.json").read_text(encoding="utf-8"))
                        case.assertEqual(errors[0]["image"], "b.png")
                    return "| x |\n|---|\n| 1 |"
            extractor = Extractor()
            with patch("vinumqa.cv_module.pipeline.CVPipeline.process_image", side_effect=AssertionError("No cache")):
                result = prepare_incrementally(self.data(), root, output, extractor=extractor)
                self.assertEqual(extractor.calls, ["a.png", "b.png", "c.png"])
                self.assertEqual(result["summary"], {"ready": 3, "error": 1, "pending": 0})
                self.assertEqual(result["samples"][1]["source"]["qid"], "1")
                prepare_incrementally(self.data(), root, output, extractor=extractor)
                self.assertEqual(len(extractor.calls), 3)
                class RepairedExtractor:
                    calls = []
                    def extract(self, path):
                        self.calls.append(Path(path).name)
                        return "| x |\n|---|\n| 2 |"
                repaired = RepairedExtractor()
                result = prepare_incrementally(self.data(), root, output, start_image=2,
                                               extractor=repaired, retry_failed=True)
                self.assertEqual(repaired.calls, ["b.png"])
                self.assertEqual(result["summary"]["ready"], 4)
                self.assertEqual(json.loads(output.with_suffix(".ocr_errors.json").read_text()), [])
            self.assertFalse((root / "cache").exists())

    def test_interrupt_and_resume_at_image_ordinal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.images(root)
            output = root / "prepared.json"
            class Extractor:
                calls = []
                def extract(self, path):
                    self.calls.append(Path(path).name)
                    if len(self.calls) == 2: raise KeyboardInterrupt()
                    return "| x |\n|---|\n| 1 |"
            extractor = Extractor()
            with self.assertRaises(KeyboardInterrupt):
                prepare_incrementally(self.data(), root, output, extractor=extractor)
            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(saved["images"][0]["status"], "ok")
            self.assertEqual(saved["images"][1]["status"], "pending")
            result = prepare_incrementally(self.data(), root, output, start_image=2, extractor=extractor)
            self.assertEqual(extractor.calls, ["a.png", "b.png", "b.png", "c.png"])
            self.assertEqual(result["summary"]["ready"], 4)

    def test_start_without_previous_results_marks_pending_and_loader_requires_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.images(root)
            class Extractor:
                def extract(self, path): return "| x |\n|---|\n| 1 |"
            paths = [root / "train.json", root / "val.json"]
            for index, path in enumerate(paths):
                data = self.data()
                for row in data: row["qid"] = f"{index}-{row['qid']}"
                result = prepare_incrementally(data, root, path, start_image=2, extractor=Extractor())
                self.assertEqual(result["summary"]["pending"], 2)
            with self.assertRaisesRegex(ValueError, "skip-unready"):
                load_prepared_pair(*paths)
            train, val = load_prepared_pair(*paths, skip_unready=True)
            self.assertEqual([row["qid"] for row in train], ["0-1", "0-3"])
            self.assertEqual(len(val), 2)

    def test_output_protected_from_changed_source_and_invalid_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "prepared.json"
            prepare_incrementally(self.data(), root, output)  # Missing images become saved errors.
            original = output.read_bytes()
            for start in [0, 5]:
                with self.assertRaises(ValueError):
                    prepare_incrementally(self.data(), root, output, start_image=start)
            changed = self.data()
            changed[0]["qa"]["question"] = "changed"
            with self.assertRaisesRegex(ValueError, "Source data"):
                prepare_incrementally(changed, root, output)
            self.assertEqual(output.read_bytes(), original)


if __name__ == "__main__": unittest.main()
