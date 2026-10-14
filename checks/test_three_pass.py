import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vinumqa.nlp_module.inference.source_selection import validate_selection, plan_feedback
from vinumqa.pipeline.repair_inference import run_repair


class ThreePassTests(unittest.TestCase):
    def test_unknown_source_and_wrong_series_are_rejected(self):
        sample = {'images': {'Image 1': 'a.png'}, 'tables': {}}
        charts = {'Image 1': {'series': [{'name': 'YoY'}]}}
        plan = {'task': 'average', 'sources': [{'id': 'Image 1', 'series': '1H26',
            'labels': ['TCB'], 'quote': 'YoY'}]}
        errors = validate_selection(plan, sample, charts, 'YoY')
        self.assertTrue(any('series absent' in e for e in errors))
        self.assertNotIn('1H26', plan_feedback(plan, ['Invalid plan']))
        plan['sources'][0]['id'] = 'Image 9'
        self.assertTrue(any('Unknown source' in e for e in validate_selection(plan, sample, charts, 'YoY')))

    def test_sparse_labels_do_not_invalidate_source_plan(self):
        plan = {'task': 'lookup', 'sources': [{'id': 'Image 1', 'series': 'YoY',
            'labels': ['Feb-26'], 'quote': 'YoY'}]}
        self.assertEqual(validate_selection(plan, {'images': {'Image 1': 'a.png'}},
            {'Image 1': {'series': [{'name': 'YoY'}], 'x_labels': ['Jan-26', 'Mar-26']}}, 'YoY'), [])

    def test_three_calls_repair_save_and_resume_without_generation(self):
        class Store:
            def close(self): pass
        class Generator:
            def __init__(self): self.calls = []
            def close(self): pass
            def generate_with_prompt(self, prompt, **kwargs):
                self.calls.append((prompt, kwargs))
                if kwargs.get('response_format') == 'source_plan':
                    return {'source_plan': {'task': 'sum', 'sources': [
                        {'id': 'Text', 'series': '', 'labels': [], 'quote': '9 and 8'}]}, 'termination': 'eos'}
                return {'program': 'add(9; 8)' if len(self.calls) == 3 else 'subtract(9; 8)',
                        'termination': 'eos', 'extracted_values': ''}
        def check(prediction, sample, charts):
            errors = [] if prediction.get('program') == 'add(9; 8)' else ['Use sum, not difference']
            return {'valid': not errors, 'errors': errors, 'cv_requests': []}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root/'input.json'
            source.write_text(json.dumps([{'qid': 'q1', 'text': ['9 and 8'], 'images': {},
                'tables': {}, 'qa': {'question': 'Sum?', 'program': 'SECRET GOLD'}}]), encoding='utf-8')
            gen = Generator()
            with patch('vinumqa.pipeline.repair_inference.check_prediction', side_effect=check), \
                 patch('vinumqa.pipeline.repair_inference.DEFAULT_REVIEWED', root/'absent.json'):
                args = (source, root, root/'adapter', root/'store.json', root/'out')
                kwargs = dict(store=Store(), generator_factory=lambda: gen, max_rounds=1, three_pass=True)
                result = run_repair(*args, **kwargs)
                self.assertTrue(result['complete'])
                self.assertEqual(len(gen.calls), 3)
                self.assertEqual(gen.calls[0][1]['max_new_tokens'], 512)
                self.assertIn('Use sum, not difference', gen.calls[-1][0])
                self.assertTrue(all('SECRET GOLD' not in prompt for prompt, _ in gen.calls))
                saved = json.loads((root/'out/state.json').read_text(encoding='utf-8'))
                self.assertEqual(saved['records']['q1']['source_selection']['validation_errors'], [])
                run_repair(*args, **kwargs)
                self.assertEqual(len(gen.calls), 3)


if __name__ == '__main__': unittest.main()
