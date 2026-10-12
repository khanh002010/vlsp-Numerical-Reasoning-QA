"""Check chart label bindings and Step-1 argument positions without executing lookups."""
import json
import re
import unicodedata
from vinumqa.utils.dsl_parser import validate_program, parse_program
from vinumqa.cv_module.structure import validate_structure
from vinumqa.cv_module.structure_grounding import resolve_series


def label_key(label):
    """Only typography: no accent stripping, translation, date-order or year guessing."""
    value = ' '.join(unicodedata.normalize('NFC', label).casefold().split())
    value = re.sub(r'\s*([/@])\s*', r'\1', value)
    if re.fullmatch(r'\d{1,2}/\d{1,2}/\d{2,4}', value):
        value = '/'.join(str(int(p)) for p in value.split('/'))
    return value


def bound_label(label, labels):
    if label in labels:
        return label
    matches = [v for v in labels if label_key(v) == label_key(label)]
    return matches[0] if len(matches) == 1 else None


def validate_evidence(program, charts, sources, evidence=None, *, tables=None, text_segments=None, question=""):
    valid, reason = validate_program(program, sources=sources)
    if not valid: return {"valid": False, "errors": [reason], "cv_requests": []}
    steps = parse_program(program)
    errors, requests = [], []
    for step in steps:
        if not step.operator.startswith("chart_"): continue
        image_id = step.args[0]
        if image_id not in charts:
            errors.append(f"Missing chart structure for {image_id}")
            requests.append({"image_id": image_id, "kind": "inspect", "region": "full", "series": ""})
            continue
        chart = validate_structure(charts[image_id])
        if chart.get('x_tick_labels'):
            errors.append(f'Step {step.step_id}: repeated source X labels in {image_id}; positional grounding required')
            requests.append({'image_id':image_id,'kind':'inspect','region':'x_axis','series':''})
            continue
        total = step.operator == "chart_total"
        series = step.args[3] if total else step.args[1]
        names = [s["name"] for s in chart["series"]]
        if bound_label(series, names) is None and resolve_series(series, chart) is None and not (total and series == "none"):
            errors.append(f"Step {step.step_id}: unverified series {series!r} in {image_id}; available={names}")
            requests.append({"image_id": image_id, "kind": "inspect", "region": "legend", "series": series})
        if step.operator in {"chart_at", "chart_total"}:
            x, y = step.args[1:3] if total else step.args[2:4]
            labels = [(x, "x_labels", "x_axis"), (y, "y_labels", "y_axis")]
        else:
            start, end = step.args[2:4]
            labels = [(start, "x_labels", "x_axis"), (end, "x_labels", "x_axis")]
            start_bound, end_bound = bound_label(start, chart['x_labels']), bound_label(end, chart['x_labels'])
            if start != "none" and end != "none" and start_bound is not None and end_bound is not None:
                if not chart["x_order_known"]:
                    errors.append(f"Step {step.step_id}: chart range order needs a full-image inspection")
                    requests.append({"image_id": image_id, "kind": "inspect", "region": "full", "series": series})
                elif chart["x_labels"].index(start_bound) > chart["x_labels"].index(end_bound):
                    errors.append(f"Step {step.step_id}: reversed chart range {start!r} -> {end!r}")
        for label, field, region in labels:
            if label != "none" and bound_label(label, chart[field]) is None:
                errors.append(f"Step {step.step_id}: unverified {field} label {label!r} in {image_id}")
                requests.append({"image_id": image_id, "kind": "inspect", "region": region, "series": series if series != "none" else ""})
    if evidence is not None:
        try:
            plan = json.loads(evidence) if isinstance(evidence, str) else evidence
            if not isinstance(plan, list) or len(plan) != len(steps): raise ValueError("Step 1 must describe every operation")
            for step, declared in zip(steps, plan):
                if not isinstance(declared, dict) or declared.get("step") != step.step_id or declared.get("operator") != step.operator:
                    raise ValueError("Step-1 operation order differs from the program")
                expected = [{"position": i, "value": arg} for i, arg in enumerate(step.args)]
                if declared.get("arguments") != expected:
                    raise ValueError(f"Step {step.step_id}: argument positions/references differ between Step 1 and program")
        except (ValueError, TypeError) as error:
            errors.append(str(error))
    unique = {json.dumps(r, sort_keys=True): r for r in requests}
    warnings = []
    if tables is not None:
        from vinumqa.nlp_module.inference.semantic_validation import validate_semantics
        semantic = validate_semantics(program, tables, text_segments or [], question)
        errors.extend(semantic["errors"])
        warnings.extend(semantic["warnings"])
    return {"valid": not errors, "errors": errors, "warnings": warnings, "cv_requests": list(unique.values()),
            "scope": "DSL, labels, ranges, argument positions and optional source/graph checks; not proof of question understanding"}
