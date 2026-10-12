"""Inventory all image sets; optionally run the current OCR pipeline on every image."""
import argparse
from pathlib import Path
from collections import Counter
from PIL import Image
from vinumqa.nlp_module.data_prep.incremental import write_json


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-root',type=Path,default=Path('data'))
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--ocr',action='store_true')
    p.add_argument('--retry-failed',action='store_true')
    args=p.parse_args();store=None;rows=[]
    if args.ocr:
        from vinumqa.cv_module.structure_store import ChartStructureStore,SavedVisionFailure
        store=ChartStructureStore(args.output_dir/'chart_structures.json',
            model_id='Qwen/Qwen2.5-VL-7B-Instruct',load_in_4bit=True,read_mode='reviewed')
    paths=sorted(x for x in args.data_root.rglob('*') if x.suffix.lower() in {'.png','.jpg','.jpeg','.webp'})
    try:
        for i,path in enumerate(paths,1):
            row={'path':str(path),'split':path.relative_to(args.data_root).parts[0]}
            try:
                with Image.open(path) as im:
                    im.load();w,h=im.size
                    row.update(width=w,height=h,pixels=w*h,mode=im.mode,needs_downscale=w*h>1400000,status='readable')
            except Exception as e:row.update(status='image_error',error=str(e))
            if store and row['status']=='readable':
                try:
                    chart=store.get(path,retry_failed=args.retry_failed)
                    row.update(status='ocr_ok',source_ambiguous=bool(chart.get('x_tick_labels')),
                               x_labels_complete=chart['x_labels_complete'],series_complete=chart['series_complete'])
                except SavedVisionFailure as e:row.update(status='ocr_error',error=str(e))
            rows.append(row)
            if store: print(f'[{i}/{len(paths)}] {path.name}: {row["status"]}',flush=True)
            write_json(args.output_dir/'image_audit.json',{'ocr_executed':args.ocr,
                'counts':dict(Counter(r['status'] for r in rows)),'images':rows,
                'limitation':'Image readability and OCR status are not pixel-grounded accuracy.'})
    finally:
        if store:store.close()
    print(dict(Counter(r['status'] for r in rows)),flush=True)


if __name__=='__main__':main()
