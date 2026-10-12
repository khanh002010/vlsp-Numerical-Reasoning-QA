import json
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from vinumqa.nlp_module.inference.generation_runtime import GenerationProgress, placement, eos_ids
from vinumqa.pipeline.repair_inference import needs_cv_before_retry, run_repair
from tests.test_repair_inference import prediction, chart


class RuntimeTests(unittest.TestCase):
    def test_gpu_placement_is_explicit_and_cpu_fallback_is_preserved(self):
        self.assertEqual(placement('cuda', True), ('cuda:0', {'': 'cuda:0'}))
        self.assertEqual(placement('cuda:1', True), ('cuda:1', {'': 'cuda:1'}))
        self.assertEqual(placement('auto', True), ('cuda', 'auto'))
        self.assertEqual(placement('cuda', False), ('cpu', 'cpu'))
        with self.assertRaises(ValueError):
            placement('disk', True)

    def test_heartbeat_distinguishes_prefill_and_completed_decode_steps(self):
        now = [10.0]
        messages = []
        progress = GenerationProgress(20, clock=lambda: now[0], emit=messages.append)
        now[0] = 40.0
        progress.report()
        self.assertIn('phase=prefill/first token', messages[-1])
        self.assertIn('last_token_step_ago=30.0s', messages[-1])
        self.assertFalse(progress(SimpleNamespace(shape=(1, 27)), None))
        now[0] = 45.0
        progress.report()
        self.assertIn('generated_tokens=7', messages[-1])
        self.assertIn('last_token_step_ago=5.0s', messages[-1])

    def test_monitor_closes_even_after_failure_and_does_not_do_model_work(self):
        with self.assertRaisesRegex(RuntimeError, 'forward'):
            with GenerationProgress(5) as progress:
                self.assertTrue(progress._thread.is_alive())
                raise RuntimeError('forward')
        self.assertFalse(progress._thread.is_alive())

    def test_eos_uses_all_generation_stop_ids(self):
        self.assertEqual(eos_ids(SimpleNamespace(eos_token_id=[2, 3]), SimpleNamespace(eos_token_id=2)), {2, 3})
        self.assertEqual(eos_ids(SimpleNamespace(eos_token_id=None), SimpleNamespace(eos_token_id=2)), {2})

    def test_incomplete_axis_routes_to_cv_but_wrong_series_still_gets_nlp_retry(self):
        c = chart()
        c['x_labels_complete'] = False
        check = {'errors': ["Step 0: unverified x_labels label '2027' in Image 1"],
                 'cv_requests': [{'image_id': 'Image 1', 'region': 'x_axis'}]}
        self.assertTrue(needs_cv_before_retry({}, check, {'Image 1': c}))
        c['x_labels_complete'] = True
        self.assertFalse(needs_cv_before_retry({}, check, {'Image 1': c}))
        c['x_labels_complete'] = False
        check['errors'].append('Step 0: unverified series WRONG')
        self.assertFalse(needs_cv_before_retry({}, check, {'Image 1': c}))

    def test_repeated_candidate_stops_extra_retries_without_faking_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'input.json'
            source.write_text(json.dumps([{'qid': 'q', 'qa': {'question': '?'}}]))
            gen = Mock(generate_with_prompt=Mock(return_value=prediction('subtract(8; 2); subtract(3; 1)')))
            result = run_repair(source, root, root/'adapter', root/'store.json', root/'out',
                                generator_factory=lambda: gen, max_rounds=1, nlp_attempts=5)
            self.assertEqual(gen.generate_with_prompt.call_count, 2)
            self.assertFalse(result['complete'])
            self.assertFalse((root/'out/results.json').exists())
            self.assertTrue((root/'out/state.json').exists())

    def test_generator_runs_synchronously_and_keeps_alternative_eos(self):
        import torch
        from vinumqa.nlp_module.inference.generate_program import ProgramGenerator

        program = 'add(2; 3)'
        row = prediction(program)
        response = f'| 1 | {row["extracted_values"]} |\n| 2 | {program} |'
        class Inputs(dict):
            def __init__(self):
                super().__init__(input_ids=torch.tensor([[10, 11]]))
                self.input_ids = self['input_ids']
            def to(self, device):
                return self
        tokenizer = Mock(return_value=Inputs(), eos_token_id=2, pad_token_id=2)
        tokenizer.decode.return_value = response
        current = threading.current_thread()
        def generate(**kwargs):
            self.assertIs(threading.current_thread(), current)
            ids = torch.tensor([[10, 11, 12, 3]])
            self.assertFalse(kwargs['stopping_criteria'][0](ids, None))
            self.assertEqual(kwargs['max_time'], 120)
            return ids
        model = Mock(config=SimpleNamespace(max_position_embeddings=4096),
                     generation_config=SimpleNamespace(eos_token_id=[2, 3]),
                     generate=Mock(side_effect=generate))
        model.get_input_embeddings.return_value.weight.device = 'cpu'
        gen = ProgramGenerator.__new__(ProgramGenerator)
        gen.model, gen.tokenizer, gen.device = model, tokenizer, 'cpu'
        gen.max_generation_seconds, gen.progress_seconds = 120, 30
        gen.use_constrained_decoding = False
        result = gen.generate_with_prompt('prompt')
        self.assertEqual(result['program'], program)
        self.assertEqual(result['termination'], 'eos')
        self.assertEqual(result['generated_tokens'], 2)
        self.assertIn('generation_seconds', result)


if __name__ == '__main__':
    unittest.main()
