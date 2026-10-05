import ast
import csv
import json
import tempfile
import unittest
from pathlib import Path

from vinumqa.utils.dsl_parser import (validate_program, parse_program, execute_program,
    normalize_program, resolve_arg, programs_equivalent, compile_plan)
from vinumqa.utils.metrics import execution_accuracy
from vinumqa.nlp_module.contracts import build_prompt, RESPONSE_PREFIX, parse_response, evidence_from_program
from vinumqa.nlp_module.critic.reflection_loop import ReflectionLoop
from vinumqa.nlp_module.training.supervision import encode_supervised, pad_supervised, validate_dataset_pair
from vinumqa.nlp_module.contracts import FORMAT_VERSION, INSTRUCTION
from vinumqa.nlp_module.inference.operator_constraint import operator_prefix, allows_operator_piece
from vinumqa.nlp_module.data_prep.format_training_data import format_sample
from vinumqa.data.context import dict_to_markdown_table, build_inline_context
from vinumqa.data.prepare_dataset import split_dataset
from vinumqa.cv_module.pipeline import CVPipeline
from vinumqa.pipeline.batch_inference import run_batch_inference

ROOT = Path(__file__).resolve().parents[1]

class FakeTokenizer:
    eos_token_id = 1
    pad_token_id = 1
    def encode(self, text, **kwargs): return [ord(c) + 2 for c in text]

class FakeGenerator:
    def __init__(self, responses): self.responses, self.prompts = iter(responses), []
    def _build_prompt(self, context, table, images, question): return build_prompt(context, question, images)
    def generate_with_prompt(self, prompt):
        self.prompts.append(prompt)
        return next(self.responses)

