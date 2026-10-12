"""Regression checks for audit failures; recognition is mocked, not scored as OCR."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from vinumqa.cv_module.grounded_review import heading, inventory, bindings, axis_plan, read_axis, read_chart
from vinumqa.cv_module.repair_audited import repair, digest


class GroundedReviewTests(unittest.TestCase):
    def test_units_and_invented_sources_are_not_metadata(self):
        for title in ('%', '(%)', 'Tỷ đồng', 'Triệu USD', 'GW'):
            with self.assertRaises(ValueError):heading({'role':'heading','title':title,'box':[0,0,1,.1]})
        heading({'role':'absent','title':'','box':None})
        with self.assertRaises(ValueError):heading({'role':'absent','title':'Time Series','box':None})
        for unit in ('100%','150%','59%','1.000','5.000'):
            with self.assertRaises(ValueError):bindings({'scales':{'left':[0,0,.1,1],'right':None},
                'series':[{'name':'A','axis':'left','unit':unit,'evidence':'tick'}]},['A'])
        bindings({'scales':{'left':[0,0,.1,1],'right':None},
                  'series':[{'name':'A','axis':'left','unit':'%','evidence':'percent scale'}]},['A'])

    def test_no_right_scale_and_exact_names(self):
        with self.assertRaisesRegex(ValueError,'nonexistent'):
            bindings({'scales':{'left':[0,0,.1,1],'right':None},
                      'series':[{'name':'A','axis':'right','unit':'%','evidence':'text on right'}]},['A'])
        v={'kind':'line','series_complete':True,'series':[
            {'name':'China','raw_text':'China','box':[0,.8,.1,.9],'source':'legend'}]}
        inventory(v)
        v['series'][0]['name']='Giá Trung Quốc'
        with self.assertRaisesRegex(ValueError,'verbatim'):inventory(v)
        v['series'][0].update(name='Biên LN, 32.4%',raw_text='Biên LN, 32.4%',source='direct')
        with self.assertRaisesRegex(ValueError,'endpoint'):inventory(v)
        v['series'][0]['name']='Biên LN';inventory(v)

    def test_reject_extra_unqualified_quarters_and_duplicate_positions(self):
        v={'role':'time','all_visible_located':True,'all_data_labelled':True,'groups':[
            {'parent_box':[.1,.9,.4,1],'boxes':[[.1,.7,.2,.8],[.2,.7,.3,.8]]},
            {'parent_box':None,'boxes':[[.5,.7,.6,.8]]}]}
        with self.assertRaisesRegex(ValueError,'Mixed parented'):axis_plan(v,'x')
        v['groups'][1]['parent_box']=[.5,.9,.8,1];axis_plan(v,'x')
        v['groups'][1]['boxes']=[[.1,.7,.2,.8]]
        with self.assertRaisesRegex(ValueError,'Duplicate tick'):axis_plan(v,'x')

    def test_tiered_quarters_preserve_years_order_and_coverage(self):
        reader=Mock();reader.last_generation={}
        plan={'role':'time','all_visible_located':True,'all_data_labelled':True,'groups':[
            {'parent_box':[.1,.9,.4,1],'boxes':[[.2,.7,.3,.8],[.1,.7,.2,.8]]},
            {'parent_box':[.5,.9,.8,1],'boxes':[[.5,.7,.6,.8]]}]}
        responses=[plan]+[{'text':s,'readable':True} for s in ['2017','2Q','1Q','2018','1Q']]+[
            {'labels':['1Q 2017','2Q 2017','1Q 2018']}]
        reader._read.side_effect=responses
        _,labels,ticks=read_axis(reader,'image','x')
        self.assertEqual(labels,['1Q 2017','2Q 2017','1Q 2018']);self.assertFalse(ticks)
        reader._read.side_effect=responses[:-1]+[{'labels':['1Q 2017','2Q 2017']}]
        with self.assertRaisesRegex(ValueError,'coverage'):read_axis(reader,'image','x')

    def test_callout_order_follows_horizontal_position(self):
        reader=Mock();reader.last_generation={}
        reader._read.side_effect=[{'role':'categorical','all_visible_located':True,'all_data_labelled':True,
            'groups':[{'parent_box':None,'boxes':[[.6,.6,.8,.7],[.1,.2,.3,.3]]}]}]+[
            {'text':s,'readable':True} for s in ['Thép','Giấy']]+[{'labels':['Giấy','Thép']}]
        self.assertEqual(read_axis(reader,'image','x')[1],['Giấy','Thép'])

    def test_literal_duplicates_retained_but_disagreement_not_silently_accepted(self):
        reader=Mock();reader.last_generation={}
        responses=[{'role':'time','all_visible_located':True,'all_data_labelled':False,
            'groups':[{'parent_box':None,'boxes':[[.1,.7,.2,.8],[.3,.7,.4,.8],[.5,.7,.6,.8]]}]}]+[
            {'text':s,'readable':True} for s in ['Jan-01','Mar-01','Jan-01']]
        reader._read.side_effect=responses+[{'labels':['Jan-01','Mar-01','Jan-01']}]
        _,labels,ticks=read_axis(reader,'image','x');self.assertFalse(labels)
        self.assertEqual(ticks,['Jan-01','Mar-01','Jan-01'])
        reader._read.side_effect=responses+[{'labels':['Jan-01','Mar-07','Jan-01']}]
        with self.assertRaisesRegex(ValueError,'disagree'):read_axis(reader,'image','x')

    def test_numeric_year_role_cannot_silently_drop_labels(self):
        reader=Mock();reader.last_generation={}
        reader._read.side_effect=[{'role':'numerical','all_visible_located':True,'all_data_labelled':False,'groups':[]},
                                  {'role':'time'},{'role':'time'}]
        with self.assertRaisesRegex(ValueError,'role disagrees'):read_axis(reader,'image','x')

    def test_integrated_reader_uses_crop_evidence_and_relocalizes_mismatch(self):
        reader=Mock();reader.last_generation={};bad_first=True
        def observe(path,prompt,box=None,**kw):
            nonlocal bad_first
            phase=kw['phase']
            if phase in {'heading_location','heading_confirmation'}:
                return {'role':'heading','title':'Metric','box':[0,0,1,.1]}
            if phase=='heading_pixels':return {'text':'Metric','readable':True}
            if phase=='series_inventory':return {'kind':'bar','series_complete':True,'series':[
                {'name':'A','raw_text':'A','source':'legend','box':[0,.9,.2,1]}]}
            if phase=='series_pixels_0':
                if bad_first:bad_first=False;return {'text':'B','readable':True}
                return {'text':'A','readable':True}
            if phase=='scale_binding':return {'scales':{'left':[0,.1,.1,.8],'right':None},
                'series':[{'name':'A','axis':'left','unit':'%','evidence':'left percent ticks'}]}
            if phase=='scale_pixels_left':return {'numeric_scale_visible':True,'unit':'%'}
            if phase=='inventory_coverage':return {'missing':[],'extra':[],'bindings_correct':True}
            if phase=='locate_ticks_x':return {'role':'time','all_visible_located':True,'all_data_labelled':True,
                'groups':[{'parent_box':None,'boxes':[[.2,.8,.3,.9],[.4,.8,.5,.9]]}]}
            if phase.startswith('tick_x'):return {'text':'2022' if phase.endswith('_0') else '2023','readable':True}
            if phase=='coverage_x':return {'labels':['2022','2023']}
            if phase=='locate_ticks_y':return {'role':'numerical','all_visible_located':True,'all_data_labelled':False,'groups':[]}
            if phase=='confirm_role_y':return {'role':'numerical'}
            raise AssertionError(phase)
        reader._read.side_effect=observe
        result=read_chart(reader,'image')
        self.assertEqual(result['x_labels'],['2022','2023'])
        self.assertTrue(result['x_labels_complete'])
        self.assertEqual(result['series'][0]['name'],'A')
        self.assertEqual(reader.last_generation['stage_errors'][0]['stage'],'series')
        self.assertIn('not_human_verified',reader.last_generation['quality_status'])

    def test_repair_rereads_selected_ok_and_preserves_others_and_resumes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); images=root/'data/train/train_images';images.mkdir(parents=True)
            for name in ['bad.png','good.png']:(images/name).write_bytes(name.encode())
            bad,good=[digest(images/name) for name in ['bad.png','good.png']]
            source=root/'source.json';q=root/'queue.json'
            original={'identity':{'model':'test'},'images':{bad:{'status':'ok','structure':{'wrong':True}},
                        good:{'status':'ok','structure':{'retain':True}}}}
            source.write_text(json.dumps(original));q.write_text(json.dumps({'images':[{'split':'train','image':'bad.png'}]}))
            calls=[]
            class Store:
                def __init__(self,path,**kw):
                    self.path=path;self.identity={'model':'test','review_recipe':'new'}
                    self.data=json.loads(path.read_text()) if path.exists() else {'images':{}}
                def get(self,path,retry_failed):
                    calls.append(path.name);self.data['images'][digest(path)]={'status':'ok','structure':{'new':True}}
                    self.path.write_text(json.dumps(self.data))
                def close(self):pass
            result=repair(source,q,root/'data',root/'out',store_factory=Store)
            self.assertEqual(result['images'][good]['structure'],{'retain':True})
            self.assertEqual(json.loads(source.read_text()),original)
            repair(source,q,root/'data',root/'out',store_factory=Store)
            self.assertEqual(calls,['bad.png'])


if __name__=='__main__':unittest.main()
