import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from vinumqa.cv_module.structure_store import ChartStructureStore
from vinumqa.nlp_module.contracts import build_prompt, parse_response
from vinumqa.nlp_module.prompting import reviewed_context
from vinumqa.nlp_module.data_prep.format_training_data import format_sample
from vinumqa.nlp_module.training.supervision import augment_source_ids, validate_dataset_pair
from vinumqa.nlp_module.training.epoch_predictions import validation_prompt, epoch_metrics, save_best_program
from vinumqa.nlp_module.inference.semantic_validation import validate_semantics
from vinumqa.evaluation.score_ocr_labels import score
from tests.test_repair_inference import chart


def sample():
    return {'qid': 'train-q', 'text': ['Revenue 125; share 4%.', '### Image 1 ###'],
            'tables': {}, 'images': {'Image 1': 'a.png'},
            'qa': {'question': 'TCB in Image 1?', 'program': 'chart_at(Image 1; TCB; 2026; none)'}}


class AccuracyImprovements(unittest.TestCase):
    def test_fraction_requires_printed_percentage(self):
        self.assertTrue(validate_semantics('multiply(125; 0.04)', {}, ['Revenue 125; share 4%.'], '?')['valid'])
        self.assertFalse(validate_semantics('multiply(125; 0.04)', {}, ['Revenue 125; count 4.'], '?')['valid'])
        self.assertFalse(validate_semantics('multiply(125; 0.05)', {}, ['Revenue 125; share 4%.'], '?')['valid'])
        self.assertTrue(validate_semantics('multiply(125; 0.037)', {}, ['Revenue 125; share 3.7%.'], '?')['valid'])

    def test_new_sft_prompt_matches_first_pass_repair_prompt_without_gold(self):
        from vinumqa.data.context import build_inline_context
        s = sample(); charts = {'Image 1': chart()}
        row = format_sample(s, image_structures=charts, prompt_profile='source-review-v1')
        context = build_inline_context(s['text'], {}, s['images'], None, chart_structures=charts)
        runtime = build_prompt(reviewed_context(context, {}), s['qa']['question'], 'Image 1')
        self.assertEqual(validation_prompt(row), runtime)
        changed = copy.deepcopy(s); changed['qa']['program'] = 'add(2; 3)'
        another = format_sample(changed, image_structures=charts, prompt_profile='source-review-v1')
        self.assertEqual(validation_prompt(row), validation_prompt(another))
        self.assertNotEqual(row['output'], another['output'])

    def test_source_augmentation_remaps_question_chart_evidence_and_program(self):
        row = format_sample(sample(), image_structures={'Image 1': chart()})
        before = copy.deepcopy(row)
        rows = augment_source_ids([row])
        self.assertEqual(row, before)
        self.assertEqual(len(rows), 2)
        aug = rows[1]
        self.assertIn('TCB in Image 2?', aug['input'])
        self.assertEqual(set(aug['charts']), {'Image 2'})
        result = parse_response(aug['output'])
        self.assertEqual(result['program'], 'chart_at(Image 2; TCB; 2026; none)')
        self.assertIn('Image 2', result['extracted_values'])
        self.assertEqual(aug['group_keys'], row['group_keys'])

    def test_profile_mismatch_rejected_before_training(self):
        from vinumqa.nlp_module.contracts import FORMAT_VERSION, INSTRUCTION
        train = format_sample(sample(), image_structures={'Image 1': chart()})
        val = copy.deepcopy(train); val['qid'] = 'val-q'; val['prompt_profile'] = 'source-review-v1'
        with self.assertRaisesRegex(ValueError, 'profiles differ'):
            validate_dataset_pair([train], [val], FORMAT_VERSION, INSTRUCTION, allow_group_overlap=True)

    def test_preparation_cannot_silently_downgrade_prompt_profile(self):
        from vinumqa.nlp_module.data_prep.prepare_structures import prepare_structured
        s = sample(); s['images'] = {}; s['text'] = ['Revenue 125; share 4%.']
        s['qa'] = {'question': 'Share?', 'program': 'multiply(125; 0.04)'}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'train.json'
            result = prepare_structured([s], tmp, out, store=Mock(), prompt_profile='source-review-v1')
            self.assertEqual(result['summary']['ready'], 1)
            with self.assertRaisesRegex(ValueError, 'different data/contract'):
                prepare_structured([s], tmp, out, store=Mock())

    def test_vision_loader_dispatches_by_architecture_without_downloading(self):
        from types import SimpleNamespace
        from vinumqa.cv_module.chart_to_table import extract_table as module
        import transformers
        config = SimpleNamespace(model_type='qwen2_5_vl')
        with patch.object(module.torch.cuda, 'is_available', return_value=False), \
             patch.object(module, 'resolve_model_directory', return_value='local-snapshot'), \
             patch.object(module.AutoProcessor, 'from_pretrained'), \
             patch.object(module.AutoConfig, 'from_pretrained', return_value=config), \
             patch.object(module.Qwen2VLForConditionalGeneration, 'from_pretrained') as old_loader, \
             patch.object(transformers.Qwen2_5_VLForConditionalGeneration, 'from_pretrained') as new_loader:
            new_loader.return_value.generation_config = SimpleNamespace()
            module.ChartToTableExtractor('Qwen/Qwen2.5-VL-7B-Instruct')
            new_loader.assert_called_once()
            self.assertTrue(new_loader.call_args.kwargs['local_files_only'])
            old_loader.assert_not_called()
            config.model_type = 'qwen2_vl'
            old_loader.return_value.generation_config = SimpleNamespace()
            module.ChartToTableExtractor()
            old_loader.assert_called_once()

    def test_metric_includes_rejected_correct_candidates_and_all_qids(self):
        s = format_sample(sample(), image_structures={'Image 1': chart()})
        p = parse_response(s['output'])['program']
        metrics = epoch_metrics([s], [{'qid': s['qid'], 'predicted': ''}], [{'qid': s['qid'], 'program': p}])
        self.assertEqual(metrics['program_accuracy'], 0)
        self.assertEqual(metrics['raw_candidate_accuracy'], 1)
        self.assertEqual(metrics['correct_candidates_rejected'], 1)
        pending = epoch_metrics([s], [], [{'qid': s['qid'], 'status': 'pending_time_budget'}])
        self.assertFalse(pending['complete'])

    def test_best_checkpoint_not_replaced_by_worse_or_partial_epoch(self):
        with tempfile.TemporaryDirectory() as tmp:
            model, tokenizer = Mock(), Mock()
            self.assertTrue(save_best_program(model, tokenizer, tmp, {'complete': True, 'program_accuracy': .5}, {}, 1, 108))
            self.assertFalse(save_best_program(model, tokenizer, tmp, {'complete': True, 'program_accuracy': .4}, {}, 2, 216))
            self.assertFalse(save_best_program(model, tokenizer, tmp, {'complete': False, 'program_accuracy': .9}, {}, 3, 324))
            self.assertEqual(model.save_pretrained.call_count, 1)
            with self.assertRaisesRegex(ValueError, 'different training run'):
                save_best_program(model, tokenizer, tmp, {'complete': True, 'program_accuracy': .6}, {'different': True}, 2, 216)

    def test_vision_store_reopens_correct_model_and_refuses_cross_recipe_reuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'store.json'
            store = ChartStructureStore(path, model_id='Qwen/Qwen2.5-VL-7B-Instruct', load_in_4bit=True, read_mode='parts')
            store.save()
            reopened = ChartStructureStore.from_saved(path)
            self.assertEqual(reopened.identity, store.identity)
            self.assertTrue(reopened.load_in_4bit)
            self.assertEqual(reopened.read_mode, 'parts')
            with self.assertRaisesRegex(ValueError, 'contract changed'):
                ChartStructureStore(path)

    def test_pixel_score_reports_missing_and_hallucinated_labels(self):
        actual = {'a.png': {'structure': {'series': [{'name':'A'}, {'name':'C'}], 'x_labels': ['2026']}}}
        ref = {'a.png': {'series':['A','B'], 'x_labels':['2025','2026']}}
        result = score(actual, ref)
        self.assertEqual(result['fields']['series']['precision'], .5)
        self.assertEqual(result['fields']['series']['recall'], .5)
        self.assertEqual(result['fields']['x_labels']['precision'], 1)
        self.assertEqual(result['fields']['x_labels']['recall'], .5)


if __name__ == '__main__': unittest.main()