class PipelineTests(unittest.TestCase):
    def test_all_code_compiles(self):
        for p in (ROOT / "vinumqa").rglob("*.py"):
            with self.subTest(path=p): ast.parse(p.read_text(encoding="utf-8-sig"))

    def test_public_gold_roundtrip(self):
        data = json.loads((ROOT / "data/public_test/public_test.json").read_text(encoding="utf-8"))
        for s in data:
            with self.subTest(qid=s["qid"]):
                p = s["qa"]["program"]
                self.assertEqual(validate_program(p, set(s["tables"]) | set(s["images"])), (True, "Valid"))
                self.assertEqual(normalize_program(normalize_program(p)), normalize_program(p))

    def test_regressions(self):
        for p in ["add(VN30; VNMidcap)", "chart_max(Table 1; x; none; none)",
                  "divide(100; 0)", "subtract(#0; 3)", "subtract(2; 1));add(1; 2)",
                  "chart_at(Image 1; x; none)", "chart_divide(Image 1; x; none; none)"]:
            self.assertFalse(validate_program(p)[0], p)
        self.assertTrue(validate_program("divide(0; 0.5)")[0])
        self.assertFalse(validate_program("subtract(2; 2);divide(1; #0)")[0])
        self.assertFalse(validate_program("chart_at(Image 2; x; none; none)", {"Image 1"})[0])

    def test_decimal_and_separators(self):
        p = "subtract(0.175;0.105);add(#0; 1)"
        self.assertAlmostEqual(execute_program(parse_program(p))[1], 1.07)
        self.assertEqual(resolve_arg("52.102", {}), 52.102)
        self.assertTrue(validate_program("chart_at(Image 1; DJIA (Mỹ); FY2020(F); none)")[0])
        with self.assertRaisesRegex(ValueError, "resolver"):
            execute_program(parse_program("chart_at(Image 1; x; none; none)"))

    def test_lookup_resolver(self):
        p = "chart_at(Image 1; ROE; 2025; none);divide(#0; 2)"
        self.assertEqual(execute_program(parse_program(p), charts={"Image 1": lambda *a: 12})[1], 6)

    def test_metrics_do_not_reward_failure(self):
        self.assertFalse(programs_equivalent("", ""))
        self.assertEqual(execution_accuracy([1, None], [1, 2]), .5)
        self.assertFalse(programs_equivalent("subtract(2; 1)", "subtract(1; 2)"))

    def test_compiler_preserves_roles(self):
        nodes = [{"id": "base", "operator": "chart_at", "args": ["Image 1", "NII", "2019", "none"]},
                 {"id": "new", "operator": "chart_at", "args": ["Image 1", "NII", "2023", "none"]},
                 {"id": "delta", "operator": "subtract", "args": [{"ref": "new"}, {"ref": "base"}]}]
        self.assertTrue(compile_plan(nodes).endswith("subtract(#1; #0)"))
        nodes[2]["args"][0] = {"ref": "delta"}
        with self.assertRaises(ValueError): compile_plan(nodes)

    def test_response_parser(self):
        r = parse_response('| 1 | [] |\n| 2 | subtract(2; 1);\nadd(#0; 3) |')
        self.assertTrue(r["valid"])
        self.assertFalse(parse_response('| 2 | subtract(2; 1)')["valid"])

    def test_evidence_preserves_duplicates(self):
        evidence = json.loads(evidence_from_program("add(9; 9);divide(#0; 2)"))
        self.assertEqual([a["value"] for a in evidence[0]["arguments"]], ["9", "9"])

    def test_shared_prompt(self):
        s = {"qid": "q", "text": ["Giá trị 9 và 3"], "tables": {}, "images": {},
             "qa": {"question": "Tổng?", "program": "add(9; 3)"}}
        f = format_sample(s)
        prompt = f["instruction"] + "\n\n" + f["input"] + "\n\n" + RESPONSE_PREFIX
        self.assertEqual(prompt, build_prompt(s["text"][0], "Tổng?"))

    def test_response_only_and_overflow(self):
        t = FakeTokenizer()
        encoded = encode_supervised(t, "prompt", "answer", 100)
        self.assertEqual(encoded["labels"][:6], [-100] * 6)
        self.assertEqual(encoded["labels"][-1], t.eos_token_id)
        with self.assertRaisesRegex(ValueError, "overflow"): encode_supervised(t, "prompt", "answer", 10)
        short = encode_supervised(t, "x", "y", 100)
        batch = pad_supervised([encoded, short], t.pad_token_id)
        self.assertEqual(batch["labels"][1][:3], [-100, ord("y") + 2, t.eos_token_id])
        self.assertTrue(all(x == -100 for x in batch["labels"][1][3:]))
        self.assertEqual(batch["attention_mask"][1][3:], [0] * 13)

    def test_training_preflight(self):
        def sample(qid, text):
            return format_sample({"qid": qid, "text": [text], "qa": {"question": "?", "program": "add(9; 3)"}})
        a, b = sample("a", "first document"), sample("b", "second document")
        validate_dataset_pair([a], [b], FORMAT_VERSION, INSTRUCTION)
        b["group_keys"] = a["group_keys"]
        with self.assertRaisesRegex(ValueError, "overlap"): validate_dataset_pair([a], [b], FORMAT_VERSION, INSTRUCTION)
        b["format_version"] = "v3"
        with self.assertRaisesRegex(ValueError, "Stale"): validate_dataset_pair([a], [b], FORMAT_VERSION, INSTRUCTION)

    def test_reflection_retry_and_last_validation(self):
        g = FakeGenerator([{"program": "divide(#1; #2)"}, {"program": "divide(9; 3)"}])
        r = ReflectionLoop(g).generate_with_reflection("", "", "", "Tỷ số?")
        self.assertTrue(r["valid"])
        self.assertEqual(len(g.prompts), 2)
        self.assertIn("Validation feedback", g.prompts[1])
        g = FakeGenerator([{"program": "divide(1; 0)"}, {"program": "divide(1; 0)"}])
        self.assertFalse(ReflectionLoop(g).generate_with_reflection("", "", "", "?")["valid"])
        g = FakeGenerator([{"error": "OOM"}])
        self.assertEqual(ReflectionLoop(g).generate_with_reflection("", "", "", "?")["error"], "OOM")

    def test_operator_names_not_first_tokens(self):
        self.assertIsNone(operator_prefix("| 1 | Image 1#x; "))
        self.assertEqual(operator_prefix("| 2 | chart_"), "chart_")
        self.assertFalse(allows_operator_piece("chart_", "divide("))
        self.assertTrue(allows_operator_piece("chart_", "at(Image"))
        self.assertIsNone(operator_prefix("| 2 | chart_at(Image 1; x; "))
        self.assertEqual(operator_prefix("|2| add(1; 2); sub"), "sub")

    def test_table_raw_values_and_headers(self):
        html = '<table><tr><td rowspan="2">Mã</td><td colspan="2">P/E</td></tr><tr><td>2024F</td><td>2025F</td></tr><tr><td>GAS</td><td>14,8</td><td>15,5</td></tr></table>'
        md = dict_to_markdown_table({"Table 1": html})
        self.assertIn("P/E@2024F", md)
        self.assertIn("14,8", md)
        self.assertIn("GAS", md)
        with self.assertRaisesRegex(ValueError, "Unresolved"):
            build_inline_context(["### Table 2 ###"], {}, {}, None)

    def test_real_multilevel_header(self):
        data = json.loads((ROOT / "data/public_test/public_test.json").read_text(encoding="utf-8"))
        sample = next(s for s in data if s["qid"] == "8d829101-30ce-504a-8f1d-9c4299018ae3")
        md = dict_to_markdown_table(sample["tables"])
        self.assertIn("Giá mục tiêu (đồng)@Trong 1 năm", md)
        self.assertIn("79.000", md)

    def test_all_dataset_tables_render(self):
        seen = set()
        for path in ["data/train/train.json", "data/public_test/public_test.json"]:
            data = json.loads((ROOT / path).read_text(encoding="utf-8"))
            for sample in data:
                for key, html in sample.get("tables", {}).items():
                    if html in seen: continue
                    seen.add(html)
                    with self.subTest(qid=sample["qid"], table=key):
                        self.assertIn(f"**{key}**", dict_to_markdown_table({key: html}))

    def test_cv_cache_and_failure(self):
        class Extractor:
            calls = 0
            def extract(self, p):
                self.calls += 1
                return "| x | y |\n|---|---|\n| 1 | 2 |"
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "chart.png"; image.write_bytes(b"fake-test-image")
            extractor = Extractor()
            a = CVPipeline(cache_dir=Path(tmp)/"cache", extractor=extractor)
            a.process_image(image)
            b = CVPipeline(cache_dir=Path(tmp)/"cache", extractor=extractor)
            self.assertEqual(a.process_image(image), b.process_image(image))
            self.assertEqual(extractor.calls, 1)
            with self.assertRaisesRegex(ValueError, "Real CV"):
                build_inline_context([], {}, {"Image 1": image}, None)

    def test_group_split(self):
        data = json.loads((ROOT / "data/train/train.json").read_text(encoding="utf-8"))
        train, val = split_dataset(data)
        images = lambda rows: {v for s in rows for v in s["images"].values()}
        self.assertFalse(images(train) & images(val))
        self.assertEqual(len(train) + len(val), len(data))
        self.assertTrue(train and val)

    def test_batch_resume_and_no_invalid_submission(self):
        class Pipeline:
            calls = 0
            def run(self, *args):
                self.calls += 1
                return {"reasoning_result": {"program": "divide(#0; 1)" if self.calls == 1 else "divide(9; 3)"}}
        with tempfile.TemporaryDirectory() as tmp:
            inp, out = Path(tmp)/"test.json", Path(tmp)/"submission.json"
            inp.write_text(json.dumps([{"qid":"q", "qa":{"question":"?"}}]))
            p = Pipeline()
            with self.assertRaises(RuntimeError): run_batch_inference(inp, out, tmp, pipeline=p)
            self.assertFalse(out.exists())
            run_batch_inference(inp, out, tmp, pipeline=p)
            run_batch_inference(inp, out, tmp, pipeline=p)
            self.assertEqual(p.calls, 2)
            self.assertEqual(json.loads(out.read_text())[0]["program"], "divide(9; 3)")

if __name__ == "__main__": unittest.main()
