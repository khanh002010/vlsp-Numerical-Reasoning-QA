"""Regression coverage for chart-role mistakes observed in the user's pilot."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from vinumqa.cv_module.structure import validate_structure, render_structure
from vinumqa.cv_module.structure_grounding import validate_layout, positioned_labels, resolve_series
from vinumqa.cv_module.reviewed_reader import read_reviewed
from vinumqa.cv_module.paddle_pilot import run_pilot
from vinumqa.cv_module.structure_store import ChartStructureStore
from vinumqa.nlp_module.inference.evidence_validation import validate_evidence
from vinumqa.cv_module.chart_lookup import resolve_chart
from vinumqa.evaluation.score_ocr_labels import score


def chart():
    return {'title':'Giá điện từ 2009 - 2023 (VND/kWh)', 'kind':'bar',
            'series':[{'name':'Giá điện từ 2009 - 2023 (VND/kWh)', 'unit':'VND/kWh'}],
            'series_source':'title', 'x_labels':['2022','2023'], 'y_labels':[],
            'x_labels_complete':True, 'series_complete':True,
            'layout':{'orientation':'vertical','x_axis_type':'categorical','y_axis_type':'numerical'}}


class VisionUpgradeTests(unittest.TestCase):
    def test_bar_geometry_and_column_transcription(self):
        from PIL import Image,ImageDraw
        from vinumqa.cv_module.bar_label_regions import bar_label_boxes,read_bar_labels
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'bars.png'
            im=Image.new('RGB',(300,200),'white');d=ImageDraw.Draw(im)
            for x,top in [(50,80),(125,50),(200,30)]: d.rectangle((x,top,x+20,150),fill=(60,110,200))
            im.save(path)
            boxes=bar_label_boxes(path)
            self.assertEqual(len(boxes),3)
            self.assertTrue(all(b[1]>.75 for b in boxes))
            reader=Mock();reader.last_generation={}
            reader._read.side_effect=[{'lines':v,'readable':True} for v in
                                     [['2010'],['2011','(Lần 1)'],['2011','(Lần 2)']]]
            labels,complete=read_bar_labels(reader,path,[])
            self.assertEqual(labels,['2010','2011 (Lần 1)','2011 (Lần 2)'])
            self.assertFalse(complete)
            Image.new('RGB',(300,200),'white').save(path)
            with self.assertRaises(ValueError):bar_label_boxes(path)

    def test_crop_evidence_recovers_omission_without_inventing_or_reordering(self):
        from vinumqa.cv_module.reviewed_reader import corroborated_candidate
        full=['A','B','C','D','E']
        self.assertEqual(corroborated_candidate([full,['A','B','D','E']],
                         [['A','B','C'],['B','D'],['D','E']]),full)
        for windows in ([['A','B'],['D','E']], [['A','B','C'],['E','D']],
                        [['A','B','C'],['D','E','F']]):
            with self.assertRaises(ValueError): corroborated_candidate([full],windows)

    def test_invalid_full_axis_enters_crop_recovery(self):
        from vinumqa.cv_module.reviewed_reader import read_axis_labels, axis_groups
        reader=Mock();reader.last_generation={}
        reader._read.side_effect=[ValueError('Duplicate categories'),ValueError('Duplicate categories')]+[
            {'labels':labels,'complete':False} for labels in
            [['2009','2010'],['2010','2011 (Lần 1)'],['2011 (Lần 1)','2011 (Lần 2)']]]
        labels,complete=read_axis_labels(reader,'image','x',[])
        self.assertEqual(labels[-1],'2011 (Lần 2)')
        self.assertFalse(complete)
        self.assertEqual(reader._read.call_args_list[2].kwargs['phase'],'axis_crop_x_0')
        with self.assertRaisesRegex(ValueError,'no parent year'):
            axis_groups({'labels':['(Lần 1)'],'complete':False},[])

    def test_review_retry_reobserves_invalid_layout_and_json_without_inventing_fields(self):
        from vinumqa.cv_module.reviewed_reader import checked_read, checked_layout
        reader=Mock(); reader.last_generation={}
        valid={**chart()['layout'], 'title':'Example'}
        reader._read.side_effect=[{**valid, 'orientation':'horizontal'}, valid]
        result=checked_read(reader,'image.png','schema',validator=checked_layout,
                            phase='review_layout',budgets=(512,))
        self.assertEqual(result,valid)
        self.assertEqual(reader._read.call_args.kwargs['phase'],'review_layout_retry')
        reader._read.side_effect=[ValueError('Expected a JSON object'),
                                 {'items':[{'box':[.1,.8,.2,.9],'lines':['2023']}], 'complete':False}]
        result=checked_read(reader,'image.png','schema',validator=lambda v: positioned_labels(v,'x'),
                            phase='positioned_x',budgets=(4096,))
        self.assertFalse(result['complete'])
        reader._read.side_effect=ValueError('Expected a JSON object')
        with self.assertRaisesRegex(ValueError,'Expected a JSON object'):
            checked_read(reader,'image.png','schema',validator=lambda v: positioned_labels(v,'x'),
                         phase='positioned_x',budgets=(4096,))

    def test_axis_roles_reject_legend_as_y_but_preserve_horizontal_rows(self):
        c=chart(); c['y_labels']=['Giá điện']
        with self.assertRaisesRegex(ValueError, 'Numerical/absent'):
            validate_structure(c)
        c['layout']={'orientation':'horizontal','x_axis_type':'numerical','y_axis_type':'categorical'}
        c['x_labels']=[]; c['y_labels']=['A','B']
        self.assertEqual(validate_structure(c)['y_labels'], ['A','B'])
        with self.assertRaisesRegex(ValueError, 'Vertical bars'):
            validate_layout({'orientation':'vertical','x_axis_type':'categorical','y_axis_type':'categorical'})

    def test_positions_preserve_repeated_years_with_own_qualifiers(self):
        value={'complete':True,'items':[
            {'box':[.4,.8,.5,.99],'lines':['2011','(Lần 2)']},
            {'box':[.2,.8,.3,.99],'lines':['2011','(Lần 1)']} ]}
        labels, _=positioned_labels(value, 'x')
        self.assertEqual(labels, ['2011 (Lần 1)','2011 (Lần 2)'])
        value['items'][1]['lines']=['2011','(Lần 2)']
        with self.assertRaisesRegex(ValueError,'Repeated labels'): positioned_labels(value,'x')

    def test_alias_requires_title_source_and_preserves_modifiers(self):
        c=validate_structure(chart())
        self.assertEqual(resolve_series('Giá điện', c), c['series'][0]['name'])
        self.assertTrue(validate_evidence('chart_at(Image 1; Giá điện; 2022; none)',{'Image 1':c},{'Image 1'})['valid'])
        self.assertIn('series_aliases', render_structure('Image 1', c))
        c['series_source']='legend'
        self.assertIsNone(resolve_series('Giá điện',validate_structure(c)))
        c['series_source']='title'; c['title']='P/E ước tính 2024'; c['series'][0]['name']=c['title']
        self.assertIsNone(resolve_series('P/E',validate_structure(c)))
        c['series_aliases']=[{'alias':'P/E','target':c['title']}]
        self.assertNotIn('series_aliases', validate_structure(c))

    def test_alias_resolution_only_changes_executor_lookup_not_program(self):
        c=validate_structure(chart()); store=Mock()
        store.get.return_value=c
        store.read_values.return_value={'complete':True,'points':[{'series':c['series'][0]['name'],
            'x_label':'2022','y_label':'none','value':1864,'raw_value':'1864','basis':'printed'}]}
        program='chart_at(Image 1; Giá điện; 2022; none)'
        self.assertEqual(resolve_chart(store,'image','chart_at','Giá điện','2022','none'),1864)
        self.assertEqual(store.read_values.call_args.args[1]['arguments'][0],c['series'][0]['name'])
        self.assertEqual(program,'chart_at(Image 1; Giá điện; 2022; none)')

    def test_reviewed_read_uses_text_groups_without_generated_boxes(self):
        reader=Mock()
        reader._read_part.return_value={'title':'', 'kind':'bar','series':[{'name':chart()['title'],'unit':'(VND/kWh)'}],
                                        'series_complete':True,'uncertain':[]}
        calls=[]
        def observe(path,prompt,box=None,**kw):
            phase=kw['phase']; calls.append(phase)
            if phase=='review_layout':
                return {**chart()['layout'],'title':chart()['title'],'kind':'bar','chart_unit':'','series_source':'title'}
            if phase=='axis_roles': return {'x_axis_type':'categorical','y_axis_type':'numerical'}
            if phase=='title_only': return {'title':chart()['title']}
            if phase in ('axis_text_x','axis_verify_x'):
                return {'complete':True,'labels':['2011 (Lần 1)','2011 (Lần 2)']}
            raise AssertionError(phase)
        reader._read.side_effect=observe
        result=read_reviewed(reader,'image.png')
        self.assertEqual(result['x_labels'],['2011 (Lần 1)','2011 (Lần 2)'])
        self.assertEqual(result['y_labels'],[])
        self.assertEqual(result['series'][0]['unit'],'VND/kWh')
        self.assertNotIn('positioned_x',calls)

    def test_axis_groups_rejects_observed_date_merge_and_legend_pollution(self):
        from vinumqa.cv_module.reviewed_reader import axis_groups, read_axis_labels
        self.assertEqual(axis_groups({'groups':[['1/2/2018','3/2/2018']], 'complete':False},[]),
                         ['1/2/2018','3/2/2018'])
        with self.assertRaisesRegex(ValueError,'Multiple dates'):
            axis_groups({'groups':[['1/2/2018 3/2/2018']], 'complete':True},[])
        from vinumqa.cv_module.reviewed_reader import validate_axis_roles
        roles={'x_axis_type':'categorical','y_axis_type':'numeric'}
        validate_axis_roles(roles)
        self.assertEqual(roles['y_axis_type'],'numerical')
        with self.assertRaisesRegex(ValueError,'Ambiguous grouped'):
            axis_groups({'groups':[['Ng?n h?ng','T12']], 'complete':False},[{'name':'T12'}])
        reader=Mock();reader.last_generation={}
        reader._read.side_effect=[{'labels':x,'complete':False} for x in
                                 [['wrong'],['different'],['2009','2010'],['2010','2011 (Lần 1)'],['2011 (Lần 1)','2011 (Lần 2)']]]
        labels,complete=read_axis_labels(reader,'image','x',[])
        self.assertEqual(labels,['2009','2010','2011 (Lần 1)','2011 (Lần 2)'])
        self.assertFalse(complete)
        self.assertEqual(reader._read.call_args_list[2].args[2],[0,0,.45,1])
        from vinumqa.cv_module.reviewed_reader import merge_axis_windows
        with self.assertRaisesRegex(ValueError,'no exact shared'):
            merge_axis_windows([['2009'],['2010']])

    def test_expanded_score_catches_hidden_y_title_and_unit_errors(self):
        ref={'a.png':{'series':['A'],'x_labels':['2023'],'y_labels':[], 'title':'Title','units':{'A':'%'}}}
        c={'series':[{'name':'A','unit':''}],'x_labels':['2023'],'y_labels':['A'],'title':''}
        result=score({'a.png':{'structure':c}},ref)
        self.assertEqual(result['fields']['series']['recall'],1)
        self.assertEqual(result['fields']['y_labels']['exact_image_rate'],0)
        self.assertIsNone(result['fields']['y_labels']['recall'])
        self.assertEqual(result['metadata']['title']['accuracy'],0)
        self.assertEqual(result['metadata']['units']['accuracy'],0)
        c.update(y_labels=[],title='Title'); c['series'][0]['unit']='%'
        self.assertEqual(score({'a.png':{'structure':c}},ref)['fields']['y_labels']['exact_image_rate'],1)
        failed = score({'a.png': {'status': 'error', 'structure': c}}, ref)
        self.assertEqual(failed['fields']['y_labels']['exact_image_rate'], 0)

    def test_missing_scale_is_not_matrix_and_legend_title_is_visually_checked(self):
        reader=Mock()
        reader._read_part.return_value={'title':'Metric','kind':'bar',
            'series':[{'name':'Metric','unit':''}],'series_complete':True,'uncertain':[]}
        def observe(path,prompt,box=None,**kw):
            phase=kw['phase']
            if phase=='review_layout': return {'title':'Metric','kind':'bar','series_source':'legend','chart_unit':''}
            if phase=='axis_roles': return {'x_axis_type':'time','y_axis_type':'none'}
            if phase=='title_only': return {'title':'Metric'}
            if phase=='verify_heading': return {'separate_heading':False,'title':''}
            if phase in ('axis_text_x','axis_verify_x'): return {'labels':['2022','2023'],'complete':False}
            raise AssertionError(phase)
        reader._read.side_effect=observe
        result=read_reviewed(reader,'image')
        self.assertEqual(result['layout']['orientation'],'vertical')
        self.assertEqual(result['title'],'')

    def test_store_recipe_reopens_but_does_not_reuse_old_parts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'store.json'
            s=ChartStructureStore(path,read_mode='reviewed'); s.save()
            self.assertEqual(ChartStructureStore.from_saved(path).read_mode,'reviewed')
            with self.assertRaisesRegex(ValueError,'contract changed'): ChartStructureStore(path,read_mode='parts')

    def test_paddle_native_tasks_resume_and_do_not_read_reference_answers(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Image bytes are only hashed by orchestration; recognition is mocked.
            path=Path(tmp)/'image.png'; path.write_bytes(b'fixture image bytes')
            recognizer=Mock()
            recognizer.recognize.return_value={'complete':True,'text':'native output','stop_reason':'eos','tokens':2,'seconds':.1}
            identity={'model':'test','max_new_tokens':1024,'max_seconds':20}
            for _ in range(2):
                run_pilot([path],Path(tmp)/'out',recognizer,['chart','spotting'],identity)
            self.assertEqual(recognizer.recognize.call_count,2)
            with self.assertRaisesRegex(ValueError,'configuration changed'):
                run_pilot([path],Path(tmp)/'out',recognizer,['chart'],{**identity,'max_new_tokens':2048})

    def test_paddle_loader_and_task_use_t4_dtype_native_prompt_and_pixel_cap(self):
        import torch
        from PIL import Image
        from transformers import AutoProcessor, AutoModelForImageTextToText
        from vinumqa.cv_module.paddle_pilot import PaddleRecognizer
        class Inputs(dict):
            def to(self, device): return self
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(torch.cuda, 'is_available', return_value=True), \
             patch.object(AutoProcessor, 'from_pretrained') as processor_loader, \
             patch.object(AutoModelForImageTextToText, 'from_pretrained') as model_loader:
            image=Path(tmp)/'a.png'; Image.new('RGB',(100,80)).save(image)
            model=model_loader.return_value.eval.return_value
            model.generation_config.eos_token_id=2
            model.generate.return_value=torch.tensor([[7,8,9,2]])
            processor=processor_loader.return_value
            from types import SimpleNamespace
            processor.image_processor=SimpleNamespace(size={'shortest_edge':3136, 'longest_edge':2359296})
            processor.apply_chat_template.return_value=Inputs(input_ids=torch.tensor([[7,8]]))
            processor.decode.return_value='recognized'
            reader=PaddleRecognizer()
            result=reader.recognize(image,'spotting',1024,30)
            self.assertEqual(model_loader.call_args.kwargs['dtype'],torch.float16)
            self.assertEqual(model_loader.call_args.kwargs['attn_implementation'],'sdpa')
            self.assertNotIn('quantization_config',model_loader.call_args.kwargs)
            call=processor.apply_chat_template.call_args
            self.assertEqual(call.args[0][0]['content'][1]['text'],'Spotting:')
            self.assertEqual(call.kwargs['images_kwargs']['size']['longest_edge'],1400000)
            self.assertEqual(result['input_image_size'],[100,80])
            self.assertTrue(result['complete'])
            processor.decode.assert_called_once_with([9,2],skip_special_tokens=True)

    def test_paddle_pixel_size_current_and_legacy_processors(self):
        from types import SimpleNamespace
        from vinumqa.cv_module.paddle_pilot import processor_size
        for proc in (SimpleNamespace(size={'shortest_edge':147456}),
                     SimpleNamespace(min_pixels=147456),
                     SimpleNamespace(size=SimpleNamespace(shortest_edge=147456))):
            self.assertEqual(processor_size(proc), {'shortest_edge':147456, 'longest_edge':1400000})
        with self.assertRaises(ValueError):
            processor_size(SimpleNamespace())


if __name__=='__main__': unittest.main()
