"""Experimental PP-OCR text boxes + Qwen visual role assignment, in separate processes."""
import argparse
import hashlib
import json
import time
from pathlib import Path
from PIL import Image
from vinumqa.cv_module.chart_to_table.image_preprocessing import preprocess_image
from vinumqa.nlp_module.data_prep.incremental import write_json


def tokens_from_result(result, width, height):
    """PaddleOCR 3.x res.json: aligned texts, scores and polygon coordinates."""
    data = result.get('res', result)
    texts, scores, polys = (data[k] for k in ('rec_texts', 'rec_scores', 'rec_polys'))
    if not len(texts) == len(scores) == len(polys): raise ValueError('Unaligned Paddle OCR outputs')
    tokens = []
    for text, confidence, poly in zip(texts, scores, polys):
        if not isinstance(text, str) or not text.strip(): continue
        xs, ys = [float(p[0]) for p in poly], [float(p[1]) for p in poly]
        box = [max(0,min(xs)/width),max(0,min(ys)/height),min(1,max(xs)/width),min(1,max(ys)/height)]
        from vinumqa.cv_module.structure import validate_box
        validate_box(box)
        tokens.append({'id': len(tokens), 'text': text, 'score': float(confidence), 'box': box})
    return tokens


def build_structure(plan, tokens):
    """Text is assembled ONLY from selected OCR IDs; Qwen supplies relationships."""
    from vinumqa.cv_module.structure import validate_structure
    by_id = {t['id']: t for t in tokens}
    def words(ids, allow_empty=False):
        if not isinstance(ids, list) or (not ids and not allow_empty): raise ValueError('Missing OCR token IDs')
        if any(type(i) is not int or i not in by_id for i in ids) or len(set(ids)) != len(ids):
            raise ValueError('Unknown or duplicated OCR token ID')
        return ' '.join(by_id[i]['text'] for i in ids)
    title = words(plan['title_ids'], True)
    series = [{'name': words(s['name_ids']), 'color': s.get('color',''), 'axis': s['axis'],
               'unit': words(s['unit_ids'],True)} for s in plan['series']]
    if any(s['axis'] not in {'left','right','none'} for s in series): raise ValueError('Invalid axis binding')
    for field in ('x_labels_complete','series_complete'):
        if type(plan.get(field)) is not bool: raise ValueError('Missing boolean '+field)
    if not isinstance(plan.get('uncertain'), list) or any(not isinstance(s,str) for s in plan['uncertain']):
        raise ValueError('uncertain must be a string list')
    return validate_structure({'title':title, 'kind':plan['kind'], 'series':series,
        'x_labels':[words(ids) for ids in plan['x_label_ids']],
        'y_labels':[words(ids) for ids in plan['y_label_ids']],
        'x_labels_complete':plan['x_labels_complete'], 'series_complete':plan['series_complete'],
        'layout':plan['layout'], 'series_source':plan['series_source'],
        'regions':{}, 'uncertain':plan['uncertain']})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase',choices=['ocr','structure'],required=True)
    parser.add_argument('--images',type=Path,default=Path('data/public_test/public_test_images'))
    parser.add_argument('--reference',type=Path,default=Path('reports/ocr_pilot10/pixel_references.json'))
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    refs=json.loads(args.reference.read_text(encoding='utf-8'))
    names=list(refs['images'])
    if len(names)!=10: raise ValueError('This pilot expects exactly ten images')
    for name in names:
        digest=hashlib.sha256((args.images/name).read_bytes()).hexdigest()
        if refs.get('sha256',{}).get(name,digest)!=digest: raise ValueError('Image changed: '+name)
    if args.phase=='ocr':
        from paddleocr import PaddleOCR
        from importlib.metadata import version
        # Documented native pipeline, explicit v5 + Vietnamese. CPU avoids changing CUDA packages.
        # Avoid the oneDNN PIR ArrayAttribute conversion failure on Kaggle CPUs.
        # Set the pipeline option explicitly so all detection/recognition models inherit it.
        print('[Paddle OCR] CPU inference; enable_mkldnn=False',flush=True)
        engine=PaddleOCR(ocr_version='PP-OCRv5',lang='vi',device='cpu',enable_mkldnn=False,
            use_doc_orientation_classify=False,use_doc_unwarping=False,use_textline_orientation=False)
        write_json(out/'ocr_environment.json',{'paddleocr':version('paddleocr'),
            'paddlepaddle':version('paddlepaddle'),'ocr_version':'PP-OCRv5','lang':'vi','device':'cpu',
            'enable_mkldnn':False})
        for i,name in enumerate(names,1):
            print(f'[Paddle OCR {i}/10] {name}',flush=True)
            folder=out/'ocr'/Path(name).stem;folder.mkdir(parents=True,exist_ok=True)
            with Image.open(args.images/name) as original:
                im=preprocess_image(original.convert('RGB'));im.save(folder/'input.png')
                width,height=im.size
            started=time.monotonic()
            results=list(engine.predict(input=str(folder/'input.png')))
            if len(results)!=1: raise ValueError('Expected one OCR page per image')
            result=results[0]
            result.save_to_json(str(folder/'raw.json'))
            result.save_to_img(str(folder))
            raw=json.loads((folder/'raw.json').read_text(encoding='utf-8'))
            tokens=tokens_from_result(raw,width,height)
            write_json(folder/'tokens.json',{'image':name,'size':[width,height],
                'source_sha256':hashlib.sha256((args.images/name).read_bytes()).hexdigest(),
                'seconds':time.monotonic()-started,'tokens':tokens})
            print(f'  saved {len(tokens)} text regions',flush=True)
        return
    from vinumqa.cv_module.structure_reader import ChartStructureReader
    from vinumqa.evaluation.score_ocr_labels import score
    reader=ChartStructureReader('Qwen/Qwen2.5-VL-7B-Instruct',load_in_4bit=True,read_mode='reviewed')
    records={}
    store={'identity':{'version':'hybrid-pilot-v1','model':'Qwen/Qwen2.5-VL-7B-Instruct',
                      'ocr':'PP-OCRv5/vi','max_pixels':1400000},'images':{}}
    prompt='''Inspect the chart image and OCR candidates. Assign visual roles using token IDs only.
OCR text may be WRONG: verify against pixels. Never infer missing years or percentages.
No bounding box generation. Reuse OCR IDs to group multiline labels in reading order.
Keep series names separate from numeric scale ticks and units. A top title is not a legend.
Do not bind series to right axis merely because its label is at right. Pie has axis none.
Numeric Y ticks are NOT y_label_ids. Only horizontal-bar row categories belong there.
Sparse printed ticks mean x_labels_complete=false. If needed text is absent/wrong,
describe it in uncertain, keep completeness false; do not invent token IDs or strings.
Return ONE JSON object with ALL these fields:
{"title_ids":[],"kind":"line","series":[{"name_ids":[0],"color":"","axis":"left","unit_ids":[]}],
"x_label_ids":[[1]],"y_label_ids":[],"x_labels_complete":false,"series_complete":false,
"series_source":"legend","layout":{"orientation":"vertical","x_axis_type":"time","y_axis_type":"numerical"},"uncertain":[]}
kind: line/bar/mixed/pie/table/unknown; orientation: vertical/horizontal/none/matrix;
axis type: time/categorical/numerical/none/unknown. series_source: legend/title/unknown.
IDs in the example are placeholders. Unit IDs must reference printed units, not tick numbers.
No question, answer or numerical computation is required. OCR candidates:
'''
    try:
        for i,name in enumerate(names,1):
            print(f'[Qwen structure {i}/10] {name}',flush=True)
            data=json.loads((out/'ocr'/Path(name).stem/'tokens.json').read_text(encoding='utf-8'))
            sha=hashlib.sha256((args.images/name).read_bytes()).hexdigest()
            if sha!=data['source_sha256']: raise ValueError('Stale OCR: '+name)
            record={'image':name,'sha256':sha,'status':'error'}
            reader.last_generation={'attempts':[]}
            started=time.monotonic();feedback=''
            for attempt in range(2):
                try:
                    plan=reader._read(str(args.images/name),prompt+json.dumps(data['tokens'],ensure_ascii=False)+feedback,
                                      budgets=(2048,),reset=False,phase='ocr_role_assignment')
                    record['role_assignment']=plan
                    structure=build_structure(plan,data['tokens'])
                    record.update(status='ok',structure=structure)
                    record.pop('error',None)
                    break
                except ValueError as error:
                    record['error']=str(error)
                    feedback='\nPrevious assignment failed validation: '+str(error)+'. Recheck pixels and return all fields.'
            record.update(generation=reader.last_generation,seconds=time.monotonic()-started,
                          verification='schema_checked_not_human_verified')
            store['images'][sha]=record;records[name]=record
            write_json(out/'chart_structures.json',store)
            print('  '+record['status']+' '+record.get('error',''),flush=True)
    finally:reader.close()
    report=score(records,refs['images'])
    report['scope']=refs['scope']
    report['status_counts']={s:sum(r['status']==s for r in records.values()) for s in ('ok','error')}
    write_json(out/'ocr_accuracy_pilot.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='images'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
