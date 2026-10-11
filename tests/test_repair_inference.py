import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from vinumqa.cv_module.structure_store import ChartStructureStore
from vinumqa.data.context import build_inline_context
from vinumqa.nlp_module.contracts import evidence_from_program, INSTRUCTION
from vinumqa.nlp_module.inference.semantic_validation import validate_semantics, table_axes
from vinumqa.pipeline.repair_inference import run_repair, check_prediction, apply_reviewed_structures, file_digest


def chart(name="TCB"):
    return {"title": "Chart", "kind": "line", "series": [{"name": name}],
            "x_labels": ["2025", "2026"], "y_labels": [], "uncertain": [], "regions": {},
            "x_labels_complete": True, "series_complete": True, "x_order_known": True}


def prediction(program):
    return {"program": program, "extracted_values": evidence_from_program(program), "termination": "eos"}


class SourceChecks(unittest.TestCase):
    def check(self, program, tables=None, text=None, question="?"):
        return validate_semantics(program, tables or {}, text or [], question)

    def test_nested_dsl_and_disconnected_branches_rejected(self):
        self.assertFalse(self.check("greater(38.7; (1+2)/2)")["valid"])
        self.assertFalse(self.check("subtract(8; 2); subtract(3; 1)")["valid"])
        self.assertTrue(self.check("subtract(8; 2); subtract(3; 1); add(#0; #1)")["valid"])

    def test_merged_headers_and_transposed_metrics(self):
        table = '<table><tr><td></td><td colspan="2">LNTT</td></tr><tr><td>MCK</td><td>6T2026</td><td>svck.</td></tr><tr><td>ACB</td><td>10735</td><td>0.4%</td></tr><tr><td>BID</td><td>18905</td><td>17.9%</td></tr></table>'
        columns, rows = table_axes(table)
        self.assertEqual(columns, ["LNTT@6T2026", "LNTT@svck."])
        self.assertEqual(rows, ["ACB", "BID"])
        q = "Tăng trưởng LNTT so với cùng kỳ cao nhất?"
        self.assertFalse(self.check("table_max(Table 1; LNTT@6T2026; none; none)", {"Table 1": table}, question=q)["valid"])
        self.assertTrue(self.check("table_max(Table 1; LNTT@svck.; ACB; BID)", {"Table 1": table}, question=q)["valid"])
        table = '<table><tr><td>Metric</td><td>2025</td><td>2026F</td></tr><tr><td>ROE (%)</td><td>11</td><td>14</td></tr></table>'
        self.assertTrue(self.check("table_max(Table 1; ROE (%); 2025; 2026F)", {"Table 1": table})["valid"])
        self.assertFalse(self.check("table_max(Table 1; ROE (%); FY2025; FY2026F)", {"Table 1": table})["valid"])
        self.assertFalse(self.check("table_max(Table 1; VNIndex; none; none)", {"Table 1": table})["valid"])

    def test_empty_leading_table_row_does_not_hide_year_headers(self):
        table = '<table><tr><td></td><td></td><td></td></tr><tr><td>FY</td><td>2025</td><td>2026F</td></tr><tr><td>EPS</td><td>4210</td><td>5249</td></tr></table>'
        self.assertEqual(table_axes(table), (["2025", "2026F"], ["EPS"]))
        self.assertTrue(self.check("table_average(Table 1; EPS; 2025; 2026F)", {"Table 1": table})["valid"])

    def test_no_numeric_evidence_from_chart_labels_and_money_ratio(self):
        self.assertFalse(self.check("divide(23647; 2105)", text=["Tháng 6: 23.647; lũy kế: 114.028"])["valid"])
        text = ["DX đạt 9,610 tỷ; AI đạt 1,842 tỷ đồng."]
        self.assertTrue(self.check("subtract(9610; 1842)", text=text)["valid"])
        bad = "divide(100; 100); multiply(9610; #0); divide(1842; #1); subtract(9610; #2)"
        self.assertTrue(any("dimensionless" in e for e in self.check(bad, text=text)["errors"]))
        self.assertTrue(self.check(bad, text=text, question="So sánh giá trị số của số tiền và tỷ số")["valid"])
        self.assertTrue(self.check("subtract(425300; 100)", text=["425,3 nghìn tỷ đồng"])["valid"])
        self.assertTrue(self.check("subtract(1; -14.9)", text=["Rút ròng 14,9 tỷ USD"])["valid"])

    def test_unavailable_chart_is_explicit_and_training_stays_strict(self):
        with self.assertRaises(KeyError):
            build_inline_context([], {}, {"Image 1": "missing.png"}, None, chart_structures={})
        ctx = build_inline_context([], {}, {"Image 1": "missing.png"}, None, chart_structures={}, allow_unavailable_images=True)
        self.assertIn("unavailable", ctx)
        sample = {"images": {"Image 1": "missing.png"}, "qa": {"question": "?"}}
        self.assertTrue(check_prediction(prediction("add(2; 3)"), sample, {})["valid"])
        result = check_prediction(prediction("chart_at(Image 1; TCB; 2026; none)"), sample, {})
        self.assertFalse(result["valid"])
        self.assertEqual(result["cv_requests"][0]["image_id"], "Image 1")

    def test_eos_and_step1_enforced(self):
        sample = {"qa": {"question": "?"}}
        pred = prediction("add(2; 3)")
        pred["termination"] = "length_or_stop"
        self.assertFalse(check_prediction(pred, sample, {})["valid"])
        pred["termination"] = "eos"
        pred["extracted_values"] = "[]"
        self.assertFalse(check_prediction(pred, sample, {})["valid"])


