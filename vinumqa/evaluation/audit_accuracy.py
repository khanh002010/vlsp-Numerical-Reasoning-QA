"""Reproducible per-QID public error audit; no model calls or label rewriting."""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path
import re

from vinumqa.nlp_module.contracts import parse_response
from vinumqa.nlp_module.inference.evidence_validation import validate_evidence
from vinumqa.nlp_module.inference.semantic_validation import validate_semantics
from vinumqa.utils.dsl_parser import parse_program, validate_program, normalize_program, programs_equivalent, MATH_OPS


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def expression(program):
    if not validate_program(program)[0]:
        return None
    nodes = []
    for step in parse_program(program):
        args = []
        for arg in step.args:
            if re.fullmatch(r'#\d+', arg):
                args.append(nodes[int(arg[1:])])
            elif step.operator in MATH_OPS:
                args.append(('number', str(Decimal(arg).normalize())))
            else:
                args.append(('label', arg))
        if step.operator in {'add', 'multiply'}:
            args.sort(key=repr)
        nodes.append((step.operator, tuple(args)))
    # Include all nodes to avoid blessing a correct final answer with unused steps.
    return nodes[-1], sorted(nodes, key=repr)


def audit(source_path, predictions_path, prepared_path):
    source = read(source_path)
    predictions = read(predictions_path)
    ids = [r['qid'] for r in predictions]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate prediction QIDs')
    pred = {r['qid']: r.get('predicted', r.get('program', '')) for r in predictions}
    if set(pred) != {s['qid'] for s in source}:
        raise ValueError('Predictions must contain every source QID exactly once')
    prepared = read(prepared_path)
    prepared = {s['qid']: s.get('data', {}) for s in prepared['samples']}
    rows, categories, groups, images = [], Counter(), defaultdict(Counter), defaultdict(lambda: {'qids': [], 'gold_binding_errors': []})
    for s in source:
        qid, p = s['qid'], pred[s['qid']]
        gold = normalize_program(s['qa']['program'], allow_newline_separators=True)
        valid, reason = validate_program(p)
        match = programs_equivalent(p, gold)
        gs, ps = parse_program(gold), parse_program(p)
        go, po = [x.operator for x in gs], [x.operator for x in ps]
        same = expression(gold) == expression(p) if valid else False
        category = ('matched' if match else 'empty_or_invalid' if not valid else
                    'same_expression_serialization' if same else
                    'same_operators_different_arguments' if go == po else 'different_operators_or_steps')
        family = '+'.join(t for t in ('chart', 'table') if any(o.startswith(t+'_') for o in go)) or 'math'
        categories[category] += 1
        groups[family].update(total=1, correct=int(match))
        charts = prepared.get(qid, {}).get('charts', {})
        sources = set(s.get('images', {})) | set(s.get('tables', {}))
        binding = validate_evidence(gold, charts, sources)
        sem_gold = validate_semantics(gold, s.get('tables', {}), s.get('text', []), s['qa']['question'])
        sem_pred = validate_semantics(p, s.get('tables', {}), s.get('text', []), s['qa']['question'])
        prepared_gold = parse_response(prepared[qid].get('output', ''))['program'] if qid in prepared else ''
        row = dict(qid=qid, question=s['qa']['question'], gold=gold, prediction=p, match=match,
                   category=category, family=family, syntax_error=None if valid else reason,
                   gold_binding_errors=binding['errors'], gold_semantic_errors=sem_gold['errors'],
                   prediction_semantic_errors=sem_pred['errors'], prepared_target_matches=programs_equivalent(gold, prepared_gold),
                   images=s.get('images', {}))
        rows.append(row)
        for request in binding.get('cv_requests', []):
            name = s['images'][request['image_id']]
            images[name]['qids'].append(qid)
            images[name]['gold_binding_errors'].extend(binding['errors'])
    return {'source_sha256': hashlib.sha256(Path(source_path).read_bytes()).hexdigest(),
            'prediction_sha256': hashlib.sha256(Path(predictions_path).read_bytes()).hexdigest(),
            'metric': 'Existing local programs_equivalent, unchanged; not official evaluator',
            'total': len(rows), 'correct': categories['matched'], 'accuracy': categories['matched']/len(rows),
            'categories': dict(categories), 'groups': dict(groups),
            'gold_binding_failed': sum(bool(r['gold_binding_errors']) for r in rows),
            'gold_semantic_flagged': sum(bool(r['gold_semantic_errors']) for r in rows),
            'prepared_target_mismatches': sum(not r['prepared_target_matches'] for r in rows),
            'ocr_review_images': {k: {'qids': sorted(set(v['qids'])), 'errors': sorted(set(v['gold_binding_errors']))} for k,v in images.items()},
            'rows': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', default='data/public_test/public_test.json')
    parser.add_argument('--predictions', default='submit/public_test/results.json')
    parser.add_argument('--prepared', default='prepared/public_test_structured.json')
    parser.add_argument('--output', default='reports/public_accuracy_v2/audit.json')
    args = parser.parse_args()
    report = audit(args.source, args.predictions, args.prepared)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in {'rows','ocr_review_images'}}, ensure_ascii=False, indent=2))
    print('Images needing label review:', len(report['ocr_review_images']), 'Report:', path)


if __name__ == '__main__':
    main()
