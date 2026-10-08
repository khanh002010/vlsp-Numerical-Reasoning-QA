import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from PIL import Image
from vinumqa.cv_module.structure_reader import ChartStructureReader
from vinumqa.cv_module.structure_output import parse_structure_output
from vinumqa.nlp_module.data_prep.prepare_structures import prepare_structured


def chart():
    return dict(title="Bank", kind="line", series=[{"name": "Bank"}],
                x_labels=["2020"], y_labels=[], x_labels_complete=True, series_complete=True)


class RecoveryTests(unittest.TestCase):
    def test_cli_backs_up_originals_and_selects_failed_only(self):
        from vinumqa.nlp_module.data_prep.retry_failed_structures import main
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prep = root / 'prepared'
            prep.mkdir()
            source = root / 'data' / 'train'
            images = source / 'train_images'
            images.mkdir(parents=True)
            (images / 'bad.png').write_bytes(b'image')
            (source / 'train.json').write_text('[]')
            (prep / 'chart_structures.json').write_text('{"images":{}}')
            artifact = {'artifact_version': 'vinumqa-prepared-structures-v1',
                        'images': [{'image': 'bad.png', 'status': 'error'},
                                   {'image': 'good.png', 'status': 'ok'}]}
            output = prep / 'train_structured.json'
            output.write_text(json.dumps(artifact))
            before = output.read_bytes()
            with patch('sys.argv', ['retry', '--prepared-dir', str(prep), '--data-root',
                                   str(root / 'data'), '--splits', 'train']), patch(
                    'vinumqa.nlp_module.data_prep.retry_failed_structures.prepare_structured',
                    return_value={'summary': {}}) as run:
                main()
            self.assertTrue(run.call_args.kwargs['only_failed'])
            backups = list((prep / 'backups').glob('*/train_structured.json'))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_bytes(), before)
            self.assertEqual(output.read_bytes(), before)

    def test_missing_flags_are_unknown_not_complete(self):
        value = chart()
        del value['x_labels_complete']
        result, repairs = parse_structure_output(json.dumps(value))
        self.assertFalse(result['x_labels_complete'])
        self.assertTrue(repairs)

    def test_focused_reads_recover_each_failure_without_guessing(self):
        for error in ('Punctuation-only y label', 'token limit', 'Each series needs its visible name',
                      'Duplicate labels in x_labels', 'Duplicate labels in series'):
            cv = ChartStructureReader.__new__(ChartStructureReader)
            cv.last_generation = {}
            value = chart()
            cv._read = Mock(side_effect=[ValueError(error), ValueError(error),
                {k: value[k] for k in ('title', 'kind', 'series', 'series_complete')},
                {k: value[k] for k in ('x_labels', 'x_labels_complete')}, {'y_labels': []}])
            result = cv.read_structure('image.png')
            self.assertEqual(result['series'], [{'name': 'Bank', 'color': '', 'axis': 'none', 'unit': ''}])
            self.assertEqual(cv._read.call_count, 5)

    def test_focused_output_still_rejects_duplicate_names(self):
        cv = ChartStructureReader.__new__(ChartStructureReader)
        cv.last_generation = {}
        value = chart()
        value['series'] *= 2
        cv._read = Mock(side_effect=[value, value, value])
        with self.assertRaisesRegex(ValueError, 'Duplicate labels in series'):
            cv._read_parts('image.png')

    def test_only_failed_preserves_success_and_updates_original_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / 'train.json'
            data = [dict(qid=str(i), images={'Image 1': f'{i}.png'}) for i in range(2)]
            for i in range(2): Image.new('RGB', (10, 10)).save(root / f'{i}.png')
            store = Mock()
            store.record.return_value = {'sha256': 'abc'}
            store.get.side_effect = [chart(), ValueError('bad OCR')]
            with patch('vinumqa.nlp_module.data_prep.format_training_data.format_sample', return_value={'output': 'target'}):
                first = prepare_structured(data, root, out, store=store)
                original = first['images'][0].copy()
                store.get.reset_mock()
                store.get.side_effect = None
                store.get.return_value = chart()
                result = prepare_structured(data, root, out, store=store, only_failed=True)
            store.get.assert_called_once_with(root / '1.png', True)
            self.assertEqual(result['images'][0], original)
            self.assertEqual(result['summary']['ready'], 2)
            self.assertEqual(json.loads(out.read_text())['summary']['error'], 0)
            self.assertEqual(json.loads(out.with_suffix('.ocr_errors.json').read_text()), [])


if __name__ == '__main__': unittest.main()
