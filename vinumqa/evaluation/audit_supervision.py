"""Audit target/source compatibility without rewriting labels or deleting samples."""
import argparse
import json
from pathlib import Path
from vinumqa.nlp_module.contracts import parse_response, source_ids
from vinumqa.nlp_module.inference.evidence_validation import validate_evidence
from vinumqa.nlp_module.training.supervision import load_prepared_pair


def audit_rows(rows):
    issues = []
    for row in rows:
        target = parse_response(row['output'])
        check = validate_evidence(target['program'], row.get('charts', {}), source_ids(row['input']),
                                  target.get('extracted_values', ''))
        if not check['valid']:
            issues.append({'qid': row['qid'], 'errors': check['errors'], 'cv_requests': check['cv_requests']})
    return {'total': len(rows), 'target_binding_failed': len(issues), 'target_binding_passed': len(rows)-len(issues),
            'note': 'Binding agreement is not OCR pixel accuracy. Aliases and sparse time axes can also fail.',
            'issues': issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--train-data', default='prepared/train_structured.json')
    parser.add_argument('--val-data', default='prepared/public_test_structured.json')
    parser.add_argument('--output', default='reports/public_accuracy_v2/supervision.json')
    args = parser.parse_args()
    train, valid = load_prepared_pair(args.train_data, args.val_data)
    report = {'train': audit_rows(train), 'public_test': audit_rows(valid)}
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    for name, result in report.items():
        print(name, {k:v for k,v in result.items() if k != 'issues'})


if __name__ == '__main__': main()
