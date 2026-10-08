import json
import unittest
from unittest.mock import Mock
from vinumqa.cv_module.structure_output import json_repetition_reason, parse_structure_output
from vinumqa.cv_module.structure_reader import ChartStructureReader
from vinumqa.cv_module.structure_parts import validate_part, normalize_locator_box


class LocalizedTests(unittest.TestCase):
    def test_short_quarter_groups_not_rejected_but_runaway_cycles_are(self):
        short = '"x_labels":' + json.dumps(['Q1','Q2','Q3','Q4'] * 4)
        self.assertIsNone(json_repetition_reason(short))
        for labels in (['Q1','Q2','Q3','Q4'] * 10, ['0'] * 40):
            self.assertIsNotNone(json_repetition_reason('"x_labels":' + json.dumps(labels)[:-1]))
        self.assertIsNone(json_repetition_reason('"values":' + json.dumps(['0'] * 40)))

    def test_pie_axis_corrected_without_changing_slice_names(self):
        value = dict(title='', kind='pie', series=[dict(name='Ocean Park 3', axis='x')],
                     x_labels=[], y_labels=[], series_complete=False, x_labels_complete=False)
        result, repairs = parse_structure_output(json.dumps(value))
        self.assertEqual(result['series'][0]['axis'], 'none')
        self.assertEqual(result['series'][0]['name'], 'Ocean Park 3')
        self.assertTrue(repairs)
        value['kind'] = 'line'
        with self.assertRaises(ValueError): parse_structure_output(json.dumps(value))

    def test_y_units_or_legend_require_another_observation(self):
        for labels in (['%'], ['Index', '% +/-'], ['Phat trien (DM)']):
            with self.assertRaises(ValueError): validate_part('y_axis', {'y_labels': labels})
            with self.assertRaises(ValueError):
                validate_part('y_axis', {'y_labels': labels, 'y_axis_type': 'numerical'})
        result, _ = validate_part('y_axis', {'y_labels': ['2020', '2021'], 'y_axis_type': 'categorical'})
        self.assertEqual(result['y_labels'], ['2020', '2021'])

    def test_duplicate_x_labels_reread_crop_not_deduplicated_or_sorted(self):
        cv = ChartStructureReader.__new__(ChartStructureReader)
        cv.last_generation = {}
        cv._read = Mock(side_effect=[{'x_labels': ['Jan-21','Jan-22','Jan-21']},
            {'box': [0.05, 0.6, 0.98, 1]},
            {'x_labels': ['Jan-21','May-21','Jan-22'], 'x_labels_complete': True}])
        result = cv._read_part('chart.png', 'x_axis', 'prompt')
        self.assertEqual(result['x_labels'], ['Jan-21','May-21','Jan-22'])
        self.assertFalse(result['x_labels_complete'])
        self.assertFalse(result['x_order_known'])
        self.assertEqual(cv._read.call_args.args[2], [0.05, 0.6, 0.98, 1])

    def test_crop_failure_remains_error_and_does_not_loop(self):
        cv = ChartStructureReader.__new__(ChartStructureReader)
        cv.last_generation = {}
        cv._read = Mock(side_effect=[ValueError('repetition'), {'box': [0,0,1,0.4]}, ValueError('still bad')])
        with self.assertRaisesRegex(ValueError, 'still bad'):
            cv._read_part('chart.png', 'legend', 'prompt')
        self.assertEqual(cv._read.call_count, 3)

    def test_y_unit_error_can_recover_to_observed_numerical_axis(self):
        cv = ChartStructureReader.__new__(ChartStructureReader)
        cv.last_generation = {}
        cv._read = Mock(side_effect=[{'y_labels': ['%']}, {'y_axis_type': 'numerical'}])
        result = cv._read_part('chart.png', 'y_axis', 'prompt')
        self.assertEqual(result['y_labels'], [])
        self.assertTrue(result['uncertain'])

    def test_locator_accepts_named_coordinates_but_not_nested_or_pixel_boxes(self):
        self.assertEqual(normalize_locator_box(dict(left=0, top=.15, right=.9, bottom=.85)),
                         [0, .15, .9, .85])
        for bad in (None, [[0,0,1,1], ['legend'], [0,0,1,1]],
                    dict(left=0, top=0, right=900, bottom=800),
                    dict(left=0, top=.9, right=1, bottom=.1),
                    dict(left=False, top=0, right=1, bottom=1)):
            with self.assertRaises(ValueError): normalize_locator_box(bad)

    def test_truncated_locator_uses_one_coarse_location_then_reads_pixels(self):
        cv = ChartStructureReader.__new__(ChartStructureReader)
        cv.last_generation = {}
        cv._read = Mock(side_effect=[ValueError('bad date loop'), ValueError('token limit'),
            {'region': 'bottom'}, {'x_labels': ['29/7/2022', '1/8/2022'], 'x_labels_complete': True}])
        result = cv._read_part('chart.png', 'x_axis', 'read X')
        self.assertEqual(result['x_labels'], ['29/7/2022', '1/8/2022'])
        self.assertEqual(cv._read.call_args.args[2], [0, .45, 1, 1])
        self.assertFalse(result['x_labels_complete'])
        self.assertFalse(result['x_order_known'])
        self.assertEqual(cv._read.call_count, 4)

    def test_uncertain_y_classification_does_not_erase_categories(self):
        cv = ChartStructureReader.__new__(ChartStructureReader)
        cv.last_generation = {}
        cv._read = Mock(side_effect=[{'y_labels': ['2020']}, {'y_axis_type': 'unknown'},
            {'box': dict(left=0, top=0, right=.5, bottom=1)},
            {'y_axis_type': 'categorical', 'y_labels': ['2020', '2021']}])
        result = cv._read_part('chart.png', 'y_axis', 'read Y')
        self.assertEqual(result['y_labels'], ['2020', '2021'])

    def test_invalid_coarse_locator_stops_without_inventing_a_crop(self):
        cv = ChartStructureReader.__new__(ChartStructureReader)
        cv.last_generation = {}
        cv._read = Mock(side_effect=[ValueError('loop'), {'box': None}, {'region': 'guess'}])
        with self.assertRaisesRegex(ValueError, 'valid coarse region'):
            cv._read_part('chart.png', 'legend', 'read legend')
        self.assertEqual(cv._read.call_count, 3)


if __name__ == '__main__': unittest.main()
