import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from tests.test_repair_inference import chart, prediction
from vinumqa.cv_module.structure_store import ChartStructureStore
from vinumqa.data.context import build_inline_context
from vinumqa.nlp_module.inference.evidence_validation import validate_evidence, bound_label
from vinumqa.nlp_module.inference.semantic_validation import validate_semantics, table_axes
from vinumqa.pipeline.repair_inference import run_repair, export_outputs, apply_reviewed_structures, file_digest


class PrivateRepair(unittest.TestCase):
    def test_dangling_image_marker_preserves_question_context_without_fake_source(self):
        text=['Before', '### Image 6 ###', 'After']
        context=build_inline_context(text,{}, {},None,chart_structures={},allow_unavailable_images=True)
        self.assertIn('Before',context)
        self.assertIn('After',context)
        self.assertIn('not an available source',context)
        self.assertNotIn('**Image 6**',context)
        with self.assertRaises(ValueError):
            build_inline_context(text,{}, {},None,chart_structures={})
    def test_table_second_key_and_discrete_selection(self):
        table = '<table><tr><td>Group</td><td>Bank</td><td>Rate</td></tr>' + ''.join(
            f'<tr><td>State</td><td>{b}</td><td>9</td></tr>' for b in ['VCB','BID','CTG','SC']) + '</table>'
        self.assertEqual(table_axes(table)[1], ['VCB','BID','CTG','SC'])
        p='table_average(Table 1; Rate; VCB; SC)'
        self.assertTrue(validate_semantics(p,{'Table 1':table},[],'Average all banks')['valid'])
        self.assertFalse(validate_semantics(p,{'Table 1':table},[],'Trung bình VCB, CTG và SC')['valid'])

    def test_newest_first_table_is_not_reversed_operand_order(self):
        table='<table><tr><td>Metric</td><td>2026</td><td>2025</td><td>2024</td></tr><tr><td>EPS</td><td>4</td><td>3</td><td>2</td></tr></table>'
        self.assertTrue(validate_semantics('table_max(Table 1; EPS; 2024; 2026)',{'Table 1':table},[],'?')['valid'])

    def test_typographic_binding_is_conservative(self):
        self.assertEqual(bound_label('09/02/2023',['9/2/2023']), '9/2/2023')
        self.assertIsNone(bound_label('2/9/2023',['9/2/2023']))
        self.assertIsNone(bound_label('Cổ phiếu',['Có phiếu']))
        self.assertIsNone(bound_label('FY 2026',['2026F']))
        self.assertIsNone(bound_label('09/02/2023',['9/2/2023','09/2/2023']))

    def test_missing_axis_requests_axis_review(self):
        result=validate_evidence('chart_at(Image 1; TCB; 2027; none)',{'Image 1':chart()},{'Image 1'})
        self.assertEqual(result['cv_requests'][0]['region'],'x_axis')

    def test_wrong_existing_series_is_repaired_without_loading_cv(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);image=root/'image.png';image.write_bytes(b'image')
            reader=Mock(read_structure=Mock(return_value=chart()),last_generation={})
            store=ChartStructureStore(root/'store.json',reader=reader)
            inp=root/'input.json'
            inp.write_text(json.dumps([{'qid':'q','images':{'Image 1':'image.png'},'qa':{'question':'TCB'}}]))
            gen=Mock(generate_with_prompt=Mock(side_effect=[prediction('chart_at(Image 1; WRONG; 2026; none)'),prediction('chart_at(Image 1; TCB; 2026; none)')]))
            result=run_repair(inp,root,root/'adapter',store.path,root/'out',store=store,generator_factory=lambda:gen,max_rounds=1)
            self.assertTrue(result['complete'])
            reader.inspect.assert_not_called()

    def test_final_export_never_contains_empty_programs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=[{'qid':'q','qa':{'question':'?'}}]
            state={'records':{'q':{'valid':True,'program':'add(2; 3)'}}}
            self.assertTrue(export_outputs(root,data,state,'done')['complete'])
            self.assertTrue((root/'results.json').exists())
            state['records']['q']['valid']=False
            self.assertFalse(export_outputs(root,data,state,'source_changed')['complete'])
            self.assertFalse((root/'results.json').exists())
            self.assertTrue(list(root.glob('results.json.*.superseded')))
            self.assertEqual(json.loads((root/'unresolved.json').read_text())[0]['candidate'],'add(2; 3)')

    def test_local_repair_connects_branches_before_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); inp=root/'input.json'
            inp.write_text(json.dumps([{'qid':'q','qa':{'question':'Tổng hai chênh lệch'}}]))
            gen=Mock(generate_with_prompt=Mock(side_effect=[prediction('subtract(8; 2); subtract(3; 1)'),prediction('subtract(8; 2); subtract(3; 1); add(#0; #1)')]))
            result=run_repair(inp,root,root/'adapter',root/'store.json',root/'out',generator_factory=lambda:gen,max_rounds=1)
            self.assertTrue(result['complete'])
            self.assertEqual(gen.generate_with_prompt.call_count,2)
            self.assertIn('Unused intermediate',gen.generate_with_prompt.call_args.args[0])
            self.assertEqual(len(json.loads((root/'out/state.json').read_text())['records']['q']['repair_history']),2)

    def test_persistent_bad_model_leaves_unresolved_not_fake_submission(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);inp=root/'input.json'
            inp.write_text(json.dumps([{'qid':'q','qa':{'question':'?'}}]))
            gen=Mock(generate_with_prompt=Mock(return_value={'program':'sum(2; 3)','termination':'eos'}))
            result=run_repair(inp,root,root/'adapter',root/'store.json',root/'out',generator_factory=lambda:gen,max_rounds=1)
            self.assertFalse(result['complete'])
            self.assertFalse((root/'out/results.json').exists())
            self.assertTrue((root/'out/state.json').exists())

    def test_oom_stops_instead_of_marking_remaining_questions_bad(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);inp=root/'input.json'
            inp.write_text(json.dumps([{'qid':str(i),'qa':{'question':'?'}} for i in range(3)]))
            gen=Mock(generate_with_prompt=Mock(return_value={'error':'CUDA out of memory','program':''}))
            with self.assertRaisesRegex(RuntimeError,'out of memory'):
                run_repair(inp,root,root/'adapter',root/'store.json',root/'out',generator_factory=lambda:gen)
            self.assertEqual(gen.generate_with_prompt.call_count,1)
            self.assertFalse((root/'out/results.json').exists())
            gen.close.assert_called_once()

    def test_reviewed_fields_survive_new_cv_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);image=root/'image.png';image.write_bytes(b'image')
            reader=Mock(read_structure=Mock(return_value=chart('bad')),
                        inspect=Mock(return_value={'structure':chart('bad again'),'full_image':True}),last_generation={})
            store=ChartStructureStore(root/'store.json',reader=reader);store.get(image)
            corrections=root/'fix.json'
            corrections.write_text(json.dumps({file_digest(image):{'patch':{'series':[{'name':'TCB'}]},'provenance':{'scope':'fields'}}}))
            apply_reviewed_structures(store,[image],corrections)
            fixed=store.inspect(image,{'image_id':'Image 1','kind':'inspect','region':'x_axis','series':''})
            self.assertEqual(fixed['series'][0]['name'],'TCB')

    def test_failed_cv_request_can_be_retried(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);image=root/'image.png';image.write_bytes(b'image')
            reader=Mock(read_structure=Mock(return_value=chart()),inspect=Mock(side_effect=[ValueError('temporary'),{'structure':chart('NEW'),'full_image':True}]),last_generation={})
            store=ChartStructureStore(root/'store.json',reader=reader)
            request={'image_id':'Image 1','kind':'inspect','region':'full','series':''}
            with self.assertRaises(RuntimeError):store.inspect(image,request)
            self.assertEqual(store.inspect(image,request,retry_failed=True)['series'][0]['name'],'NEW')


if __name__=='__main__': unittest.main()
