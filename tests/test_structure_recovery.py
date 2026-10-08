"""Regressions from the Kaggle CV failures, without changing image evidence/gold."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from PIL import Image

from vinumqa.cv_module.structure import (
    STRUCTURE_PROMPT, LEGACY_STRUCTURE_PROMPT, LEGACY_STRUCTURE_PROMPT_SHA256,
)
from vinumqa.cv_module.structure_output import parse_structure_output, json_repetition_reason
from vinumqa.cv_module.structure_reader import ChartStructureReader
from vinumqa.cv_module.structure_store import ChartStructureStore, SavedVisionFailure
from vinumqa.nlp_module.data_prep.prepare_structures import prepare_structured
from vinumqa.nlp_module.contracts import parse_response
from vinumqa.utils.dsl_parser import normalize_program, validate_program, parse_program

ROOT = Path(__file__).resolve().parents[1]


def structure():
    return {"title": "TCB", "kind": "line", "series": [{"name": "TCB", "axis": "left"}],
            "x_labels": ["2019", "2020"], "y_labels": [], "x_labels_complete": True,
            "series_complete": True, "regions": {}, "uncertain": []}


def generation(value, eos=True, tokens=100, reason=None):
    return {"text": value if isinstance(value, str) else json.dumps(value, ensure_ascii=False),
            "eos": eos, "tokens": tokens, "token_ids": [1] * tokens, "seconds": 1,
            "stop_reason": reason or ("eos" if eos else "stopped_without_eos")}


def reader(results):
    value = ChartStructureReader.__new__(ChartStructureReader)
    value.backend = Mock(max_pixels=1400000)
    value.backend.prepare_inputs.return_value = ("inputs", "prompt")
    value.backend.generate_once.side_effect = results
    return value


class OutputTests(unittest.TestCase):
    def test_empty_y_labels_and_duplicates_are_vocabulary_cleanup_only(self):
        original = structure()
        original["y_labels"] = ["0%", "100%", "", None, "0%", " 100% ", "Doanh thu"]
        result, repairs = parse_structure_output(json.dumps(original))
        self.assertEqual(result["y_labels"], ["0%", "100%", "Doanh thu"])
        self.assertIn("removed duplicate y label", repairs)
        self.assertIn("removed empty y label", repairs)
        self.assertEqual(result["series"][0]["name"], "TCB")
        original["y_labels"] = [100]
        with self.assertRaises(ValueError): parse_structure_output(json.dumps(original))

    def test_bare_keys_and_trailing_commas_preserve_literal_text(self):
        value = structure()
        value["title"] = 'Literal ,color:red and {axis: left}, quote "here"'
        text = json.dumps(value, ensure_ascii=False).replace('"axis":', 'axis:')
        text = text[:-1] + ',}'
        result, repairs = parse_structure_output(text)
        self.assertEqual(result["title"], value["title"])
        self.assertEqual(result["series"][0]["axis"], "left")
        self.assertIn("quoted key: axis", repairs)
        self.assertIn("removed trailing comma", repairs)

    def test_truncated_json_duplicate_keys_and_series_remain_errors(self):
        for text in ['{"title":"unterminated', '{"title":"a","title":"b"}']:
            with self.assertRaises(ValueError): parse_structure_output(text)
        value = structure()
        value["series"] = [{"name": "Nhà nước", "color": color} for color in ("red", "gray", "maroon")]
        with self.assertRaisesRegex(ValueError, "Duplicate labels in series"):
            parse_structure_output(json.dumps(value))

    def test_punctuation_loop_stops_without_rejecting_repeated_numeric_values(self):
        self.assertTrue(json_repetition_reason('{"y_labels":[' + '")","(",' * 30))
        self.assertTrue(json_repetition_reason('{"y_labels":[' + '"",' * 15))
        self.assertIsNone(json_repetition_reason('{"values":[' + '"100",' * 30))

    def test_old_enum_placeholders_become_unknown_metadata(self):
        value = structure()
        value["kind"] = "line/bar/pie/mixed/table/unknown"
        value["series"][0]["axis"] = "left/right/none"
        result, _ = parse_structure_output(json.dumps(value))
        self.assertEqual(result["kind"], "unknown")
        self.assertEqual(result["series"][0]["axis"], "none")
        self.assertNotIn("line/bar/pie/mixed/table/unknown", STRUCTURE_PROMPT)


class RetryTests(unittest.TestCase):
    def test_duplicate_series_triggers_one_new_prompt_preserving_both_outputs(self):
        bad = structure()
        bad["series"] *= 3
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "image.png"
            Image.new("RGB", (100, 100)).save(path)
            cv = reader([generation(bad), generation(structure())])
            cv.read_structure(path)
            self.assertEqual([a["phase"] for a in cv.last_generation["attempts"]], ["primary", "retry"])
            self.assertIn("Duplicate labels in series", cv.last_generation["retry_reason"])
            prompts = [call.args[1] for call in cv.backend.prepare_inputs.call_args_list]
            self.assertNotEqual(prompts[0], prompts[1])
            self.assertIn("legend", prompts[1])
            self.assertEqual(cv.backend.generate_once.call_count, 2)

    def test_time_limit_and_incomplete_json_never_accepted_or_retried_forever(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "image.png"
            Image.new("RGB", (100, 100)).save(path)
            # Even syntactically complete text without EOS is not declared successful.
            cv = reader([generation(structure(), eos=False), generation('{"title":"partial'),
                         generation('{"title":"partial'), generation({"box": None}),
                         generation({"region": "unknown"})])
            with self.assertRaises(ValueError): cv.read_structure(path)
            self.assertEqual(cv.backend.generate_once.call_count, 5)
            cv = reader([generation('{"x_labels":[', False, 1024),
                         generation('{"x_labels":[', False, 2048), generation('{"title":"partial'),
                         generation('{"title":"partial'), generation({"box": None}),
                         generation({"region": "unknown"})])
            with self.assertRaises(ValueError): cv.read_structure(path)
            self.assertEqual([c.args[1] for c in cv.backend.generate_once.call_args_list], [1024, 2048, 2048, 1024, 256, 128])


class MigrationTests(unittest.TestCase):
    def test_known_legacy_store_preserves_success_failure_and_provenance(self):
        self.assertEqual(hashlib.sha256(LEGACY_STRUCTURE_PROMPT.encode()).hexdigest(), LEGACY_STRUCTURE_PROMPT_SHA256)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good, bad = root / "good.png", root / "bad.png"
            good.write_bytes(b"good")
            bad.write_bytes(b"bad")
            cv = Mock(read_structure=Mock(side_effect=[structure(), ValueError("old failure")]), last_generation={})
            store = ChartStructureStore(root / "store.json", reader=cv)
            store.get(good)
            with self.assertRaises(SavedVisionFailure): store.get(bad)
            data = json.loads(store.path.read_text(encoding="utf-8"))
            data["identity"]["prompt_sha256"] = LEGACY_STRUCTURE_PROMPT_SHA256
            for record in data["images"].values(): record.pop("prompt_sha256")
            store.path.write_text(json.dumps(data), encoding="utf-8")
            fresh_reader = Mock(read_structure=Mock(return_value=structure()), last_generation={})
            fresh = ChartStructureStore(store.path, reader=fresh_reader)
            fresh.get(good, retry_failed=True)
            with self.assertRaises(SavedVisionFailure): fresh.get(bad)
            fresh_reader.read_structure.assert_not_called()
            self.assertEqual(fresh.record(good)["prompt_sha256"], LEGACY_STRUCTURE_PROMPT_SHA256)
            fresh.get(bad, retry_failed=True)
            fresh_reader.read_structure.assert_called_once_with(str(bad))
            self.assertEqual(fresh.record(bad)["prompt_sha256"], fresh.identity["prompt_sha256"])
            self.assertEqual(len(fresh.data["migrations"]), 1)
            self.assertEqual(ChartStructureStore(store.path).get(good), fresh.get(good))

    def test_unknown_prompt_or_changed_pixels_still_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "store.json"
            store = ChartStructureStore(path)
            store.save()
            baseline = json.loads(path.read_text())
            for change in ({"prompt_sha256": "unrecognized"},
                           {"prompt_sha256": LEGACY_STRUCTURE_PROMPT_SHA256, "max_pixels": 750000}):
                data = copy.deepcopy(baseline)
                data["identity"].update(change)
                path.write_text(json.dumps(data))
                with self.assertRaisesRegex(ValueError, "contract changed"): ChartStructureStore(path)


class TargetTests(unittest.TestCase):
    def test_all_real_targets_prepare_without_discarding_the_missing_separator_sample(self):
        for split in ("train", "public_test"):
            data = json.loads((ROOT / f"data/{split}/{split}.json").read_text(encoding="utf-8"))
            for sample in data:
                program = normalize_program(sample["qa"]["program"], allow_newline_separators=True)
                self.assertTrue(validate_program(program)[0], sample["qid"])
                if sample["qid"] == "05a85e9c-7c27-529f-924b-466218915da3":
                    self.assertEqual([s.operator for s in parse_program(program)], ["chart_average", "table_average", "subtract"])
                    self.assertEqual(parse_program(program)[-1].args, ["#0", "#1"])
                    self.assertFalse(validate_program(sample["qa"]["program"])[0])  # Inference remains strict.

    def test_newline_normalization_does_not_touch_labels_or_accept_adjacent_steps(self):
        fixed = normalize_program("add(1; 2)\n\nsubtract(#0; 1)", allow_newline_separators=True)
        self.assertEqual(fixed, "add(1; 2); subtract(#0; 1)")
        program = "chart_at(Image 1; Nhóm (A)\nCấp 1; 2020; none)"
        self.assertEqual(parse_program(normalize_program(program, allow_newline_separators=True))[0].args[1], "Nhóm (A)\nCấp 1")
        for program in ["add(1; 2)subtract(#0; 1)", "add(1; 2)\nbad(3; 4)", "INVALID"]:
            with self.assertRaises(ValueError): normalize_program(program, allow_newline_separators=True)

    def test_preparation_rebuilds_saved_target_error_without_reading_images_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / "image.png"
            image.write_bytes(b"image")
            sample = {"qid": "missing-separator", "images": {"Image 1": image.name},
                      "qa": {"question": "?", "program": "chart_at(Image 1; TCB; 2020; none)\nsubtract(#0; 1)"}}
            cv = Mock(read_structure=Mock(return_value=structure()), last_generation={})
            store = ChartStructureStore(root / "store.json", reader=cv)
            output = root / "train.json"
            artifact = prepare_structured([sample], root, output, store=store)
            artifact["samples"] = [{"qid": sample["qid"], "status": "error", "source": sample, "error": "INVALID"}]
            output.write_text(json.dumps(artifact), encoding="utf-8")
            loaded = ChartStructureStore(store.path, reader_factory=Mock(side_effect=AssertionError("No CV needed")))
            recovered = prepare_structured([sample], root, output, store=loaded)
            self.assertEqual(recovered["summary"]["ready"], 1)
            program = parse_response(recovered["samples"][0]["data"]["output"])["program"]
            self.assertEqual(program, "chart_at(Image 1; TCB; 2020; none); subtract(#0; 1)")


if __name__ == "__main__": unittest.main()
