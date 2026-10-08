import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch

from vinumqa.cv_module.structure import validate_structure, validate_request, merge_observation
from vinumqa.cv_module.structure_store import ChartStructureStore, SavedVisionFailure
from vinumqa.cv_module.pipeline import CVInitializationError
from vinumqa.cv_module.chart_lookup import resolve_chart
from vinumqa.nlp_module.contracts import evidence_from_program, parse_response, RESPONSE_PREFIX, build_prompt
from vinumqa.nlp_module.inference.evidence_validation import validate_evidence
from vinumqa.nlp_module.data_prep.prepare_structures import prepare_structured
from vinumqa.nlp_module.data_prep.format_training_data import format_sample
from vinumqa.nlp_module.training.supervision import load_prepared_pair
from vinumqa.nlp_module.training.epoch_predictions import export_epoch_predictions
from vinumqa.nlp_module.training.session_control import SessionBudget, make_session_callback
from vinumqa.pipeline.full_pipeline import ViNumQAPipeline


def chart():
    return validate_structure({"title": "TCB", "kind": "line",
        "series": [{"name": "TCB"}, {"name": "Kỳ vọng thị trường"}],
        "x_labels": ["Jun-21", "Jul-21"], "y_labels": [],
        "x_labels_complete": True, "series_complete": True,
        "regions": {"legend": [0.1, 0.8, 0.9, 1]}})


PROGRAM = "chart_at(Image 1; TCB; Jul-21; none); subtract(#0; 2)"


def response(program=PROGRAM):
    return {"program": program, "extracted_values": evidence_from_program(program), "valid": True}


def point(series="TCB", x="Jul-21", value=12, basis="printed"):
    return {"series": series, "x_label": x, "y_label": "none", "value": value,
            "raw_value": str(value), "basis": basis}


class StructureTests(unittest.TestCase):
    def test_schema_rejects_duplicates_and_invalid_crop(self):
        for value in ([0, 0, 2, 1], [0.9, 0, 0.1, 1], [True, 0, 1, 1]):
            with self.assertRaises(ValueError):
                validate_request({"image_id": "Image 1", "box": value}, {"Image 1"})
        c = chart()
        c["series"].append(c["series"][0])
        with self.assertRaisesRegex(ValueError, "Duplicate"): validate_structure(c)
        for request in [{"image_id": "Image 2"}, {"image_id": "Image 1", "kind": "answer"}]:
            with self.assertRaises(ValueError): validate_request(request, {"Image 1"})

    def test_valid_program_keeps_lookup_and_all_reference_positions(self):
        self.assertTrue(validate_evidence(PROGRAM, {"Image 1": chart()}, {"Image 1"}, evidence_from_program(PROGRAM))["valid"])
        evidence = json.loads(evidence_from_program(PROGRAM))
        self.assertEqual(evidence[1]["arguments"], [{"position": 0, "value": "#0"}, {"position": 1, "value": "2"}])
        evidence[1]["arguments"].reverse()
        self.assertFalse(validate_evidence(PROGRAM, {"Image 1": chart()}, {"Image 1"}, evidence)["valid"])

    def test_labels_sources_ranges_and_operators_checked(self):
        for program in [PROGRAM.replace("Image 1", "Image 2"), PROGRAM.replace("TCB;", "TCBB;"),
                        PROGRAM.replace("Jul-21", "Aug-21"), "chart_max(Image 1; TCB; Jul-21; Jun-21)",
                        "chart_at(Table 1; TCB; Jul-21; none)", "chart_divide(Image 1; TCB; none; none)"]:
            with self.subTest(program=program):
                self.assertFalse(validate_evidence(program, {"Image 1": chart()}, {"Image 1", "Table 1"})["valid"])
        c = chart()
        c["x_labels_complete"] = False
        self.assertTrue(validate_evidence("chart_max(Image 1; TCB; none; none)", {"Image 1": c}, {"Image 1"})["valid"])
        self.assertTrue(validate_evidence("chart_total(Image 1; Jul-21; none; none)", {"Image 1": c}, {"Image 1"})["valid"])

    def test_crop_does_not_claim_global_order_or_completeness(self):
        c = merge_observation(chart(), chart())
        self.assertFalse(c["x_order_known"])
        checked = validate_evidence("chart_max(Image 1; TCB; Jun-21; Jul-21)", {"Image 1": c}, {"Image 1"})
        self.assertFalse(checked["valid"])
        self.assertEqual(checked["cv_requests"][0]["region"], "full")

    def test_cv_request_is_a_separate_response(self):
        result = parse_response('{"cv_request":{"image_id":"Image 1","region":"legend"}}')
        self.assertEqual(result["cv_request"]["region"], "legend")
        self.assertFalse(result["valid"])


