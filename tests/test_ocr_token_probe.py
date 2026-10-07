import json
import tempfile
import unittest
from pathlib import Path
from vinumqa.cv_module.ocr_token_probe import run_probe


class ProbeTests(unittest.TestCase):
    def test_truncated_output_saved_and_all_budgets_run(self):
        calls = []
        def generate(budget):
            calls.append(budget)
            return {"text": "| a |\n| a |", "raw_text": "raw<end>", "token_ids": [1]*budget,
                    "eos": budget == 2, "seconds": 0.5}
        with tempfile.TemporaryDirectory() as tmp:
            result = run_probe(generate, [2, 4], tmp)
            self.assertEqual(calls, [2, 4])
            self.assertEqual(result["results"][1]["status"], "limit_reached")
            self.assertEqual((Path(tmp)/"tokens_4.md").read_text(), "| a |\n| a |")
            self.assertEqual(result["results"][1]["repeated_lines"], [{"line": "| a |", "count": 2}])

    def test_failure_and_interruption_keep_previous_files(self):
        def generate(budget):
            if budget == 2: raise RuntimeError("test error")
            if budget == 8: raise KeyboardInterrupt()
            return {"text": "table", "raw_text": "table", "token_ids": [1], "eos": True, "seconds": 0.1}
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(KeyboardInterrupt): run_probe(generate, [2, 4, 8], tmp)
            result = json.loads((Path(tmp)/"summary.json").read_text())
            self.assertEqual([r["status"] for r in result["results"]], ["error", "eos"])
            self.assertTrue((Path(tmp)/"tokens_4.md").exists())
            self.assertTrue((Path(tmp)/"tokens_2.error.json").exists())


if __name__ == "__main__": unittest.main()
