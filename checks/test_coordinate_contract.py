import unittest
from vinumqa.cv_module.coordinate_contract import normalize_observation


class CoordinateTests(unittest.TestCase):
    def test_declared_frames(self):
        for system, size, box in [('normalized_1000', None, [100,200,900,400]),
                                  ('pixels', [200,100], [20,20,180,40])]:
            value = normalize_observation({'coordinate_system': system, 'coordinate_size': size,
                'series': [{'name': 'A', 'box': box}], 'groups': [{'parent_box': None, 'boxes': [box]}]})
            self.assertEqual(value['series'][0]['box'], [.1,.2,.9,.4])
            self.assertEqual(value['groups'][0]['boxes'], [[.1,.2,.9,.4]])

    def test_ambiguous_or_invalid_boxes_rejected(self):
        for value in [{'box': [10,5,827,34]},
                      {'coordinate_system':'pixels', 'box':[1,2,3,4]},
                      {'coordinate_system':'normalized_1000', 'box':[900,2,100,4]},
                      {'coordinate_system':'normalized_1000', 'box':[0,0,1001,500]}]:
            with self.assertRaises(ValueError): normalize_observation(value)

    def test_absent_heading(self):
        self.assertIsNone(normalize_observation({'role':'absent','title':'','box':None})['box'])


if __name__ == '__main__': unittest.main()
