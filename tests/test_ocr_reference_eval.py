import unittest

from vinumqa.cv_module.chart_to_table.reference_eval import evaluate_reference


TABLE = "| Quý | GDP (%) | Tham chiếu (%) |\n|---|---|---|\n|1Q19|7.0%|~7.0%|\n|2Q19|-4.2%|~7.0%|"
REFERENCE = {
    "categories": ["1Q19", "2Q19"],
    "series": ["GDP (%)", "Tham chiếu (%)"],
    "cells": [{"category": "2Q19", "series": "GDP (%)", "value": "-4.2%"}],
}


class ReferenceEvaluationTests(unittest.TestCase):
    def test_exact_values_labels_and_order_pass(self):
        result = evaluate_reference(TABLE, REFERENCE)
        self.assertTrue(result["reference_passed"])
        self.assertEqual(result["actual_category_count"], 2)
        self.assertEqual(result["actual_series_count"], 2)
        self.assertEqual(result["cell_accuracy"], 1)
        self.assertEqual(result["cell_coverage"], 1)

    def test_hallucinated_years_fail_even_with_valid_markdown(self):
        text = TABLE + "\n|2099|~7.0%|~7.0%|\n|2100|~7.0%|~7.0%|"
        result = evaluate_reference(text, REFERENCE)
        self.assertFalse(result["reference_passed"])
        self.assertEqual(result["extra_categories"], ["2099", "2100"])
        self.assertFalse(result["category_order_matches"])

    def test_flat_series_can_be_correct(self):
        text = "| Quý | GDP |\n|---|---|\n" + "\n".join(f"|{i}Q19|0|" for i in range(1, 5))
        result = evaluate_reference(text, {"categories": [f"{i}Q19" for i in range(1, 5)], "series": ["GDP"]})
        self.assertTrue(result["reference_passed"])
        self.assertIsNone(result["cell_accuracy"])
        self.assertIn("not been measured", result["caveat"])

    def test_lost_negative_sign_and_estimate_marker_are_wrong(self):
        for replacement in ("4.2%", "~-4.2%", "-4.2", "-4,2%"):
            result = evaluate_reference(TABLE.replace("-4.2%", replacement), REFERENCE)
            self.assertFalse(result["reference_passed"])
            self.assertEqual(result["wrong_cells"], 1)
            self.assertEqual(result["cell_accuracy"], 0)
            self.assertEqual(result["cell_coverage"], 1)

    def test_missing_and_ambiguous_cells_are_not_guessed(self):
        text = TABLE + "\n|2Q19|9.0%|~7.0%|"
        result = evaluate_reference(text, REFERENCE)
        self.assertEqual(result["duplicate_categories"], ["2Q19"])
        self.assertEqual(result["missing_cells"], 1)
        self.assertEqual(result["cell_coverage"], 0)
        self.assertFalse(result["reference_passed"])
        absent = evaluate_reference(TABLE.replace("GDP (%)", "Invented"), REFERENCE)
        self.assertEqual(absent["missing_series"], ["GDP (%)"])
        self.assertEqual(absent["extra_series"], ["Invented"])
        self.assertEqual(absent["missing_cells"], 1)
        blank = evaluate_reference(TABLE.replace("-4.2%", ""), REFERENCE)
        self.assertEqual(blank["missing_cells"], 1)
        self.assertEqual(blank["cell_coverage"], 0)

    def test_reordered_categories_fail_but_series_can_reorder(self):
        table = "| Quý | Tham chiếu (%) | GDP (%) |\n|---|---|---|\n|1Q19|~7.0%|7.0%|\n|2Q19|~7.0%|-4.2%|"
        self.assertTrue(evaluate_reference(table, REFERENCE)["reference_passed"])
        lines = table.splitlines()
        result = evaluate_reference("\n".join(lines[:2] + list(reversed(lines[2:]))), REFERENCE)
        self.assertFalse(result["category_order_matches"])
        self.assertFalse(result["reference_passed"])

    def test_fences_escaped_pipes_and_whitespace(self):
        table = "```markdown\n| Category | A \\| B |\n|:---|---:|\n| Q1   2020 | -4.2 % |\n```"
        reference = {"categories": [" Q1 2020 "], "series": ["A | B"],
                     "cells": [{"category": "Q1 2020", "series": "A | B", "value": "-4.2  %"}]}
        self.assertTrue(evaluate_reference(table, reference)["reference_passed"])

    def test_format_alone_has_no_accuracy(self):
        result = evaluate_reference(TABLE, {})
        self.assertFalse(result["reference_passed"])
        self.assertIsNone(result["cell_accuracy"])
        self.assertIsNone(result["cell_coverage"])

    def test_partial_cell_reference_is_explicit(self):
        result = evaluate_reference(TABLE, {"cells": REFERENCE["cells"]})
        self.assertTrue(result["reference_passed"])
        self.assertIsNone(result["expected_category_count"])
        self.assertIsNone(result["category_order_matches"])
        self.assertIn("only the supplied reference cells", result["caveat"])

    def test_invalid_output_and_reference_return_helpful_failure(self):
        for text, reference in (("plain text", REFERENCE),
                                ("|a|b|\n|---|---|\n|1|", REFERENCE),
                                (TABLE, {"cells": [{"category": "1Q19"}]}),
                                (TABLE, {"categories": ["1Q19", "1Q19"]})):
            with self.subTest(text=text, reference=reference):
                result = evaluate_reference(text, reference)
                self.assertFalse(result["reference_passed"])
                self.assertIn("error", result)
                self.assertIsNone(result["cell_accuracy"])


if __name__ == "__main__":
    unittest.main()
