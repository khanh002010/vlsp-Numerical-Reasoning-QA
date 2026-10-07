import unittest

from vinumqa.cv_module.chart_to_table.quality import repetition_reason, validate_table, extract_with_retries


GOOD = "| Quý | GDP (%) |\n|---|---|\n| 1Q19 | ~6,5 |\n| 2Q19 | N/A |"
LOOP = "| Biểu đồ |\n|---|---|\n| " + "TRỤC X - TRỤC Y - " * 100


def result(text, eos=False, count=128):
    return {"text": text, "eos": eos, "token_ids": [1] * count, "seconds": 0.1}


class OCRQualityTests(unittest.TestCase):
    def test_real_inline_loop_pattern_detected_with_partial_tail(self):
        for suffix in ("", "TRỤC", "TRỤC X -"):
            self.assertIn("inline_repetition", repetition_reason(LOOP + suffix))
        with self.assertRaisesRegex(ValueError, "inline_repetition"):
            validate_table(LOOP)

    def test_valid_repeated_values_are_not_a_loop(self):
        table = "| Quý | Series A | Series B |\n|---|---|---|\n"
        table += "\n".join(f"| {q}Q{y} | 0 | 0 |" for y in range(2019, 2025) for q in range(1, 5))
        self.assertIsNone(repetition_reason(table))
        self.assertEqual(validate_table(table), table)
        self.assertEqual(validate_table(GOOD), GOOD)

    def test_malformed_table_rejected(self):
        for text in ("| Title |\n|---|---|\n| data |", "| a | b |\n|---|---|\n| 1 |", "plain text"):
            with self.assertRaises(ValueError): validate_table(text)

    def test_loop_gets_one_alternate_prompt_and_no_budget_growth(self):
        calls, attempts = [], []
        def generate(budget, fallback):
            calls.append((budget, fallback))
            return result(LOOP)
        with self.assertRaisesRegex(ValueError, "alternate prompt"):
            extract_with_retries(generate, [2048, 4096, 8192, 16384], attempts)
        self.assertEqual(calls, [(2048, False), (2048, True)])
        self.assertEqual(len(attempts), 2)
        self.assertIn("quality_error", attempts[0])

    def test_alternate_prompt_can_recover(self):
        attempts = []
        table = extract_with_retries(lambda b, f: result(GOOD, True) if f else result(LOOP),
                                     [2048, 4096], attempts)
        self.assertEqual(table, GOOD)
        self.assertTrue(attempts[-1]["fallback"])

    def test_truncation_grows_until_eos(self):
        calls = []
        def generate(budget, fallback):
            calls.append((budget, fallback))
            return result(GOOD, eos=budget == 4096, count=budget if budget == 2048 else 100)
        self.assertEqual(extract_with_retries(generate, [2048, 4096], []), GOOD)
        self.assertEqual(calls, [(2048, False), (4096, False)])

    def test_no_eos_at_ceiling_is_rejected_even_with_valid_table(self):
        with self.assertRaisesRegex(ValueError, "maximum token budget"):
            extract_with_retries(lambda b, f: result(GOOD, count=b), [2048, 4096], [])

    def test_malformed_eos_tries_alternate_prompt(self):
        attempts = []
        extract_with_retries(lambda b, f: result(GOOD if f else "| a |", True), [1024], attempts)
        self.assertEqual(len(attempts), 2)


if __name__ == "__main__":
    unittest.main()
