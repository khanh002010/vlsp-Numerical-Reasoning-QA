import unittest
from vinumqa.cv_module.hybrid_pilot import tokens_from_result, build_structure, prompt_tokens
import json
from copy import deepcopy


class HybridTests(unittest.TestCase):
    def test_prompt_compaction_preserves_text_and_artifact(self):
        tokens=[{'id':7,'text':'Doanh thu 2026F; 12,34%', 'score':0.987654321,
                 'box':[0.123456789,0.234567891,0.345678912,0.456789123]}]
        original=deepcopy(tokens)
        compact=prompt_tokens(tokens)
        row=json.loads(compact)[0]
        self.assertEqual(row[:2],[7,tokens[0]['text']])
        self.assertTrue(all(abs(a-b)<=0.00005 for a,b in zip(row[2:],tokens[0]['box'])))
        self.assertEqual(tokens,original)
        self.assertLess(len(compact),len(json.dumps(tokens,ensure_ascii=False)))

    def test_paddle_coordinates_and_alignment(self):
        raw={'res':{'rec_texts':['A'],'rec_scores':[.9],'rec_polys':[[[10,20],[30,20],[30,40],[10,40]]]}}
        tokens=tokens_from_result(raw,100,200)
        self.assertEqual(tokens[0]['box'],[.1,.1,.3,.2])
        raw['res']['rec_scores']=[]
        with self.assertRaises(ValueError):tokens_from_result(raw,100,200)

    def test_structure_uses_only_real_token_ids(self):
        tokens=[{'id':0,'text':'Revenue'},{'id':1,'text':'2026F'}]
        plan={'title_ids':[],'kind':'bar','series':[{'name_ids':[0],'axis':'left','unit_ids':[]}],
              'x_label_ids':[[1]],'y_label_ids':[],'x_labels_complete':False,'series_complete':True,
              'series_source':'legend','layout':{'orientation':'vertical','x_axis_type':'time','y_axis_type':'numerical'},'uncertain':[]}
        chart=build_structure(plan,tokens)
        self.assertEqual(chart['series'][0]['name'],'Revenue')
        self.assertEqual(chart['x_labels'],['2026F'])
        plan['series'][0]['name_ids']=[99]
        with self.assertRaises(ValueError):build_structure(plan,tokens)


if __name__=='__main__':unittest.main()