class RepairRoundTests(unittest.TestCase):
    def test_interrupt_then_resume_skips_saved_question(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inp = root / "input.json"
            inp.write_text(json.dumps([{"qid": str(i), "qa": {"question": str(i)}} for i in range(2)]))
            store = ChartStructureStore(root / "store.json")
            first = Mock(generate_with_prompt=Mock(side_effect=[prediction("add(2; 3)"), KeyboardInterrupt()]))
            with self.assertRaises(KeyboardInterrupt):
                run_repair(inp, root, root / "adapter", store.path, root / "out", store=store,
                           generator_factory=lambda: first, max_rounds=1)
            self.assertFalse((root / 'out/results.json').exists())
            rows = json.loads((root / "out/accepted.partial.json").read_text())
            self.assertTrue(rows[0]["predicted"])
            self.assertEqual(len(rows), 1)
            self.assertEqual(json.loads((root/'out/unresolved.json').read_text())[0]['qid'], '1')
            second = Mock(generate_with_prompt=Mock(return_value=prediction("add(2; 3)")))
            self.assertTrue(run_repair(inp, root, root / "adapter", store.path, root / "out", store=store,
                                      generator_factory=lambda: second, max_rounds=1)["complete"])
            second.generate_with_prompt.assert_called_once()

    def test_changed_shared_structure_regenerates_previously_accepted_question(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.png").write_bytes(b"image")
            inp = root / "input.json"
            inp.write_text(json.dumps([{"qid": q, "images": {"Image 1": "a.png"}, "qa": {"question": q}} for q in ["first", "second"]]))
            reader = Mock(read_structure=Mock(return_value=chart("TCBB")), last_generation={},
                          inspect=Mock(return_value={"structure": chart("TCB"), "full_image": True}))
            store = ChartStructureStore(root / "store.json", reader_factory=lambda: reader)
            calls = []
            def generate(prompt):
                calls.append(prompt)
                use_old = '"name":"TCBB"' in prompt and "### Question\nfirst" in prompt
                return prediction(f"chart_at(Image 1; {'TCBB' if use_old else 'TCB'}; 2026; none)")
            generator = Mock(generate_with_prompt=Mock(side_effect=generate))
            run_repair(inp, root, root / "adapter", store.path, root / "out", store=store,
                       generator_factory=lambda: generator, max_rounds=2, nlp_attempts=1)
            self.assertEqual(len(calls), 4)
            output = json.loads((root / "out/results.json").read_text())
            self.assertTrue(all("; TCB;" in r["predicted"] for r in output))

    def test_cv_grouping_gpu_exclusion_resume_and_output_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "image.png").write_bytes(b"image")
            active, calls = set(), []
            case = self
            class Reader:
                last_generation = {}
                def __init__(self):
                    case.assertNotIn("nlp", active)
                    active.add("cv")
                def read_structure(self, path): return chart("TCBB")
                def inspect(self, *args):
                    calls.append("inspect")
                    return {"structure": chart(), "full_image": True}
                def close(self): active.remove("cv")
            class Generator:
                def __init__(self):
                    case.assertNotIn("cv", active)
                    active.add("nlp")
                def generate_with_prompt(self, prompt):
                    case.assertIn(INSTRUCTION, prompt)
                    case.assertNotIn("GOLD_SECRET", prompt)
                    calls.append("generate")
                    return prediction("chart_at(Image 1; TCB; 2026; none)")
                def close(self): active.remove("nlp")
            data = [{"qid": str(i), "images": {"Image 1": "image.png"}, "qa": {"question": "TCB?", "program": "GOLD_SECRET"}} for i in range(2)]
            inp = root / "input.json"
            inp.write_text(json.dumps(data), encoding="utf-8")
            store = ChartStructureStore(root / "store.json", reader_factory=Reader)
            kwargs = dict(store=store, generator_factory=Generator, max_rounds=2)
            result = run_repair(inp, root, root / "adapter", store.path, root / "out", **kwargs)
            self.assertTrue(result["complete"])
            self.assertEqual(calls.count("inspect"), 1)
            self.assertFalse(active)
            output = json.loads((root / "out/results.json").read_text())
            self.assertEqual(len(output), 2)
            self.assertEqual(set(output[0]), {"qid", "predicted"})
            before = list(calls)
            run_repair(inp, root, root / "adapter", store.path, root / "out", **kwargs)
            self.assertEqual(calls, before)

    def test_failed_unneeded_image_does_not_block_text_question(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "broken.png").write_bytes(b"broken")
            inp = root / "input.json"
            inp.write_text(json.dumps([{"qid": "q", "images": {"Image 1": "broken.png"}, "qa": {"question": "2+3?"}}]))
            reader = Mock(read_structure=Mock(side_effect=ValueError("unreadable")), last_generation={})
            store = ChartStructureStore(root / "store.json", reader_factory=lambda: reader)
            gen = Mock(generate_with_prompt=Mock(return_value=prediction("add(2; 3)")))
            summary = run_repair(inp, root, root / "adapter", store.path, root / "out", store=store,
                                 generator_factory=lambda: gen, max_rounds=1)
            self.assertTrue(summary["complete"])
            reader.read_structure.assert_called_once()

    def test_reviewed_correction_requires_exact_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / "a.png"
            image.write_bytes(b"original")
            corrections = root / "corrections.json"
            corrections.write_text(json.dumps({file_digest(image): {"structure": chart(), "provenance": {"method": "pixels"}}}))
            store = ChartStructureStore(root / "store.json")
            image.write_bytes(b"different")
            apply_reviewed_structures(store, [image], corrections)
            self.assertIsNone(store.record(image))
            image.write_bytes(b"original")
            apply_reviewed_structures(store, [image], corrections)
            self.assertEqual(store.get(image)["series"][0]["name"], "TCB")


if __name__ == "__main__":
    unittest.main()
