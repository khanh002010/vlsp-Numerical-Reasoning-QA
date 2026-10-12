"""Re-read audited images, including semantically incorrect status=ok records.

Writes a separate, resumable store and leaves the input artifact untouched.
"""
import argparse
import copy
import hashlib
import json
import time
from pathlib import Path

from vinumqa.nlp_module.data_prep.incremental import write_json


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def repair(source, queue, data_root, output_dir, max_minutes=90, store_factory=None):
    from vinumqa.cv_module.structure_store import ChartStructureStore, SavedVisionFailure
    source, queue, data_root, output_dir = map(Path,(source,queue,data_root,output_dir))
    source=source.resolve();output_dir=output_dir.resolve()
    if source in {output_dir/'chart_structures.json',output_dir/'retried_chart_structures.json'}:
        raise ValueError('Output must not overwrite source; choose another output directory')
    original=json.loads(source.read_text(encoding='utf-8'))
    audit=json.loads(queue.read_text(encoding='utf-8'))
    jobs=[];seen=set()
    for item in audit['images']:
        split=item['split'];name=item['image']
        if split not in {'train','public_test','private_test'} or Path(name).name!=name or '/' in name or '\\' in name:
            raise ValueError('Invalid audited image path')
        path=data_root/split/(split+'_images')/name
        sha=digest(path)
        if sha not in original['images']:raise ValueError('Image hash missing from input store: '+name)
        if sha not in seen:jobs.append((path,sha));seen.add(sha)
    output_dir.mkdir(parents=True,exist_ok=True)
    identity={'source_sha256':digest(source),'queue_sha256':digest(queue)}
    manifest=output_dir/'repair_manifest.json'
    if manifest.exists():
        if json.loads(manifest.read_text(encoding='utf-8'))!=identity:
            raise ValueError('Source/queue changed; use a new output directory')
    else:write_json(manifest,identity)
    snapshot=output_dir/'source_snapshot.json'
    if not snapshot.exists():write_json(snapshot,original)
    factory=store_factory or ChartStructureStore
    store=factory(output_dir/'retried_chart_structures.json',
                  model_id=original['identity']['model'],load_in_4bit=original['identity'].get('load_in_4bit',False),
                  read_mode='reviewed')
    merged_path=output_dir/'chart_structures.json'
    merged=copy.deepcopy(original)
    # A mixed store explicitly retains per-record origin recipes. Retained rows are
    # NOT presented as having passed the new reader or a human accuracy check.
    merged['identity']=store.identity
    merged['repair_provenance']={**identity,'selected_images':len(jobs),
        'retained_outside_queue':len(original['images'])-len(jobs),
        'input_identity':original['identity'],'human_verified':False}
    for row in merged['images'].values():
        row.setdefault('reader_identity',original['identity'])
    for sha,row in store.data['images'].items():
        if sha not in seen:raise ValueError('Retry store contains an image outside this repair queue')
        merged['images'][sha]=copy.deepcopy(row)
        merged['images'][sha]['reader_identity']=store.identity
    write_json(merged_path,merged)
    start=time.monotonic()
    print(f'[Repair] selected={len(jobs)}, retained={len(original["images"])-len(jobs)}',flush=True)
    try:
        for i,(path,sha) in enumerate(jobs,1):
            if time.monotonic()-start>=max_minutes*60:
                print('[Repair] Time budget reached between images; progress saved',flush=True);break
            previous=store.data['images'].get(sha)
            if previous and previous['status']=='ok':
                print(f'[{i}/{len(jobs)}] {path.name}: SKIP_ALREADY_REREAD',flush=True)
                continue
            print(f'[{i}/{len(jobs)}] {path.name}: START',flush=True)
            try:store.get(path,retry_failed=True)
            except SavedVisionFailure as e:print('  SAVED_ERROR: '+str(e),flush=True)
            row=copy.deepcopy(store.data['images'][sha])
            row['reader_identity']=store.identity
            merged['images'][sha]=row
            write_json(merged_path,merged)
            print('  SAVED_'+row['status'].upper(),flush=True)
    finally:store.close()
    print('Saved '+str(merged_path)+'; OCR success still requires pixel review.',flush=True)
    return merged


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--queue',type=Path,required=True)
    p.add_argument('--data-root',type=Path,default=Path('data'))
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--max-minutes',type=float,default=90)
    a=p.parse_args()
    if a.max_minutes<=0:p.error('--max-minutes must be positive')
    repair(a.source,a.queue,a.data_root,a.output_dir,a.max_minutes)


if __name__=='__main__':main()
