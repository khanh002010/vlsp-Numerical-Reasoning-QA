import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from PIL import Image
from vinumqa.cv_module.structure_parts import parse_visual_choice
from vinumqa.cv_module.structure_reader import ChartStructureReader


class ChoiceTests(unittest.TestCase):
    def test_equivalent_complete_replies(self):
        for text in ('full', 'FULL.', '"full"', '{"region":"full"}', '```json\n{"region":"full"}\n```'):
            self.assertEqual(parse_visual_choice(text, 'region'), {'region': 'full'})
        for text in ('numerical', 'The vertical Y axis is a numerical scale.',
                     '{"y_axis_type":"numerical"}'):
            self.assertEqual(parse_visual_choice(text, 'y_axis_type'), {'y_axis_type': 'numerical'})

    def test_ambiguity_negation_truncation_and_duplicate_keys_rejected(self):
        for text in ('not numerical', 'The vertical Y axis is not a numerical scale.',
                     'numerical or categorical', 'probably numerical',
                     '{"y_axis_type":"numerical", "y_axis_type":"categorical"}',
                     '{"y_axis_type":"numerical", "other":"categorical"}',
                     '{"y_axis_type":"numerical"', 'null', '[]'):
            with self.assertRaises(ValueError): parse_visual_choice(text, 'y_axis_type')
        with self.assertRaises(ValueError): parse_visual_choice('top or bottom', 'region')

    def make_reader(self, replies):
        cv = ChartStructureReader.__new__(ChartStructureReader)
        cv.last_generation = {'attempts': []}
        cv.backend = Mock(max_pixels=1400000)
        cv.backend.prepare_inputs.return_value = ('inputs', '')
        cv.backend.generate_once.side_effect = [dict(text=t, tokens=20, token_ids=[1]*20,
                                                    eos=eos, seconds=1, stop_reason='eos' if eos else 'token_limit')
                                               for t, eos in replies]
        return cv

    def test_actual_generation_path_recovers_y_without_locator(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'image.png'
            Image.new('RGB', (50,50)).save(path)
            cv = self.make_reader([(json.dumps({'y_axis_type':'numerical','y_labels':['VN-Index','MSH VN']}), True),
                                   ('The vertical Y axis is a numerical scale.', True)])
            result = cv._read_part(path, 'y_axis', 'Read Y')
            self.assertEqual(result['y_labels'], [])
            self.assertEqual(cv.backend.generate_once.call_count, 2)
            self.assertEqual(cv.last_generation['attempts'][-1]['parsed_choice'], {'y_axis_type':'numerical'})

    def test_coarse_plain_full_reaches_crop_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'image.png'
            Image.new('RGB', (50,50)).save(path)
            cv = self.make_reader([('invalid',True), ('{"box":null}',True), ('full',True),
                                   ('{"x_labels":["Jan-20"],"x_labels_complete":false}',True)])
            result = cv._read_part(path, 'x_axis', 'Read X')
            self.assertEqual(result['x_labels'], ['Jan-20'])
            self.assertEqual(cv.last_generation['attempts'][-1]['box'], [0,0,1,1])

    def test_plain_choice_not_allowed_for_structures_or_incomplete_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'image.png'
            Image.new('RGB', (50,50)).save(path)
            for phase, eos in [('primary', True), ('locate_coarse_legend', False)]:
                cv = self.make_reader([('full',eos)])
                with self.assertRaises(ValueError):
                    cv._read(path, 'prompt', phase=phase, budgets=(128,))


if __name__ == '__main__': unittest.main()