class StoreTests(unittest.TestCase):
    def test_shared_bytes_read_once_across_names_and_processes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a, b = root / "a.png", root / "b.png"
            a.write_bytes(b"same-image")
            b.write_bytes(a.read_bytes())
            reader = Mock(read_structure=Mock(return_value=chart()), last_generation={})
            store = ChartStructureStore(root / "structures.json", reader=reader)
            store.get(a)
            store.get(b)
            store.close()
            fresh = ChartStructureStore(store.path, reader_factory=Mock(side_effect=AssertionError("Must not load CV")))
            self.assertEqual(fresh.get(a), chart())
            reader.read_structure.assert_called_once()
            # A changed image is not silently assigned the old structure.
            b.write_bytes(b"different-image-size")
            self.assertIsNone(fresh.record(b))

    def test_image_failure_is_saved_and_retry_requires_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.png"
            path.write_bytes(b"image")
            reader = Mock(read_structure=Mock(side_effect=ValueError("bad output")), last_generation={})
            store = ChartStructureStore(Path(tmp) / "store.json", reader=reader)
            for _ in range(2):
                with self.assertRaises(SavedVisionFailure): store.get(path)
            reader.read_structure.assert_called_once()
            reader.read_structure.side_effect = None
            reader.read_structure.return_value = chart()
            self.assertEqual(store.get(path, retry_failed=True), chart())

    def test_initialization_error_does_not_blacklist_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.png"
            path.write_bytes(b"image")
            store = ChartStructureStore(Path(tmp) / "store.json", reader_factory=Mock(side_effect=RuntimeError("GPU missing")))
            for _ in range(2):
                with self.assertRaises(CVInitializationError): store.get(path)
            store.reader_factory.assert_called_once()
            self.assertIsNone(store.record(path))

    def test_requests_reused_across_sample_ids_and_failures_saved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.png"
            path.write_bytes(b"image")
            reader = Mock(read_structure=Mock(return_value=chart()), last_generation={})
            reader.inspect.return_value = {"structure": chart(), "full_image": True}
            store = ChartStructureStore(Path(tmp) / "store.json", reader=reader)
            request = validate_request({"image_id": "Image 1"}, {"Image 1"})
            store.inspect(path, request)
            store.inspect(path, {**request, "image_id": "Image 2"})
            reader.inspect.assert_called_once()
            reader.read_values.side_effect = ValueError("unreadable")
            for _ in range(2):
                with self.assertRaises(SavedVisionFailure): store.read_values(path, {"operator": "chart_at"})
            reader.read_values.assert_called_once()


