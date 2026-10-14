import unittest
from vinumqa.cv_module.hybrid_pilot import tokens_from_result, build_structure


class HybridTests(unittest.TestCase):
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