class ReaderTests(unittest.TestCase):
    def make_reader(self, results):
        from vinumqa.cv_module.structure_reader import ChartStructureReader
        reader = ChartStructureReader.__new__(ChartStructureReader)
        reader.backend = Mock(max_pixels=1400000)
        reader.backend.prepare_inputs.return_value = ("inputs", "prompt")
        reader.backend.generate_once.side_effect = results
        return reader

    def result(self, count, eos=False):
        return {"text": json.dumps(chart()), "tokens": count, "token_ids": [1] * count,
                "eos": eos, "seconds": 1, "stop_reason": "eos" if eos else "token_limit"}

    def test_reader_grows_to_2048_only_and_stops_on_time_limit(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chart.png"
            Image.new("RGB", (100, 100)).save(path)
            for results, expected in [([self.result(1024), self.result(2048)], [1024, 2048]),
                                      ([self.result(100)], [1024])]:
                reader = self.make_reader(results)
                with self.assertRaisesRegex(ValueError, "bounded"): reader._read(path, "test", structure=True)
                self.assertEqual([call.args[1] for call in reader.backend.generate_once.call_args_list], expected)

    def test_reader_crops_region_and_explains_lookup_argument_order(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chart.png"
            Image.new("RGB", (100, 100)).save(path)
            reader = self.make_reader([self.result(100, True), self.result(100, True)])
            result = reader.inspect(path, {"region": "legend", "series": "TCB"}, chart())
            self.assertFalse(result["full_image"])
            self.assertEqual(reader.backend.prepare_inputs.call_args.args[0].size, (80, 20))
            reader.read_values(path, {"operator": "chart_total", "arguments": ["Jul-21", "none", "none"]}, chart())
            self.assertIn("chart_total(image_id; x_label; y_label_or_none; series_name_or_none)",
                          reader.backend.prepare_inputs.call_args.args[1])


class PreparationTests(unittest.TestCase):
    def samples(self, prefix=""):
        return [{"qid": prefix + str(i), "images": {"Image 1": name}, "text": ["### Image 1 ###"],
                 "qa": {"question": "TCB tháng 7 trừ 2?", "program": PROGRAM}}
                for i, name in enumerate(["a.png", "b.png", "a.png", "c.png"])]

    def test_save_each_image_and_resume_after_interruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, case = Path(tmp), self
            for name in ("a.png", "b.png", "c.png"): (root / name).write_bytes(name.encode())
            output = root / "prepared.json"
            calls = []
            def read(path):
                calls.append(Path(path).name)
                if len(calls) == 2:
                    saved = json.loads(output.read_text(encoding="utf-8"))
                    case.assertEqual(saved["summary"]["ready"], 2)
                    raise KeyboardInterrupt()
                return chart()
            reader = Mock(read_structure=Mock(side_effect=read), last_generation={})
            store = ChartStructureStore(root / "store.json", reader_factory=lambda: reader)
            with self.assertRaises(KeyboardInterrupt): prepare_structured(self.samples(), root, output, store=store)
            saved = prepare_structured(self.samples(), root, output, start_image=2, store=store)
            self.assertEqual(saved["summary"], {"ready": 4, "pending": 0, "error": 0})
            self.assertEqual(calls, ["a.png", "b.png", "b.png", "c.png"])

    def test_failure_keeps_source_and_portable_ready_samples(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("a.png", "b.png", "c.png"): (root / name).write_bytes(name.encode())
            def read(path):
                if Path(path).name == "b.png": raise ValueError("bad image")
                return chart()
            reader = Mock(read_structure=Mock(side_effect=read), last_generation={})
            store = ChartStructureStore(root / "store.json", reader_factory=lambda: reader)
            paths = [root / "train.json", root / "val.json"]
            for index, path in enumerate(paths):
                saved = prepare_structured(self.samples(str(index)), root, path, store=store)
                self.assertEqual(saved["summary"]["error"], 1)
                self.assertIn("source", saved["samples"][1])
                self.assertEqual(json.loads(path.with_suffix(".ocr_errors.json").read_text())[0]["image"], "b.png")
            self.assertEqual(reader.read_structure.call_count, 3)
            for name in ("a.png", "b.png", "c.png"): (root / name).unlink()
            with self.assertRaisesRegex(ValueError, "skip-unready"): load_prepared_pair(*paths)
            train, val = load_prepared_pair(*paths, skip_unready=True)
            self.assertEqual((len(train), len(val)), (3, 3))
            self.assertIn('"name":"TCB"', train[0]["input"])

    def test_prepared_prompt_matches_inference_without_gold(self):
        sample = self.samples()[0]
        formatted = format_sample(sample, image_structures={"Image 1": chart()})
        from vinumqa.data.context import build_inline_context
        context = build_inline_context(sample["text"], {}, sample["images"], None, chart_structures={"Image 1": chart()})
        self.assertEqual(formatted["instruction"] + "\n\n" + formatted["input"] + "\n\n" + RESPONSE_PREFIX,
                         build_prompt(context, sample["qa"]["question"], "Image 1"))
        self.assertNotIn(PROGRAM, formatted["input"])


class NumericTests(unittest.TestCase):
    def store(self, points, c=None):
        return SimpleNamespace(read_values=lambda *a: {"complete": True, "points": points}, get=lambda *a: c or chart())

    def test_lookup_and_aggregate_coverage(self):
        self.assertEqual(resolve_chart(self.store([point()]), "image", "chart_at", "TCB", "Jul-21", "none"), 12)
        points = [point(x="Jun-21", value=10), point(value=12)]
        self.assertEqual(resolve_chart(self.store(points), "image", "chart_average", "TCB", "none", "none"), 11)
        with self.assertRaisesRegex(ValueError, "Missing/extra"):
            resolve_chart(self.store(points[:1]), "image", "chart_sum", "TCB", "none", "none")
        c = chart()
        c["x_labels_complete"] = False
        with self.assertRaisesRegex(ValueError, "incomplete"):
            resolve_chart(self.store(points, c), "image", "chart_max", "TCB", "none", "none")

    def test_estimates_and_incomplete_series_require_explicit_handling(self):
        store = self.store([point(basis="estimated")])
        with self.assertRaisesRegex(ValueError, "allow_estimates"):
            resolve_chart(store, "image", "chart_at", "TCB", "Jul-21", "none")
        self.assertEqual(resolve_chart(store, "image", "chart_at", "TCB", "Jul-21", "none", True), 12)
        c = chart()
        c["series_complete"] = False
        with self.assertRaisesRegex(ValueError, "incomplete set"):
            resolve_chart(self.store([point(), point(series="Kỳ vọng thị trường")], c), "image", "chart_total", "Jul-21", "none", "none")


class OrchestrationTests(unittest.TestCase):
    def setup_flow(self, root, results, initial=None, value_failure=False):
        events, active, prompts = [], set(), []
        path = root / "image.png"
        path.write_bytes(b"image")
        case = self
        class Reader:
            last_generation = {}
            def __init__(self):
                case.assertNotIn("nlp", active)
                active.add("cv")
                events.append("cv_load")
            def read_structure(self, path):
                events.append("structure")
                return initial or chart()
            def inspect(self, *args):
                events.append("inspect")
                return {"structure": chart(), "full_image": True}
            def read_values(self, *args):
                events.append("values")
                if value_failure: raise ValueError("unreadable point")
                return {"complete": True, "points": [point()]}
            def close(self):
                active.remove("cv")
                events.append("cv_close")
        iterator = iter(results)
        class NLP:
            def __init__(self):
                case.assertNotIn("cv", active)
                active.add("nlp")
                events.append("nlp_load")
            def process(self, *args):
                prompts.append(args[0])
                return copy.deepcopy(next(iterator))
            def close(self):
                active.remove("nlp")
                events.append("nlp_close")
        store = ChartStructureStore(root / "store.json", reader_factory=Reader)
        return ViNumQAPipeline(store=store, nlp_factory=NLP), {"Image 1": str(path)}, events, prompts

    def test_shared_image_uses_one_read_and_numeric_lookup_is_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipeline, images, events, _ = self.setup_flow(Path(tmp), [response(), response()])
            for _ in range(2):
                result = pipeline.run([], {}, images, "?")
                self.assertEqual(result["reasoning_result"]["program"], PROGRAM)
                self.assertTrue(result["reasoning_result"]["valid"])
                self.assertIsNone(result["answer"])
            self.assertEqual(events.count("structure"), 1)
            self.assertEqual(events.count("nlp_load"), 1)
            self.assertNotIn("values", events)
            pipeline.close()

    def test_missing_series_reinspection_switches_models_and_updates_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            incomplete = chart()
            incomplete["series"] = [{"name": "TCBB"}]
            pipeline, images, events, prompts = self.setup_flow(Path(tmp), [response(), response()], initial=incomplete)
            result = pipeline.run([], {}, images, "?")
            self.assertTrue(result["reasoning_result"]["valid"])
            self.assertEqual(events.count("inspect"), 1)
            self.assertIn('"name":"TCB"', prompts[-1])
            self.assertEqual(events, ["cv_load", "structure", "cv_close", "nlp_load", "nlp_close",
                                      "cv_load", "inspect", "cv_close", "nlp_load"])
            pipeline.close()

    def test_explicit_request_is_served_without_final_numeric_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            request = {"cv_request": {"image_id": "Image 1", "region": "legend"}}
            pipeline, images, events, _ = self.setup_flow(Path(tmp), [request, response()])
            result = pipeline.run([], {}, images, "?")
            self.assertTrue(result["reasoning_result"]["valid"])
            self.assertEqual(events.count("inspect"), 1)
            self.assertNotIn("values", events)
            pipeline.close()

    def test_execution_preserves_program_on_success_and_failure(self):
        for fail in [False, True]:
            with self.subTest(fail=fail), tempfile.TemporaryDirectory() as tmp:
                pipeline, images, events, _ = self.setup_flow(Path(tmp), [response()], value_failure=fail)
                result = pipeline.run([], {}, images, "?", execute=True)
                self.assertEqual(result["reasoning_result"]["program"], PROGRAM)
                self.assertEqual(result["answer"], None if fail else 10)
                self.assertEqual("execution_error" in result["reasoning_result"], fail)
                self.assertEqual(events.count("values"), 1)
                pipeline.close()

    def test_missing_labels_cannot_cause_unbounded_requests_or_valid_prediction(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = response(PROGRAM.replace("TCB;", "Invented;"))
            pipeline, images, events, _ = self.setup_flow(Path(tmp), [bad] * 6)
            result = pipeline.run([], {}, images, "?")["reasoning_result"]
            self.assertFalse(result["valid"])
            self.assertLessEqual(events.count("inspect"), 2)
            pipeline.close()


class SessionTests(unittest.TestCase):
    def test_time_budget_saves_checkpoint_including_contract(self):
        now = [0]
        budget = SessionBudget(1, reserve_minutes=10, clock=lambda: now[0])
        self.assertFalse(budget.expired())
        now[0] = 3000
        self.assertTrue(budget.expired())
        fake_transformers = ModuleType("transformers")
        fake_transformers.TrainerCallback = object
        with tempfile.TemporaryDirectory() as tmp, patch.dict("sys.modules", {"transformers": fake_transformers}):
            tokenizer = Mock()
            callback = make_session_callback(budget, {"contract": "test"}, tokenizer)
            args, state = SimpleNamespace(output_dir=tmp), SimpleNamespace(global_step=50)
            control = SimpleNamespace(should_save=False, should_training_stop=False, should_evaluate=True)
            callback.on_step_end(args, state, control)
            self.assertTrue(control.should_save and control.should_training_stop)
            self.assertFalse(control.should_evaluate)
            callback.on_save(args, state, control)
            saved = json.loads((Path(tmp) / "checkpoint-50/pipeline_manifest.json").read_text())
            self.assertEqual(saved, {"contract": "test"})
            tokenizer.save_pretrained.assert_called_once()

    def test_partial_validation_saved_and_cv_requests_deferred(self):
        now = [0]
        budget = SessionBudget(1, reserve_minutes=0, clock=lambda: now[0])
        samples = [format_sample({"qid": str(i), "qa": {"question": "?", "program": PROGRAM},
                                 "images": {"Image 1": "image.png"}}, image_structures={"Image 1": chart()}) for i in range(3)]
        def generate(prompt):
            now[0] = 3600
            return '| 1 | ' + evidence_from_program(PROGRAM) + ' |\n| 2 | ' + PROGRAM + ' |'
        with tempfile.TemporaryDirectory() as tmp:
            rows = export_epoch_predictions(samples, generate, tmp, 1, 50, budget)
            self.assertEqual(rows[0]["predicted"], PROGRAM)
            self.assertEqual(rows[1]["predicted"], "")
            diag = json.loads((Path(tmp) / "epoch_1_step_50.diagnostics.json").read_text())
            self.assertEqual(diag[1]["status"], "pending_time_budget")
            rows = export_epoch_predictions(samples[:1], lambda p: '{"cv_request":{"image_id":"Image 1"}}', tmp, 2, 100)
            self.assertEqual(rows[0]["predicted"], "")
            self.assertTrue((Path(tmp) / "epoch_2_step_100.cv_requests.json").exists())


if __name__ == "__main__": unittest.main()
